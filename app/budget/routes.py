"""backend/app/budget/routes.py."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Budget, BudgetItem , Profile # Ensure BudgetItem is imported
from app.forms import BudgetForm, IncomeForm
from app.budget.budget_logic import calculate_budget, create_excel

budget_bp = Blueprint('budget', __name__, template_folder='budget')

@budget_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_budget():
    form = BudgetForm()
    if request.method == 'POST':
        print("✅ POST request received!")
        
        # Capture the budget name from the form (and store it in session if needed)
        session['budget_name'] = form.budget_name.data
        
        # Get the list of category names using the new input name "category_name[]"
        category_names = request.form.getlist('category_name[]')
        if not category_names:
            flash("No categories provided. Please add at least one category.", "danger")
            return redirect(url_for('budget.create_budget'))
        
        categories = {}
        # For each category, get its subcategories using the corresponding index
        for i, category in enumerate(category_names):
            # For each category card, the subcategories inputs are named "subcategory_i[]"
            subcategories = request.form.getlist(f'subcategory_{i}[]')
            # Filter out any empty subcategory strings
            subcategories = [sub for sub in subcategories if sub.strip() != '']
            categories[category] = subcategories

        session['categories'] = categories
        session.modified = True  # Ensures the session updates properly
        print("💾 Session Data Saved:", session.get('categories'))
        
        flash("Budget categories created! Proceeding to input details.", "success")
        return redirect(url_for('budget.input_budget'))
    
    print("📌 GET request received - Rendering Form")
    return render_template('budget/budget_create.html', form=form)





@budget_bp.route('/input', methods=['GET', 'POST'])
@login_required
def input_budget():
    # Ensure the user has a profile
    if not current_user.profile:
        flash("Please complete your profile before creating a budget.", "warning")
        return redirect(url_for('profile.profile'))

    # Retrieve categories from session. Expected format: { "Category": ["Subcat1", "Subcat2", ...], ... }
    categories = session.get('categories', {})
    print("DEBUG: Retrieved categories from session:", categories)
    if not categories:
        flash("No categories found. Please start by creating your budget.", "warning")
        return redirect(url_for('budget.create_budget'))

    form = BudgetForm()  # Your BudgetForm should include at least an 'income' field

    if request.method == 'POST':
        print("✅ Budget input form submitted!")  # Debug: POST received

        # Step 1: Collect minimum and preferred payments from the form inputs
        budget_details = {}
        for category, budget_items in categories.items():
            budget_details[category] = {}
            for item_name in budget_items:
                input_min_name = f'min_{item_name}'
                input_pref_name = f'pref_{item_name}'
                min_payment = request.form.get(input_min_name, 0)
                pref_payment = request.form.get(input_pref_name, 0)
                try:
                    budget_details[category][item_name] = {
                        'min_payment': float(min_payment),
                        'pref_payment': float(pref_payment)
                    }
                except ValueError:
                    budget_details[category][item_name] = {
                        'min_payment': 0.0,
                        'pref_payment': 0.0
                    }
                print(f"DEBUG: Processing item '{item_name}' in category '{category}' with {input_min_name}={min_payment} and {input_pref_name}={pref_payment}")

        print("DEBUG: Collected budget_details:", budget_details)

        # Step 2: Create a new Budget instance and commit it to get its ID
        try:
            new_budget = Budget(
                user_id=current_user.id,
                profile_id=current_user.profile.id,  # Ensure budget is linked to user's profile
                name=session.get('budget_name', "My New Budget"),  # Use budget name from session
                gross_income=(form.income.data if form.income.data is not None else 0),
                # Do not assign income_type and state here since they're properties that pull from the profile
                tax_withholding=0,  # Default to 0
                retirement_contribution=(current_user.profile.retirement_contribution if current_user.profile else 0),
                benefit_deductions=(current_user.profile.benefit_deductions if current_user.profile else 0)
            )
            db.session.add(new_budget)
            db.session.commit()
            print(f"DEBUG: New Budget Created with ID: {new_budget.id}")
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: Error creating Budget: {e}")
            flash("An error occurred while saving your budget. Please try again.", "danger")
            return redirect(url_for('budget.input_budget'))

        # Step 3: Create BudgetItems using new_budget.id and the collected details
        for category, budget_items in categories.items():
            for item_name in budget_items:
                try:
                    min_payment = budget_details[category][item_name]['min_payment']
                    pref_payment = budget_details[category][item_name]['pref_payment']
                    print(f"DEBUG: Creating BudgetItem for '{item_name}' in '{category}' using Budget ID: {new_budget.id}")
                    budget_item = BudgetItem(
                        category=category,
                        name=item_name,
                        minimum_payment=min_payment,
                        preferred_payment=pref_payment,
                        budget_id=new_budget.id  # Associate with the new budget
                    )
                    db.session.add(budget_item)
                    print(f"DEBUG: BudgetItem for '{item_name}' added to session.")
                except Exception as e:
                    print(f"ERROR: Error creating BudgetItem for '{item_name}': {e}")

        # Step 4: Commit all BudgetItems to the database
        try:
            print("DEBUG: Flushing session to database...")
            db.session.flush()  # Push changes (not a permanent commit)
            print("DEBUG: Data flushed to the database!")
            db.session.commit()
            print("DEBUG: Data successfully committed to the database!")
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: Error committing BudgetItems: {e}")
            flash("An error occurred while saving your budget items. Please try again.", "danger")
            return redirect(url_for('budget.input_budget'))

        # Step 5: Optionally store details in session (for later use, e.g., in results)
        session['budget_details'] = budget_details
        session.modified = True
        flash("Budget details successfully captured. View your calculated results.", "success")
        return redirect(url_for('budget.results'))

    print("DEBUG: GET request received - Rendering Budget Input Form")
    return render_template('budget/budget_input.html', categories=categories, form=form)









@budget_bp.route('/results', methods=['GET', 'POST'])
@login_required
def results():
    budget_details = session.get('budget_details', {})
    income = float(request.form.get('income', 0)) if request.method == 'POST' else 0

    # Compute budget summary
    summary = calculate_budget(budget_details, income)

    # Display warnings based on income-to-debt ratio
    if summary['income_to_debt_ratio'] > 0.43:
        flash("Your debt-to-income ratio is considered high risk.", 'danger')
    elif summary['income_to_debt_ratio'] > 0.35:
        flash("Your debt-to-income ratio is concerning.", 'warning')
    else:
        flash("Your debt-to-income ratio is healthy. Keep up the good work!", 'success')

    return render_template('budget/budget_results.html', budget=budget_details, summary=summary)


@budget_bp.route('/save', methods=['POST'])
@login_required
def save_budget():
    budget_details = session.get('budget_details', {})
    budget_name = session.get('budget_name', 'My Budget')
    user_id = current_user.id

    if not budget_details:
        flash("No budget data to save.", "warning")
        return redirect(url_for('main.dashboard'))

    # Create a new budget instance
    budget = Budget(name=budget_name, user_id=user_id)
    db.session.add(budget)
    db.session.commit()

    # Add budget items
    for category, subcategories in budget_details.items():
        for subcategory, payments in subcategories.items():
            budget_item = BudgetItem(
                budget_id=budget.id,
                category=category,
                name=subcategory,
                minimum_payment=payments['min_payment'],
                preferred_payment=payments['pref_payment']
            )
            db.session.add(budget_item)

    db.session.commit()
    flash("Budget saved successfully!", "success")
    return redirect(url_for('main.dashboard'))



@budget_bp.route('/export', methods=['POST'])
@login_required
def export_budget():
    user_data = request.form.to_dict(flat=True)
    budget_details = calculate_budget(user_data)
    return create_excel(budget_details)


@budget_bp.route('/view/<int:budget_id>', methods=['GET'])
@login_required
def view_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    if budget.user_id != current_user.id:
        flash("You are not authorized to view this budget.", "danger")
        return redirect(url_for('main.dashboard'))
    budget_items = BudgetItem.query.filter_by(budget_id=budget.id).all()
    return render_template('budget/view_budget.html', budget=budget, budget_items=budget_items)


@budget_bp.route('/edit/<int:budget_id>', methods=['GET', 'POST'])
@login_required
def edit_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    if budget.user_id != current_user.id:
        flash("You are not authorized to edit this budget.", "danger")
        return redirect(url_for('main.dashboard'))
    
    # Initialize the form with the existing budget data
    form = BudgetForm(obj=budget)
    
    if form.validate_on_submit():
        # Update budget details from form data
        budget.name = form.budget_name.data
        budget.gross_income = form.income.data or 0
        budget.pay_period = form.pay_period.data
        budget.rent = form.rent.data or 0
        # You can update additional fields as needed
        try:
            db.session.commit()
            flash("Budget updated successfully!", "success")
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating your budget. Please try again.", "danger")
    
    return render_template('budget/edit_budget.html', form=form, budget=budget)



@budget_bp.route('/delete/<int:budget_id>', methods=['POST'])
@login_required
def delete_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    if budget.user_id != current_user.id:
        flash("You do not have permission to delete this budget.", "danger")
        return redirect(url_for('main.dashboard'))
    
    db.session.delete(budget)
    db.session.commit()
    flash("Budget deleted successfully!", "success")
    return redirect(url_for('main.dashboard'))


@budget_bp.route('/income', methods=['GET', 'POST'])
@login_required
def income():
    form = IncomeForm()
    profile = Profile.query.filter_by(user_id=current_user.id).first()

    if not profile:
        flash("Please complete your profile before entering budget details.", "warning")
        return redirect(url_for('profile.profile'))  # Redirect to profile setup

    budget = Budget.query.filter_by(user_id=current_user.id, profile_id=profile.id).first()

    if form.validate_on_submit():
        if not budget:
            budget = Budget(user_id=current_user.id, profile_id=profile.id, name="Default Budget")

        budget.gross_income = form.gross_income.data
        budget.gross_income_frequency = form.gross_income_frequency.data

        # Collect and store other income sources
        other_income = []
        for field in form.other_income_sources.entries:
            if field.data['name'] and field.data['amount']:  # Ensure valid data
                other_income.append({
                    'category': field.data['category'],
                    'name': field.data['name'],
                    'amount': field.data['amount'],
                    'frequency': field.data['frequency']
                })

        budget.other_income_sources = other_income if other_income else None

        db.session.add(budget)
        db.session.commit()
        
        flash("Income data saved successfully!", "success")
        return redirect(url_for('main.dashboard'))

    # Pre-populate form with existing budget data
    elif budget:
        form.gross_income.data = budget.gross_income
        form.gross_income_frequency.data = budget.gross_income_frequency

        # Ensure WTForms expects proper fields instead of raw JSON data
        form.other_income_sources.entries = []
        if budget.other_income_sources:
            for income in budget.other_income_sources:
                entry = form.other_income_sources.append_entry()
                entry.category.data = income.get('category', 'other')
                entry.name.data = income.get('name', '')
                entry.amount.data = income.get('amount', 0.0)
                entry.frequency.data = income.get('frequency', 'monthly')

    return render_template('budget/income.html', form=form)







# @budget_bp.route('/input', methods=['GET', 'POST'])
# def input_budget():
#     form = BudgetForm()
#     if form.validate_on_submit():
#         # Process form data and redirect to /results
#         user_data = {
#             'income': form.income.data or 0,
#             'pay_period': form.pay_period.data,
#             'rent': form.rent.data or 0,
#             'utilities': {
#                 'electricity': form.utilities.electricity.data or 0,
#                 'water': form.utilities.water.data or 0,
#                 'internet': form.utilities.internet.data or 0,
#                 'gas': form.utilities.gas.data or 0,
#             },
#             'debts': {
#                 'card1': form.debts.card1.data or 0,
#                 'card2': form.debts.card2.data or 0,
#                 'card3': form.debts.card3.data or 0,
#                 'card4': form.debts.card4.data or 0,
#                 'card5': form.debts.card5.data or 0,
#             },
#             'loans': {
#                 'vehicle1': form.loans.vehicle1.data or 0,
#                 'vehicle2': form.loans.vehicle2.data or 0,
#                 'vehicle3': form.loans.vehicle3.data or 0,
#                 'boat1': form.loans.boat1.data or 0,
#                 'boat2': form.loans.boat2.data or 0,
#                 'boat3': form.loans.boat3.data or 0,
#             },
#             'groceries': form.groceries.data or 0,
#             'transportation': form.transportation.data or 0,
#         }
#         # Save user_data to the session or pass it to the results page
#         request.form = user_data
#         return redirect(url_for('budget.results'))
#     return render_template('budget/budget_input.html', form=form)



# @budget_bp.route('/results', methods=['POST'])
# def results():
#     # Access user data from the request
#     user_data = {
#         'income': float(request.form.get('income', 0) or 0),
#         'pay_period': request.form.get('pay_period', 'monthly'),
#         'rent': float(request.form.get('rent', 0) or 0),
#         'utilities': {
#             'electricity': float(request.form.get('utilities-electricity', 0) or 0),
#             'water': float(request.form.get('utilities-water', 0) or 0),
#             'internet': float(request.form.get('utilities-internet', 0) or 0),
#             'gas': float(request.form.get('utilities-gas', 0) or 0),
#         },
#         'debts': {
#             'card1': float(request.form.get('debts-card1', 0) or 0),
#             'card2': float(request.form.get('debts-card2', 0) or 0),
#             'card3': float(request.form.get('debts-card3', 0) or 0),
#             'card4': float(request.form.get('debts-card4', 0) or 0),
#             'card5': float(request.form.get('debts-card5', 0) or 0),
#         },
#         'loans': {
#             'vehicle1': float(request.form.get('loans-vehicle1', 0) or 0),
#             'vehicle2': float(request.form.get('loans-vehicle2', 0) or 0),
#             'vehicle3': float(request.form.get('loans-vehicle3', 0) or 0),
#             'boat1': float(request.form.get('loans-boat1', 0) or 0),
#             'boat2': float(request.form.get('loans-boat2', 0) or 0),
#             'boat3': float(request.form.get('loans-boat3', 0) or 0),
#         },
#         'groceries': float(request.form.get('groceries', 0) or 0),
#         'transportation': float(request.form.get('transportation', 0) or 0),
#     }

#     # Calculate the budget
#     budget = calculate_budget(user_data)
#     income_to_debt_ratio = budget['income_to_debt_ratio']

#     if income_to_debt_ratio > 0.43:
#         flash("Your debt to income ratio is considered high risk", 'danger')
#     elif income_to_debt_ratio > 0.35:
#         flash("Your debt to income ratio is considered concerning", 'warning')
#     else:
#         flash("Your debt to income ratio is healthy, keep up the good work", 'success')

#     # Pass the cleaned data to calculate_budget
#     budget = calculate_budget(user_data)

#     # Render the results page
#     return render_template('budget/budget_results.html', budget=budget)




# @budget_bp.route('/download', methods=['POST'])
# def download():
#     from app.budget.budget_logic import create_excel  # Import here to avoid circular dependency
#     budget_data = request.form.get('budget_data')
#     response = create_excel(budget_data)
#     return response



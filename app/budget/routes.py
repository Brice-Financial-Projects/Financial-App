"""backend/app/budget/routes.py."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Budget, BudgetItem, Profile  # Ensure BudgetItem is imported
from app.forms import BudgetForm, IncomeForm
from app.budget.budget_logic import calculate_budget, create_excel

budget_bp = Blueprint('budget', __name__, template_folder='budget')

@budget_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_budget():
    form = BudgetForm()
    
    if request.method == 'POST':
        print("✅ POST request received!")
        
        # Store budget name in session
        session['budget_name'] = form.budget_name.data
        
        # Get the list of category names
        category_names = request.form.getlist('category_name[]')
        if not category_names:
            flash("No categories provided. Please add at least one category.", "danger")
            return redirect(url_for('budget.create_budget'))
        
        categories = {}
        # Process categories and subcategories
        for i, category in enumerate(category_names):
            subcategories = request.form.getlist(f'subcategory_{i}[]')
            subcategories = [sub for sub in subcategories if sub.strip() != '']
            categories[category] = subcategories

        session['categories'] = categories
        session.modified = True  # Ensures Flask updates session
        print("💾 Session Data Saved:", session.get('categories'))
        
        flash("Budget categories created! Proceeding to input details.", "success")
        return redirect(url_for('budget.input_budget'))  # ✅ FIX: Redirecting to the correct page
    
    print("📌 GET request received - Rendering Form")
    return render_template('budget/budget_create.html', form=form)


@budget_bp.route('/input', methods=['GET', 'POST'])
@login_required
def input_budget():
    if not current_user.profile:
        flash("Please complete your profile before creating a budget.", "warning")
        return redirect(url_for('profile.profile'))

    categories = session.get('categories', {})
    print("DEBUG: Retrieved categories from session:", categories)
    
    if not categories:
        flash("No categories found. Please start by creating your budget.", "warning")
        return redirect(url_for('budget.create_budget'))

    form = BudgetForm()

    if request.method == 'POST':
        print("✅ Budget input form submitted!")  

        # Step 1: Collect budget details from form inputs
        budget_details = {}
        for category, items in categories.items():
            budget_details[category] = {}
            for item in items:
                min_payment = request.form.get(f'min_{item}', 0)
                pref_payment = request.form.get(f'pref_{item}', 0)
                budget_details[category][item] = {
                    'min_payment': float(min_payment),
                    'pref_payment': float(pref_payment)
                }
                print(f"DEBUG: Captured {item}: Min={min_payment}, Pref={pref_payment}")

        # Step 2: Create Budget and store it
        try:
            new_budget = Budget(
                user_id=current_user.id,
                profile_id=current_user.profile.id,
                name=session.get('budget_name', "My New Budget"),
                gross_income=(form.income.data if form.income.data is not None else 0),
                retirement_contribution=current_user.profile.retirement_contribution,
                benefit_deductions=current_user.profile.benefit_deductions
            )
            db.session.add(new_budget)
            db.session.commit()  # ✅ FIX: Ensure the budget is actually saved!
            print(f"DEBUG: New Budget Created with ID: {new_budget.id}")
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: Error creating Budget: {e}")
            flash("An error occurred while saving your budget. Please try again.", "danger")
            return redirect(url_for('budget.input_budget'))

        # Step 3: Save Budget Items
        for category, items in budget_details.items():
            for item, payments in items.items():
                try:
                    budget_item = BudgetItem(
                        category=category,
                        name=item,
                        minimum_payment=payments['min_payment'],
                        preferred_payment=payments['pref_payment'],
                        budget_id=new_budget.id
                    )
                    db.session.add(budget_item)
                except Exception as e:
                    print(f"ERROR: Error creating BudgetItem for '{item}': {e}")

        # Step 4: Final commit for Budget Items
        try:
            db.session.commit()
            print("DEBUG: All budget items saved successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: Error saving budget items: {e}")
            flash("An error occurred while saving budget items. Please try again.", "danger")
            return redirect(url_for('budget.input_budget'))

        # Step 5: Store for Results Page
        session['budget_details'] = budget_details
        session.modified = True
        flash("Budget details successfully captured. Proceed to income input.", "success")
        return redirect(url_for('budget.income'))  # ✅ Redirecting to Income Entry!

    print("DEBUG: GET request received - Rendering Budget Input Form")
    return render_template('budget/budget_input.html', categories=categories, form=form)


@budget_bp.route('/income', methods=['GET', 'POST'])
@login_required
def income():
    form = IncomeForm()
    profile = Profile.query.filter_by(user_id=current_user.id).first()

    if not profile:
        flash("Please complete your profile before entering income details.", "warning")
        return redirect(url_for('profile.profile'))

    budget = Budget.query.filter_by(user_id=current_user.id, profile_id=profile.id).first()

    if not budget:
        flash("No budget found. Please create a budget first.", "warning")
        return redirect(url_for('budget.create_budget'))

    # Check if the user already has a primary income source
    primary_income = GrossIncome.query.filter_by(budget_id=budget.id, category="W2 Job").first()

    if request.method == 'POST' and form.validate_on_submit():
        if not primary_income:
            # Create a new W2 primary job income entry
            primary_income = GrossIncome(
                budget_id=budget.id,
                category="W2 Job",
                source="Primary Job",
                gross_income=form.gross_income.data,
                frequency=form.gross_income_frequency.data,
                tax_type="W2",
                state_tax_ref=budget.state
            )
            db.session.add(primary_income)
        else:
            # Update existing primary income
            primary_income.gross_income = form.gross_income.data
            primary_income.frequency = form.gross_income_frequency.data

        # Handle additional income sources
        other_income_data = []
        for field in form.other_income_sources.entries:
            if field.data['name'] and field.data['amount']:
                other_income_data.append({
                    'category': field.data['category'],
                    'name': field.data['name'],
                    'amount': field.data['amount'],
                    'frequency': field.data['frequency']
                })

        budget.other_income_sources = other_income_data if other_income_data else None

        db.session.commit()
        flash("Income details saved successfully!", "success")
        return redirect(url_for('budget.results'))

    # Pre-fill form with existing income data
    if primary_income:
        form.gross_income.data = primary_income.gross_income
        form.gross_income_frequency.data = primary_income.frequency

    return render_template('budget/income.html', form=form)


@budget_bp.route('/view/<int:budget_id>', methods=['GET'])
@login_required
def view_budget(budget_id):
    """View an individual budget and its details."""
    budget = Budget.query.get_or_404(budget_id)
    
    if budget.user_id != current_user.id:
        flash("You are not authorized to view this budget.", "danger")
        return redirect(url_for('main.dashboard'))

    budget_items = BudgetItem.query.filter_by(budget_id=budget.id).all()

    return render_template('budget/view_budget.html', budget=budget, budget_items=budget_items)

@budget_bp.route('/edit/<int:budget_id>', methods=['GET', 'POST'])
@login_required
def edit_budget(budget_id):
    """Allow users to edit an existing budget."""
    budget = Budget.query.get_or_404(budget_id)
    
    if budget.user_id != current_user.id:
        flash("You are not authorized to edit this budget.", "danger")
        return redirect(url_for('main.dashboard'))
    
    form = BudgetForm(obj=budget)  # Pre-fill form with existing budget data
    
    if form.validate_on_submit():
        # Update budget fields with submitted form data
        budget.name = form.budget_name.data
        budget.gross_income = form.income.data or 0
        budget.pay_cycle = form.pay_cycle.data
        budget.retirement_contribution = form.retirement_contribution.data or 0
        budget.benefit_deductions = form.benefit_deductions.data or 0

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
    """Allow users to delete an existing budget."""
    budget = Budget.query.get_or_404(budget_id)

    if budget.user_id != current_user.id:
        flash("You do not have permission to delete this budget.", "danger")
        return redirect(url_for('main.dashboard'))
    
    try:
        db.session.delete(budget)
        db.session.commit()
        flash("Budget deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the budget. Please try again.", "danger")

    return redirect(url_for('main.dashboard'))








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



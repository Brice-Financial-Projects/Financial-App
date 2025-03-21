"""backend/app/budget/routes.py."""

from flask import Blueprint, render_template, request, redirect, current_app, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Budget, BudgetItem, Profile, GrossIncome
from app.forms import BudgetForm, IncomeForm
from app.budget.budget_logic import BudgetCalculator
from contextlib import contextmanager



budget_bp = Blueprint('budget', __name__, template_folder='budget')

@budget_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_budget():
    form = BudgetForm()

    # Ensure the budget name exists in session (redirect if not)
    budget_name = session.get('budget_name')
    if not budget_name:
        flash("Please enter a budget name before proceeding.", "warning")
        return redirect(url_for('budget.budget_name'))

    if request.method == 'POST':
        category_names = request.form.getlist('category_name[]')

        if not category_names:
            flash("No categories provided. Please add at least one category.", "danger")
            return redirect(url_for('budget.create_budget'))

        # Clear categories from session to avoid conflicts
        session.pop('categories', None)

        # Store categories in session for tracking
        categories = {}
        for i, category in enumerate(category_names):
            subcategories = request.form.getlist(f'subcategory_{i}[]')
            subcategories = [sub.strip() for sub in subcategories if sub.strip()]
            categories[category] = subcategories

        session['categories'] = categories
        session.modified = True  

        flash("Budget categories created! Proceeding to input details.", "success")
        return redirect(url_for('budget.input_budget'))

    return render_template('budget/budget_create.html', form=form, budget_name=budget_name)





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

    # Get the most recent budget by ordering by ID in descending order
    budget = Budget.query.filter_by(user_id=current_user.id, profile_id=profile.id).order_by(Budget.id.desc()).first()
    print(f"Current budget ID: {budget.id if budget else 'None'}")

    if not budget:
        flash("No budget found. Please create a budget first.", "warning")
        return redirect(url_for('budget.create_budget'))

    # Initialize the income_entries list - prevent UnboundLocalError
    income_entries = []
    
    primary_income = GrossIncome.query.filter_by(budget_id=budget.id, category="W2 Job").first()

    if request.method == 'POST':
        print("Form Data:", request.form)
        
        # Print CSRF tokens for debugging
        form_csrf = request.form.get('csrf_token') 
        expected_csrf = form.csrf_token.current_token
        print(f"CSRF DEBUG - Form token: {form_csrf}")
        print(f"CSRF DEBUG - Expected token: {expected_csrf}")
        
        # Use the proper CSRF validation method
        if form.validate_on_submit():
            try:
                print(f"====== PROCESSING INCOME FORM FOR BUDGET {budget.id} ======")
                
                # STEP 1: Handle primary income (W2 Job)
                if form.gross_income.data and form.gross_income_frequency.data:
                    if not primary_income:
                        primary_income = GrossIncome(
                            budget_id=budget.id,
                            category="W2 Job",
                            source="Primary Job",
                            gross_income=form.gross_income.data,
                            frequency=form.gross_income_frequency.data,
                            tax_type="W2",
                            state_tax_ref=profile.state
                        )
                        db.session.add(primary_income)
                        print(f"Adding primary income: ${form.gross_income.data} ({form.gross_income_frequency.data})")
                    else:
                        primary_income.gross_income = form.gross_income.data
                        primary_income.frequency = form.gross_income_frequency.data
                        primary_income.state_tax_ref = profile.state
                        print(f"Updating primary income: ${form.gross_income.data} ({form.gross_income_frequency.data})")
                    
                    try:
                        # Save primary income immediately
                        db.session.commit()
                        print("Primary income saved successfully")
                    except Exception as e:
                        print(f"ERROR! Failed to save primary income: {str(e)}")
                        db.session.rollback()

                # STEP 2: Process manually submitted income sources from HTML form first
                # We'll collect them in memory before making any database changes
                new_incomes = []
                sources_added = 0
                
                for i in range(10):  # Limit to 10 entries maximum for safety
                    category = request.form.get(f'other_income_sources-{i}-category')
                    name = request.form.get(f'other_income_sources-{i}-name')
                    amount_str = request.form.get(f'other_income_sources-{i}-amount')
                    frequency = request.form.get(f'other_income_sources-{i}-frequency')
                    
                    # Break if we've processed all entries
                    if category is None:
                        break
                    
                    # Only add if we have both name and amount
                    if name and amount_str:
                        try:
                            amount = float(amount_str)
                            
                            # Determine the tax type based on the category
                            tax_type = "W2" if category == "side_job" else "Other"
                            
                            # Create the income object but don't add to session yet
                            new_income = GrossIncome(
                                budget_id=budget.id,
                                category=category,
                                source=name,
                                gross_income=amount,
                                frequency=frequency,
                                tax_type=tax_type,
                                state_tax_ref=profile.state
                            )
                            
                            new_incomes.append(new_income)
                            sources_added += 1
                            print(f"Created income object: {name} - ${amount} ({frequency}) with tax_type: {tax_type}")
                        except (ValueError, TypeError) as e:
                            print(f"Error with amount conversion: {e}")
                            flash(f"Invalid amount for income source '{name}'", "danger")
                    else:
                        print(f"Skipping entry {i}: missing name ({name}) or amount ({amount_str})")
                
                # STEP 3: Delete existing additional income sources only if we have new ones
                if new_incomes:
                    existing_other_income = GrossIncome.query.filter(
                        GrossIncome.budget_id == budget.id,
                        GrossIncome.category != "W2 Job"
                    ).all()

                    print(f"Found {len(existing_other_income)} existing income sources for budget {budget.id}")
                    
                    for income in existing_other_income:
                        print(f"Deleting income source: {income.source} - ${income.gross_income}")
                        db.session.delete(income)
                    
                    try:
                        # Commit deletions immediately
                        db.session.commit()
                        print("Deleted existing income sources")
                    except Exception as e:
                        print(f"ERROR! Failed to delete existing income sources: {str(e)}")
                        db.session.rollback()
                    
                    # STEP 4: Now add all the new income sources
                    for income in new_incomes:
                        db.session.add(income)
                    
                    try:
                        # Commit all the new income sources
                        db.session.commit()
                        print(f"Successfully added {len(new_incomes)} new income sources")
                    except Exception as e:
                        print(f"ERROR! Failed to add new income sources: {str(e)}")
                        db.session.rollback()

                # Double-check that entries were saved
                verification = GrossIncome.query.filter(
                    GrossIncome.budget_id == budget.id,
                    GrossIncome.category != "W2 Job"
                ).all()
                
                print(f"Final verification: Found {len(verification)} income sources in database")
                for inc in verification:
                    print(f"  - Verified: {inc.source}: ${inc.gross_income} ({inc.frequency}) - Tax Type: {inc.tax_type}")
                
                if sources_added > 0:
                    flash(f"Successfully saved {sources_added} income sources!", "success")
                else:
                    flash("No additional income sources were added.", "info")

                # Check which button was clicked
                if 'preview' in request.form:
                    return redirect(url_for('budget.preview'))  # Redirect to preview page
                return redirect(url_for('budget.income'))  # Stay on same page if "Save" was clicked

            except Exception as e:
                db.session.rollback()
                print(f"ERROR IN INCOME FORM PROCESSING: {str(e)}")
                flash(f"An error occurred while saving income details: {str(e)}", "danger")
        else:
            # Form validation failed
            print("Form Validation Errors:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error in {field}: {error}", "danger")
            
            # Re-create income entries list from the form data for re-rendering the form
            i = 0
            income_entries = []
            while True:
                category = request.form.get(f'other_income_sources-{i}-category')
                name = request.form.get(f'other_income_sources-{i}-name')
                amount = request.form.get(f'other_income_sources-{i}-amount')
                frequency = request.form.get(f'other_income_sources-{i}-frequency')
                
                if category is None:
                    break
                    
                income_entries.append({
                    'category': category,
                    'name': name,
                    'amount': amount,
                    'frequency': frequency
                })
                i += 1

    # Pre-fill form with existing data
    if primary_income:
        form.gross_income.data = primary_income.gross_income
        form.gross_income_frequency.data = primary_income.frequency

    # Always regenerate a fresh CSRF token before rendering the form
    # This ensures that it matches what Flask-WTF expects
    form.csrf_token.data = form.csrf_token.current_token
    print(f"Generated fresh CSRF token: {form.csrf_token.current_token}")
    
    # Pull fresh data from database for display
    other_income = GrossIncome.query.filter(
        GrossIncome.budget_id == budget.id,
        GrossIncome.category != "W2 Job"
    ).all()

    print(f"Display: Found {len(other_income)} other income sources for budget {budget.id}:")
    for inc in other_income:
        print(f"  - {inc.source}: ${inc.gross_income} ({inc.frequency}) - Tax Type: {inc.tax_type}")
        income_entries.append({
            'category': inc.category,
            'name': inc.source,
            'amount': inc.gross_income,
            'frequency': inc.frequency
        })
    
    # Set main form fields
    if primary_income:
        form.gross_income.data = primary_income.gross_income
        form.gross_income_frequency.data = primary_income.frequency
    
    # Return the form without any empty entries if none exist in the database
    return render_template('budget/income.html', form=form, other_income=income_entries)





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


@budget_bp.route('/name', methods=['GET', 'POST'])
@login_required
def budget_name():
    form = BudgetForm()

    # Clear session data related to previous budgets (except for income)
    session.pop('categories', None)
    session.pop('budget_name', None)

    # Get all existing budgets for this user
    existing_budgets = Budget.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST':
        budget_name = form.budget_name.data.strip()

        # Check if the budget name is already taken
        existing_budget = Budget.query.filter_by(user_id=current_user.id, name=budget_name).first()
        if existing_budget:
            flash("A budget with this name already exists. Please choose a different name.", "danger")
            return redirect(url_for('budget.budget_name'))

        # Store the new budget name in session
        session['budget_name'] = budget_name
        flash("Budget name saved! Proceed to budget details.", "success")
        return redirect(url_for('budget.create_budget'))

    return render_template('budget/name.html', form=form, existing_budgets=existing_budgets)


@budget_bp.route('/preview', methods=['GET', 'POST'])
@login_required
def preview():
    """Display all budget details for review before final submission."""
    # Get the user's profile
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash("Please complete your profile before previewing your budget.", "warning")
        return redirect(url_for('profile.profile'))
    
    # Get the most recent budget
    budget = Budget.query.filter_by(user_id=current_user.id).order_by(Budget.id.desc()).first()
    if not budget:
        flash("No budget found. Please create a budget first.", "warning")
        return redirect(url_for('budget.budget_name'))
    
    print(f"Loading preview for budget: {budget.id} - {budget.name}")
    
    # Get all income sources
    income_sources = GrossIncome.query.filter_by(budget_id=budget.id).all()
    primary_income = next((income for income in income_sources if income.category == "W2 Job"), None)
    other_income = [income for income in income_sources if income.category != "W2 Job"]
    
    # Get all budget items (expenses)
    budget_items = BudgetItem.query.filter_by(budget_id=budget.id).all()
    
    # Organize budget items by category for display
    expenses_by_category = {}
    for item in budget_items:
        if item.category not in expenses_by_category:
            expenses_by_category[item.category] = []
        expenses_by_category[item.category].append(item)
    
    # Create a form for CSRF protection
    from flask_wtf import FlaskForm
    form = FlaskForm()
    
    # Process form submission if this is a POST request
    if request.method == 'POST':
        if form.validate_on_submit() and 'calculate_budget' in request.form:
            # Mark the budget as ready for calculation
            budget.status = 'ready'
            db.session.commit()
            flash("Budget ready for calculation! Proceeding to final budget page.", "success")
            return redirect(url_for('budget.calculate', budget_id=budget.id))
    
    # Return the budget review template with all data
    return render_template(
        'budget/preview.html',
        budget=budget,
        primary_income=primary_income,
        other_income=other_income,
        expenses_by_category=expenses_by_category,
        profile=profile,
        form=form
    )


@budget_bp.route('/calculate/<int:budget_id>', methods=['GET'])
@login_required
def calculate(budget_id):
    """Calculate the final budget with tax estimations and display the results."""
    try:
        # Get the budget
        budget = Budget.query.get_or_404(budget_id)

        # Check authorization first
        if budget.user_id != current_user.id:
            flash("You do not have permission to view this budget.", "danger")
            return redirect(url_for('main.dashboard'))

        calculator = BudgetCalculator(budget)
        # Check if there are any income sources before calculating
        if not budget.gross_income_sources:
            flash("Please add income sources before calculating.", "warning")
            return redirect(url_for('budget.income', budget_id=budget_id))

        tax_data = calculator.calculate_tax_withholdings()

        budget_result = calculator.calculate_final_budget(budget, budget.gross_income_sources,
                                                          budget.budget_items, tax_data, budget.profile)

        # Update budget status to 'finalized'
        budget.status = 'finalized'
        db.session.commit()

        return render_template(
            'budget/results.html',
            budget=budget,
            income_sources=budget.gross_income_sources,
            budget_items=budget.budget_items,
            tax_data=tax_data,
            budget_result=budget_result
        )
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while calculating your budget. Please try again later.", "danger")
        return redirect(url_for('budget.preview'))


@budget_bp.route('/download/<int:budget_id>', methods=['GET'])
@login_required
def download_budget(budget_id):
    """Generate and download an Excel file with the budget details."""
    # Get the budget
    budget = Budget.query.get_or_404(budget_id)
    
    if budget.user_id != current_user.id:
        flash("You do not have permission to download this budget.", "danger")
        return redirect(url_for('main.dashboard'))
    
    # Get the user's profile
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    
    # Get all income sources
    income_sources = GrossIncome.query.filter_by(budget_id=budget.id).all()
    
    # Get all budget items (expenses)
    budget_items = BudgetItem.query.filter_by(budget_id=budget.id).all()
    
    try:
        # Calculate tax withdrawals
        tax_data = calculate_tax_withholdings(budget, income_sources, profile)

        
        # Calculate the final budget
        calculator = BudgetCalculator(budget)
        budget_result = calculator.calculate_final_budget(budget, income_sources, budget_items, tax_data, profile)
        
        # Create Excel file
        from datetime import datetime
        budget_data = {
            'budget_name': budget.name,
            'created_date': datetime.now().strftime('%Y-%m-%d'),
            'monthly_income': budget_result['monthly_gross_income'],
            'net_income': budget_result['monthly_net_income'],
            'total_expenses': budget_result['total_expenses'],
            'remaining_money': budget_result['remaining_money'],
            'details': {
                'Income Sources': {source.source: source.gross_income for source in income_sources},
                'Expenses': {f"{item.category} - {item.name}": (item.preferred_payment if item.preferred_payment > 0 else item.minimum_payment) for item in budget_items},
                'Tax Withholdings': {
                    'Federal Tax': tax_data['total_monthly_federal_tax'],
                    'State Tax': tax_data['total_monthly_state_tax'],
                    'FICA Tax': tax_data['total_monthly_fica_tax']
                },
                'Deductions': {
                    'Retirement Contribution': profile.retirement_contribution,
                    'Benefit Deductions': profile.benefit_deductions
                }
            }
        }
        
        # Generate the Excel file
        return create_excel(budget_data)
        
    except Exception as e:
        flash(f"An error occurred while generating the Excel file: {str(e)}", "danger")
        return redirect(url_for('budget.calculate', budget_id=budget_id))


@budget_bp.errorhandler(Exception)
def handle_error(error):
    db.session.rollback()  # Roll back any failed transactions
    current_app.logger.error(f"Error: {str(error)}")
    flash("An error occurred. Please try again.", "danger")
    return redirect(url_for('main.dashboard'))


# Add a context manager for database transactions
@contextmanager
def safe_transaction():
    try:
        yield
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e


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



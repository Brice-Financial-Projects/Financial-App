"""app/profile/routes.py"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app.profile.forms import ProfileForm
from app.models import Profile, db
from app.profile import profile_bp

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    user_profile = Profile.query.filter_by(user_id=current_user.id).first()

    if form.validate_on_submit():
        if not user_profile:
            user_profile = Profile(user_id=current_user.id)  # Create profile if it doesn't exist

        # ✅ Ensure all data is correctly updated
        user_profile.first_name = form.first_name.data
        user_profile.last_name = form.last_name.data
        user_profile.state = form.state.data
        user_profile.income_type = form.income_type.data
        user_profile.retirement_contribution_type = form.retirement_contribution_type.data  # ✅ Fixed missing field
        user_profile.retirement_contribution = form.retirement_contribution_value.data
        user_profile.pay_cycle = form.pay_cycle.data  # ✅ Fixed missing field
        user_profile.benefit_deductions = form.monthly_benefit_deductions.data

        # ✅ Save the profile
        db.session.add(user_profile)
        db.session.commit()

        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile.profile'))  # ✅ Redirect to dashboard after updating

    # ✅ Prepopulate form with existing profile data if available
    elif user_profile:
        form.first_name.data = user_profile.first_name
        form.last_name.data = user_profile.last_name
        form.state.data = user_profile.state
        form.income_type.data = user_profile.income_type
        form.retirement_contribution_type.data = user_profile.retirement_contribution_type  # ✅ Fixed missing field
        form.retirement_contribution_value.data = user_profile.retirement_contribution
        form.pay_cycle.data = user_profile.pay_cycle  # ✅ Fixed missing field
        form.monthly_benefit_deductions.data = user_profile.benefit_deductions

    return render_template('profile/profile.html', form=form)



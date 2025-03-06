"""app/profile/forms.py"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, SubmitField
from wtforms.validators import DataRequired, InputRequired, NumberRange

# A complete list of states (50 states)
states = [
    ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'),
    ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'),
    ('CT', 'Connecticut'), ('DE', 'Delaware'), ('FL', 'Florida'),
    ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'),
    ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'),
    ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'),
    ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'),
    ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'),
    ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'),
    ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'),
    ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'),
    ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'),
    ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'),
    ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'),
    ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'),
    ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'),
    ('WI', 'Wisconsin'), ('WY', 'Wyoming')
]

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    income_type = SelectField(
        'Income Type', 
        choices=[('Salary', 'Salary'), ('Hourly', 'Hourly'), ('Commission', 'Commission')],
        validators=[DataRequired()]
    )
    state = SelectField('State', choices=states, validators=[DataRequired()])
    retirement_contribution_type = SelectField(
        'Retirement Contribution Type', 
        choices=[('percent', 'Percent'), ('fixed', 'Fixed Amount')],
        validators=[DataRequired()]
    )
    retirement_contribution_value = FloatField(
        'Retirement Contribution Value',
        validators=[InputRequired(), NumberRange(min=0)]
    )
    pay_cycle = SelectField(
        'Pay Cycle', 
        choices=[('weekly', 'Weekly'), ('biweekly', 'Biweekly'), ('monthly', 'Monthly'), ('bimonthly', 'Bimonthly')],
        validators=[DataRequired()]
    )
    monthly_benefit_deductions = FloatField(
        'Monthly Benefit Deductions',
        validators=[InputRequired(), NumberRange(min=0)]
    )
    submit = SubmitField('Save Profile')

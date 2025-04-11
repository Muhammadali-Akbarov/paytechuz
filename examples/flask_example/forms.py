"""
Forms for Flask example.
"""
from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class OrderForm(FlaskForm):
    """
    Form for creating and updating orders.
    """
    amount = FloatField(
        'Amount',
        validators=[
            DataRequired(),
            NumberRange(min=1, message='Amount must be at least 1')
        ]
    )
    submit = SubmitField('Create Order')

from decimal import Decimal, ROUND_HALF_UP
from django import template
import locale

register = template.Library()


@register.filter(name='filter_reformat_number')
def reformat_number(value):
    if value is None:
        return ""
     # Format number
    try:
        # Convert the value to a Decimal for precision and consistent formatting
        decimal_value = Decimal(value)
        # Format the number with commas for thousands separators and two decimal places
        return "{:,.0f}".format(decimal_value)
    except (ValueError, TypeError, decimal.InvalidOperation) as e:
        return str(value)


@register.filter(name='filter_reformat_number_two_decimals')
# Reformat argument as comma-separated number 
def reformat_number_two_decimals(value):
    if value is None:
        return ""
    # Format number
    try:
        # Convert the value to a Decimal for precision and consistent formatting
        decimal_value = Decimal(value)
        # Format the number with commas for thousands separators and two decimal places
        return "{:,.2f}".format(decimal_value)
    except (ValueError, TypeError, decimal.InvalidOperation) as e:
        return str(value)


@register.filter(name='filter_usd')
def filter_usd(value):
    """Format value as USD."""
    
    try:
        # Convert value to float if it's not already a numeric type
        numeric_value = float(value)
    except ValueError:
        # If value cannot be converted to float, return it as is or handle the error
        return value  # Or you might want to handle the error differently, perhaps logging it

    # Threshold for considering a value effectively zero
    threshold = 0.005  # Adjust this value as necessary
    if -threshold < value < threshold:
        value = 0  # Treat as zero
    if value >= 0:
        return f'${value:,.2f}'
    else:
        return f'(${-value:,.2f})'


# Custom jinja filter: x.xx% or (x.xx%)
@register.filter(name='filter_percentage')
def filter_percentage(value):
    """Format a value as a percentage with two decimal places."""
    try:
        # Convert value to float
        numeric_value = float(value)
        # Format the value as a percentage
        return f'{numeric_value:.2f}%'
    except (ValueError, TypeError):
        # Return the value as is if there's an error in conversion
        return value


from django import forms
from django.core.exceptions import ValidationError
import re



# Custom validator 1: Ensure user input does not contain prohibited chars. 
user_input_allowed_letters_lower = 'a-z'
user_input_allowed_letters_upper = 'A-Z'
user_input_allowed_numbers = '0-9'
user_input_allowed_symbols = '-.@_ '
# Escape the symbols for safe inclusion in regex pattern
user_input_allowed_symbols_escaped = re.escape(user_input_allowed_symbols or '')
user_input_allowed_all = ''.join([user_input_allowed_letters_lower, 
                                user_input_allowed_letters_upper,
                                user_input_allowed_numbers, 
                                user_input_allowed_symbols_escaped])
# Regular expression pattern to match the entire string
allowed_chars_check_pattern = r'^[' + user_input_allowed_all + r']+$'
# Define function (no prohibited chars = True).
def allowed_chars(user_input):
    if not re.match(allowed_chars_check_pattern, str(user_input)):
        print(f'running allowed_chars_validator...  failed for input: {user_input}')
        raise ValidationError(f'Error: Allowed characters include: { user_input_allowed_letters_lower}, { user_input_allowed_letters_upper}, { user_input_allowed_numbers}, and { user_input_allowed_symbols }')
    print(f'running allowed_chars_validator...  passed for input: {user_input}')


# EmailField plus:
# - forces user input to lowercase
# - trims input
class EmailFieldLowerStripProhibitedChars(forms.EmailField):
    def clean(self, user_input):
        user_input = super().clean(user_input)  # Perform the standard cleaning and validation first
        user_input = user_input.lower().strip()
        allowed_chars(user_input)
        return user_input

# CharField: plus
# - trims input
# - titlecases input
class CharFieldTitleCaseStripProhibitedChars(forms.CharField):
    def clean(self, user_input):
        user_input = super().clean(user_input)  # Perform the standard cleaning and validation first
        user_input = user_input.title().strip()
        allowed_chars(user_input)
        return user_input


class CharFieldStripProhibitedCharsPhone(forms.CharField):
    def clean(self, user_input):
        user_input = super().clean(user_input)  # Perform the standard cleaning and validation first
        user_input = user_input.title().strip()
        allowed_chars(user_input)
        return user_input



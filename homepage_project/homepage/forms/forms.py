from django import forms
from .custom_fields import EmailFieldLowerStripProhibitedChars

class ContactForm(forms.Form):
    name = CharFieldTitleCaseStripProhibitedChars(
        label='Name:',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Your name here', 
        'class': 'form-control', 
        'autofocus': 'autofocus'}))
    email = EmailFieldLowerStripProhibitedChars(
        label='Email address:', 
        max_length=100, 
        widget=forms.EmailInput(attrs={'placeholder': 'emailaddress@example.com',
        'class': 'form-control'}))
    phone = forms.CharField(
        label='WhatsApp number:', 
        max_length=20, 
        widget=forms.TextInput(attrs={'placeholder': '+62....', 
        'class': 'form-control'}))
    body = forms.CharField(label='Message:', max_length= 2000, widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'A hot dog is absolutely a sandwich. Convince me otherwise.', 'class': 'form-control'}))
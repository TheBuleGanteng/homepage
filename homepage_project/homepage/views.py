from .forms.forms import ContactForm
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render


# Create your views here.
def index(request):
    return render(request, 'homepage/index.html')

def contact(request):

    # Handle if method = post
    if request.method == 'POST':

        # Instantiate the form with POST data
        form = ContactForm(request.POST)
        
        # Handle if method = post + form is valid
        if form.is_valid():
            messages.success(request, 'Your message has been sent. Thank you!')
            return redirect('homepage:index') 
        
        # Handle if method = post BUT form is invalid
        else:
            messages.error(request, 'Please correct the errors below and try again.')
            return render(request, 
            'homepage/contact.html', 
            {'form': form})

    # Handle if method is GET
    else:
        # Que up form
        form = ContactForm()
        # For GET requests: render the html with the form
        return render(request, 'homepage/contact.html', {'form': form})

    
    

def returnkey(request):
    return render(request, 'homepage/returnkey.html')

def tokobox(request):
    return render(request, 'homepage/tokobox.html')

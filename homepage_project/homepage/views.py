from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms.forms import ContactForm
from .helpers import datetime, dnr_email_address, domain_name, get_country_code, info_email_address, os, Path, requests, send_email


# Construct the path to the .env file
env_path = Path('.') / '.' / '.env'


# View that handles CSP violation reporting 
@csrf_exempt
@require_POST
def csp_violation_report(request):
    # Process report
    return JsonResponse({'status': 'ok'})


# View to that performs an HTTP request to the substack API. Used to bypass CORS issues.
def substack_proxy(request):
    print(f'running substack_proxy() ... function started')
    
    # Target URL to fetch from Substack API
    target_url = 'https://substackapi.com/api/feeds/?limit=3&sort=new'
    
    # Forward the request to the Substack API
    response = requests.get(target_url)
    print(f'running substack_proxy() ... JsonResponse(response.json(), safe=False) is { JsonResponse(response.json(), safe=False) } ')
    
    # Return the Substack API response as a JSON response
    return JsonResponse(response.json(), safe=False)


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
            try:
                name = request.POST['name']
                email = request.POST['email']
                sender = os.getenv('INFO_EMAIL_ADDRESS')
                recipient = os.getenv('INFO_EMAIL_ADDRESS')
                country_code = get_country_code(request.POST['phone_0']) 
                phone = country_code+' '+request.POST['phone_1'] or None
                body = request.POST['body']
                subject = 'New mattmcdonnell.net contact form submission'
                attachments = None
                body = f'''Sender name: { name }
Sender email address: { email }
Sender phone: { phone }
Message body: { body }
Message timestamp: { datetime.now() }

Thank you,
{ domain_name }-bot at your service!
'''

                send_email(body=body, recipient=recipient, sender=sender, subject=subject)                
                messages.success(request, 'Your message has been sent. Thank you!')
                return redirect('homepage:index')
            
            except ValueError as e:
                print(f'running contact_view ... Error: {e}  Displaying error message and contact.html ')
                messages.error(request, 'Please complete all required fields and try again')
                return render(request, 
                'homepage/contact.html', 
                {'form': form})
        
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

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms.forms import ContactForm
from .helpers import configure_logging, datetime, dnr_email_address, domain_name, get_country_code, info_email_address, logging, os, Path, requests, send_email
from google.oauth2 import service_account
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import os



# Configures logger
logger = logging.getLogger(__name__)

# Construct the path to the .env file
env_path = Path('.') / '.' / '.env'
logger.debug(f'env_path is: { env_path }')


# View that handles CSP violation reporting 
@csrf_exempt
@require_POST
def csp_violation_report(request):
    # Process report
    return JsonResponse({'status': 'ok'})


# View to that performs an HTTP request to the substack API. Used to bypass CORS issues.
def substack_proxy(request):
    print(f'running substack_proxy() ... function started')
    logger.debug(f'running substack_proxy() ... function started')
    
    # Target URL to fetch from Substack API
    target_url = 'https://substackapi.com/api/feeds/?limit=3&sort=new'
    
    # Forward the request to the Substack API
    response = requests.get(target_url)
    print(f'running substack_proxy() ... JsonResponse(response.json(), safe=False) is { JsonResponse(response.json(), safe=False) } ')
    logger.debug(f'running substack_proxy() ... JsonResponse(response.json(), safe=False) is { JsonResponse(response.json(), safe=False) } ')
    
    # Return the Substack API response as a JSON response
    logger.debug(f'running substack_proxy() ... function ended')
    return JsonResponse(response.json(), safe=False)



# Readiness check (needed for serving via GCP)
def readiness_check(request):
    
    logger.debug(f'starting readiness_check() ... ')

    # Perform any necessary checks here, such as database connectivity,
    # availability of external services, etc.
    # For simplicity, this example assumes the app is always ready.

    #try:
        # Your check logic here
        # For example: check_database_connection()
        #logger.info("Readiness check passed")
    #except Exception as e:
        #logger.error(f"Readiness check failed: {e}")
        #return HttpResponse('Service Unavailable', status=503)

    logger.debug(f'ended readiness_check() ... ')
    return HttpResponse('Ready', status=200)



# Create your views here.
def index(request):
    logger.debug(f'starting index() ... ')
    logger.debug(f'ending index() ... ')
    return render(request, 'homepage_app/index.html')

def contact(request):
    print(f'running contact() ... starting view')
    logger.info(f'running contact() ... starting view')

    # Handle if method = post
    if request.method == 'POST':
        print(f'starting contact() ... method is POST')
        logger.info(f'starting contact() ... method is POST')


        # Instantiate the form with POST data
        form = ContactForm(request.POST)
        print(f'running contact() ... method is POST and form is: { form }')
        logger.info(f'running contact() ... method is POST and form is: { form }')
        
        # Handle if method = post + form is valid
        if form.is_valid():
            print(f'running contact() ... method is POST and form passes validation')
            logger.info(f'running contact() ... method is POST and form passes validation')

            try:
                name = request.POST['name']
                print(f'running contact() ... name is { name }')
                logger.info(f'running contact() ... method is POST and form passes validation')

                email = request.POST['email']
                sender = os.getenv('INFO_EMAIL_ADDRESS')
                print(f'running contact() ... sender is: {sender}')
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
                return redirect('homepage_app:index')
            
            except ValueError as e:
                print(f'running contact_view ... Error: {e}  Displaying error message and contact.html ')
                messages.error(request, 'Please complete all required fields and try again')
                return render(request, 
                'homepage_app/contact.html', 
                {'form': form})
        
        # Handle if method = post BUT form is invalid
        else:
            messages.error(request, 'Please correct the errors below and try again.')
            return render(request, 
            'homepage_app/contact.html', 
            {'form': form})

    # Handle if method is GET
    else:
        # Que up form
        form = ContactForm()
        # For GET requests: render the html with the form
        return render(request, 'homepage_app/contact.html', {'form': form})
    

def returnkey(request):
    return render(request, 'homepage_app/returnkey.html')


def tokobox(request):
    return render(request, 'homepage_app/tokobox.html')





def send_test_email_inner():
    try:
        # Absolute path to the service account file
        SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'gitignored', 'gmail_access_credentials.json')

        # Define the required scope for sending emails
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']

        # Use the service account to acquire credentials
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        # Specify the user to impersonate
        user_to_impersonate = "matt@mattmcdonnell.net"  # Replace with the email of the user you're impersonating

        # Impersonate the user
        credentials = credentials.with_subject(user_to_impersonate)

        # Build the Gmail service
        service = build('gmail', 'v1', credentials=credentials)

        # Create a simple MIMEText email
        email_msg = MIMEText("This is a test email sent from a service account.")
        email_msg['to'] = "matt@mattmcdonnell.net"  # Replace with the recipient's email address
        email_msg['from'] = 'matt@mattmcdonnell.net'
        email_msg['subject'] = "Test Email"

        # Encode the email message in base64
        encoded_message = base64.urlsafe_b64encode(email_msg.as_bytes()).decode()

        # Create the message body
        message_body = {'raw': encoded_message}

        # Send the email
        message = service.users().messages().send(userId='me', body=message_body).execute()
        print(f"Message Id: {message['id']}")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise


def send_test_email(request):
    send_test_email_inner()  # Call the function
    return HttpResponse("Check the console for the list of Gmail labels.")
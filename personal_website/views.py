import base64
from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms.forms import ContactForm
from .helpers import configure_logging, datetime, dnr_email_address, PROJECT_NAME, get_country_code, info_email_address, logging, os, Path, requests, send_email
from google.oauth2 import service_account
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import os
import xml.etree.ElementTree as ET
import phonenumbers
from phonenumbers import geocoder


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
def fetch_substack_rss(request):
    logger.debug(f'running fetch_substack_rss() ... function started')
    
    
    #  Static cache key for the RSS feed.
    cache_key = 'substack_rss_feed'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        logger.debug('Serving from cache')
        return JsonResponse({'articles': cached_data})


    # If not in cache, fetch the data
    target_url = 'https://matthewmcdonnell.substack.com/feed'
    logger.debug(f'running fetch_substack_rss() ... target_url is: { target_url }')
    
    try:
        response = requests.get(target_url)
    
        # If there is an ok response from the RSS feed url, do the following...
        if response.status_code == 200:
            logger.debug(f'running fetch_substack_rss() ... response from target url was: { response.status_code }')

            # Namespaces are required to correctly parse elements like dc:creator
            namespaces = {
                'dc': 'http://purl.org/dc/elements/1.1/'
            }

            root = ET.fromstring(response.content)
            items = root.findall('.//item')

            # Forward the request to the Substack API
            number_of_articles = 3

            articles = []
            for item in items[:number_of_articles]:  # Limiting to the first 3 articles
                title = item.find('title').text
                description = item.find('description').text
                link = item.find('link').text
                pubDate = item.find('pubDate').text
                # Extracting author name using the namespace dictionary
                author = item.find('dc:creator', namespaces).text if item.find('dc:creator', namespaces) is not None else "Unknown"
                enclosure = item.find('enclosure')
                image = enclosure.get('url') if enclosure is not None else None

                articles.append({
                    'title': title,
                    'description': description,
                    'link': link,
                    'pubDate': pubDate,
                    'author': author,  # Author name extracted from dc:creator
                    'image': image,
                })
                
            # Cache the data for future requests
            cache.set(cache_key, articles, timeout=300)  # Cache for 5 minutes
            logger.debug('Data fetched and cached')
            return JsonResponse({'articles': articles})

        # If the substack RSS does not return 200    
        else:
            logger.error('Failed to fetch RSS feed')
            return JsonResponse({'error': 'Failed to fetch RSS feed'}, status=500)

    except requests.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)

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
def index_view(request):
    logger.debug(f'starting index() ... ')
    logger.debug(f'ending index() ... ')
    return render(request, 'personal_website/index.html')


#---------------------------------------------------------------------------

def contact_view(request):
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
            logger.info(f'running contact() ... method is POST and form passes validation')

            try:
                # Take in data from form
                name = request.POST['name']
                email = request.POST['email']
                phone = request.POST['phone']
                body = request.POST['body']
                logger.debug(f'running contact() ... name is { name }')
                logger.debug(f'running contact() ... email is { email }')
                logger.debug(f'running contact() ... phone is { phone }')
                logger.debug(f'running contact() ... body is { body }')

                # Pull in data from .env
                sender = os.getenv('EMAIL_ADDRESS_INFO')
                recipient = os.getenv('EMAIL_ADDRESS_INFO')
                logger.debug(f'running contact() ... sender is { sender }')
                logger.debug(f'running contact() ... recipient is { recipient }')
                
                # Populate the required fields for send_email()
                subject = 'New mattmcdonnell.net contact form submission'
                attachments = None
                body = f'''Sender name: { name }
Sender email address: { email }
Sender phone: { phone }
Message body: { body }
Message timestamp: { datetime.now() }

Thank you,
{ PROJECT_NAME }-bot at your service!
'''

                send_email(body=body, recipient=recipient, sender=sender, subject=subject)                
                messages.success(request, 'Your message has been sent. Thank you!')
                return redirect('personal_website:index')
            
            except ValueError as e:
                print(f'running contact_view ... Error: {e}  Displaying error message and contact.html ')
                messages.error(request, 'Please complete all required fields and try again')
                return render(request, 
                'personal_website/contact.html', 
                {'form': form})
        
        # Handle if method = post BUT form is invalid
        else:
            logger.error(f'running contact() ... form is invalid. Errors: {form.errors}')
            messages.error(request, 'Please correct the errors below and try again.')
            return render(request, 
            'personal_website/contact.html', 
            {'form': form})

    # Handle if method is GET
    else:
        # Que up form
        form = ContactForm()
        # For GET requests: render the html with the form
        return render(request, 'personal_website/contact.html', {'form': form})
    

def returnkey_view(request):
    return render(request, 'personal_website/returnkey.html')


def sitemap_view(request):
    return render(request, 'personal_website/sitemap.html')

def tokobox_view(request):
    return render(request, 'personal_website/tokobox.html')

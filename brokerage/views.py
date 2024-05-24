from decimal import Decimal, ROUND_HALF_UP
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Q, F, Func, Sum, Value
from django.db.models.functions import Length
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.dateformat import DateFormat
from django.utils.dateparse import parse_date
from django.utils.http import urlencode
from django.views.decorators.http import require_http_methods
from .forms import *
from .helpers import *
import logging
from .models import Listing, Transaction
import os
import re
import traceback
from users.models import UserProfile

logger = logging.getLogger('django')

#-------------------------------------------------------------------------------

@login_required(login_url='users:login')
@require_http_methods(['GET'])
def index_view(request):
    logger.debug('running brokerage app, index ... view started')

    # Log session key for debugging
    logger.debug(f'Session key in index_view: {request.session.session_key}')

    # Retrieve the user object for the logged-in user
    user = request.user
    cache_key = f'portfolio_{user.pk}'  # Unique key for each user
    portfolio = cache.get(cache_key)

    if not portfolio:
        portfolio = process_user_transactions(user)
        cache.set(cache_key, portfolio, timeout=300)  # Cache the data for 5 minutes (300 seconds)
        logger.debug(f'running / ... for user {user} ... portfolio.cash is: { portfolio.cash }')
    


    # Render the index page with the user and portfolio context
    context = {
        'user': user,
        'portfolio': portfolio,
    }
    
    # Render page, passing user and portfolio objects
    return render(request, 'brokerage/index.html', context)

#----------------------------------------------------------------------------

@login_required(login_url='users:login')
@require_http_methods(['GET'])
def index_detail_view(request):
    logger.debug('running brokerage app, index_detail_view ... view started')

    # Retrieve the user object for the logged-in user
    user = request.user
    cache_key = f'portfolio_{user.pk}'  # Unique key for each user
    portfolio = cache.get(cache_key)

    if not portfolio:
        portfolio = process_user_transactions(user)
        cache.set(cache_key, portfolio, timeout=300)  # Cache the data for 5 minutes (300 seconds)
        logger.debug(f'running / ... for user {user} ... portfolio.cash is: { portfolio.cash }')

    # Call the function to create the portfolio object for the user
    portfolio = process_user_transactions(user)
    logger.debug(f'running / ... for user {user} ... portfolio.cash is: { portfolio.cash }')

    # Render the index page with the user and portfolio context
    context = {
        'user': user,
        'portfolio': portfolio,
    }
    
    # Render page, passing user and portfolio objects
    return render(request, 'brokerage/index-detail.html', context)

#----------------------------------------------------------------------------

@login_required(login_url='users:login')
@require_http_methods(['GET', 'POST'])
def buy_view(request):
    logger.debug('running brokerage app, buy_view ... view started')

    # Retrieve the user object for the logged-in user
    user = request.user
    cache_key = f'portfolio_{user.pk}'  # Unique key for each user
    portfolio = cache.get(cache_key)

    # Display the BuyForm
    form = BuyForm(request.POST or None) # This will handle both POST and initial GET

    if request.method == 'POST':
        logger.debug('running brokerage app, buy_view ... user submitted via POST')

        if form.is_valid():
            logger.debug('running brokerage app, buy_view ... user submitted via POST and form passed validation')
        
            # Assigns to variables the username and password passed in via the form in login.html
            symbol = form.cleaned_data['symbol']
            shares = form.cleaned_data['shares']
            print(f'running buy_view ... symbol is: { symbol }')
            print(f'running buy_view ... shares is: { shares }')
            transaction_type = 'BOT'
            logger.debug(f'running brokerage app, buy_view ... symbol is: { symbol } and shares is: { shares }')

            # Check is symbol is valid
            check_valid_symbol_result = check_valid_symbol(symbol)
            logger.debug(f'running buy_view ... check_valid_symbol_result is: { check_valid_symbol_result }')
            
            if not check_valid_symbol_result['success']:
                logger.debug(f'running brokerage app, buy_view ... user-entered symbol: { symbol } is not valid. check_valid_symbol_result is: { check_valid_symbol_result }')
                messages.error(request, check_valid_symbol_result['message'])
                return render(request, 'brokerage/buy.html', {'form': form})
            
            # Check if shares is valid
            check_valid_shares_result = check_valid_shares(shares=shares, symbol=symbol, transaction_type=transaction_type, user=user)
            if not check_valid_shares_result['success']:
                logger.debug(f'running brokerage app, buy_view ... user-entered shares: { shares } is not sufficient for transaction type: { transaction_type } and symbol: { symbol }.')
                messages.error(request, check_valid_shares_result['message'])
                return render(request, 'brokerage/buy.html', {'form': form})

            # If symbol + shares are valid, proceed with processing the share purchase
            new_transaction = process_buy(symbol=symbol, shares=shares, user=user, check_valid_shares_result=check_valid_shares_result)
            
            # Refresh the portfolio to account for the purchase
            portfolio = process_user_transactions(user)
            cache.set(cache_key, portfolio, timeout=300)  # Cache the data for 5 minutes (300 seconds)
            logger.debug(f'running brokerage app, buy_view ... for user {user} ... portfolio.cash is: { portfolio.cash }')
            
            # Flash success message and redirect to index
            logger.debug(f'running brokerage app, buy_view ... successfully processed new_transaction: { new_transaction }.')
            messages.success(request, 'Share purchase processed successfully!')
            return HttpResponseRedirect(reverse('brokerage:index'))
        
        # If form fails validation
        else:
            logger.debug('running brokerage app, buy_view ... user submitted via POST and form failed validation')
            messages.error(request, 'Error: Invalid input. Please see the red text below for assistance.')
            return render(request, 'brokerage/buy.html', {'form': form})

    # If user arrived via GET
    else:
        logger.debug(f'running users app, profile_view ... user arrived via GET')
        return render(request, 'brokerage/buy.html', {'form': form})


#--------------------------------------------------------------------------------------------

# Checks if a symbol is valid, returns either a JSON list of results or an exception + error message
@require_http_methods(['POST'])
def check_valid_shares_view(request):
    logger.debug('running brokerage app, check_valid_shares_view ... view started')

    user = request.user
    symbol = request.POST.get('symbol', '')
    shares = request.POST.get('shares', 0)
    transaction_type = request.POST.get('transaction_type', '')
    
    # Ensure shares are parsed as integer safely
    try:
        shares = int(shares)
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Shares must be an integer.'})
    
    check_valid_shares_result = check_valid_shares(shares=shares, symbol=symbol, transaction_type=transaction_type, user=user)
    
    return JsonResponse(check_valid_shares_result)
    
#-------------------------------------------------------------------------------------------

# Checks if a symbol is valid per FMP API
@require_http_methods(['POST'])
def check_valid_symbol_view(request):
    
    # Get the value for symbol, assuming it's nothing if no submission via post.
    symbol = request.POST.get('symbol', '')
    
    if not symbol:
        return JsonResponse({'success': False, 'response': 'No symbol provided'}, status=400)
    
    
    check_valid_symbol_result = check_valid_symbol(symbol)
    
    # Using status=200 for all responses since the function handles error messaging
    return JsonResponse(check_valid_symbol_result, status=200)

#----------------------------------------------------------------------------

@login_required(login_url='users:login')
@require_http_methods(['GET', 'POST'])
def history_view(request):
    logger.debug(f'running brokerage app, history_view ... view started')

    form = HistoryForm(request.POST or None)  # Initialize form with POST data if available
    history = None

    # Request is POST
    if request.method == 'POST': 
        logger.debug(f'running brokerage app, history_view ... user submitted via POST')

        if form.is_valid():
            logger.debug(f'running brokerage app, history_view ... user submitted via POST and the form passed validation')
            
            date_start = form.cleaned_data['date_start']
            date_end = form.cleaned_data['date_end']
            transaction_type = form.cleaned_data['transaction_type']

            # Prepare URL parameters, only adding those provided to avoid errors
            url_params = []
            if date_start:
                url_params.append('date_start={}'.format(date_start.strftime('%Y-%m-%d')))
            if date_end:
                url_params.append('date_end={}'.format(date_end.strftime('%Y-%m-%d')))
            if transaction_type:
                url_params.append('transaction_type={}'.format(transaction_type))

            # Create the base URL for redirection
            base_url = reverse("brokerage:history")
            
            # Only add parameters to the URL if they exist
            if url_params:
                query_string = '&'.join(url_params)
                redirect_url = '{}?{}'.format(base_url, query_string)
            else:
                redirect_url = base_url
            
            # Redirect to the constructed URL
            return redirect(redirect_url)
        
        else:
            logger.debug(f'running brokerage app, history_view ... user submitted via POST and the form failed validation')
            messages.error(request, 'Error via POST: Invalid input. Please see the red text below for assistance.')            
            return render(request, 'brokerage/history.html', {'form': form, 'user': request.user, 'history': history})

    # Request is GET
    else:
        logger.debug(f'running brokerage app, history_view ... user arrived via GET')
        
        date_start = request.GET.get('date_start')
        date_end = request.GET.get('date_end')
        transaction_type = request.GET.get('transaction_type')

        logger.debug(f'running brokerage app, history_view ... user arrived via GET and request.GET.get(date_start) is: { date_start }')
        logger.debug(f'running brokerage app, history_view ... user arrived via GET and request.GET.get(date_end) is: { date_end }')
        logger.debug(f'running brokerage app, history_view ... user arrived via GET and request.GET.get(transaction_type) is: { transaction_type }')

        # If date_start and date_end are in the URL
        if date_start and date_end:

            date_start = parse_date(date_start)
            date_end = parse_date(date_end)

            if date_start and date_end:
                # Secondary validation to ensure ending date is not before start date
                if date_end < date_start:
                    messages.error(request, 'Ending date cannot be before starting date.')
                    return render(request, 'brokerage/history.html', {'form': form, 'user': request.user, 'history': history})
                
                # If date_start, date_end, and transaction_type are in the URL
                if transaction_type:
                    logger.debug(f'running brokerage app, history_view ... url contains date_start, date_end, and transaction_type')    
                    form = HistoryForm(data={'date_start': date_start, 'date_end': date_end, 'transaction_type': transaction_type})

                # If only date_start and date_end are in the URL
                else: 
                    # Take in the dates in the URL and processes them via the form, so as to leverage the form's built-in validation capabilities.
                    logger.debug(f'running brokerage app, history_view ... url contains date_start and date_end')
                    form = HistoryForm(data={'date_start': date_start, 'date_end': date_end})

            # date_start and date_end are in the HTML, but parsing fails. Throw an error.
            else:
                logger.debug(f'running brokerage app, history_view ... form failed validation')
                logger.debug(f'Form errors: {form.errors}')  # Log specific form errors
                messages.error(request, 'Error in GET: Invalid date format. Please use YYYY-MM-DD format.')
                
        # If only transaction_type is in the URL
        elif transaction_type:
            logger.debug(f'running brokerage app, history_view ... url contains transaction_type only')
            form = HistoryForm(data={'transaction_type': transaction_type})

        # Neither date_start, nor date_end, nor transaction_type are in the URL
        else:
            form = HistoryForm(data={})

        user = request.user
        
        # Perform the DB query with the relevant params
        if date_start and date_end:
            if transaction_type in ['BOT', 'SLD']:
                # Filter by date range and transaction type if type is 'BOT' or 'SLD'
                history = user.transaction_set.filter(timestamp__date__gte=date_start, timestamp__date__lte=date_end, type=transaction_type)
            else:
                # Filter by date range only of transaction_type is not BOT or SLD, or transaction_type is not present at all.
                history = user.transaction_set.filter(timestamp__date__gte=date_start, timestamp__date__lte=date_end)
        elif transaction_type in ['BOT', 'SLD']:
            # Filter by date range and transaction type if type is 'BOT' or 'SLD'
                history = user.transaction_set.filter(type=transaction_type)
        else:
            history = user.transaction_set.all()

        # Some additional calculations needed to for history:
        for transaction in history:
            if transaction.type == 'SLD':
                transaction.total_CG_pre_tax = transaction.STCG + transaction.LTCG
                transaction.total_CG_pre_tax_percent = transaction.total_CG_pre_tax / transaction.transaction_value_total
                transaction.total_CG_tax = transaction.LTCG_tax + transaction.STCG_tax
                transaction.STCG_post_tax = transaction.STCG * (1 - user.userprofile.tax_rate_STCG)
                transaction.LTCG_post_tax = transaction.LTCG * (1 - user.userprofile.tax_rate_LTCG)
                transaction.total_CG_post_tax = transaction.STCG_post_tax + transaction.LTCG_post_tax 
                transaction.total_CG_post_tax_percent = transaction.total_CG_post_tax /  transaction.transaction_value_total
        
        context = {
        'form': form,
        'history': history,
        'user': request.user,
        }

        return render(request, 'brokerage/history.html', context)


#--------------------------------------------------------------------------------

@require_http_methods('GET')
def quote_view(request):
    logger.debug('running brokerage app, quote_view ... view started')

    url_symbol = request.GET.get('symbol' or None)

    if request.method == 'POST' or url_symbol:
        
        # Display the QuoteForm
        form = QuoteForm(request.POST or None) # This will handle both POST and initial GET

        # If user submits QuoteForm or there is a symbol in the url
        if form.is_valid() or url_symbol:
            logger.debug('running brokerage app, quote_view ... user submitted via POST and form passed validation')
        
            # Pull in the queried_symbol via either the url or submission of the form
            queried_symbol = url_symbol or form.cleaned_data['symbol']
            
            # Hit the FMP API to pull the company profile pertaining to queried_symbol
            company_profile = company_data(queried_symbol)
            logger.debug(f'running brokerage app, quote_view ... quote requested for symbol: { queried_symbol }')
            
            # Retrieve the user object (will return AnonymousUser if user is not logged in)
            user = request.user
            logger.debug(f'running brokerage app, quote_view ... user is: { user }')

            # If the user is logged in, pull the portfolio object for this user
            if user != 'AnonymousUser':
                cache_key = f'portfolio_{user.pk}'  # Unique key for each user
                portfolio = cache.get(cache_key)

                # If there is no cached portfolio for the logged-in user, re-create the portfolio object and cache it
                if not portfolio:
                    portfolio = process_user_transactions(user)
                    
                    cache.set(cache_key, portfolio, timeout=300)  # Cache the data for 5 minutes (300 seconds)
                logger.debug(f'running / ... for user {user} ... portfolio is: { portfolio }')
                
                # Sell button check: Look in the portfolio to see if it contains queried_symbol
                for symbol in portfolio.portfolio_data:

                    # Access the data for the current symbol in the loop of the symbols in the portfolio
                    symbol_data = portfolio.portfolio_data[symbol]

                    # If the portfolio contains shares outstanding of queried_symbol, user can sell
                    if symbol == queried_symbol and symbol_data['shares_outstanding'] > 0:
                        company_profile['can_sell'] = True
                        break
                    else:
                        company_profile['can_sell'] = False
                    logger.debug(f'running / ... for user {user} ... company_profile[can_sell] is: { company_profile["can_sell"] }')    
                
                # Buy button check: If the portfolio contains cash > the per share price of queried_symbol, user can buy
                if user.userprofile.cash > company_profile['price']:
                    company_profile['can_buy'] = True
                else:
                    company_profile['can_buy'] = False
                logger.debug(f'running / ... for user {user} ... company_profile[can_buy] is: { company_profile["can_buy"] }')

            # If the user is not logged in, user cannot buy or sell
            else:
                company_profile['can_sell'] = False
                company_profile['can_buy'] = False

        
            # Some additional calculations displayed in in the html
            company_profile['changes_percent'] = reformat_number_two_decimals(company_profile['changes'] / (company_profile['price'] - company_profile['changes']) )
            company_profile['changes_percent_negative'] = company_profile['changes_percent'] + '%'
            company_profile['changes_percent_positive'] = '+' + company_profile['changes_percent'] + '%'
            company_profile['mktCap_reformatted'] = reformat_usd(company_profile['mktCap'] / 1000000000) + ' billion'
            company_profile['volAvg_reformatted'] = reformat_number(company_profile['volAvg']) + ' daily shares'
            min_val, max_val = company_profile['range'].split('-')
            company_profile['range_reformatted'] = f"${min_val} - ${max_val}"

            # Render a template with the company data
            return render(request, 'brokerage/quoted.html', {'company_profile': company_profile, 'symbol': queried_symbol})

        # If QuoteForm fails validation
        else:
            logger.debug('running brokerage app, quote_view ... validation errors in QuoteForm')
            messages.error(request, 'Error: Invalid input. Please see the red text below for assistance.')            
            return render(request, 'brokerage/quote.html', {'form': form})

    else:
        # GET request without a symbol, show only the form
        form = QuoteForm()
        return render(request, 'brokerage/quote.html', {'form': form})        
            
#--------------------------------------------------------------------------------

@login_required(login_url='users:login')
@require_http_methods(['GET', 'POST'])
def sell_view(request):
    logger.debug('running brokerage app, sell_view ... view started')

    # Retrieve the user object and portfolio for the logged-in user
    user = request.user
    cache_key = f'portfolio_{user.pk}'  # Unique key for each user
    portfolio = cache.get(cache_key)
    logger.debug(f'running sell_view ... user is { user }')
    
    # Retrieve the list of shares owned
    symbols_query = Transaction.objects.filter(user=user, type='BOT').values_list('symbol', flat=True).distinct()
    logger.debug(f'running sell_view ... user is { user }, symbols_query is { symbols_query }')
    symbols = [(symbol, symbol) for symbol in symbols_query]  # Prepare tuple pairs
    logger.debug(f'running sell_view ... user is { user }, symbols_query is { symbols_query }, symbols is: { symbols }')
    form = SellForm(request.POST or None, symbols=symbols)  # Form is instantiated here for both GET and POST

    if request.method == 'POST':
    
        if form.is_valid():
            
            # Assigns to variables the username and password passed in via the form in login.html
            symbol = form.cleaned_data['symbol']
            shares = form.cleaned_data['shares']
            transaction_type = 'SLD'
            logger.debug(f'running sell_view ... user is: { user } and symbol is: { symbol }')
            logger.debug(f'running buy_view ... user is: { user } and shares is: { shares }')
                    
            # Back-end validation to ensure symbol is valid
            if symbol not in symbols_query:
                logger.debug(f'running sell_view ... user is: { user } and symbol is: { symbol }, but symbol not found in symbols: { symbols } ')
                messages.error(request, 'Error: Symbol not found in user list of symbols already owned. Please check your input and try again.')
                return render(request, 'brokerage/sell.html', {'form': form})

            # Back-end validation to ensure shares is valid
            check_valid_shares_result = check_valid_shares(shares=shares, symbol=symbol, transaction_type=transaction_type, user=user)
            if not check_valid_shares_result['success']:
                logger.debug(f'running brokerage app, sell_view ... user is: { user }, symbol is {symbol}, user-entered shares: { shares } is not sufficient for transaction type: { transaction_type }.')
                messages.error(request, check_valid_shares_result['message'])
                return render(request, 'brokerage/sell.html', {'form': form})
    
            # If both back-end validations pass, process the sale
            new_transaction = process_sell(symbol=symbol, shares=shares, user=user)
            logger.debug(f'running sell_view ... user is: { user }, new transaction processed successfully: { new_transaction }')
            
            # Refresh the portfolio to account for the purchase
            portfolio = process_user_transactions(user)
            cache.set(cache_key, portfolio, timeout=300)  # Cache the data for 5 minutes (300 seconds)
            logger.debug(f'running brokerage app, sell_view ... for user {user} ... portfolio.cash is: { portfolio.cash }')
            
            # Flash the success message and redirect to index.
            logger.debug(f'running brokerage app, sell_view ... for user {user} ... processed share sale and refreshed user portfolio. Redirecting to index.')
            messages.success(request, 'Share sale processed successfully!')
            return HttpResponseRedirect(reverse('brokerage:index'))

        # If form fails validation
        else:
            logger.debug('running brokerage app, sell_view ... user submitted via POST and form failed validation')
            messages.error(request, 'Error: Invalid input. Please see the red text below for assistance.')
            return render(request, 'brokerage/sell.html', {'form': form})
    
    # If request is GET
    else:
        return render(request, 'brokerage/sell.html', {'form': form})

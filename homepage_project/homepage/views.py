from django.http import HttpResponse
from django.shortcuts import render
# Test change

# Create your views here.
def index(request):
    return render(request, 'homepage/index.html')

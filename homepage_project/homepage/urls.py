from django.urls import path
from . import views

# Defines application's namespace (set in project's urls.py file)
app_name = 'homepage'

urlpatterns = [
    path("", views.index, name='index')
    
]

from django.urls import include, path
from django.shortcuts import redirect
from . import views
from .views import fetch_substack_rss

# Defines application's namespace (set in project's urls.py file)
app_name = 'personal_website'

urlpatterns = [
    path('', views.index, name='index'),
    path('contact', views.contact, name='contact'),
    #path('csp/', include('csp.urls', namespace='csp')),
    path('returnkey', views.returnkey, name='returnkey'),
    path('fetch-substack-rss', fetch_substack_rss, name='fetch_substack_rss'),
    path('tokobox', views.tokobox, name='tokobox'),
]

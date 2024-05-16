from django.urls import include, path
from django.shortcuts import redirect
from . import views
from .views import fetch_substack_rss

# Defines application's namespace (set in project's urls.py file)
app_name = 'personal_website'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('contact/', views.contact_view, name='contact'),
    #path('csp/', include('csp.urls', namespace='csp')),
    path('returnkey/', views.returnkey_view, name='returnkey'),
    path('fetch-substack-rss/', fetch_substack_rss, name='fetch-substack-rss'),
    path('sitemap/', views.sitemap_view, name='sitemap'),
    path('tokobox/', views.tokobox_view, name='tokobox'),
]

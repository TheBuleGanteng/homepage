from django.urls import path
from . import views
from .views import fetch_substack_rss

# Defines application's namespace (set in project's urls.py file)
app_name = 'personal_website'

urlpatterns = [
    path('', views.index, name='index'),
    path('contact', views.contact, name='contact'),
    path('csp-violation-report', views.csp_violation_report),
    path('returnkey', views.returnkey, name='returnkey'),
    path('fetch-substack-rss', fetch_substack_rss, name='fetch_substack_rss'),
    path('tokobox', views.tokobox, name='tokobox'),
]

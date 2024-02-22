from django.urls import path
from . import views
from .views import substack_proxy

# Defines application's namespace (set in project's urls.py file)
app_name = 'homepage'

urlpatterns = [
    path('', views.index, name='index'),
    path('contact', views.contact, name='contact'),
    path('csp-violation-report', views.csp_violation_report),
    path('returnkey', views.returnkey, name='returnkey'),
    path('api/substack-proxy/', substack_proxy, name='substack_proxy'),
    path('tokobox', views.tokobox, name='tokobox')
]

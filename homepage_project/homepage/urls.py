from django.urls import path
from . import views

# Defines application's namespace (set in project's urls.py file)
app_name = 'homepage'

urlpatterns = [
    path('', views.index, name='index'),
    path('contact', views.contact, name='contact'),
    path('returnkey', views.returnkey, name='returnkey'),
    path('substack-proxy/', views.substack_proxy, name='substack_proxy'),
    path('tokobox', views.tokobox, name='tokobox')
]

"""
URL configuration for homepage project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from personal_website.views import readiness_check
from utils.views import readiness_check_view


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('personal_website.urls', namespace='personal_website')),
    path('csp/', include('csp.urls', namespace='csp')),
    path('myfinance50/', include([
        path('', include(('brokerage.urls', 'brokerage'), namespace='brokerage')),
        path('', include(('users.urls', 'users'), namespace='users')),
    ])),
    path('readiness_check/', readiness_check, name='readiness_check'),
    path('utils/', include('utils.urls', namespace='utils')),
]


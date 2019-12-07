"""SimilarWebProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path
from app.views import process_files_view, get_unique_urls_view, get_num_of_session_view, get_median_per_site_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('process-files/', process_files_view),
    path('unique-urls/', get_unique_urls_view),
    path('num-sessions/', get_num_of_session_view),
    path('median', get_median_per_site_view)
]

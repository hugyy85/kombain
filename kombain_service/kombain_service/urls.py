"""kombain_service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, include
from .view import home, sign_up, create_report, listing_reports, show_report
from .settings import DEBUG, MEDIA_URL, MEDIA_ROOT


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('sign_up/', sign_up, name='sign_up'),
    path('create_report/', create_report, name='creation'),
    path('', home),
    path('listing/', listing_reports, name='listing'),
    path('<username>/report/<int:report_id>/', show_report),
]


if DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.conf.urls.static import static

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        MEDIA_URL, document_root=MEDIA_ROOT)

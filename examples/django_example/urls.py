"""
URL configuration for example project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('payments/', include('paytechuz.integrations.django.urls')),
    path('orders/', include('orders.urls')),
]

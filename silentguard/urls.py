"""
URL configuration for silentguard project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from home import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('scan/', views.scan_message, name='scan_message'),
    path('scan/result/<int:msg_id>/', views.scan_result, name='scan_result'),

    path('report/', views.report_fraud, name='report_fraud'),
    path('check/', views.check_transaction, name='check_transaction'),

    path('learn/', views.learn, name='learn'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('activity/', views.activity_log, name='activity_log'),
    path('receive-sms/', views.receive_sms, name='receive_sms'),
    path('incoming-sms/', views.incoming_sms, name='incoming_sms'),
]



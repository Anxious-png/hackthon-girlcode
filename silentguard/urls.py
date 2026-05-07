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
    path("logout/", views.logout_view, name="logout"),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('scan/', views.scan_message, name='scan_message'),
    path('scan/result/<int:msg_id>/', views.scan_result, name='scan_result'),
    path("lock-account/", views.lock_account, name="lock_account"),
    path("confirm-login/", views.confirm_login, name="confirm_login"),

    path('report/', views.report_fraud, name='report_fraud'),
    path('check/', views.check_transaction, name='check_transaction'),
    path('set-goal/', views.set_saving_goal, name='set_savings_goal'),
    path('savings-dashboard/', views.savings_dashboard, name='savings_dashboard'),
    path('transfer-to-savings/', views.transfer_to_savings, name='transfer_to_savings'),

    path('profile/', views.profile_view, name='profile'),

    path('set-pin/', views.set_pin, name='set_pin'),
    path('pin-locked/', views.pin_locked, name='pin_locked'),
    path('unlock-pin/', views.unlock_pin, name='unlock_pin'),

    path('learn/', views.learn, name='learn'),
    path('learn/<int:pk>/', views.learn_detail, name='learn_detail'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('activity/', views.activity_log, name='activity_log'),
    path('receive-sms/', views.receive_sms, name='receive_sms'),
    path('incoming-sms/', views.incoming_sms, name='incoming_sms'),

    path("deposit/", views.deposit_money, name="deposit_money"),
    path("add-savings/", views.add_savings, name="add_savings"),
    path("savings-dashboard/", views.savings_dashboard, name="savings_dashboard"),
    path("withdraw/", views.withdraw_money, name="withdraw_money"),
    
    path("investments/", views.invest, name="investment_options"),
    path("transaction-history/", views.transaction_history, name="transaction_history"),
]



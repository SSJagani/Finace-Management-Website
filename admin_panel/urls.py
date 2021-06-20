from django.urls import path,include
from . import views
urlpatterns = [
	path('',views.admin_login,name='admin_login'),
	path('logout', views.logout, name='logout'),
	path('profile',views.admin_profile,name='admin_profile'),
	path('dashboard', views.dashboard, name='admin_dashboard'),

	# Agent add/update/delete/check
	path('agent_list',views.agent_list,name='agent_list'),
	path('add_agent',views.add_agent,name='add_agent'),
	path('get_agent',views.get_agent,name='get_agent'),
	path('delete_agent',views.delete_agent,name='delete_agent'),
	path('agent_check_email',views.agent_check_email,name='agent_check_email'),
	# path('activate/<uidb64>/<token>/',views.agent_activate,name='activate'),

	# Customer add/update/delete/check
	path('customer_list',views.customer_list,name='admin_customer_list'),
	path('add_customer',views.add_customer,name='add_customer'),
	path('delete_customer',views.delete_customer,name='delete_customer'),
	path('customer_check_email',views.customer_check_email,name='customer_check_email'),
	path('get_customer',views.get_customer,name='get_customer'),

	path('staff_list',views.staff_list,name='staff_list'),

	# Bank Collab add/update/delete/check
	path('bank_collab_list',views.bank_collab_list,name='bank_collab_list'),
	path('data_json',views.json_data,name='data_json'),

	# Loan Type add/update/delete/check
	path('loan_type',views.loan_type,name='loan_type'),
	path('add_loan_type',views.add_loan_type,name='add_loan_type'),
	path('check_loan_type',views.check_loan_type,name='check_loan_type'),
	path('get_loan_type',views.get_loan_type,name='get_loan_type'),

	# Loan add/update/delete/check
	path('loan_list',views.loan_list,name='loan_list'),
	path('get_customer_loan',views.get_customer_loan,name='get_customer_loan'),
	path('add_loan',views.add_loan,name='add_loan'),
]
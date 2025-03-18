from django.urls import path,include
from . import views
urlpatterns = [
	path('',views.agent_login,name='agent_login'),
	path('logout', views.logout, name='logout'),
	path('profile',views.agent_profile,name='agent_profile'),
	path('dashboard', views.dashboard, name='agent_dashboard'),

	path('activate/<uidb64>/<token>/',views.agent_activate,name='agent_activate'),

	path('customer_list',views.customer_list,name='agent_customer_list'),
	path('add_customer',views.add_customer,name='add_customer'),
	path('delete_customer',views.delete_customer,name='delete_customer'),
	path('customer_check_email',views.customer_check_email,name='customer_check_email'),
	path('get_customer',views.get_customer,name='get_customer'),
]
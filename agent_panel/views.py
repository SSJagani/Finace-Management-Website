from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.contrib.auth import authenticate
from django.conf import settings
from django.contrib import messages
from django.db.models import Count

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from django.contrib.auth import get_user_model
from admin_panel.models import customer
Agent = get_user_model()
import string
from random import *

#Comman function use
def pasword_create():
	characters = string.ascii_letters + string.punctuation  + string.digits
	password =  "".join(choice(characters) for x in range(10))
	print(password)
	return password


# Create your views here.
def agent_login(request):
	# if 'agent_id' in request.session:
	# 	return redirect("agent_deshboard")
	# else:
		if request.method =='POST':
			if 'email' not in request.POST or request.POST['email'] == "":
				messages.error(request, "Enter Email Address !")
				return redirect('agent_login')
			elif 'password' not in request.POST or request.POST['password'] == "":
				messages.error(request, "Enter Password !")
				return redirect('agent_login')
			else:
				email_address = request.POST['email']
				password = request.POST['password']
				print(request.POST,'\n',email_address,password)
				agent = authenticate(email_address = email_address ,password=password)
				if agent is not None:
					if not agent.is_admin:
						if agent.is_active:
							request.session['agent_id'] = agent.agent_id
							request.session['user_name'] = agent.full_name
							# request.session['profile_photo'] = agent.profile_photo
							return redirect('agent_dashboard')
						else:
							messages.error(request, "Your Account Is Not Active.")
							return redirect('agent_login')
					else:
						request.session['agent_id'] = agent.agent_id
						request.session['user_name'] = agent.full_name
						# request.session['profile_photo'] = agent.profile_photo
						return redirect('admin_dashboard')
				else:
					messages.error(request, "invalid credential!")
					return redirect('agent_login')
		else:
			return render(request,'agent_panel/authentication/login.html')
			# return render(request ,'agent_panel/authentication/login.html')

def logout(request):
	request.session.flush()
	return redirect('/agent_ksf')

def agent_activate(request,uidb64,token):
	try:
		uid = urlsafe_base64_decode(uidb64).decode()
		agent = Agent._default_manager.get(pk=uid)
	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
		agent = None
	if agent is not None and default_token_generator.check_token(agent, token):
		agent.is_active = True
		agent.save()
		message = render_to_string('admin_panel/subadmin/agent_form.html',{'agents':agent})
		print(type(message))
		mail_subject = 'Activate successfully your account.'
		to_email = agent.email_address
		email = EmailMessage(
			mail_subject, message, to=[to_email]
		)
		email.send()
		return render(request, 'admin_panel/authentication/acc_active_email_done.html')
	else:
		return render(request, 'admin_panel/authentication/acc_active_email_fail.html')

def agent_profile(request):
	if not 'agent_id' in request.session:
		return redirect('/agent_ksf')
	else:
		if request.method == 'POST':
			print("===================================")
			print(request.POST)
			print("===================================")
			agent_qry = Agent.objects.get(agent_id = request.session['agent_id'])
			if request.POST['full_name'] == "":
				messages.error(request, "Enter full name !")
				return redirect('agent_profile')
			elif request.POST['email_address'] == "":
				messages.error(request, "Enter email address !")
				return redirect('agent_profile')
			elif request.POST['agent_gender'] == "":
				messages.error(request, "Enter Gender!")
				return redirect('agent_profile')
			elif request.POST['agent_dob'] == "":
				messages.error(request, "Enter agent Date Of Birth!")
				return redirect('agent_profile')
			elif request.POST['agent_address'] == "":
				messages.error(request, "Enter address!")
				return redirect('agent_profile')
			qry_email = Agent.objects.filter(email_address = request.POST['email_address']).values('agent_id')

			if qry_email.exists():
				if qry_email[0]['agent_id'] != request.session['agent_id']:
					messages.error(request, request.POST['email']+" Email Address Already Exists, Please Enter Differnt Email.")
					return redirect('agent_profile')
				else:
					full_name = request.POST['full_name']
					email_address = request.POST['email_address']
					agent_gender = request.POST['agent_gender']
					agent_dob = request.POST['agent_dob']
					agent_address = request.POST['agent_address']
					if 'password' in request.POST and request.POST['password'] != '':
						if 'confirmpassword' in request.POST and request.POST['confirmpassword'] != '':
							password = request.POST['password']
							confirmpassword = request.POST['confirmpassword']
							if password == confirmpassword:
								agent_qry.full_name = full_name
								agent_qry.email_address = email_address
								agent_qry.set_password(password)
								# agent_qry.save()
								request.session.flush()
								return redirect('/admin_ksf')
							else:
								messages.error(request, "Enter Same Password in Both Password Filed.")
								return redirect('agent_profile')
						else:
							return redirect('agent_profile')
					else:
						agent_qry.full_name = full_name
						agent_qry.email_address = email_address
						agent_qry.agent_gender = agent_gender
						agent_qry.agent_dob = agent_dob
						agent_qry.agent_address = agent_address
						agent_qry.save()
						request.session['user_name'] = full_name
						return redirect('agent_profile')
		else:
			qry_agent = Agent.objects.get(agent_id=request.session['agent_id'])
			contect = {"agent_profile" : qry_agent}
			return render(request , 'agent_panel/subadmin/profile_agent.html',contect)


def dashboard(request):
	if not 'agent_id' in request.session:
		return redirect('/agent_ksf')
	else:
		Qry_Total_customer = customer.objects.annotate(count=Count('customer_id')).filter(who_add=request.session['agent_id'])
		# .exclude(is_admin=True) 
		context = {
			'customer':Qry_Total_customer
		}
		return render(request, 'agent_panel/subadmin/dashboard.html', context)


def customer_list(request):
	if not 'agent_id' in request.session:
		return redirect("/agent_ksf")
	else:
		qry_customer = customer.objects.all().filter(who_add=request.session['agent_id']).order_by('-customer_id')
		context = {'customer_list':qry_customer}
	return render(request,'agent_panel/subadmin/customer_list.html',context)

def add_customer(request):
	print(request.POST)
	print(request.FILES)
	if not 'agent_id' in request.session:
		return redirect('/admin_ksf')
	else:
		if request.method == 'POST':
			qry_last = customer.objects.all().values("customer_no","account_no").last()
			if qry_last:
				account_no=int(qry_last['account_no'])+1
				customer_no=int(qry_last['customer_no'])+1
			else:
				customer_no = 202100001
				account_no = 2021123450001

			customer_password = pasword_create()
			customer_fullname = request.POST['full_name']
			customer_email = request.POST['email_address']
			customer_contact_no = request.POST['phone_number']
			customer_gender = request.POST['customer_gender']
			customer_dob = request.POST['customer_dob']
			residential_address = request.POST['residential_address']
			permenant_address = request.POST['permenant_address']
			religion = request.POST['religion']
			cast = request.POST['cast']
			maiden_name = request.POST['maiden_name']
			education = request.POST['education']
			occupation = request.POST['occupation']
			other_occupation = request.POST['other_occupation']
			marial_status = request.POST['maratal_status']
			account_type = request.POST['account_type']
			branch_name = request.POST['branch_name']
			# account_no = request.POST['account_no']
			# customer_no = request.POST['customer_no']
			account_operter = request.POST['account_operter']
			joint_holder_name = request.POST['joint_holder_name']
			customer_aadharcard_no = request.POST['customer_aadharcard_no']
			customer_pancard_no = request.POST['customer_pancard_no']
			if request.POST['customer_id'] != '':
				qry_update = customer.objects.get(customer_id=request.POST['customer_id'])
				qry_update.full_name=customer_fullname
				qry_update.customer_email=customer_email
				qry_update.customer_contact_no=customer_contact_no
				qry_update.customer_gender=customer_gender
				qry_update.customer_dob=customer_dob
				qry_update.residential_address=residential_address
				qry_update.permenant_address=permenant_address
				qry_update.religion=religion
				qry_update.cast=cast
				qry_update.maiden_name=maiden_name
				qry_update.education=education
				qry_update.occupation=occupation
				qry_update.other_occupation=other_occupation
				qry_update.marial_status=marial_status
				qry_update.account_type=account_type
				qry_update.branch_name=branch_name
				# qry_update.account_no=account_no
				# qry_update.customer_no=customer_no
				qry_update.account_operter=account_operter
				qry_update.joint_holder_name=joint_holder_name
				qry_update.customer_aadharcard_no=customer_aadharcard_no
				qry_update.customer_pancard_no=customer_pancard_no
				try:
					if 'customer_photo' in request.FILES:
						customer_profile_photo = request.FILES['customer_photo']
						qry_update.customer_profile_photo.delete()
						qry_update.customer_profile_photo=customer_profile_photo
					if 'customer_aadharcard' in request.FILES:
						customer_aadharcard_image = request.FILES['customer_aadharcard']
						qry_update.customer_aadharcard_image.delete()
						qry_update.customer_aadharcard_image=customer_aadharcard_image
					if 'customer_pancard' in request.FILES:
						customer_pancard_image = request.FILES['customer_pancard']
						qry_update.customer_pancard_image.delete()
						qry_update.customer_pancard_image=customer_pancard_image
					if 'customer_sign_image' in request.FILES:
						customer_sign_image = request.FILES['customer_sign_image']
						qry_update.customer_sign_image.delete()
						qry_update.customer_sign_image = customer_sign_image
				except Exception as e:
					print("=======>",e)
					
				qry_update.save()
				return redirect("agent_customer_list")
			else:
				try:
					customer_aadharcard_image = request.FILES['customer_photo']
					customer_profile_photo = request.FILES['customer_aadharcard']
					customer_pancard_image = request.FILES['customer_pancard']
					customer_sign_image = request.FILES['customer_sign_image']
					who_add = request.session['agent_id']
					qry_customer = customer(full_name=customer_fullname,customer_email=customer_email,customer_contact_no=customer_contact_no,
								customer_gender=customer_gender,customer_dob=customer_dob,residential_address=residential_address,
								permenant_address=permenant_address,religion=religion,cast=cast,education=education,occupation=occupation,
								other_occupation=other_occupation,marial_status=marial_status,account_type=account_type,branch_name=branch_name,
								account_no=account_no,customer_no=customer_no,account_operter=account_operter,joint_holder_name=joint_holder_name,
								customer_aadharcard_no=customer_aadharcard_no,customer_pancard_no=customer_pancard_no,
								customer_aadharcard_image=customer_aadharcard_image,customer_profile_photo=customer_profile_photo,
								customer_pancard_image=customer_pancard_image,customer_sign_image=customer_sign_image,maiden_name=maiden_name,who_add=who_add)
					qry_customer.set_password(customer_password)
					qry_customer.save()
					# E-mail send start
					current_site = get_current_site(request)
					mail_subject = 'Activate your account.'
					message = render_to_string('admin_panel/authentication/acc_active_email.html', {
						'user': qry_customer,
						'domain': current_site.domain,
						'uid': urlsafe_base64_encode(force_bytes(qry_customer.pk)),
						'token': default_token_generator.make_token(qry_customer),
						'password':customer_password
					})
					to_email = customer_email
					email = EmailMessage(
						mail_subject, message, settings.EMAIL_HOST_USER,to=[to_email]
					)
					email.send()
					print(email.__dict__)
					print("emaill send Successfully")
					return redirect('agent_customer_list')
				except Exception as e:
					print("Error in add Customer====>",e)
					messages.error(request,str(e))
					return redirect("agent_customer_list")
		else:
			return redirect('agent_customer_list')

def customer_check_email(request):
	if not 'agent_id' in request.session:
		return redirect("/")
	else:
		if request.method == 'POST':
			if 'customer_id' in request.POST:
				customer_id = request.POST['customer_id']
				email = request.POST['email_address']
				# customer_no = request.POST['customer_no']
				# account_no = request.POST['account_no']
				qry_email = customer.objects.filter(customer_email=email).values('customer_id')
				if qry_email.exists():
					if int(qry_email[0]['customer_id']) == int(customer_id):
						return JsonResponse(True,safe=False)
					else:
						return JsonResponse(False,safe=False)
				else:
					return JsonResponse(True,safe=False)
			else:
				email = request.POST['email_address']
				# customer_no = request.POST['customer_no']
				# account_no = request.POST['account_no']
				qry_email = customer.objects.filter(customer_email=email)
				if qry_email.exists():
					return JsonResponse(False,safe=False)
				else:
					return JsonResponse(True,safe=False)
		else:
			return redirect("agent_customer_list")

def delete_customer(request):
	if not 'agent_id' in request.session:
		return redirect("/")
	else:
		if request.method == 'POST':
			customer_id = request.POST['delete_customer_id']
			try:
				qry_delete = customer.objects.get(customer_id=customer_id)
				qry_delete.customer_aadharcard_image.delete()
				qry_delete.customer_profile_photo.delete()
				qry_delete.customer_pancard_image.delete()
				qry_delete.customer_sign_image.delete()
				qry_delete.delete()
				return JsonResponse("Successfully delete Customer",safe=False)
			except Exception as e:
				print("error in got delete user=====>",str(e))
				return JsonResponse("Error Got delete Customer",safe=False)	
		else:
			return redirect('agent_customer_list')

def get_customer(request):
	if not 'agent_id' in request.session:
		return redirect('/admin_ksf')
	else:
		if request.method == 'POST':
			customer_id = request.POST['customer_id']
			qry_customer_get = customer.objects.filter(customer_id=customer_id).values()
			return JsonResponse(list(qry_customer_get)[0],safe=False)
		else:
			return redirect('agent_customer_list')
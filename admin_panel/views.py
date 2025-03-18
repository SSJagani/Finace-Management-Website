from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.conf import settings
from django.contrib import messages
from django.db.models import Count
from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

# <-------------------------------import model------------------------>
from django.contrib.auth import get_user_model
from .models import customer,LoanType
Agent = get_user_model()
import traceback #full exception error show
import string
from random import *
import json

#Comman function use
def pasword_create():
	characters = string.ascii_letters + string.punctuation  + string.digits
	password =  "".join(choice(characters) for x in range(10))
	print(password)
	return password

# Create your views here.
def admin_login(request):
	if request.method == 'POST':
		print('email' not in request.POST)
		if 'email' not in request.POST or request.POST['email'] == "":
			messages.error(request, "Enter Email Address !")
			return redirect('admin_login')
		elif 'password' not in request.POST and request.POST['password'] == "":
			messages.error(request, "Enter Password !")
			return redirect('admin_login')
		else:
			email = request.POST['email']
			password = request.POST['password']
			agent = authenticate(email_address = email ,password=password)
			print(agent)
			if agent is not None:
				if not agent.is_admin:
					messages.error(request, "only admin can login!")
					return redirect('admin_login')
				else:
					request.session['agent_id'] = agent.agent_id
					request.session['user_name'] = agent.full_name
					# request.session['profile_photo'] = agent.profile_photo
					return redirect('admin_dashboard')
			else:
				messages.error(request, "invalid credential!")
				return redirect('admin_login')
			# return render(request,'admin_panel/subadmin/base.html')
	else:
		return render(request,'admin_panel/authentication/login.html')

def logout(request):
	request.session.flush()
	return redirect('/admin_ksf')

def admin_profile(request):
	if not 'agent_id' in request.session:
		return redirect('/admin_ksf')
	else:
		if request.method == 'POST':
			agent_qry = Agent.objects.get(agent_id = request.session['agent_id'])
			if request.POST['full_name'] == "":
					messages.error(request, "Enter full name !")
					return redirect('admin_profile')
			elif request.POST['email'] == "":
				messages.error(request, "Enter email address !")
				return redirect('admin_profile')
			qry_email = Agent.objects.filter(email_address = request.POST['email']).values('agent_id')

			if qry_email.exists():
				if qry_email[0]['agent_id'] != request.session['agent_id']:
					messages.error(request, request.POST['email']+" Email Address Already Exists, Please Enter Differnt Email.")
					return redirect('admin_profile')
				else:
					full_name = request.POST['full_name']
					email_address = request.POST['email']
					if 'password' in request.POST and request.POST['password'] != '':
						if 'confirmpassword' in request.POST and request.POST['confirmpassword'] != '':
							password = request.POST['password']
							confirmpassword = request.POST['confirmpassword']
							if password == confirmpassword:
								agent_qry.full_name = full_name
								agent_qry.email_address = email_address
								agent_qry.set_password(password)
								agent_qry.save()
								request.session.flush()
								return redirect('/admin_ksf')
							else:
								messages.error(request, "Enter Same Password in Both Password Filed.")
								return redirect('admin_profile')
						else:
							return redirect('admin_profile')
					else:
						agent_qry.full_name = full_name
						agent_qry.email_address = email_address
						agent_qry.save()
						request.session['user_name'] = full_name
						return redirect('admin_profile')
		else:
			qry_agent = Agent.objects.get(agent_id=request.session['agent_id'])
			contect = {"user_profile" : qry_agent}
			return render(request , 'admin_panel/subadmin/profile.html',contect)


def dashboard(request):
	if not 'agent_id' in request.session:
		return redirect('/admin_ksf')
	else:
		Qry_Total_agent = Agent.objects.annotate(count=Count('agent_id')).exclude(is_admin=True) 
		Qry_Total_customer = customer.objects.annotate(count=Count('customer_id'))
		# .exclude(is_admin=True) 
		context = {
			'agents':Qry_Total_agent,
			'customer':Qry_Total_customer
		}
		return render(request, 'admin_panel/subadmin/deshboard.html', context)

def agent_list(request):
	if not 'agent_id' in request.session:
		return redirect('/admin_ksf')
	else:
		agent_list = Agent.objects.all().order_by('-agent_id').exclude(is_admin=True)
		contxt ={ "agent_list" : agent_list }
		return render(request,'admin_panel/subadmin/agent_list.html',contxt)

def add_agent(request):
	if not 'agent_id' in request.session:
		return redirect('/admin_ksf')
	else:
		if request.method == 'POST':
			try:
				qry_last = Agent.objects.all().values('agent_no').last()
				if qry_last['agent_no']:
					agent_no = 'Agent'+str(int(qry_last['agent_no'].split('Agent')[-1])+1)
				else:
					agent_no = 'Agent20210001'
				agent_password = pasword_create()
				# agent_no = request.POST['agent_no']
				agent_id = request.POST['agent_id']
				agent_full_name = request.POST['full_name']
				agent_email_address = request.POST['email_address']
				agent_address = request.POST['agent_address']
				agent_contact_no = request.POST['agent_phone']
				agent_dob = request.POST['agent_dob']
				agent_gender = request.POST['agent_gender']
				try:
					if agent_id != '':
						qry_agent_update = Agent.objects.get(agent_id=agent_id)
						qry_agent_update.agent_full_name  = agent_full_name
						qry_agent_update.agent_email_address = agent_email_address
						qry_agent_update.agent_address = agent_address
						qry_agent_update.agent_contact_no = agent_contact_no
						qry_agent_update.agent_dob = agent_dob
						qry_agent_update.agent_gender = agent_gender
						if 'agent_photo' in request.FILES:
							agent_photo = request.FILES['agent_photo']
							qry_agent_update.profile_photo = agent_photo
						if 'agent_idetity_doc' in request.FILES:
							agent_idetity_doc = request.FILES['agent_idetity_doc']
							qry_agent_update.identity_doc = agent_idetity_doc
						qry_agent_update.save()
					else:
						agent_photo = request.FILES['agent_photo']
						agent_idetity_doc = request.FILES['agent_idetity_doc']
						agent_qry = Agent(agent_no=agent_no,profile_photo=agent_photo,full_name=agent_full_name,
										email_address=agent_email_address,agent_gender=agent_gender,agent_dob=agent_dob,
										agent_address=agent_address,identity_doc=agent_idetity_doc,agent_contact_no=agent_contact_no)
						agent_qry.set_password(agent_password)
						agent_qry.save()
						# E-mail send start
						current_site = get_current_site(request)
						mail_subject = 'Activate your account.'
						message = render_to_string('admin_panel/authentication/acc_active_email.html', {
							'user': agent_qry,
							'domain': current_site.domain,
							'uid': urlsafe_base64_encode(force_bytes(agent_qry.pk)),
							'token': default_token_generator.make_token(agent_qry),
							'password':agent_password
						})
						to_email = agent_email_address
						email = EmailMessage(
							mail_subject, message, settings.EMAIL_HOST_USER, to=[to_email]
						)
						email.send()
						print(email.__dict__)
						print("emaill send Successfully")
					return redirect("agent_list")
				except Exception as e:
					messages.error(request,str(e))
					print(e,traceback.print_exc())
					return redirect("agent_list")
			except Exception as e:
				messages.error(request,str(e))
				return redirect("agent_list")
		else:
			return redirect("agent_list")

def agent_check_email(request):
	if not 'agent_id' in request.session:
		return redirect('/admin_ksf')
	else:
		if request.method == 'POST':
			print(request.POST)
			if 'agent_id' in request.POST:
				upadte_agent_id = request.POST['agent_id']
				email_address = request.POST['email_address']
				email_exist = Agent.objects.filter(email_address = email_address).values('agent_id')
				if email_exist.exists():
					if int(email_exist[0]['agent_id']) != int(upadte_agent_id):
						return JsonResponse(False,safe=False)
					else:
						return JsonResponse(True,safe=False)
				else:	
					return JsonResponse(True,safe=False)
			else: 
				email_address = request.POST['email_address']
				email_exist = Agent.objects.filter(email_address = email_address)
				if email_exist.exists():
					return JsonResponse(False,safe=False)
				else:
					return JsonResponse(True,safe=False)	
		else:
			return redirect("agent_list")

def get_agent(request):
	if not 'agent_id' in request.session:
		return redirect('/admin_ksf')
	else:
		if request.method == 'POST':
			agent_id = request.POST['agent_id']
			qry_agent_get = Agent.objects.filter(agent_id = agent_id).values()
			return JsonResponse(list(qry_agent_get)[0],safe=False)
			return redirect("agent_list")
		else:
			return redirect("agent_list")

def delete_agent(request):
	if not 'agent_id' in request.session:
		return redirect('/admin_ksf')
	else:
		if request.method == 'POST':
			try:
				delete_agent_id = request.POST['delete_agent_id']
				qry_delete = Agent.objects.get(agent_id = delete_agent_id)
				qry_delete.profile_photo.delete()
				qry_delete.identity_doc.delete()
				qry_delete.delete()
				return JsonResponse("Successfully delete agent",safe=False)
			except Exception as e:
				print("Error in delete user====>",str(e))
				return JsonResponse("Error Got delete agent",safe=False)	
		else:
			return redirect("agent_list")

# def agent_activate(request,uidb64,token):
# 	try:
# 		uid = urlsafe_base64_decode(uidb64).decode()
# 		agent = Agent._default_manager.get(pk=uid)
# 	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
# 		agent = None
# 	if agent is not None and default_token_generator.check_token(agent, token):
# 		agent.is_active = True
# 		agent.save()
# 		message = render_to_string('admin_panel/subadmin/agent_form.html',{'agents':agent})
# 		print(type(message))
# 		mail_subject = 'Activate your account.'
# 		to_email = agent.email_address
# 		email = EmailMessage(
# 			mail_subject, message, to=[to_email]
# 		)
# 		email.send()
# 		return render(request, 'admin_panel/authentication/acc_active_email_done.html')
# 	else:
# 		return render(request, 'admin_panel/authentication/acc_active_email_fail.html')



def customer_list(request):
	if not 'agent_id' in request.session:
		return redirect("/admin_ksf")
	else:
		qry_customer = customer.objects.all().order_by('-customer_id')
		context = {'customer_list':qry_customer}
	return render(request,'admin_panel/subadmin/customer_list.html',context)

def add_customer(request):
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
				return redirect("admin_customer_list")
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
						mail_subject, message, settings.EMAIL_HOST_USER, to=[to_email]
					)
					email.send()
					print(email.__dict__)
					print("emaill send Successfully")
					return redirect('admin_customer_list')
				except Exception as e:
					print("Error in add Customer====>",e)
					messages.error(request,str(e))
					return redirect("admin_customer_list")
		else:
			return redirect('admin_customer_list')

def customer_check_email(request):
	if not 'agent_id' in request.session:
		return redirect("/admin_ksf")
	else:
		if request.method == 'POST':
			if 'customer_id' in request.POST:
				customer_id = request.POST['customer_id']
				email = request.POST['email_address']
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
				qry_email = customer.objects.filter(customer_email=email)
				if qry_email.exists():
					return JsonResponse(False,safe=False)
				else:
					return JsonResponse(True,safe=False)
		else:
			return redirect("admin_customer_list")

def delete_customer(request):
	if not 'agent_id' in request.session:
		return redirect("/admin_ksf")
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
			return redirect('admin_customer_list')

def get_customer(request):
	if not 'agent_id' in request.session:
		return redirect('/admin_ksf')
	else:
		if request.method == 'POST':
			customer_id = request.POST['customer_id']
			qry_customer_get = customer.objects.filter(customer_id=customer_id).values()
			return JsonResponse(list(qry_customer_get)[0],safe=False)
		else:
			return redirect('admin_customer_list')
 

def staff_list(request):
	if not 'agent_id' in request.session:
		return redirect('/admin_ksf')
	else:
		return render(request,'admin_panel/subadmin/404_page.html')

# ================= sempla Data  =============================

def bank_collab_list(request):
	if not 'agent_id' in request.session:
		return redirect('/admin_ksf')
	else:
		return render(request,'admin_panel/subadmin/bank_collab.html')

def json_data(request):
	qry_customer = customer.objects.all().order_by('-customer_id').values('customer_id','full_name','customer_email','customer_contact_no','customer_gender','customer_dob','permenant_address')
	context = {'qry_customer':list(qry_customer)}
	print(context)
	return JsonResponse(context)

# ================= sempla Data  =============================



def loan_type(request):
	if not 'agent_id' in request.session:
		return redirect('/admin_ksf')
	else:
		qry_loan_type = LoanType.objects.all().order_by('-loan_type_id')
		context = {'loantypes':qry_loan_type}
		return render(request,'admin_panel/subadmin/loan_type.html',context)

def add_loan_type(request):
	if not 'agent_id' in request.session:
		return redirect('/admin_ksf')
	else:
		if request.method == 'POST':
			loan_type_id = request.POST['loan_type_id']
			loan_type_name = request.POST['loan_type_name']
			if loan_type_id != '':
				try:
					qry_update_loan_type = LoanType.objects.get(loan_type_id = loan_type_id)
					qry_update_loan_type.loan_type_name = loan_type_name
					qry_update_loan_type.save()
					messages.success(request,'Successfully Updated Loan Type.')
					return redirect('loan_type')	
				except Exception as e:
					print("Loan Type Update==>",e)
					messages.error(request,'Got Error like'+str(e))
					return redirect('loan_type')
			else:
				qry_add_loan_type = LoanType(loan_type_name = loan_type_name)
				try:
					qry_add_loan_type.save()
					messages.success(request,'Successfully Added Loan Type.')
					return redirect('loan_type')
				except Exception as e:
					print("Loan Type Add==>",e)
					messages.error(request,'Got Error like'+str(e))
					return redirect('loan_type')
		else:
			return redirect('loan_type')

def check_loan_type(request):
	if not 'agent_id' in request.session:
		return redirect('/admin_ksf')
	else:
		if request.method == 'POST':
			print(request.POST)
			loan_type_id = request.POST['loan_type_id']
			loan_type_name = request.POST['loan_type_name']
			qry_check_loan_type = LoanType.objects.filter(loan_type_name=loan_type_name).values('loan_type_id')
			if qry_check_loan_type.exists():
				if loan_type_id != '':
					if int(qry_check_loan_type[0]['loan_type_id']) == int(loan_type_id):
						return JsonResponse(True,safe=False)
					else:
						return JsonResponse(False,safe=False)
				else:
					return JsonResponse(False,safe=False)
			else:
				return JsonResponse(Tru,safe=False)
		else:
			return JsonResponse("Get Method Not Allow.",safe=False)

def get_loan_type(request):
	if not 'agent_id' in request.session:
		return redirect('/admin_ksf')
	else:
		if request.method == 'POST':
			print(request.POST)
			loan_type_id = request.POST['loan_type_id']
			qry_get_loan_type = LoanType.objects.filter(loan_type_id=loan_type_id).values('loan_type_id','loan_type_name')
			if qry_get_loan_type.exists():
				return JsonResponse(list(qry_get_loan_type),safe=False)
			else:
				return JsonResponse(True,safe=False)
		else:
			return JsonResponse("Get Method Not Allow.",safe=False)

def loan_list(request):
	if not 'agent_id' in request.session:
		return redirect('/admin_ksf')
	else:
		return render(request,'admin_panel/subadmin/loan_list.html')

def get_customer_loan(request):
	if not 'agent_id' in request.session:
		return redirect('/admin_ksf')
	else:
		if request.method == 'POST':
			qry_customer = customer.objects.all().order_by('-customer_id').values('customer_id','full_name','account_no')
			qry_loan_type = LoanType.objects.all().order_by('-loan_type_id').values('loan_type_id','loan_type_name')
			if qry_customer or qry_loan_type:
				context ={'customer_list':list(qry_customer),'loan_type_list':list(qry_loan_type)}
				return JsonResponse(context,safe=False)
			else:
				return JsonResponse(False,safe=False)
		else:
			return JsonResponse("Get Method Not Allow.",safe=False)

def add_loan(request):
	if not 'agent_id' in request.session:
		return redirect('/admin_ksf')
	else:
		if request.method == 'POST':
			print(request.POST)
			print(request.FILES)
			# <QueryDict: {'csrfmiddlewaretoken': ['vVKpXRHuAkMXfYHTjWHNOKsSCHtoAsjJb7t6JDFqC4upzK3FcbAKXV6QYTQKPHJg'], 
			# 'loan_type_id': ['5'], 'customer_name': ['1'], 'loan_cost': ['2012'], 'loan_interst': ['12'], 'loan_year': ['20'], 
			# 'nominees1_name': ['asdfgtre sd adfsdfs'], 'nominees2_name': ['asdfgtre sd adfsdfs']}>
			# <MultiValueDict: {'last_3year_income': [<InMemoryUploadedFile: 4089682219.pdf (application/pdf)>], 
			# 'loan_document': [<InMemoryUploadedFile: Aadhaar.pdf (application/pdf)>], 
			# 'nominees1_photo': [<InMemoryUploadedFile: FeesChallan_637387016903832321.pdf (application/pdf)>], 
			# 'nominees1_proof': [<InMemoryUploadedFile: final_bill.pdf (application/pdf)>], 
			# 'nominees1_sign': [<InMemoryUploadedFile: salary.docx (application/vnd.openxmlformats-officedocument.wordprocessingml.document)>], 
			# 'nominees2_photo': [<InMemoryUploadedFile: final_bill.pdf (application/pdf)>], 
			# 'nominees2_proof': [<InMemoryUploadedFile: bill1.pdf (application/pdf)>], 
			# 'nominees2_sign': [<InMemoryUploadedFile: salary-certificate-sample-1-638.jpg (image/jpeg)>]}>

			
			return HttpResponse("done")
		else:
			return redirect('loan_list')
		
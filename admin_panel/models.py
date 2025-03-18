from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email_address, password=None):
        if not email_address:
            raise ValueError('Users must have an email address')

        user = self.model(
            email_address=self.normalize_email(email_address),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email_address, password):
        user = self.create_user(
            email_address,
            password=password,
        )
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    agent_id = models.AutoField(primary_key=True)
    agent_no = models.CharField(max_length=30,unique=True,null=True)
    profile_photo = models.ImageField(upload_to='agent_profile',null=True)
    full_name = models.CharField(max_length=150,null=True)
    agent_dob = models.DateField(null=True)
    email_address = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    agent_contact_no = models.CharField(max_length=12,null=True)
    password = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    agent_address = models.TextField(null=True)
    agent_gender = models.CharField(max_length=100)
    identity_doc = models.ImageField(upload_to='agent_identity_documents',null=True)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)

    USERNAME_FIELD = 'email_address'
    REQUIRED_FIELDS = [] # Email & Password are required by default.

    def __str__(self):              # __unicode__ on Python 2
        return self.email_address
    def has_perm(self, perm, obj=None):
        return True
    def has_module_perms(self, app_label):
        return True

    objects = UserManager()

class CustomerManager(BaseUserManager):
    def create_customer(self, email_address, password=None):
        if not email_address:
            raise ValueError('Customer must have an email address')

        customer = self.model(
            email_address=self.normalize_email(email_address),
        )
        customer.set_password(password)
        customer.save(using=self._db)
        return customer

class customer(AbstractBaseUser):
    customer_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=150)
    customer_email = models.EmailField(max_length=255,unique=True)
    customer_contact_no =  models.CharField(max_length=12,null=True)
    customer_gender = models.CharField(max_length=30)
    customer_dob = models.DateField(null=True)
    residential_address = models.TextField()
    permenant_address = models.TextField()
    maiden_name = models.CharField(max_length=150)
    religion = models.CharField(max_length=100)
    cast = models.CharField(max_length=100)
    password = models.CharField(max_length=200)
    education = models.CharField(max_length=150)
    occupation = models.CharField(max_length=150)
    other_occupation = models.CharField(max_length=150,null=True) # Not remove null because other_occupation is black 
    marial_status = models.CharField(max_length=150)
    account_type = models.CharField(max_length=150)
    branch_name = models.CharField(max_length=150)
    account_no = models.CharField(max_length=20,unique=True)
    customer_no = models.CharField(max_length=20,unique=True)
    account_operter =models.CharField(max_length=100)
    joint_holder_name = models.CharField(max_length=150)
    customer_profile_photo = models.ImageField(upload_to='customer_profile_photos')
    customer_sign_image = models.ImageField(upload_to='customer_sign_image')
    customer_aadharcard_no = models.CharField(max_length=20)
    customer_aadharcard_image = models.ImageField(upload_to='customer_aadharcard_images')
    customer_pancard_no = models.CharField(max_length=20)
    customer_pancard_image = models.ImageField(upload_to='customer_pancard__images')
    is_active = models.BooleanField(default=False)
    who_add = models.CharField(max_length=20)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now = True)

    class Meta:
        db_table = 'Customer'

    objects = CustomerManager()


class LoanType(models.Model):
    loan_type_id = models.AutoField(primary_key=True)
    loan_type_name = models.CharField(max_length=255)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now = True)

    class Meta:
        db_table = 'loantype'

class LoanList(models.Model):
    loan_id = models.AutoField(primary_key=True)
    loan_number = models.CharField(unique=True)
    loan_type_id = models.F
    customer_name = models.
    loan_cost = models.
    loan_interst = models.
    loan_year = models.
    last_3year_income = models.
    loan_document = models.
    nominees1_name = models.
    nominees1_photo = models.
    nominees1_proof = models.
    nominees1_sign = models.
    nominees2_name = models.
    nominees2_photo = models.
    nominees2_proof = models.
    nominees2_sign = models.

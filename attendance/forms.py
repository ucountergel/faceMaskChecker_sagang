from re import T
from unicodedata import category

from django import forms
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm, UserChangeForm

from django.contrib.auth.models import User
from attendance.models import UserProfile


class UserRegistration(UserCreationForm):
    email = forms.EmailField(max_length=250,help_text="The email field is required.")
    first_name = forms.CharField(max_length=250,help_text="The First Name field is required.")
    last_name = forms.CharField(max_length=250,help_text="The Last Name field is required.")
    cam = forms.CharField(max_length=250, help_text="The cam field is required.")

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2', 'first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.get(email = email)
        except Exception as e:
            return email
        raise forms.ValidationError(f"The {user.email} mail is already taken/exists.")

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username = username)
        except Exception as e:
            return username
        raise forms.ValidationError(f"The {user.username} mail is already taken/exists.")

    def clean_cam(self):
        cam = self.cleaned_data['cam']
        try:
            profile = UserProfile.objects.get(cam=cam)
        except Exception as e:
            return cam
        raise forms.ValidationError(f"The {profile.cam} id cam is already taken/exists.")


class UpdateFaculty(UserChangeForm):
    username = forms.CharField(max_length=250,help_text="The username field is required.")
    email = forms.EmailField(max_length=250,help_text="The email field is required.")
    first_name = forms.CharField(max_length=250,help_text="The First Name field is required.")
    last_name = forms.CharField(max_length=250,help_text="The Last Name field is required.")
    cam = forms.CharField(max_length=250, help_text="The cam field is required.")
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')

    def __init__(self, user= None,*args, **kwargs):
        self.user = user
        super(UpdateFaculty, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.exclude(id= self.user.id).get(email = email)
        except Exception as e:
            return email
        raise forms.ValidationError(f"The {user.email} mail is already taken/exists.")

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.exclude(id=self.user.id).get(username=username)
        except Exception as e:
            return username
        raise forms.ValidationError(f"The {user.username} mail is already taken/exists.")
    def clean_cam(self):
        cam = self.cleaned_data['cam']
        try:
            profile = UserProfile.objects.exclude(id=self.user.id).get(cam=cam)
        except Exception as e:
            return cam
        raise forms.ValidationError(f"The {profile.cam} id cam is already taken/exists.")


class UpdateProfile(forms.ModelForm):
    username = forms.CharField(max_length=250,help_text="The Username field is required.")
    email = forms.EmailField(max_length=250,help_text="The Email field is required.")
    first_name = forms.CharField(max_length=250,help_text="The First Name field is required.")
    last_name = forms.CharField(max_length=250,help_text="The Last Name field is required.")
    current_password = forms.CharField(max_length=250)

    class Meta:
        model = User
        fields = ('email', 'username','first_name', 'last_name')

    def clean_current_password(self):
        if not self.instance.check_password(self.cleaned_data['current_password']):
            raise forms.ValidationError(f"Password is Incorrect")

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.exclude(id=self.cleaned_data['id']).get(email = email)
        except Exception as e:
            return email
        raise forms.ValidationError(f"The {user.email} mail is already taken/exists")

    def clean_cam(self):
        cam = self.cleaned_data['cam']
        try:
            profile= UserProfile.objects.exclude(id=self.cleaned_data['id']).get(cam = cam)
        except Exception as e:
            return cam
        raise forms.ValidationError(f"The {profile.cam} id cam is already taken/exists")

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.exclude(id=self.cleaned_data['id']).get(username = username)
        except Exception as e:
            return username
        raise forms.ValidationError(f"The {user.username} mail is already taken/exists")


class UpdateProfileMeta(forms.ModelForm):
    dob = forms.DateField(help_text="The Birthday field is required.")
    contact = forms.CharField(max_length=250,help_text="The Contact field is required.")
    address = forms.CharField(help_text="The Contact field is required.")

    class Meta:
        model = UserProfile
        fields = ('dob', 'contact', 'address','gender','avatar')


class UpdateProfileMetass(forms.ModelForm):
    gmail = forms.CharField(max_length=250, required=False, help_text="You can fill out this email field.")
    SystemName = forms.CharField(help_text="The Contact field is required.")

    class Meta:
        model = UserProfile
        fields = ('gmail','SystemName')


class UpdateProfileMetas(forms.ModelForm):
    dob = forms.DateField(help_text="The Birthday field is required.")
    contact = forms.CharField(max_length=250,help_text="The Contact field is required.")
    address = forms.CharField(help_text="The Contact field is required.")
    users_types = forms.CharField(max_length=250, help_text="The Users_Types field is required.")
    cam = forms.CharField(max_length=250, help_text="The cam field is required.")
    Assigned_places = forms.CharField(max_length=250, help_text="The assigned place field is required.")

    class Meta:
        model = UserProfile
        fields = ('dob', 'contact', 'address','gender','avatar','users_types','cam','Assigned_places')




class UpdatePasswords(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm rounded-0'}), label="Old Password")
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm rounded-0'}), label="New Password")
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm rounded-0'}), label="Confirm New Password")

    class Meta:
        model = User
        fields = ('old_password','new_password1', 'new_password2')


class UpdateProfileAvatar(forms.ModelForm):
    avatar = forms.ImageField(help_text="The Avatar field is required.")
    current_password = forms.CharField(max_length=250)

    class Meta:
        model = UserProfile
        fields = ('avatar',)
    
    def __init__(self,*args, **kwargs):
        self.user = kwargs['instance']
        kwargs['instance'] = self.user.profile
        super(UpdateProfileAvatar,self).__init__(*args, **kwargs)

    def clean_current_password(self):
        if not self.user.check_password(self.cleaned_data['current_password']):
            raise forms.ValidationError("Password is Incorrect")


class AddAvatar(forms.ModelForm):
    avatar = forms.ImageField(help_text="The Avatar field is required.")

    class Meta:
        model = UserProfile
        fields = ('avatar',)

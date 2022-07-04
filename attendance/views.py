from unicodedata import category
from aiohttp import request
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from faceMaskChecker_sagang.settings import MEDIA_ROOT, MEDIA_URL
from attendance.models import  UserProfile
from django.http.response import StreamingHttpResponse
from attendance.facemask_detector import VideoCamera, IPWebCam, MaskDetect, LiveWebCam,MaskDetects

from attendance.forms import UserRegistration, UpdateProfile, UpdateProfileMeta, UpdateProfileAvatar, AddAvatar,UpdatePasswords, UpdateFaculty, UpdateProfileMetas, UpdateProfileMetass

context = {
    'page_title' : 'FaceMask Checker System',

}
#login
def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')

#Logout

def ShowLoginPage(request):
    return render(request, "start_page.html")

def superadmin(request):
        return render(request, "login.html")

def admin1(request):
    return render(request, "login1.html")

def logoutuser(request):
    logout(request)
    return redirect('/')

@login_required
def home(request):
    context['page_title'] = 'Home'
    faculty = UserProfile.objects.filter(user_type = 2).count()
    context['faculty'] = faculty
    if request.user.profile.user_type == 1:
        faculty = UserProfile.objects.filter(user_type=2).count()
    return render(request, 'home.html',context)




def registerUser(request):
    user = request.user
    if user.is_authenticated:
        return redirect('home-page')
    context['page_title'] = "Register User"
    if request.method == 'POST':
        data = request.POST
        form = UserRegistration(data)
        if form.is_valid():
            form.save()
            newUser = User.objects.all().last()
            try:
                profile = UserProfile.objects.get(user = newUser)
            except:
                profile = None
            if profile is None:
                UserProfile(user = newUser, dob= data['dob'], contact= data['contact'],cam= data['cam'],users_types= data['users_types'],Assigned_places= data['Assigned_places'], address= data['address'], avatar = request.FILES['avatar']).save()
            else:
                UserProfile.objects.filter(id = profile.id).update(user = newUser, dob= data['dob'], contact= data['contact'],cam= data['cam'],users_types= data['users_types'],Assigned_places= data['Assigned_places'], address= data['address'])
                avatar = AddAvatar(request.POST,request.FILES, instance = profile)
                if avatar.is_valid():
                    avatar.save()
            username = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('password1')
            loginUser = authenticate(username= username, password = pwd)
            login(request, loginUser)
            return redirect('home-page')
        else:
            context['reg_form'] = form

    return render(request,'register.html',context)

@login_required
def profile(request):
    context = {
        'page_title':"My Profile"
    }

    return render(request,'profile.html',context)

@login_required
def prof(request):
    context = {
        'page_title':"System"
    }

    return render(request,'prof.html',context)

    
@login_required
def update_profile(request):
    context['page_title'] = "Update Profile"
    user = User.objects.get(id= request.user.id)
    profile = UserProfile.objects.get(user= user)
    context['userData'] = user
    context['userProfile'] = profile
    if request.method == 'POST':
        data = request.POST
        # if data['password1'] == '':
        # data['password1'] = '123'
        form = UpdateProfile(data, instance=user)
        if form.is_valid():
            form.save()
            form2 = UpdateProfileMeta(data, instance=profile)
            if form2.is_valid():
                form2.save()
                messages.success(request,"Your Profile has been updated successfully")
                return redirect("profile")
            else:
                # form = UpdateProfile(instance=user)
                context['form2'] = form2
        else:
            context['form1'] = form
            form = UpdateProfile(instance=request.user)
    return render(request,'update_profile.html',context)

def update_profiles(request):
        context['page_title'] = "Update Profile"
        user = User.objects.get(id=request.user.id)
        profile = UserProfile.objects.get(user=user)
        context['userData'] = user
        context['userProfile'] = profile
        if request.method == 'POST':
            data = request.POST
            # if data['password1'] == '':
            # data['password1'] = '123'
            form = UpdateProfileMetass(data, instance=user)
            if form.is_valid():
                form.save()
                form2 = UpdateProfileMetass(data, instance=profile)
                if form2.is_valid():
                    form2.save()
                    messages.success(request, "Your Profile has been updated successfully")
                    return redirect("prof")
                else:
                    # form = UpdateProfile(instance=user)
                    context['form2'] = form2
            else:
                context['form1'] = form
                form = UpdateProfile(instance=request.user)
        return render(request, 'update_System.html', context)


@login_required
def update_avatar(request):
    context['page_title'] = "Update Avatar"
    user = User.objects.get(id= request.user.id)
    context['userData'] = user
    context['userProfile'] = user.profile
    if user.profile.avatar:
        img = user.profile.avatar.url
    else:
        img = MEDIA_URL+"/default/default-avatar.png"

    context['img'] = img
    if request.method == 'POST':
        form = UpdateProfileAvatar(request.POST, request.FILES,instance=user)
        if form.is_valid():
            form.save()
            messages.success(request,"Your Profile has been updated successfully")
            return redirect("profile")
        else:
            context['form'] = form
            form = UpdateProfileAvatar(instance=user)
    return render(request,'update_avatar.html',context)

@login_required
def update_password(request):
    context['page_title'] = "Update Password"
    if request.method == 'POST':
        form = UpdatePasswords(user = request.user, data= request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Your Account Password has been updated successfully")
            update_session_auth_hash(request, form.user)
            return redirect("profile")
        else:
            context['form'] = form
    else:
        form = UpdatePasswords(request.POST)
        context['form'] = form
    return render(request,'update_password.html',context)



#Faculty
@login_required
def faculty(request):
    user = UserProfile.objects.filter(user_type = 2).all()
    context['page_title'] = "Admin Security Personnel Surveillance Account Management"
    context['faculties'] = user
    return render(request, 'faculty_mgt.html',context)

@login_required
def manage_faculty(request,pk=None):
    if pk == None:
        faculty = {}
    elif pk > 0:
        faculty = UserProfile.objects.filter(id=pk).first()

    else:

        faculty = {}
    context['page_title'] = "Manage Admin Security Personnel"
    context['faculty'] = faculty
    return render(request, 'manage_faculty.html',context)

@login_required
def view_faculty(request,pk=None):
    if pk == None:
        faculty = {}
    elif pk > 0:
        faculty = UserProfile.objects.filter(id=pk).first()
    else:
        faculty = {}
    context['page_title'] = "Manage Admin Security Personnel"
    context['faculty'] = faculty
    return render(request, 'faculty_details.html',context)

@login_required
def save_faculty(request):
    resp = { 'status' : 'failed', 'msg' : '' }
    if request.method == 'POST':
        data = request.POST
        if data['id'].isnumeric() and data['id'] != '':
            user = User.objects.get(id = data['id'])
        else:
            user = None
        if not user == None:
            form = UpdateFaculty(data = data, user = user, instance = user)
        else:
            form = UserRegistration(data)
        if form.is_valid():
            form.save()

            if user == None:
                user = User.objects.all().last()
            try:
                profile = UserProfile.objects.get(user = user)
            except:
                profile = None
            if profile is None:
                form2 = UpdateProfileMetas(request.POST,request.FILES)
            else:
                form2 = UpdateProfileMetas(request.POST,request.FILES, instance = profile)
                if form2.is_valid():
                    form2.save()
                    resp['status'] = 'success'
                    messages.success(request,'Admin Security Personnel has been saved successfully.')
                else:
                    User.objects.filter(id=user.id).delete()
                    for field in form2:
                        for error in field.errors:
                            resp['msg'] += str(error + '<br>')
            
        else:
            for field in form:
                for error in field.errors:
                    resp['msg'] += str(error + '<br>')

    return HttpResponse(json.dumps(resp),content_type='application/json')

@login_required
def delete_faculty(request):
    resp={'status' : 'failed', 'msg':''}
    if request.method == 'POST':
        id = request.POST['id']
        try:
            faculty = User.objects.filter(id = id).first()
            faculty.delete()
            resp['status'] = 'success'
            messages.success(request,'Admin Security Personnel has been deleted successfully.')
        except Exception as e:
            raise print(e)
    return HttpResponse(json.dumps(resp),content_type="application/json")


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def video_feed(request):
    return StreamingHttpResponse(gen(VideoCamera()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


def webcam_feed(request):
    return StreamingHttpResponse(gen(IPWebCam()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


def mask_feed(request):
    return StreamingHttpResponse(gen(MaskDetect()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')
def mask_feeds(request):
    return StreamingHttpResponse(gen(MaskDetects()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')
"""def lop_feed(request):
    return StreamingHttpResponse(gen(SocialDistanceAnalysis()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')"""


def livecam_feed(request):
    return StreamingHttpResponse(gen(LiveWebCam()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')



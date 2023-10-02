from django.shortcuts import render,redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
# Create your views here.

def login(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        
        user=auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('/')
        else:
            messages.info(request, 'invalid creds')
            return redirect('login')
    else:
        return render(request,'login.html')

def register(request):
    if request.method =='POST':
        username=request.POST['username']
        first_name=request.POST['address']
        password1=request.POST['password1']
        password2=request.POST['password2']
        
        if password1==password2:
            if User.objects.filter(username=username).exists():
                messages.info(request,"username taken")
                return redirect('register')
            elif User.objects.filter(first_name=first_name).exists():
                messages.info(request,"you are already a member")
                return redirect('register')
            else:
                user=User.objects.create_user(username=username,password=password1,first_name=first_name)
                user.save()
                messages.info(request,'user created')
                return redirect('/')
        else:
            messages.info(request,"password not matching")
            return redirect('register')
            
    else:
        return render(request,'register.html')
    
    
def logout(request):
    auth.logout(request)
    return redirect('/')
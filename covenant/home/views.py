from django.shortcuts import render
from .models import users
# Create your views here.
def home(request):
    return render(request,'home.html')
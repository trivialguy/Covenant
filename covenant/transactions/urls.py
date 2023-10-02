from django.urls import path
from . import views

urlpatterns = [
    path("transactions",views.transaction,name='transactions')
]

from django.db import models

# Create your models here.
class transactions(models.Model):
    Vote=models.CharField()
    address=models.CharField()
    secret_key=models.CharField(unique=True,editable=False)

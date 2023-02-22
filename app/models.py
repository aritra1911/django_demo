from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fname = models.CharField(max_length=128, blank=False, null=False)
    lname = models.CharField(max_length=128, blank=False, null=False)
    mname = models.CharField(max_length=128, blank=True, null=True, default='')
    panno = models.IntegerField()

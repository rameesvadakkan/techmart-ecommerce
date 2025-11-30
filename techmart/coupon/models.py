from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.PositiveIntegerField(help_text="Enter percentage (10 = 10%)")
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valid_from = models.DateField()
    valid_to = models.DateField()
    active = models.BooleanField(default=True)

    def is_valid(self):
        today = date.today()
        return self.active and self.valid_from <= today <= self.valid_to

    def __str__(self):
        return self.code
from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models
# from organization.models import *

class AdditionalUserData(models.Model):
    GENDER_CHOICES = [
        ('M','Male'),
        ('F','Female'),
        ('O', 'Other'),
        ('U', 'Prefer not to say'),
    ]
    is_organizer = models.BooleanField('organizer status', default=False)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, default='U')
    date_of_birth = models.DateField()  

    def __str__(self):
        username = self.user.username if hasattr(self, 'user') and self.user else "No User"
        return (
            f"Username: {username}"
        )

class User(AbstractUser):
    additional_data = models.OneToOneField(
        AdditionalUserData, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='user'
    ) 

    @property
    def short_username(self):
        parts = self.username.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        elif len(self.username) >= 2:
            return self.username[:2].upper()
        elif len(self.username) == 1:
            return (self.username[0]).upper()
        else:
            return 'UK'
    
    def __str__(self):
        return (
            f"{self.username}"
        )


class Order_addtional_details(models.Model):
    team_name = models.CharField(max_length=100)
    category = models.ForeignKey('organization.Category', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    

class Order(models.Model):
    order_id = models.CharField(max_length=100, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    status = models.BooleanField(default=False)
    order_timestamp = models.DateTimeField(auto_now_add=True)
    order_details = models.OneToOneField(Order_addtional_details, on_delete=models.CASCADE, related_name='order_details', blank=True, null=True)
    
    signature = models.CharField(max_length=255, blank=True, null=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    
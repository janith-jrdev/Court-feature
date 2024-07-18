from django.contrib.auth.models import AbstractUser
from django.db import models

class AdditionalUserData(models.Model):
    GENDER_CHOICES = [
        ('M','Male'),
        ('F','Female'),
        ('O', 'Other'),
        ('U', 'Prefer not to say'),
    ]
    is_organiser = models.BooleanField('organizer status', default=False)
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

    def __str__(self):
        return (
            f"{self.username}"
        )



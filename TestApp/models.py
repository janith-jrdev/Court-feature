from django.contrib.auth.models import AbstractUser
from django.db import models

class add_userData(models.Model):
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
        return (
            f"ID: {self.id}, "
            f"Is Organiser: {self.is_organiser}, "
            f"Gender: {self.get_gender_display()}, "
            f"Date of Birth: {self.date_of_birth}"
        )

class User(AbstractUser):
    last_name = None
    first_name = None
    full_name = None
    email = models.EmailField(max_length=254, blank=False, unique=True)
    name = models.CharField('full name', max_length=254)
    cart = models.ManyToManyField('organisers.Team', blank=True)
    verified = models.BooleanField(default=False)
    orders = models.ManyToManyField('Order', blank=True, related_name='orders_all')
    orders_success = models.ManyToManyField('Order', blank=True, related_name='orders_paid')
    add_User = models.ForeignKey(add_userData, blank=True, null=True, on_delete=models.SET_NULL)  

    def __str__(self):
        return (
            f"ID: {self.id}, "
            f"Email: {self.email}, "
            f"Name: {self.name}, "
            f"Verified: {self.verified}, "
            f"Add User: {self.add_User}"
        )



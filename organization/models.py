from django.db import models
from core.models import User
# Create your models here.
class Organization(models.Model):
    name = models.CharField(max_length=255)
    ph_number = models.CharField(max_length=10)
    mail = models.EmailField(max_length=255)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class Tournament(models.Model):
    name = models.CharField(max_length=255)
    details = models.TextField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    venue_address = models.CharField(max_length=1024)
    venue_link = models.URLField(max_length=512)
    categories = models.ManyToManyField('Category', blank=True)
    
    # things to be added
        # poster
        # courts
        
    def __str__(self):
        return f"{self.name} - {self.organization.name}"
    
class Category(models.Model):
    name = models.CharField(max_length=255)
    details = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    registration_status = models.BooleanField(default=True)
    
    # things to be added
        # winner
        # teams
        # fixture type
        
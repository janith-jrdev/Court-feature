from django.db import models
from core.models import User,Match
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from datetime import datetime
import json

# Create your models here.
class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    ph_number = models.CharField(max_length=10)
    mail = models.EmailField(max_length=255)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organization")
    # details = models.TextField() ??
    def __str__(self):
        return self.name

class Tournament(models.Model):
    name = models.CharField(max_length=255)
    details = models.TextField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="tournaments")
    start_date = models.DateField()
    end_date = models.DateField()
    venue_address = models.CharField(max_length=1024)
    venue_link = models.URLField(max_length=512)
    ph_number = models.CharField(max_length=10, default="")
    #poster = models.ImageField(upload_to='posters/')
    # things to be added
        
        # courts
        
    @property
    def completed(self):
        return self.end_date < datetime.now().date()
        
    def __str__(self):
        return f"{self.name} - {self.organization.name}"

from uuid import uuid4

class Court(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='courts')
    is_available = models.BooleanField(default=True)
    current_match = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.tournament.name}"

class Category(models.Model):
    name = models.CharField(max_length=255)
    details = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    winner = models.ForeignKey('Team', on_delete=models.SET_NULL, blank= True, null= True, related_name="won_categories")
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="categories")
    fixture = models.ForeignKey('Fixture', on_delete=models.SET_NULL, related_name="category_fixture", blank= True, null= True)
    registration_status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.tournament.name}"

class Fixture(models.Model):
    FIXTURE_CHOICES = [
        ('KO', 'Knockout'),
        ('RR', 'Round Robin'),
        ('RR_KO', 'Round Robin + Knockout'),
    ]
    fixtureType = models.CharField(max_length=5, choices=FIXTURE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="fixture_category", blank= True, null= True)
    fixture_data = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('fixture_data', 'object_id')
    scheduled_matches = models.ManyToManyField('Match', related_name='scheduled_matches', blank=True)
    
    def save(self, *args, **kwargs):
        if self.fixtureType == 'KO':
            self.fixture_data = ContentType.objects.get_for_model(Knockout)
        elif self.fixtureType == 'RR':
            self.fixture_data = ContentType.objects.get_for_model(RoundRobin)
        elif self.fixtureType == 'RR_KO':
            self.fixture_data = ContentType.objects.get_for_model(RoundRobinKnockout)
        super(Fixture, self).save(*args, **kwargs)
        
    def __str__(self):
        return f"Fixture - {self.fixtureType} - {self.category.name} - {self.category.tournament.name}"
        

class Knockout(models.Model):
    _json = models.TextField(db_column='json', blank=True, null=True)
    
    @property
    def json(self):
        return json.loads(self._json) if self._json else None
    
    @json.setter
    def json(self, value):
        self._json = json.dumps(value) if value is not None else None
    fixing_manual = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category")
    bracket_teams = models.ManyToManyField('Team', related_name='bracket', blank=True)
    winners_bracket = models.ManyToManyField('Team', related_name='bracket_winners', blank=True)
    bracket_matches = models.ManyToManyField('Match', related_name='bracket_match', blank=True)
    all_matches = models.ManyToManyField('Match', related_name='bracket_all_matches', blank=True)
    ko_stage = models.IntegerField(default=-1)
    def __str__(self):
        return f"Knockout - {self.category.name} - {self.category.tournament.name}"
    
class RoundRobin(models.Model):
    ...
    def __str__(self):
        return f"Round Robin - {self.category.name} - {self.category.tournament.name}"

class RoundRobinKnockout(models.Model):
    ...
    def __str__(self):
        return f"Round Robin + Knockout - {self.category.name} - {self.category.tournament.name}"

class Team(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="teams")
    # payment_method = models.CharField(max_length=255)
    # payment mode
    
    def __str__(self):
        return f"{self.name} - {self.category.name} - {self.category.tournament.name}"

class Match(models.Model):
    # Teams
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="match_team1", blank=True, null=True)
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="match_team2", blank=True, null=True)
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, related_name="match_winner", blank=True, null=True)

    # Match details
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="match_category")
    match_state = models.BooleanField(default=False)
    match_number = models.IntegerField(null=True, blank=True)
    stage_number = models.IntegerField(null=True, blank=True)

    # Set information
    no_sets = models.IntegerField(default=1)
    sets = models.ManyToManyField('SetScoreboard', related_name='match_sets', blank=True)
    current_set = models.ForeignKey('SetScoreboard', on_delete=models.SET_NULL, related_name='match_current_set', blank=True, null=True)

    # Scoring
    win_points = models.IntegerField(default=15)

    # TODO: Add court information when scheduling matches or create a new model for courts
    
    def __str__(self):
        team1, team2 = "Bye", "Bye"
        if self.team1:
            team1 = self.team1.name
        if self.team2:
            team2 = self.team2.name
        
        return f"{team1} vs {team2} - {self.category.name} - {self.category.tournament.name}"
    
class SetScoreboard(models.Model):
    set_no = models.IntegerField()
    team1_score = models.IntegerField(default=0)
    team2_score = models.IntegerField(default=0)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='set_match')
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, related_name='set_winner', blank=True, null=True)
    set_state = models.BooleanField(default=False)
    # win set score
    def __str__(self):
        return f"Set {self.set_no} - {self.match.team1.name} vs {self.match.team2.name} - {self.match.category.name} - {self.match.category.tournament.name}"
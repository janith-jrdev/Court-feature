from django.db import models
from core.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

# Create your models here.
class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    ph_number = models.CharField(max_length=10)
    mail = models.EmailField(max_length=255)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    # details = models.TextField() ??
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
    categories = models.ForeignKey('Category', blank=True,null=True, on_delete=models.CASCADE, related_name="tournament_category")
    ph_number = models.CharField(max_length=10, default="")
    #poster = models.ImageField(upload_to='posters/')
    # things to be added
        
        # courts
        
    def __str__(self):
        return f"{self.name} - {self.organization.name}"

class Category(models.Model):
    name = models.CharField(max_length=255)
    details = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    teams = models.ManyToManyField('Team', related_name='category_team', blank= True)# can be removed
    fixture = models.ForeignKey('Fixture', on_delete=models.CASCADE, related_name='category_fixture', blank= True, null= True)
    winner = models.ForeignKey('Team', on_delete=models.SET_NULL, related_name='category_winner', blank= True, null= True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="category_tournament")
    registration_status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.tournament.name}"

class Fixture(models.Model):
    FIXTURE_CHOICES = [
        ('KO', 'Knockout'),
        ('RR', 'Round Robin'),
        ('RR_KO', 'Round Robin + Knockout'),
    ]
    fixtureType = models.CharField(max_length=5, choices=FIXTURE_CHOICES, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="fixture_category", blank= True, null= True)
    fixture_data = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('fixture_data', 'object_id')
    
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
    json = models.JSONField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="knockout_category")
    bracket_teams = models.ManyToManyField('Team', related_name='knockout_bracket', blank=True)
    winners_bracket = models.ManyToManyField('Team', related_name='knockout_winners', blank=True)
    # bracket_matches = models.ManyToManyField('Match', related_name='knockout_match', blank=True)
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
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="team_category")
    # payment_method = models.CharField(max_length=255)
    # payment mode
    
    def __str__(self):
        return f"{self.name} - {self.category.name} - {self.category.tournament.name}"
    
class Match(models.Model):
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="match_team1")
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="match_team2")
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, related_name="match_winner", blank=True, null=True)
    match_state = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="match_category")
    # court 
    no_sets = models.IntegerField(default=1)
    sets = models.ManyToManyField('SetScoreboard', related_name='match_sets', blank=True)
    current_set = models.ForeignKey('SetScoreboard', on_delete=models.SET_NULL, related_name='match_current_set', blank=True, null=True)
    def __str__(self):
        return f"{self.team1.name} vs {self.team2.name} - {self.category.name} - {self.category.tournament.name}"
    
class SetScoreboard(models.Model):
    set_no = models.IntegerField()
    team1_score = models.IntegerField(default=0)
    team2_score = models.IntegerField(default=0)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='set_match')
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, related_name='set_winner', blank=True, null=True)
    set_state = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Set {self.set_no} - {self.match.team1.name} vs {self.match.team2.name} - {self.match.category.name} - {self.match.category.tournament.name}"
from sportshunt.utils import *
from django.contrib import messages
from .models import *
from datetime import datetime
import re, json

# make a AbstractValidator class
class AbstractValidator:
    def __init__(self, data, req):
        self.data = clean_querydict(data)
        self.req = req
        self.user = req.user
        self.errors = {}
        self.validatation = self.clean_validate_save()
    
    
    def clean_validate_save(self):
        clean_and_validate_fns = [fn for fn in dir(self) if fn.startswith('validate_')]
        for fn in clean_and_validate_fns:
            fn_call = getattr(self, fn)
            _, key = fn.split('_', 1)
            fn_data = self.data.get(key, "").strip()
            fn_call(fn_data)
            
        if self.errors:
            for key, value in self.errors.items():
                messages.error(self.req, f"{key}: {value}")
            return False
            
        return self.save()

class OrganizationValidator(AbstractValidator):
    
    def validate_name(self, name):
        if not name:
            self.errors['name'] = "Name cannot be empty"
            return False
        if Organization.objects.filter(name=name).exists():
            self.errors['name'] = "Organization with this name already exists"
            return False
        return True
    
    def validate_ph_number(self, ph_number):
        if not ph_number:
            self.errors['ph_number'] = "Phone number cannot be empty"
            return False
        if len(ph_number) != 10:
            self.errors['ph_number'] = "Phone number should be 10 digits"
            return False
        if not ph_number.isdigit():
            self.errors['ph_number'] = "Phone number should contain only digits"
            return False
        return True
    
    def validate_mail(self, mail):
        if not mail:
            self.errors['mail'] = "Email cannot be empty"
            return False
        return True
    
    def save(self):
        try:
            Organization.objects.create(
                name=self.data.get('name'),
                ph_number=self.data.get('ph_number'),
                mail=self.data.get('mail'),
                admin=self.user
            )
        except Exception as e:
            self.errors['save'] = str(e)
            if self.errors:
                for key, value in self.errors.items():
                    messages.error(self.req, f"{key}: {value}")
            return False
        return True
       
class TournamentValidator(AbstractValidator):
    def __init__(self, data, req):
        self.tournament_id = None
        super().__init__(data, req)

    def validate_name(self, name):
        if not name:
            self.errors['name'] = "Name cannot be empty"
            return False
        return True

    def validate_details(self, details):
        if not details:
            self.errors['details'] = "Details cannot be empty"
            return False
        return True
    
    def validate_start_date(self, start_date):
        if not start_date:
            self.errors['start_date'] = "Start date cannot be empty"
            return False
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if start_date < datetime.now():
            self.errors['start_date'] = "Start date cannot be in the past"
            return False
        return True
    
    def validate_end_date(self, end_date):
        if not end_date:
            self.errors['end_date'] = "End date cannot be empty"
            return False
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        start_date = datetime.strptime(self.data.get('start_date'), '%Y-%m-%d')
        if end_date < datetime.now():
            self.errors['end_date'] = "End date cannot be in the past"
            return False
        if end_date < start_date:
            self.errors['end_date'] = "End date cannot be before start date"
            return False
        return True
    
    def validate_ph_number(self, ph_number):
        if not ph_number:
            self.errors['ph_number'] = "Phone number cannot be empty"
            return False
        if len(ph_number) != 10:
            self.errors['ph_number'] = "Phone number should be 10 digits"
            return False
        if not ph_number.isdigit():
            self.errors['ph_number'] = "Phone number should contain only digits"
            return False
        return True
    
    def validate_venue_address(self, venue_address):
        if not venue_address:
            self.errors['venue_address'] = "Venue address cannot be empty"
            return False
        return True
    
    def validate_venue_link(self, venue_link):
        google_maps_regex = r'^https?:\/\/(?:www\.|maps\.app\.)?(?:google\.com\/maps\/|goo\.gl\/)\S*$'
        if venue_link and not re.match(google_maps_regex, venue_link):
            self.errors['venue_link'] = 'Invalid Google Maps link'
            return False

        return True
    
    def save(self):
        try:
            org_instance = Organization.objects.get(id=int(self.req.session.get('organization')))
            tournament_instance = Tournament.objects.create(
                name=self.data.get('name'),
                details=self.data.get('details'),
                organization= org_instance,
                start_date=self.data.get('start_date'),
                end_date=self.data.get('end_date'),
                venue_address=self.data.get('venue_address'),
                venue_link=self.data.get('venue_link'),
                ph_number=self.data.get('ph_number')
            )
        except Exception as e:
            self.errors['save'] = str(e)
            if self.errors:
                for key, value in self.errors.items():
                    messages.error(self.req, f"{key}: {value}")
            return False
        self.tournament_id = tournament_instance.id
        return True
    
class CategoryValidator(AbstractValidator):
    def __init__(self, data, req, tournament_id):
        self.tournament_id = tournament_id
        self.category_id = None
        super().__init__(data, req)
    
    def validate_name(self, name):
        if not name:
            self.errors['name'] = "Name cannot be empty"
            return False
        if Category.objects.filter(name=name, tournament_id=self.tournament_id).exists():
            self.errors['name'] = "Category with this name already exists in the tournament"
            return False
        if name == "new_category":
            self.errors['name'] = "Invalid category name"
            return False
        return True

    def validate_details(self, details):
        if not details:
            self.errors['details'] = "Details cannot be empty"
            return False
        return True
    
    def validate_price(self, price):
        if not price:
            self.errors['price'] = "Price cannot be empty"
            return False
        try:
            price = float(price)
            if price < 0:
                self.errors['price'] = "Price cannot be negative"
                return False
        except ValueError:
            self.errors['price'] = "Invalid price format"
            return False
        return True
    

    
    def save(self):
        try:
            tournament_instance = Tournament.objects.get(id=self.tournament_id)
            category_instance = Category.objects.create(
                name=self.data.get('name'),
                details=self.data.get('details'),
                price=self.data.get('price'),
                tournament=tournament_instance,
                registration_status=True
            )
        except Exception as e:
            self.errors['save'] = str(e)
            if self.errors:
                for key, value in self.errors.items():
                    messages.error(self.req, f"{key}: {value}")
            return False
        self.category_id = category_instance.id
        return True


def ScheduleMatchValidator(data, category_instance, ko_instance):
    data = json.loads(data)
    if not data:
        return False, "Invalid JSON data"
    
    match_instances = []
    for match in data:
        team1, team2 = match.get('team1'), match.get('team2')
        
        if not team1 and not team2:
            return False, "Team name cannot be empty"
        
        if team1:
            team1 = Team.objects.get(id=team1, category=category_instance)
        
        if team2:
            team2 = Team.objects.get(id=team2, category=category_instance)
        
        match_instance = Match.objects.create(
            category=category_instance,
            team1=team1,
            team2=team2,
            no_sets=3
        )
        
        if not team1:
            match_instance.winner = team2
            ko_instance.winners_bracket.add(team2)
        elif not team2:
            match_instance.winner = team1
            ko_instance.winners_bracket.add(team1)
        else:
            match_instances.append(match_instance)
        
        match_instance.save()
    ko_instance.bracket_matches.set(match_instances)
    ko_instance.save()
    return True, "matches scheduled successfully"
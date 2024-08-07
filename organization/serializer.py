from .models import *

def tournamentSerializer(tournament):
     # tournament
        #poster(later),
     return {
        'id': tournament.id,
        'name': tournament.name,
        'details': tournament.details,
        'start_date': tournament.start_date,
        'end_date': tournament.end_date,
        'organization': tournament.organization,
        'venue': tournament.venue_address,
        'venue_link': tournament.venue_link,
        'categories': tournament.categories.all(), 
        'ph_number': tournament.ph_number,
     }
     
def categorySerializer(category):

   return {
         'id': category.id,
         'name': category.name,
         'details': category.details,
         'price': category.price,
         'teams': category.teams.all(),
         'fixture': category.fixture,
         'winner': category.winner,
         'tournament': category.tournament,
         'registration_status': category.registration_status,
   }
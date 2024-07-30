from .models import *

def tournamentSerializer(tournament):
     # tournament
        #poster(later),
     return {
        'id': tournament.id,
        'name': tournament.name,
        'status': tournament.status,
        'description': tournament.description,
        'start_date': tournament.start_date,
        'end_date': tournament.end_date,
        'organization': tournament.organization,
        'venue': tournament.venue_address,
        'venue_link': tournament.venue_link,
        'category': tournament.category_tournaments, 
        'ph_number': tournament.ph_number,
    # 'location': tournament.location,
    # 'teams': [teamSerializer(team) for team in tournament.teams.all()],
    # 'matches': [matchSerializer(match) for match in tournament.matches.all()],
     }
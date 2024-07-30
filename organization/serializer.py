from .models import *

def tournamentSerializer(tournament):
    # something like this
    # return {
    #     'id': tournament.id,
    #     'name': tournament.name,
    #     'description': tournament.description,
    #     'start_date': tournament.start_date,
    #     'end_date': tournament.end_date,
    #     'location': tournament.location,
    #     'organization': organizationSerializer(tournament.organization),
    #     'teams': [teamSerializer(team) for team in tournament.teams.all()],
    #     'matches': [matchSerializer(match) for match in tournament.matches.all()],
    # }
    ...
from .models import *
import math

def tournamentSerializer(tournament):
    # tournament
    # poster(later),
    return {
        "id": tournament.id,
        "name": tournament.name,
        "details": tournament.details,
        "start_date": tournament.start_date,
        "end_date": tournament.end_date,
        "organization": tournament.organization,
        "venue": tournament.venue_address,
        "venue_link": tournament.venue_link,
        "categories": tournament.categories.all(),
        "ph_number": tournament.ph_number,
    }


def categorySerializer(category):
    # print(category.fixture.content_object.bracket_matches.all())
    data = {
        "id": category.id,
        "name": category.name,
        "details": category.details,
        "price": category.price,
        "teams": category.teams.all(),
        "winner": category.winner,
        "tournament": category.tournament,
        "registration_status": category.registration_status,
    }
    
    # if no fixture.scheduled matches and no ko.bracket matches
        # but ko.winners bracket has teams then
            # if len = 1 : winner = team
            # else: create matches with those teams
    
    if category.fixture and category.fixture.fixtureType == "KO":
        teams_data = []
        if category.fixture.content_object.bracket_teams.all():
            for team in category.fixture.content_object.bracket_teams.all():
                teams_data.append({"id": team.id, "name": team.name})
            
            print(teams_data, len(teams_data))
            next_power_of_2 = 2 ** math.ceil(math.log2(len(teams_data)))
            byes = next_power_of_2 - len(teams_data)
            
            for i in range(byes):
                teams_data.append({"id": "None", "name": "Bye"})
                
            print(teams_data)
            data["teams_data"] = teams_data
    return data

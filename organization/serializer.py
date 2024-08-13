from .models import *


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

    if category.fixture:
        data["fixture"] = category.fixture
        if category.fixture.fixtureType:
            data["fixture_type"] = category.fixture.fixtureType
            if category.fixture.content_object:
                data["fixture_data"] = category.fixture.content_object
                if category.fixture.content_object.fixing_manual:
                    data["winners_bracket"] = (
                        category.fixture.content_object.winners_bracket.all()
                    )
                    data["bracket_matches"] = (
                        category.fixture.content_object.bracket_matches.all()
                    )
                    
    print(data)
    return data

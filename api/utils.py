from organization.models import *
import math

def create_team(category_instance, team_name):
    return Team.objects.create(
        name=team_name,
        category=category_instance
    )
    
def create_ko_fixture(category_instance, data):
    fixture_mode = data.get('fixture_mode', False)
    
    ko_instance = Knockout.objects.create(
        category=category_instance, 
        fixing_manual=fixture_mode
    )
    
    teams = category_instance.teams.all()
    ko_instance.bracket_teams.set(teams)
    no_teams = len(teams)
    cur_lvl = math.ceil(math.log2(no_teams))
    
    ko_instance.ko_stage = cur_lvl
    ko_instance.save()
    
    fixture_instance = Fixture.objects.create(
        fixtureType='KO', 
        category=category_instance,
        content_object=ko_instance
    )
    
    category_instance.fixture = fixture_instance
    category_instance.save()
    
    return {"message": "Fixture type updated successfully"}

def schedule_ko_match(fixture_instance, data):
    ko_instance = fixture_instance.content_object
    match_id = int(data.get('match'))
    no_sets = int(data.get('no_sets'))
    
    match_instance = Match.objects.get(id=match_id)
    match_instance.no_sets = no_sets
    match_instance.win_points = int(data.get("set_winning_points"))
    match_instance.save()
    
    for i in range(no_sets):
        set_instance = SetScoreboard.objects.create(set_no=i+1, match=match_instance)
        match_instance.sets.add(set_instance)

    match_instance.current_set = SetScoreboard.objects.get(set_no=1, match=match_instance)
    match_instance.save()

    fixture_instance.scheduled_matches.add(match_instance)
    fixture_instance.save()
    
    ko_instance.bracket_matches.remove(match_instance)
    ko_instance.save()
    
    return {"message": "Match scheduled successfully"}



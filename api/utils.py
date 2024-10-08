from organization.models import *
import math, json

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

class Fixture_Json_Manager:
    def __init__(self, ko_instance):
        self.ko_instance = ko_instance
        self.fixture_json = self._load_fixture_json()

    def _load_fixture_json(self):
        if not self.ko_instance.json:
            return {"rounds": []}
        return json.loads(self.ko_instance.json)

    def update_fixture_json(self, match_instances, data):
        current_round = []
        for match_instance in match_instances:
            match_json = {
                "id": match_instance.id,
                "teams": [match_instance.team1.name if match_instance.team1 else "BYE", match_instance.team2.name if match_instance.team2 else "BYE"],
                "winner": 0 if not match_instance.team2 else 1 if not match_instance.team1 else None
            }
            current_round.append(match_json)
        
        # Add all matches to the first round
        self.fixture_json["rounds"].append({"matches": current_round})

        # Add empty rounds for future stages
        teams_count = len(data["matches"])
        while teams_count > 1:
            teams_count = teams_count // 2
            empty_round = {
                "matches": [
                    {
                        "id": None,
                        "teams": [None, None],
                        "winner": None
                    } for _ in range(teams_count)
                ]
            }
            self.fixture_json["rounds"].append(empty_round)
        
        self.ko_instance.json = json.dumps(self.fixture_json)
        self.ko_instance.all_matches.set(match_instances)
        self.ko_instance.save()

        return self.fixture_json

    def update_winner(self, match_id, winner):
        for round_index, round in enumerate(self.fixture_json["rounds"]):
            for match in round["matches"]:
                if match["id"] == match_id:
                    match["winner"] = 0 if winner == 0 else 1
                    # Add the winner to the next stage matches
                    if round_index + 1 < len(self.fixture_json["rounds"]):
                        next_round = self.fixture_json["rounds"][round_index + 1]
                        next_match_index = match_id // 2
                        if next_match_index < len(next_round["matches"]):
                            next_match = next_round["matches"][next_match_index]
                            if match_id % 2 == 0:
                                next_match["teams"][0] = match["teams"][winner]
                            else:
                                next_match["teams"][1] = match["teams"][winner]
                    break
        self.ko_instance.json = json.dumps(self.fixture_json)
        self.ko_instance.save()

        
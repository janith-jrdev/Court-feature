from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from organization.models import *
from core.models import *
import json
from django.core.exceptions import ObjectDoesNotExist
from organization.validators import *
from django.conf import settings
from django.urls import reverse
import razorpay
from .decorators import *
import math
from .utils import Fixture_Json_Manager
from django.views.decorators.csrf import csrf_exempt

@valid_json_data
@host_required
def off_registration(req, category_id):
    category_instance = get_object_or_404(Category, id=category_id)
    data = json.loads(req.body)
    team_name = data.get('team_name')
    
    if not team_name:
        return JsonResponse({"message": "Team name cannot be empty"}, status=400)
    
    if not category_instance.registration_status:
        return JsonResponse({"message": "Registration closed"}, status=400)
    
    Team.objects.create(
        name=team_name,
        category=category_instance
    )
    
    return JsonResponse({"message": "Registration successfully"}, status=200)


@host_required
def close_categoryReg(req, category_id):
    print("close category")
    category_instance = Category.objects.get(id=category_id)
    category_instance.registration_status = False
    category_instance.save()
    Teams=category_instance.teams.all()
    
    if Teams and len(Teams) < 2:
        category_instance.winner = Teams[0]
        category_instance.save()
        return JsonResponse({"message": "Category over"})
    
    print("category closed")
    return JsonResponse({"message": "Registration closed successfully"})

@valid_json_data
@host_required
def fixturetype_form(req, category_id):
    category_instance = Category.objects.get(id=category_id)

    data = json.loads(req.body)
    fixture_type = data.get('fixtureType')
    
    if not fixture_type:
        return JsonResponse({"message": "Fixture type cannot be empty"}, status=400)
    
    if fixture_type not in ['KO']: #, 'RR', 'RR_KO' add these later
        return JsonResponse({"message": "Invalid fixture type"}, status=400)
    
    fixture_instance = Fixture.objects.create(fixtureType=fixture_type, category=category_instance)
    
    if fixture_type == 'KO':
        fixture_mode = data.get('koOption', "Manual")

        if fixture_mode not in ['Manual', 'Automatic']:
            return JsonResponse({"message": "Invalid fixture mode"}, status=400)
        
        if fixture_mode == 'Manual':
            fixture_mode = True
        else:
            fixture_mode = False
        
        ko_instance = Knockout.objects.create(category=category_instance, fixing_manual=fixture_mode)
        ko_instance.bracket_teams.set(category_instance.teams.all())
        no_teams = category_instance.teams.count()
        cur_lvl =  math.ceil(math.log2(no_teams))
        ko_instance.ko_stage = cur_lvl 
        ko_instance.save()
        
        fixture_instance.content_object = ko_instance
        fixture_instance.save()
        category_instance.fixture = fixture_instance
        category_instance.save()

        return JsonResponse({"message": "Fixture type updated successfully"})
    
    return JsonResponse({"message": "some server side error, ps it should be KO."}, status=500)

@host_required
def schedule_match(req, category_id):
    category_instance = Category.objects.get(id=category_id)
    fixture_instance = category_instance.fixture    
    if not fixture_instance:
        return JsonResponse({"message": "Fixture not created yet"}, status=400)
    
    data = json.loads(req.body)

    if fixture_instance.fixtureType == 'KO':
        ko_instance = fixture_instance.content_object
        bracket_matches = [match.id for match in ko_instance.bracket_matches.all()]
        
        match_id = int(data.get('match_id'))
        if not match_id in bracket_matches:
            return JsonResponse({"message": "Match not in bracket matches"}, status=400)
        
        match_instance = Match.objects.get(id=match_id)
        match_instance.current_set = SetScoreboard.objects.get(set_no=1, match=match_instance)
        match_instance.save()
        
        # Find available court
        available_court = Court.objects.filter(
            tournament=category_instance.tournament, 
            is_available=True
        ).first()
        
        if available_court:
            # Assign match to court
            available_court.current_match = match_instance
            available_court.is_available = False
            available_court.save()
            
            fixture_instance.scheduled_matches.add(match_instance)
            fixture_instance.save()
            ko_instance.bracket_matches.remove(match_instance)
            ko_instance.save()
            
            return JsonResponse({
                "message": "Match scheduled successfully", 
                "court": str(available_court.id)
            })
        else:
            # Add to waiting queue if no courts available
            # You might want to implement a more sophisticated queuing system
            return JsonResponse({"message": "No courts available. Match queued."}, status=400)
    else:
        return JsonResponse({"message": "Other fixture types are not created yet"}, status=500)
        
# create order -> get category, tournament ids, thn 
# get price from category, thn create order

# @csrf_exempt # remove it later
def create_order(req):
    print("create order")
    #  use decorator fr this
    if req.method != "POST":
        return JsonResponse({"message": "Invalid request method"}, status=400)
    
    if not req.body:
        return JsonResponse({"message": "Invalid request body"}, status=400)
    
    data = json.loads(req.body)
    
    category_id = data.get('category_id', None)
    team_name = data.get('team_name', None)
    print(category_id, team_name, 'data')
    if not (category_id and team_name):
        return JsonResponse({"message": "Invalid JSON data, team name or category not found"}, status=400)
    
    category_instance = Category.objects.get(id=category_id)
    Tournament_instance = category_instance.tournament
    
    category_price = category_instance.price
    
    
    currency = 'INR'
    amount = int(category_price * 100)
    
    try:
        razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID,
                                        settings.RAZOR_SECRET_KEY))

        print("razorpay client created", razorpay_client)
        razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                        currency=currency,
                                                        payment_capture='0'))
        
    except Exception as e:
        print(f'error from razorpay side {e}')
        return JsonResponse({"error": f'error from razorpay side {e}'}, status=400)
        
    callback_url = req.build_absolute_uri(reverse('core:checkout')) # add next url too 
    
    try:
        order_instance = Order.objects.create(order_id=razorpay_order['id'], user=req.user, amount=amount)
        order_details = Order_additional_details.objects.create(
            team_name=team_name,
            category=category_instance,
            tournament=Tournament_instance,
            user=req.user,
            order_id_id=order_instance.order_id
        )
    except Exception as e:
        return JsonResponse({"error": f"Error creating order or order details: {e}"}, status=500)
    response = {}
    response['razorpay_order_id'] = razorpay_order['id']
    response['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    response['razorpay_amount'] = amount
    response['currency'] = currency
    response['callback_url'] = callback_url
    
    
    return JsonResponse(response)
    



@host_required
def create_matches_ko_manual(req, category_id):
    import time
    start_time = time.time()
    category_instance = Category.objects.get(id=category_id)
    fixture = category_instance.fixture
    
    if fixture.fixtureType != "KO":
        return JsonResponse({"message": "Only Knockout fixtures are supported"}, status=400)
    
    ko_instance = fixture.content_object
    if not ko_instance.fixing_manual:
        return JsonResponse({"message": "fixture type is automatic, works only for KO-manual"}, status=400)
    
    data = json.loads(req.body)
    print(data)
    
    if len(data["matches"]) < math.ceil(ko_instance.bracket_teams.count() / 2):
        return JsonResponse({"message": "Not enough matches"}, status=400)
    
    no_sets = int(data.get("no_sets"))
    points_win = int(data.get("points_win"))
    
    match_instances = []

    for match_num, match in enumerate(data["matches"], start=1):
        team1 = match.get("team1", None)
        team2 = match.get("team2", None)
        
        # both teams cant be None
        if not (team1 or team2):
            return JsonResponse({"message": "Invalid team id"}, status=400)
        
        # remove team from bracket teams
        if team1:
            team1 = Team.objects.get(id=team1)
            ko_instance.bracket_teams.remove(team1)
        
        if team2:
            team2 = Team.objects.get(id=team2)
            ko_instance.bracket_teams.remove(team2)
        
        match_instance = Match.objects.create(
            category=category_instance,
            team1=team1,
            team2=team2,
            no_sets=no_sets,
            win_points=points_win,
            match_number=match_num,
            stage_number=ko_instance.ko_stage
        )
        match_instances.append(match_instance)
        if not team1:
            match_instance.winner = team2
            ko_instance.winners_bracket.add(team2)
        elif not team2:
            match_instance.winner = team1
            ko_instance.winners_bracket.add(team1)
        else:
            sets = []
            for set_no in range(no_sets):
                sets.append(SetScoreboard.objects.create(set_no=set_no+1, match=match_instance))
                
            ko_instance.bracket_matches.add(match_instance)
            match_instance.sets.set(sets)

        match_instance.save()
        ko_instance.save()


    fixture_manager = Fixture_Json_Manager(ko_instance)
    fixture_json = fixture_manager.update_fixture_json(match_instances, data)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")

    return JsonResponse({"message": "Matches created successfully", "fixture": fixture_json})

@host_required
def schedule_match(req, category_id):
    print("schedule match")
    category_instance = Category.objects.get(id=category_id)
    fixture_instance = category_instance.fixture    
    if not fixture_instance:
        return JsonResponse({"message": "Fixture not created yet"}, status=400)
    
    data = json.loads(req.body)

    if fixture_instance.fixtureType == 'KO':
        ko_instance = fixture_instance.content_object
        bracket_matches =[match.id for match in  ko_instance.bracket_matches.all()]
        
        match_id = int(data.get('match_id'))
        if not match_id in bracket_matches:
            return JsonResponse({"message": "Match not in bracket matches"}, status=400)
        
        # courts, feature add here
        match_instance = Match.objects.get(id=match_id)
        match_instance.current_set = SetScoreboard.objects.get(set_no=1, match=match_instance)
        match_instance.save()
        
        fixture_instance.scheduled_matches.add(match_instance)
        fixture_instance.save()
        ko_instance.bracket_matches.remove(match_instance)
        ko_instance.save()
        
        
    else:
        return JsonResponse({"message": "Other fixture types are not created yet"}, status=500)
        
    return JsonResponse({"message": "Match scheduled successfully"})

@host_required
def score_match(req, match_id):

    data = json.loads(req.body)
    team_id = data.get('team_id')
    inc = data.get('inc', False)
    
    # check if match is scheduled
    match_instance = Match.objects.get(id=match_id)
    category_instance = match_instance.category
    schedule_matches = [match.id for match in category_instance.fixture.scheduled_matches.all()]
    if not match_instance.id in schedule_matches:
        return JsonResponse({"message": "Match not scheduled!"}, status=400)
    
    # check if match is over
    if match_instance.match_state:
        return JsonResponse({"message": "Match already over"}, status=400)
    
    # check if team is valid
    if (match_instance.team1.id == team_id or match_instance.team2.id == team_id):
        
        # get current set
        cur_set = match_instance.current_set
        #     check if set is over
        if cur_set.set_state:
            return JsonResponse({"message": "Set already over"}, status=400)

        # if inc
        if inc:
        #     inc the score
            if team_id == match_instance.team1.id:
                cur_set.team1_score += 1
            else:
                cur_set.team2_score += 1
                
            #if the score above win points
            if cur_set.team1_score >= match_instance.win_points or cur_set.team2_score >= match_instance.win_points:
                
                no_set = match_instance.no_sets
                team1_wins = 0
                team2_wins = 0
                
                cur_set.set_state = True
                if cur_set.team1_score > cur_set.team2_score:
                    cur_set.winner = match_instance.team1
                else:
                    cur_set.winner = match_instance.team2
                cur_set.save()
                
                all_sets = match_instance.sets.all()
                
                for set_data in all_sets:
                    if set_data.set_state:
                        if set_data.winner == match_instance.team1:
                            team1_wins += 1
                        elif set_data.winner == match_instance.team2:
                            team2_wins += 1
                                    
                majority_sets = math.ceil(no_set / 2)

                if team1_wins >= majority_sets or team2_wins >= majority_sets:
                    team_no = 0 if team1_wins >= majority_sets else 1
                    match_instance.winner = match_instance.team1 if team1_wins >= majority_sets else match_instance.team2
                    
                    match_instance.match_state = True
                    match_instance.save()
                    category_instance.fixture.scheduled_matches.remove(match_instance)
                    category_instance.fixture.save()
                    
                    # check if all matches are over
                    ko_instance = category_instance.fixture.content_object
                    # manuplate json
                    Fixture_Json_Manager(ko_instance).update_winner(match_instance.id, team_no, match_instance.winner.name)
                    ko_instance.winners_bracket.add(match_instance.winner)
                    ko_instance.save()
                    
                    print(f"scheduled matches: {category_instance.fixture.scheduled_matches.all()}")
                    print(f"bracket matches: {ko_instance.bracket_matches.all()}")
                    
                    if not category_instance.fixture.scheduled_matches.all() and not ko_instance.bracket_matches.all():

                        json_data = json.loads(ko_instance.json)

                        json_data["rounds"][ko_instance.ko_stage - match_instance.stage_number]['matches'][match_instance.match_number - 1]["winner"] = 0 if team1_wins >= majority_sets else 1
                        ko_instance.json = json.dumps(json_data)
                        ko_instance.save()
                        print("json updated")
                        if winners:=ko_instance.winners_bracket.all():
                            if ko_instance.ko_stage == 1:
                                print("category over /dawda")
                                len_winners = len(winners)
                                if not len_winners == 1:
                                    return JsonResponse({"message": "Uh oh, something went wrong"})
                                category_instance.winner = winners[0]
                                ko_instance.bracket_teams.clear()
                                category_instance.save()
                                return JsonResponse({"message": "Category over"})
                            
                            
                            ko_instance.bracket_teams.clear()  # ughh should this be here?
                            ko_instance.bracket_teams.set(winners)
                            # schedule matches for next stage automatically
                            all_matches = ko_instance.all_matches.filter(stage_number=ko_instance.ko_stage).order_by('match_number')
                            
                            for i in range(0, len(all_matches), 2):
                                match_instance = Match.objects.create(
                                    category=category_instance,
                                    team1=all_matches[i].winner,
                                    team2=all_matches[i+1].winner,
                                    no_sets=match_instance.no_sets,
                                    win_points=match_instance.win_points,
                                    match_number=i+1,  # Add match number here
                                    stage_number=ko_instance.ko_stage - 1
                                )
                                sets = []
                                for set_no in range(match_instance.no_sets):
                                    sets.append(SetScoreboard.objects.create(set_no=set_no+1, match=match_instance ))
                                match_instance.sets.set(sets) 
                                ko_instance.all_matches.add(match_instance)
                                ko_instance.bracket_matches.add(match_instance)
                                
                            # Update the existing JSON with new matches
                            new_matches = []
                            for match in ko_instance.bracket_matches.filter(stage_number=ko_instance.ko_stage - 1).order_by('match_number'):
                                new_match = {
                                    "id": match.id,
                                    "teams": [match.team1.name, match.team2.name],
                                    "winner": None
                                }
                                new_matches.append(new_match)
                            
                            json_data = json.loads(ko_instance.json)
                            if json_data is None:
                                ko_instance.json = {"rounds": []}
                            
                            # Find the index of the round we need to update
                            round_index = len(json_data["rounds"]) - (ko_instance.ko_stage - 1)
                            
                            # Update the existing round or append a new one if it doesn't exist
                            if round_index < len(json_data["rounds"]):
                                json_data["rounds"][round_index]["matches"] = new_matches
                            else:
                                json_data["rounds"].append({"matches": new_matches})
                                
                            ko_instance.json = json.dumps(json_data)
                            ko_instance.winners_bracket.clear()
                            ko_instance.ko_stage -= 1
                            ko_instance.save()
                            category_instance.fixture.save()
                            
                            
                            return JsonResponse({"message": "THis stage is over, create matches for next stage"})
                        print("something went wrong")
                        return JsonResponse({"message": "Match over"})
                 
                else:
                    next_set = match_instance.set_match.get(set_no=cur_set.set_no + 1)
                    match_instance.current_set = next_set
                    match_instance.save()
                return JsonResponse({"message": "Set over"})
    

            else:
                cur_set.save()
                return JsonResponse({"message": "Score updated successfully"})
        else:
            if team_id == match_instance.team1.id:
                cur_set.team1_score -= 1
            elif team_id == match_instance.team2.id:
                cur_set.team2_score -= 1
            cur_set.save()
            return JsonResponse({"message": "Score updated successfully"})
    else:
        return JsonResponse({"message": "Invalid team id"}, status=400)

# @host_required
# def score_match(req, match_id):
#     # Existing scoring logic...
    
#     # After match completion
#     if match_instance.match_state:
#         # Find and release the court
#         court = Court.objects.filter(current_match=match_instance).first()
#         if court:
#             court.is_available = True
#             court.current_match = None
#             court.save()
        
#         # Check and schedule next match from queue if exists
#         next_queued_match = fixture_instance.scheduled_matches.filter(match_state=False).first()
#         if next_queued_match and Court.objects.filter(is_available=True).exists():
#             # Implement logic to schedule this match
#             schedule_match_for_court(next_queued_match)
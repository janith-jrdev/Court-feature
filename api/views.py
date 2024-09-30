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

@valid_json_data
@host_required
def off_registration(req, category_id):
    category_instance = get_object_or_404(Category, id=category_id)
    data = json.loads(req.body)
    team_name = data.get('team_name')
    
    if not team_name:
        return JsonResponse({"message": "Team name cannot be empty"}, status=400)
    
    Team.objects.create(
        name=team_name,
        category=category_instance
    )
    
    return JsonResponse({"message": "Registration successfully"})


@host_required
def close_categoryReg(req, category_id):
    category_instance = Category.objects.get(id=category_id)
    category_instance.registration_status = False
    category_instance.save()
    Teams=category_instance.teams.all()
    
    if Teams and len(Teams) < 2:
        category_instance.winner = Teams[0]
        category_instance.save()
        return JsonResponse({"message": "Category over"})
        
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

@valid_json_data
@host_required
# look in to it alone
def schedule_match(req, category_id):
    category_instance = Category.objects.get(id=category_id)
    data = json.loads(req.body)
    fixture_instance = category_instance.fixture
    
    if not fixture_instance:
        return JsonResponse({"message": "Fixture not created yet"}, status=400)
    
    if fixture_instance.fixtureType == 'KO':
        ko_instance = fixture_instance.content_object
        bracket_matches =[match.id for match in  ko_instance.bracket_matches.all()]
        
        match_id = int(data.get('match'))
        if not match_id in bracket_matches:
            return JsonResponse({"message": "Match not in bracket matches"}, status=400)
        
        noSets = int(data.get('no_sets'))
        match_instance = Match.objects.get(id=match_id)
        match_instance.no_sets = noSets
        match_instance.win_points = int(data.get("set_winning_points"))
        match_instance.save()
        
        # create sets and assign em
        for i in range(noSets):
            set_instance = SetScoreboard.objects.create(set_no=i+1, match=match_instance)
            match_instance.sets.add(set_instance)
        
        match_instance.current_set = SetScoreboard.objects.get(set_no=1, match=match_instance)
        match_instance.save()
        
        fixture_instance.scheduled_matches.add(match_instance)
        fixture_instance.save()
        ko_instance.bracket_matches.remove(match_instance)
        ko_instance.save()
        return JsonResponse({"message": "Match scheduled successfully"})
    
    return JsonResponse({"message": "Other fixture types are not created yet"}, status=500)
        
# create order -> get category, tournament ids, thn 
# get price from category, thn create order

def create_order(req):
    if req.method != "POST":
        return JsonResponse({"message": "Invalid request method"}, status=400)
    
    data = json.loads(req.body)
    if not data:
        return JsonResponse({"message": "Invalid JSON data"}, status=400)
    
    category_id = data.get('category_id')
    # tournament_id = data.get('tournament_id')
    team_name = data.get('team_name')
    
    category_instance = Category.objects.get(id=category_id)
    Tournament_instance = category_instance.tournament
    
    category_price = category_instance.price
    
    
    currency = 'INR'
    amount = category_price * 100
    
    try:
        razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID,
                                        settings.RAZOR_SECRET_KEY))
        
        razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                        currency=currency,
                                                        payment_capture='0'))
        
    except Exception as e:
        print(f'error from razorpay side {e}')
        return JsonResponse({"error": f'error from razorpay side {e}'}, status=400)
        
    callback_url = reverse('core:checkout') # add next url too 
    
    order_details = Order_addtional_details.objects.create(team_name=team_name, category=category_instance, tournament=Tournament_instance, user=req.user)
    order_instance = Order.objects.create(order_id=razorpay_order['id'], user=req.user, amount=amount, tournament=Tournament_instance, category=category_instance, order_details=order_details)

    response = {}
    response['razorpay_order_id'] = razorpay_order['id']
    response['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    response['razorpay_amount'] = amount
    response['currency'] = currency
    response['callback_url'] = callback_url
    
    
    print(order_instance)
    return JsonResponse(response)    
    




@host_required
def create_matches_ko_manual(req, category_id):
    
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
    
    for match in data["matches"]:
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
        
        # if want to add match no add here
        match_instance = Match.objects.create(
            category=category_instance,
            team1=team1,
            team2=team2,
            no_sets=no_sets,
            win_points=points_win,
        )
        
        if not team1:
            match_instance.winner = team2
            ko_instance.winners_bracket.add(team2)
        elif not team2:
            match_instance.winner = team1
            ko_instance.winners_bracket.add(team1)
        else:
            sets = []
            for set_no in range(no_sets):
                sets.append(SetScoreboard.objects.create(set_no=set_no+1, match=match_instance ))
                
            ko_instance.bracket_matches.add(match_instance)
            match_instance.sets.set(sets)

        match_instance.save()
        ko_instance.save()
    
    return JsonResponse({"message": "Matches created successfully"})

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
    # CHECK DEC WORKS IN ADMIN PANEL
    # get match_id [args]

    # get team_id [req data]
    # get inc/dec [req data]
    data = json.loads(req.body)
    team_id = data.get('team_id')
    inc = data.get('inc', False)
    
    print("hereee",data)
    
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
            print("win points")
            print(cur_set.team1_score, cur_set.team2_score, match_instance.win_points)
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

                print("wins")
                print(team1_wins, team2_wins, majority_sets, team1_wins >= majority_sets or team2_wins >= majority_sets)
                
                if team1_wins >= majority_sets or team2_wins >= majority_sets:
                    match_instance.winner = match_instance.team1 if team1_wins >= majority_sets else match_instance.team2
                    
                    match_instance.match_state = True
                    match_instance.save()
                    category_instance.fixture.scheduled_matches.remove(match_instance)
                    category_instance.fixture.save()
                    
                    # check if all matches are over
                    ko_instance = category_instance.fixture.content_object
                    ko_instance.winners_bracket.add(match_instance.winner)
                    ko_instance.save()
                    
                    print(f"scheduled matches: {category_instance.fixture.scheduled_matches.all()}")
                    print(f"bracket matches: {ko_instance.bracket_matches.all()}")
                    
                    if not category_instance.fixture.scheduled_matches.all() and not ko_instance.bracket_matches.all():
                        
                        if winners:=ko_instance.winners_bracket.all():
                            if ko_instance.ko_stage == 1:
                                len_winners = len(winners)
                                if not len_winners == 1:
                                    return JsonResponse({"message": "Uh oh, something went wrong"})
                                category_instance.winner = winners[0]
                                category_instance.save()
                                return JsonResponse({"message": "Category over"})
                            
                            
                            ko_instance.bracket_teams.clear()  # ughh should this be here?
                            ko_instance.bracket_teams.set(winners)
                            # schedule matches for next stage automatically
                            
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


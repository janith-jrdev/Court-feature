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
        
    return JsonResponse({"message": "Registration closed successfully"})

@valid_json_data
@host_required
def fixturetype_form(req, category_id):
    category_instance = Category.objects.get(id=category_id)

    data = json.loads(req.body)
    fixture_type = data.get('fixture_type')
    
    if not fixture_type:
        return JsonResponse({"message": "Fixture type cannot be empty"}, status=400)
    
    if fixture_type not in ['KO']: #, 'RR', 'RR_KO' add these later
        return JsonResponse({"message": "Invalid fixture type"}, status=400)
    
    fixture_instance = Fixture.objects.create(fixtureType=fixture_type, category=category_instance)
    
    if fixture_type == 'KO':
        fixture_mode = data.get('fixture_mode')
        ko_instance = Knockout.objects.create(category=category_instance, fixing_manual=True)
        ko_instance.bracket_teams.set(category_instance.teams.all())
        
        no_teams = category_instance.teams.count()
        nearest_power_of_2 = 2 ** math.ceil(math.log2(no_teams))
        byesNeeded = nearest_power_of_2 - no_teams
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
def increment_set_score(req, match_id):
    # args: match_id, team_id
    match_instance = Match.objects.get(id=match_id)
    
    if match_instance.match_state:
        return JsonResponse({"message": "Match already over"}, status=400)
    
    data = json.loads(req.body)
    team_id = int(data.get('team_id'))
    # category_instance
    
    category_instance = match_instance.category
    schedule_matches = [match.id for match in category_instance.fixture.scheduled_matches.all()]
    # and check if match is scheduled
    
    if not match_instance.id in schedule_matches:
        return JsonResponse({"message": "Match not scheduled!"}, status=400)
    
    team_1 = match_instance.team1.id == team_id
    team_2 = match_instance.team2.id == team_id

    if not ( team_1 or team_2):
        return JsonResponse({"message": "Invalid team id"}, status=400)
    
    match_current_set = match_instance.current_set
    if not match_current_set:
        match_current_set = match_instance.sets.get(set_no=1)
        
    if match_current_set.set_state and match_current_set.set_no == match_instance.no_sets:
        return JsonResponse({"message": "match already over"}, status=400)
    
    # if win is 15, team1,2 has 14,14 then the win point will be like increase by 2.
    
    if team_1:
        match_current_set.team1_score += 1
    elif team_2:
        match_current_set.team2_score += 1
    else:
        return JsonResponse({"message": "Invalid team id"}, status=400)
    
    match_current_set.save()
    return JsonResponse({"message": "Score updated successfully"})


@host_required
def complete_set(req, match_id):
    match_instance = Match.objects.get(id=match_id)
    
    if match_instance.match_state:
        return JsonResponse({"message": "Match already over"}, status=400)
    
    # category_instance
    category_instance = match_instance.category
    schedule_matches = [match.id for match in category_instance.fixture.scheduled_matches.all()]
    # and check if match is scheduled
    if not match_instance.id in schedule_matches:
        return JsonResponse({"message": "Match not scheduled!"}, status=400)
    
    match_current_set = match_instance.current_set
    if match_current_set.set_state:
        return JsonResponse({"message": "Set already over"}, status=400)
    
    match_current_set.set_state = True
    
    if match_current_set.team1_score > match_current_set.team2_score:
        match_current_set.winner = match_instance.team1
    elif match_current_set.team1_score < match_current_set.team2_score:
        match_current_set.winner = match_instance.team2
    else:
        return JsonResponse({"message": "Set cant be tied"}, status=400)
    
    match_current_set.save()
    team_wins = {
        'team1': sum(1 for set_data in match_instance.sets.all() if set_data.set_state and set_data.winner == match_instance.team1),
        'team2': sum(1 for set_data in match_instance.sets.all() if set_data.set_state and set_data.winner == match_instance.team2)
    }
    total_sets = match_instance.no_sets
    
    if match_current_set.set_no == total_sets:#this will be edited
        print("Match over")

        if team_wins['team1'] > team_wins['team2']:
            match_instance.winner = match_instance.team1
        elif team_wins['team1'] < team_wins['team2']:
            match_instance.winner = match_instance.team2
        else:
            return JsonResponse({"message": "Match cant be tied"}, status=400)
        match_instance.match_state = True
        match_instance.save()
        
        # adding to winner bracket
        ko_instance = category_instance.fixture.content_object
        ko_instance.winners_bracket.add(match_instance.winner)
        # then checking if all matches are over
        if not ko_instance.bracket_matches.all():
            if winners:=ko_instance.winners_bracket.all():
                print(ko_instance.ko_stage, " wdwadad")
                if ko_instance.ko_stage == 0:
                    # some error here

                    len_winners = len(winners)
                    if not len_winners == 1:
                        return JsonResponse({"message": "Uh oh, something went wrong"})
                    category_instance.winners.add(winners[0])
                    category_instance.save()
                    return JsonResponse({"message": "Category over"})
                
                ko_instance.bracket_teams.set(winners)
                category_instance.fixture.content_object.winners_bracket.clear()
                category_instance.fixture.scheduled_matches.clear()
                ko_instance.ko_stage -= 1
                ko_instance.save()
                category_instance.fixture.save()
                
                # call a util fn to create matches for next stage
            return JsonResponse({"message": "THis stage is over, create matches for next stage"})
        
        # new winner bracket -> bracket_teams
        # or better create it automatically
        # also its better to store all the matches in seprate field in ko model
        
        return JsonResponse({"message": "Match over"})
    
    else:
        # if any team wins the majority of the sets then the match is over
        majority = math.ceil(total_sets / 2)
        if team_wins['team1'] >= majority:
            # team 1 wins
            return JsonResponse({"message": "Match over by majority"})
        elif team_wins['team2'] >= majority:
            # team 2 wins
            return JsonResponse({"message": "Match over by majority"})
        
    next_set = match_instance.sets.get(set_no=match_current_set.set_no + 1)
    match_instance.current_set = next_set
    match_instance.save()
    return JsonResponse({"message": "Set over"})


# def complete_match(req, match_id):
    match_instance = Match.objects.get(id=match_id)
    
    if match_instance.match_state:
        return JsonResponse({"message": "Match already over"}, status=400)
    
    if req.method != "POST":
        return JsonResponse({"message": "Invalid request method"}, status=400)
    
    
    all_sets = match_instance.sets.all()
    
    team_wins = {'team1': 0, 'team2': 0}
    
    for set_data in all_sets:
        if not set_data.set_state:
            return JsonResponse({"message": "All sets not completed"}, status=400)
        
        if set_data.winner == match_instance.team1:
            team_wins['team1'] += 1
        else:
            team_wins['team2'] += 1
    
    if team_wins['team1'] > team_wins['team2']:
        match_instance.winner = match_instance.team1
    elif team_wins['team1'] < team_wins['team2']:
        match_instance.winner = match_instance.team2
    else:
        return JsonResponse({"message": "Match cant be tied"}, status=400)
    
    match_instance.match_state = True
    match_instance.save()
    
    category_instance = match_instance.category
    if not category_instance.fixture.scheduled_matches.all() :
        if category_instance.fixture.fixtureType == 'KO':
            if category_instance.fixture.content_object.bracket_matches.all():
                return JsonResponse({"message": "All matches over"})
            winner_bracket = category_instance.fixture.content_object.bracket_winners.all()
            if winner_bracket:
                category_instance.fixture.content_object.bracket_teams.set(winner_bracket)
                
            
        # return JsonResponse({"message": "All matches over"})
    
    return JsonResponse({"message": "Match over"})

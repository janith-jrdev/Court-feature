from django.contrib import messages
from datetime import datetime
from .models import *

def clean_querydict(querydict):
    return {k: v[-1] for k, v in querydict.lists()}

class addtionalUserData_validator:
    def __init__(self, data, user):
        """_summary_
        validate additional user data
        
        Args:
            data (_type_): req.POST
                DOB: date_of_birth 
                is_org: is_organiser
                gender: gender
                
        Process:
            clean the data
                -dob
                    - str to date
            validates data
                -dob
                    -not in future
                -is_org
                    -boolean
                -gender
                    -valid choice
            saves the data
            
        
        Returns:
            _type_: _description_
            if valid:
                saves the data
                returns True
            else:
                returns False
        
        """
        self.user = user
        self.data = clean_querydict(data)
        self.errors = {}
        self.clean_validate_save()
        
    def validate_dob(self, dob):
        print(f'validate_dob: {dob}')
        try:
            dob = datetime.strptime(dob, '%Y-%m-%d')
        except ValueError:
            self.errors['date_of_birth'] = "Invalid date format"
            return False
        
        if dob > datetime.now():
            self.errors['date_of_birth'] = "Date of birth cannot be in the future"
            return False
        
        return True
    
    def validate_gender(self, gender):
        print(f'validate {gender}')
        if gender not in ['M', 'F', 'O', 'U']:
            self.errors['gender'] = "invalid gender data"
            return False
        return True
    
    def save(self):
        data = self.data
        is_org = False
        if data.get('is_organiser', None):
            is_org = True

        try:
            add_userdata = AdditionalUserData.objects.create(
                date_of_birth=data['dob'],
                is_organiser= is_org,
                gender=data['gender'],
            )
            User.objects.filter(username=self.user).update(additional_data=add_userdata)
            print(f'add_userdata: {add_userdata}')
        except Exception as e:
            self.errors['save'] = str(e)
            print(f'error: {e}')
            
        if self.errors:
            for key, value in self.errors.items():
                messages.error(self.request, f"{key}: {value}")
            return False
        return True
    
    def clean_validate_save(self):
        clean_and_validate_fns = [fn for fn in dir(self) if fn.startswith('validate_')]        
        for fn in clean_and_validate_fns:
            fn_call = getattr(self, fn)
            _, key = fn.split('_', 1)
            fn_data = self.data.get(key)
            if fn_data and not fn_call(fn_data):
                return False
        
        return self.save()
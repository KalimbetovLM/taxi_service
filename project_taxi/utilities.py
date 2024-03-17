import random
import re
from rest_framework.exceptions import ValidationError

def set_id():
    letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    digit1 = random.randint(100,1000)
    digit2 = random.randint(10,100)
    digit3 = random.randint(10,100)
    letter1 = random.choice(letters)
    letter2 = random.choice(letters)
    id = letter1 + letter2 + str(digit1) + str(digit2) + str(digit3)
    return id

email_regex = re.compile(r"\S+@\S+\.\S+")
phone_regex = "^\\+?[1-9][0-9]{7,14}$"
username_regex = re.compile(r"^[a-zA-Z0-9_.-]+$")

def user_type_regex(userinput):
    if re.fullmatch(email_regex,userinput):
        userinput = "email"
    elif re.fullmatch(phone_regex,userinput):
        userinput = "phone"
    elif re.fullmatch(username_regex,userinput):
        userinput = "username"
    else:
        raise ValidationError({
            "success": False,
            "message": "Please, enter a correct credentials"
        })
    return userinput
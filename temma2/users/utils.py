# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
import json
from decouple import config
import requests
from requests.auth import HTTPBasicAuth
# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
ACCOUNT_SID = config("ACCOUNT_SID")
AUTH_TOKEN = config("AUTH_TOKEN")
FROM = config("FROM")
CONTENT_SID=config("CONTENT_SID")

url = f"https://api.twilio.com/2010-04-01/Accounts/{ACCOUNT_SID}/Messages.json"

def twilio_whatsapp(receiver):

    data = {
    "To": f"whatsapp:{receiver}",  # recipient
    "From": f"whatsapp:{FROM}",  # your approved Twilio WhatsApp sender
    "ContentSid":f"{CONTENT_SID}",  # your template SID
    }

    response = requests.post(url, data=data, auth=HTTPBasicAuth(ACCOUNT_SID, AUTH_TOKEN))
    response.raise_for_status()
    return response.text
    # print(response.status_code)


# print(response.text)











    #  message = client.messages.create(
    #      from_=f"whatsapp:{config('FROM')}",
    #      to=f"whatsapp:{receiver}",
    #      content_sid=config("CONTENT_SID"),
    #  )

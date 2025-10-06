# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
import json
from decouple import config
# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = config("ACCOUNT_SID")
auth_token = config("AUTH_TOKEN")
client = Client(account_sid, auth_token)

def twilio_whatsapp(receiver):
     message = client.messages.create(
         from_=f"whatsapp:{config('FROM')}",
         to=f"whatsapp:{receiver}",
         content_sid=config("CONTENT_SID"),
     )

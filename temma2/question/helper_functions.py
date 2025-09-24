from django.core.mail import EmailMessage
from temma.settings import EMAIL_HOST_USER
import jwt
from datetime import datetime, timedelta
from decouple import config


def email_sender(email, title, body):

    message = EmailMessage(
        title, body, EMAIL_HOST_USER, [email]) #"hiraanwar1998@gmail.com", "EvaSofia_@live.nl",
    message.send()
    return "DONE!"

def email_sender_for_admin(title, body, emails=[]):

    message = EmailMessage(
        title, body, EMAIL_HOST_USER, emails) #"hiraanwar1998@gmail.com", "EvaSofia_@live.nl",
    message.send()
    return "DONE!"

# to should be a list
def send_email_with_HTML(subject, html_content, to=[]):
    msg = EmailMessage(subject, html_content, EMAIL_HOST_USER, to)
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()

from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string
def email_by_template(subject, ctx, template_path, to=[]):
    # Load the HTML template
    html_template = get_template(template_path)
    
    # Populate the template with data from the context dictionary
    html_content = html_template.render(ctx)
    
    # Create the email message
    email = EmailMultiAlternatives(
        subject=subject,
        body=strip_tags(html_content),  # Use the plain text version as fallback
        from_email=EMAIL_HOST_USER,
        to=to
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    # Attach the HTML content
def email_by_template_svg(subject, ctx, template_path, to=[]):
    svg_content = render_to_string(template_path, ctx)

    # Create a plain text version of the email (optional)
    text_content = strip_tags(svg_content)
    from_email=EMAIL_HOST_USER
    # Create the email message object
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)

    # Attach the SVG content as HTML
    msg.attach_alternative(svg_content, "text/html")

    # Send the email
    msg.send()
    print("MESSSAGE SENT")

# Your secret key to sign the token
SECRET_KEY = config('SECRET_KEY_DECODE')


from datetime import datetime, timedelta, timezone
import jwt

def generate_token(user_id, student_id, user_type):
    # Set the expiration time to 24 hours from now using timezone-aware datetime
    expiration_time = datetime.now(timezone.utc) + timedelta(hours=24)
    
    # Convert datetime to Unix timestamp
    exp_timestamp = int(expiration_time.timestamp())
    
    # Payload containing the user ID and expiration time
    payload = {
        'user_id': user_id,
        'student_id': student_id,
        'exp': exp_timestamp,
        'user_type': user_type
    }
    
    # Generate the JWT token
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def decode_token(token):
    # try:
        # Decode the token and return the payload
    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    return payload


def generate_token_passcode(pass_code, school_name):
    # Set the expiration time to 24 hours from now
    # expiration_time = datetime.utcnow() + timedelta(hours=24)
    
    # Payload containing the user ID and expiration time
    payload = {
        'pass_code': pass_code,
        "school_name": school_name,
    }
    
    # Generate the JWT token
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

# def decode_token(token):
#     # try:
#         # Decode the token and return the payload
#     payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
#     return payload


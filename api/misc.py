from envelope import Envelope
from pydantic import EmailStr


###############################################################################
# Communications with users
def send_email_api_key(email: EmailStr, api_key: str, days_valid: int):
    """ function to send the api key to a user. Shamelessly stolen from the official docs """

    subject = "API-key reset"
    hostname = baseurl
    smtp_from = config['MAIL_FROM']

    body = """
Dear %s,

you (or someone) requested a new api-key for the service at %s.
Here is your new API key:

%s


This key is valid for %s days.

You can find instructions on how to use it at %s.
In case you did not request an API key, please ignore this email.

Kind regards,
the automatic API buttler
""" % (email, hostname, api_key, days_valid, hostname)

    Envelope()\
        .message(body)\
        .subject(subject)\
        .to(email)\
        .sender(smtp_from)\
        .smtp("localhost")\
        .send()


from mailjet_rest import Client
from os import environ
import asyncio

async def send_mailjet_email(email: str, name: str, code:str):

    api_key = environ.get("MAILJET_API_KEY")
    api_secret = environ.get("MAILJET_API_SECRET")

    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
    'Messages': [
        {
        "From": {
            "Email": "cyberucr@gmail.com",
            "Name": "Email Verification"
        },
        "To": [
            {
            "Email": email,
            "Name": name
            }
        ],
        "Subject": "UCR Email Verification",
        "TextPart": f"Here is your code: {code}",
        "HTMLPart": f"Go back to where you entered the verification command and enter the command /code. Then paste the following code: <b>{code}</b>.",
        "CustomID": "UCRStudentVerificationBot"
        }
    ]
    }
    result = mailjet.send.create(data=data)
    return int(result.status_code)==200
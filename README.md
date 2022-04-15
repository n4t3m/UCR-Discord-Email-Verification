# UC Riverside Discord Email Verification Bot

hello hello, welcome to another repo with my ~~wonderful~~ code :)

This is a discord bot (using the pycord libary) that verifies people who have UCR email addresses by giving them a configurable role. The bot utilizes slash commands to do this.

## how it workz

Here is how it works from the user's POV: It's simple (I hope):
- Go to a channel where you have permissions to type
- Enter ``/verify <ucr email address>``
- You will be sent an email from ``cyberucr@gmailcom`` containing a 6 digit code. Open the email and grab the code.
- Head back to the discord channel where you typed ``/verify``. Enter ``/code <code>``. You will be given a role which will demonstrate that you have access to a UCR email address.

How it works from a server owner's POV:
- Invite the bot using this link: ''<link to be added it exists but im still testing>''
- Configure the role that will be added to users who verify using /setverifiedrole <role>. YOU MUST HAVE ADMINISTRATOR PERMS TO DO THIS.
- People who verify will be given the specified role. If no specific role has been selected, the bot will create a role called ``UCR Verified`` and assign it to verified people.

Here is a quick technical description of how verification works:
- user input is an email, parse the input to make sure its actually an email. 
- check email to see if its ``@ucr.edu``. 
- If it is, check to see if user has already verified on another server with this bot (theres a mongodb database). If they have already verified with the bot at one point in time, they will be auto verified and get the role instantly. If not, they will be sent an email through the mailjet email API.
- They get a code which can be used to verify with. This code is stored in MongoDB and is associated with the userid on the account.

here are some screenshots:
- i am lazy

## Secrets

Here is what the .env file should look like =))

```
#Discord Config
VERIFICATION_BOT_TOKEN=
#Mailjet Config
MAILJET_API_KEY =
MAILJET_API_SECRET = 
#MongoDB Atlas
MONGO_CONNECTION_STRING=
```
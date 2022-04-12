import discord
import random
import re
from random import randrange
import asyncio
import pymongo
from mailjet_email import send_mailjet_email
from dotenv import load_dotenv, find_dotenv
from os import environ

#pip install -U git+https://github.com/Pycord-Development/pycord

#Environment Variables
load_dotenv(find_dotenv())
TOKEN = environ.get("VERIFICATION_BOT_TOKEN")
CONNECTION_STRING = environ.get("MONGO_CONNECTION_STRING")

#Initialize MongoDB
connection = pymongo.MongoClient(CONNECTION_STRING)
db = connection.get_database('userdata')
records = db.userdata_records
server_records = db.serverdata

#bot = commands.Bot(command_prefix='!', description=description, intents=intents)
#bot.verification_codes = {}
bot = discord.Bot()

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print('------')

@bot.event
async def on_guild_remove(guild):
    server_records.delete_one({'guildid': guild.id})


async def removeRecord(did: int):
    await asyncio.sleep(300)
    res = records.find_one({'did': did})
    if not res:
        print('Something bad happened, ruh roh')
        return
    if res['state']=="unverified":
        res = records.delete_one({'did': did})

async def addUserToDB(discordid: int, code: str, email: str):
    user = {
        'did': discordid,
        'code': code,
        'email': email.lower(),
        'state': 'unverified'
    }
    res = records.insert_one(user)
    if res:
        return True
    else:
        return False

async def addRoleToVerifiedUser(ctx):
    res = server_records.find_one({'guildid': ctx.guild.id})
    #if there is no record, create one
    if not res:
        #no record found:
        try:
            newrole = await ctx.guild.create_role(name="UCR Verified")
        except:
            await ctx.respond('Bot Does not have permissions to create role. Assign a role using /setVerifiedRole or give the bot permissions to create a role.')
            return
        await addServerToDB(ctx.guild.id, newrole.id)
        s = 1+1
    #at this point there will be a record for the server, so we add it to the user
    res = server_records.find_one({'guildid': ctx.guild.id})
    #now we need to make sure the role still exits
    rid = res['roleid']
    r = ctx.guild.get_role(rid)
    if not r:
        #role does not exist, we must create a new role
        try:
            newrole = await ctx.guild.create_role(name="UCR Verified")
        except:
            await ctx.respond('Bot Does not have permissions to create role. Assign a role using /setVerifiedRole or give the bot permissions to create a role.')
            return 
        role_updates = {'roleid': newrole.id}
        res = server_records.update_one({'guildid': ctx.guild.id}, {'$set': role_updates})
    #now the role exists for sure, poggers
    res = server_records.find_one({'guildid': ctx.guild.id})
    rid = res['roleid']
    r = ctx.guild.get_role(rid)
    await ctx.author.add_roles(r, reason="User Verified")
    return

async def addServerToDB(guildid: int, roleid: int):
    server = {
        'guildid': guildid,
        'roleid': roleid,
    }
    res = server_records.find_one({'guildid': guildid})
    if not res:
        server_records.insert_one(server)
    return

@bot.slash_command(
    name="add",
    description="Test command to ensure the bot is working. Adds two integers.",
    guild_ids=[929180791760642059]
)
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.respond(left + right, ephemeral=True)
    return


@bot.slash_command(
    name="setverifiedrole",
    description="[ADMIN ONLY] Set the role given to verified users."
)
async def setVerifiedRole(ctx,
                            newrole: discord.Option(discord.Role, "[ADMIN ONLY] The role given to users who verify their email addresses.")
                        ):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond('Only administrators can use this command', ephemeral=True)
        return
    if newrole.is_default():
        await ctx.respond('You must use a custom role, not @everyone or @here.', ephemeral=True)
        return
    res = server_records.find_one({'guildid': ctx.guild.id})
    if not res:
        await addServerToDB(ctx.guild.id, newrole.id)
    else:
        role_updates = {'roleid': newrole.id}
        res = server_records.update_one({'guildid': ctx.guild.id}, {'$set': role_updates})
    await ctx.respond(f'Role has been updated to {newrole.name}', ephemeral=True)
    return


@bot.slash_command(
    name="getverifiedrole",
    description="Get the name of the role given to verified users."
)
async def getVerifiedRole(ctx):
    res = server_records.find_one({'guildid': ctx.guild.id})
    if not res:
        await ctx.respond("There is currently no role configured. Use /setVerifiedRole to set a role given to verified users. If no role is set, a role will automatically be created upon the next verification.",ephemeral=True)
        return
    rid = res['roleid']
    r = ctx.guild.get_role(rid)
    if not r:
        await ctx.respond("The role previously configured appears to have been deleted. Use /setVerifiedRole to set a new role given to verified users, or a role will be automatically created upon the next verification.",ephemeral=True)
        return
    await ctx.respond(f'The current role given to verified users is {r.name}', ephemeral=True)
    return


@bot.slash_command(
    name="verify",
    description="Verify your account by providing your email address."
)
async def verify(ctx, 
                    email: discord.Option(str, "UCR email address. Example: jlin013@ucr.edu")
                ):
    #if not isinstance(ctx.channel, discord.channel.DMChannel):
        #return
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if not re.search(regex, email):
        await ctx.respond("Invalid Email Address.", ephemeral=True)
        return
    if not email.lower().split("@")[1]=="ucr.edu":
        await ctx.respond("Only @ucr.edu email addresses are able to verify.", ephemeral=True)
        return
    if "email.ucr.edu" in email.lower():
        await ctx.respond("Please use your netid@ucr.edu", ephemeral=True)

    code = f"{randrange(10)}{randrange(10)}{randrange(10)}{randrange(10)}{randrange(10)}{randrange(10)}"

    #check if in db already
    res = records.find_one({'did': ctx.author.id})
    if not res:
        #not in db, create user
        res = records.find_one({'email': email.lower()})
        if res:
            await ctx.respond(f"{email} is already tied to another Discord account.", ephemeral=True)
            return
        res = await addUserToDB(ctx.author.id, code, email.lower())
    else:
        #in database
        if res['state']=="verified":
            await ctx.respond(f"Thank you for verifying {ctx.author.mention}!", ephemeral=True)
            #proceed to role assignment
            await addRoleToVerifiedUser(ctx)
            return
        else:
            #in verification process
            await ctx.respond(f'Check email {res["email"]} for code. After 5 minutes your code will expire and you can request a new one. **If you do not see a verification email, check your spam.** After 5 minutes, you can request a new verification code.', ephemeral=True)
        return

    success = await send_mailjet_email(email, ctx.author.name, str(code))

    if success:
        await ctx.respond("Verification Email Sent.", ephemeral=True)
    else:
        await ctx.respond("Email failed to send, lol oops. Please contact bot administrator(nate).", ephemeral=True)
        return
    
    await removeRecord(ctx.author.id)

@bot.slash_command(
    name="code",
    description="Enter the verification code sent to you after using the verify command."
)
async def code(ctx, 
                code: discord.Option(int, "Verification code sent to your email.")
            ):
    #if not isinstance(ctx.channel, discord.channel.DMChannel):
        #return
    
    res = records.find_one({'did': ctx.author.id})
    if not res:
        await ctx.respond("You must request a verification code.", ephemeral=True)
        return
    
    if res['state']=="verified":
        await ctx.respond('Account has already been verified.', ephemeral=True)
        await addRoleToVerifiedUser(ctx)
    else:
        if int(code) == int(res['code']):
            #update status to verified
            
            user_updates = {'state': 'verified'}
            records.update_one({'did': ctx.author.id}, {'$set': user_updates})
            await ctx.respond(f"Thank you for verifying {ctx.author.mention}!", ephemeral=True)
            await addRoleToVerifiedUser(ctx)
            return
        else:
            await ctx.respond("The code you have entered is incorrect.", ephemeral=True)

bot.run(TOKEN)
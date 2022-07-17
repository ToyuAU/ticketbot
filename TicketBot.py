import discord
from discord.ext import commands, tasks
from discord.utils import get
import json

#Create Exit Function
def exit_menu():
    input("Press Enter to exit...")
    exit()

#Load Data File
data = json.loads(open('data.json').read())

#Check Data File Errors / Info
if data['token'] == "":
    print("Please enter your token in data.json")
    exit_menu()

if data['prefix'] == "":
    print("Please enter your prefix in data.json")
    exit_menu()

if data['ticket-message-id'] == 0:
    print(f"Ticket Message ID Missing. Please Run {data['prefix']}newticket #channel")

if data['ticket-creation-category-id'] == 0:
    print(f"Ticket Creation Category ID Missing. Tickets will be created at bottom of the server")

#Create Bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=data["prefix"], intents=intents)

@bot.event
async def on_ready():
    print(" ")
    print("----------------------------------------------------")
    print("Bot is ready!")
    print(f"Logged in as {bot.user.name}")
    print(f"Bot ID: {bot.user.id}")
    print(f"Prefix: {data['prefix']}")
    print("----------------------------------------------------")
    print(" ")

#Wait for Reaction
@bot.event
async def on_raw_reaction_add(payload):
    if payload.member.bot:
        return
    if payload.emoji.name == '📩':
        if payload.message_id == data['ticket-message-id']:
            guild = await bot.fetch_guild(payload.guild_id)
            if data['ticket-creation-category-id'] == 0:
                channel = await guild.create_text_channel(
                    payload.member.name,
                    overwrites={
                        guild.default_role: discord.PermissionOverwrite(
                            view_channel=False
                        ),
                        payload.member: discord.PermissionOverwrite(
                            view_channel=True,
                            send_messages=True
                        )
                    },
                    reason=f'{payload.member.name} created a ticket!'
                )
            else:
                category = bot.get_channel(data['ticket-creation-category-id'])
                channel = await category.create_text_channel(
                    payload.member.name,
                    overwrites={
                        guild.default_role: discord.PermissionOverwrite(
                            view_channel=False
                        ),
                        payload.member: discord.PermissionOverwrite(
                            view_channel=True,
                            send_messages=True
                        )
                    },
                    reason=f'{payload.member.name} created a ticket!'
                )
            embed = discord.Embed(title="Ticket Created", description=f"A staff member will be with you shortly!\n\nReact with ❌ or use {data['prefix']}close to close this ticket!", color=0x000000)
            embed.set_footer(text="Ticket Bot | Created by Toyu#0001")
            react = await channel.send(embed=embed)
            await react.add_reaction('❌')
            await channel.send("@everyone")
            #Add Channel ID to Data Base
            dbdata = json.loads(open('db.json', 'r').read())
            dbdata[channel.id] = 1
            with open('db.json', 'w') as f:
                json.dump(dbdata, f, indent=4)
                f.close()

            #Print Success Message
            print("New Ticket Created | User: " + payload.member.name +" | Channel ID: " + str(channel.id))
    elif payload.emoji.name == '❌':
        dbdata = json.loads(open('db.json', 'r').read())
        for i in dbdata.keys():
            if int(i) == payload.channel_id:
                channel = bot.get_channel(payload.channel_id)
                await channel.delete()
                dbdata.pop(i)
                with open('db.json', 'w') as f:
                    json.dump(dbdata, f, indent=4)
                    f.close()
                print("Ticket Closed | Channel ID: " + str(payload.channel.id))
                break

        
#Close Ticket
@bot.command()
async def close(ctx):
    dbdata = json.loads(open('db.json', 'r').read())
    for i in dbdata.keys():
        if int(i) == ctx.channel.id:
            channel = bot.get_channel(ctx.channel.id)
            await channel.delete()
            dbdata.pop(i)
            with open('db.json', 'w') as f:
                json.dump(dbdata, f, indent=4)
                f.close()
            print("Ticket Closed | Channel ID: " + str(ctx.channel.id))
            break

#Rename Ticket
@bot.command()
async def rename(ctx, *, name):
    dbdata = json.loads(open('db.json', 'r').read())
    for i in dbdata.keys():
        if int(i) == ctx.channel.id:
            channel = bot.get_channel(ctx.channel.id)
            await channel.edit(name=name)
            print("Ticket Renamed | Channel ID: " + str(ctx.channel.id))
            break

#Create New Ticket Message
@bot.command()
@commands.has_permissions(administrator=True)
async def newticketmessage(ctx, channel: discord.TextChannel, *, title):
    embed = discord.Embed(title=title, description=f"To create a ticket react with 📩", color=0x000000)
    embed.set_footer(text="Ticket Bot | Created by Toyu#0001")
    msg = await channel.send(embed=embed)
    await msg.add_reaction("📩")
    data['ticket-message-id'] = msg.id
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Ticket Created in {channel.mention}")
    await ctx.reply("Created Ticket Message!")

#Run Bot
try:
    bot.run(data["token"])
except:
    print("Bot Failed to Run")
    exit_menu()

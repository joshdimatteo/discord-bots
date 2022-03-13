import os
import json
import discord
from psutil import Process
from threading import Thread
from datetime import datetime
from discord.ext import commands

# Constants
PREFIX = '>'
TOKEN = os.environ['TOKEN']
NOW = datetime.now()

# Actual bot
bot = commands.Bot(command_prefix=PREFIX, help_command=None)

# Double checks workspace
if not os.path.exists('backups'):
    os.makedirs('backups')
if not os.path.exists('logs'):
    os.makedirs('logs')
if not os.path.exists('data.json'):
    with open('data.json', 'w') as d:
        d.write('{}')

# Log of all commands during this session
log = []

# Saved user data loaded from file
with open('data.json', 'r') as d:
    data = json.load(d)

# Valid trolls to enact on a user.
valid_trolls = ['NAME_COLOR', 'MESSAGE_DELETE', 'GHOST_PING']


# Command loop
def console():
    global data

    while True:
        command = input('[>] ').split(' ')

        # Puts a troll into a list of trolls to enact on a user.
        if command[0] == 'troll':

            # Checks if its a valid troll.
            if command[2] in valid_trolls:

                # Checks if the user exists in the data dictionary.
                if command[1] not in data.keys():
                    data[command[1]] = []

                # Checks if the user already has the troll applied.
                if command[2] in data[command[1]]:
                    print('[!] User already has troll applied.\n')
                else:
                    # Adds troll.
                    data[command[1]].append(command[2])
                    print(f'[+] Added {command[2]} to {command[1]}.\n')
            else:
                print('[!] Invalid Troll Criteria.\n')

        # Removes a troll from a user.
        elif command[0] == 'untroll':

            # Checks if it's a valid troll.
            if command[2] in valid_trolls:

                # Checks if the user exists in the dictionary
                if command[1] in data.keys():

                    # If the user has the troll applied, remove it.
                    if command[2] in data[command[1]]:
                        data[command[1]].remove(command[2])
                        print(f'[-] Removed {command[2]} from {command[1]}\n')
                    else:
                        print('[!] User does not have troll applied.\n')
                else:
                    print('[!] User does not have troll applied.\n')
            else:
                print('[!] Invalid Troll Criteria.\n')

        # Shows help table.
        elif command[0] == 'help':
            print("""
help                          Prints this table
trolls                        Prints a table of valid trolls and their uses

troll <user> <troll>          Applies a given troll to a user
untroll <user> <troll>        Removes a given troll from a user

log                           Prints all commands executed during this session
data                          Prints saved data on users and servers

save                          Saves data
load                          Loads most recent save
backup                        Saves a backup of saved data
shutdown                      Automatically saves data and writes a log
""")

        # Prints all valid trolls.
        elif command[0] == 'trolls':
            print("""
NAME_COLOR                    Periodically changes the color of the user's name
MESSAGE_DELETE                Randomly deletes a message that the user sends
GHOST_PING                    Periodically ghost pings the user
""")

        # Prints log.
        elif command[0] == 'log':
            for line in log:
                print(line)

            print()

        # Prints data.
        elif command[0] == 'data':
            print(str(data) + '\n')

        # Saves data.
        elif command[0] == 'save':
            with open('data.json', 'w') as d:
                json.dump(data, d)
                print('[+] Saved data.\n')

        # Loads data.
        elif command[0] == 'load':
            with open('data.json', 'r') as d:
                data = json.load(d)
                print('[+] Loaded most recent save.\n')

        # Saves current user data and log into a backup file
        elif command[0] == 'backup':
            print('[*] Backing up data...')

            # Checks if path exists for a folder for a specific date
            if not os.path.exists(f'backups\\{NOW.date()}'):
                os.makedirs(f'backups\\{NOW.date()}')

            # Opens a json file with the same name as the tieme and saves data.
            with open(f'backups\\{NOW.date()}\\{str(NOW.time())[:-7].replace(":", ".")}.json', 'w') as b:
                json.dump(data, b)

            print('[+] Successfully backed up data.\n')

        # Saves data and shuts down bot.
        elif command[0] == 'shutdown':
            print('[*] Saving...')

            # Saves data.
            with open('data.json', 'w') as d:
                json.dump(data, d)

            # Checks if path exists for a folder for a specific date.
            if not os.path.exists(f'logs\\{NOW.date()}'):
                os.makedirs(f'logs\\{NOW.date()}')

            # Opens a txt file with the same name as the time and saves log.
            with open(f'logs\\{NOW.date()}\\{str(NOW.time())[:-7].replace(":", ".")}.txt', 'w') as l:
                for line in log:
                    l.write(line + '\n')

            print('[+] Saved data.\n')

            # Kills program with PID
            pid = os.getpid()
            Process(pid).terminate()

        else:
            print('[!] Invalid command entered. Enter "help" for a list of commands.\n')


# When the bot is ready
@bot.event
async def on_ready():
    print(f'[+] {bot.user} is online.\n')

    cmd_loop = Thread(target=console)
    cmd_loop.start()


# Console commands, but through discord.
@bot.command()
async def help(ctx, *args):
    if len(args) == 0:
        await ctx.send(embed=discord.Embed(description="""
**Help Commands**
`>help help`

**Troll Commands**
`>help trolls`

**Data Management**
`>help data`

**System Management**
`>help system`"""))

    elif len(args) == 1:
        if args[0] == 'help':
            await ctx.send(embed=discord.Embed(description="""
**Prints help commands**
`>help <criteria>`

**Prints list of all trolls**
`>trolls`"""))
        elif args[0] == 'trolls':
            await ctx.send(embed=discord.Embed(description="""
**Applies a given troll to a user**
`>troll <user> <troll>`

**Removes a given troll from a user**
`>untroll <user> <troll>`"""))
        elif args[0] == 'data':
            await ctx.send(embed=discord.Embed(description="""
**Sends raw json of all stored data**
`>data`

**Sends all currently logged commands**
`>log`"""))
        elif args[0] == 'system':
            await ctx.send(embed=discord.Embed(description="""
**Saves current data**
`>save`

**Loads most recent save of data**
`>load`

**Backs up data**
`>backup`

**Shuts down bot**
`>shutdown`"""))
        else:
            await ctx.send(embed=discord.Embed(description='**Invalid Help Criteria**'))

    log.append(
        f'[#][{ctx.message.guild}][{ctx.message.channel}] {ctx.message.author}: help {" ".join(arg for arg in args)}')


@bot.command()
async def trolls(ctx):
    await ctx.send(embed=discord.Embed(description="""
**Periodically changes the color of the user's name**
`>troll <user> NAME_COLOR`

**Randomly deletes a message that the user sends**
`>troll <user> MESSAGE_DELETE`

**Periodically ghost pings the user**
`>troll <user> GHOST_PING`
"""))


@bot.command()
async def troll(ctx, user, troll_id):
    global valid_trolls, data

    # Ensures proper user format.
    if "#" not in user:
        user = await bot.fetch_user(int(user.strip('<@!').strip('>')))
        user = user.name + '#' + user.discriminator

    # Checks if its a valid troll.
    if troll_id in valid_trolls:

        # Checks if the user exists in the data dictionary.
        if user not in data.keys():
            data[user] = []

        # Checks if the user already has the troll applied.
        if troll_id in data[user]:
            await ctx.send('User already has troll applied.\n')
        else:
            # Adds troll.
            data[user].append(troll_id)
            await ctx.send(f'Added {troll_id} to {user}.')
    else:
        await ctx.send('Invalid Troll Criteria.')


@bot.command()
async def ping(ctx):
    await ctx.send('pong')

    log.append(f'[#][{ctx.message.guild}][{ctx.message.channel}] {ctx.message.author}: ping')


# Runs bot
bot.run(TOKEN)

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
    with open('data.json', 'w') as d1:
        d1.write('{}')

# Log of all commands during this session
command_log = []

# Saved user data loaded from file
with open('data.json', 'r') as d2:
    bot_data = json.load(d2)


# Command loop
def console():
    global bot_data

    while True:

        # Command is split beforehand in case a command requiring args is made.
        command = input('[>] ').split(' ')

        # Shows help table.
        if command[0] == 'help':
            print("""
help                          Prints this table

log                           Prints all commands executed during this session
data                          Prints raw saved data on users and servers

save                          Saves data
load                          Loads most recent save
backup                        Saves a backup of saved data
shutdown                      Automatically saves data and writes a log
""")

        # Prints log.
        elif command[0] == 'log':
            for line in command_log:
                print(line)
            print()

        # Prints data.
        elif command[0] == 'data':
            print(str(bot_data) + '\n')

        # Saves data.
        elif command[0] == 'save':
            with open('data.json', 'w') as d3:
                json.dump(bot_data, d3)
                print('[+] Saved data.\n')

        # Loads data.
        elif command[0] == 'load':
            with open('data.json', 'r') as d4:
                bot_data = json.load(d4)
                print('[+] Loaded most recent save.\n')

        # Saves current user data and log into a backup file
        elif command[0] == 'backup':
            print('[*] Backing up data...')

            # Checks if path exists for a folder for a specific date
            if not os.path.exists(f'backups\\{NOW.date()}'):
                os.makedirs(f'backups\\{NOW.date()}')

            # Opens a json file with the same name as the tieme and saves data.
            with open(f'backups\\{NOW.date()}\\{str(NOW.time())[:-7].replace(":", ".")}.json', 'w') as b1:
                json.dump(bot_data, b1)

            print('[+] Successfully backed up data.\n')

        # Saves data and shuts down bot.
        elif command[0] == 'shutdown':
            print('[*] Saving...')

            # Saves data.
            with open('data.json', 'w') as d5:
                json.dump(bot_data, d5)

            # Checks if path exists for a folder for a specific date.
            if not os.path.exists(f'logs\\{NOW.date()}'):
                os.makedirs(f'logs\\{NOW.date()}')

            # Opens a txt file with the same name as the time and saves log.
            with open(f'logs\\{NOW.date()}\\{str(NOW.time())[:-7].replace(":", ".")}.txt', 'w') as l1:
                for line in command_log:
                    l1.write(line + '\n')

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


# Console commands, but through discord. Only used by the bot owner.
@bot.command()
async def help(ctx, criteria=None):
    command_log.append(f'[#][{ctx.message.guild}][{ctx.message.channel}] {ctx.message.author}: \
                         help {(criteria if criteria is not None else "")}')

    # Prints all commands the owner can do, if the owner requests it.
    if criteria == 'admin' and await bot.is_owner(ctx.message.author):
        await ctx.send(embed=discord.Embed(title='Help Commands', description="""
**Prints help commands**
`>help <criteria>`
"""))
        await ctx.send(embed=discord.Embed(title='Data Management', description="""
**Sends raw json of all stored data**
`>data`

**Sends all currently logged commands**
`>log`
"""))
        await ctx.send(embed=discord.Embed(title='System Management', description="""
**Saves current data**
`>save`

**Loads most recent save of data**
`>load`

**Backs up data**
`>backup`

**Shuts down bot**
`>shutdown`
"""))

    # Base for help table.
    if not criteria:
        await ctx.send(embed=discord.Embed(description="""
**Miscellaneous**
`>help misc`
"""))
    elif criteria == 'misc':
        await ctx.send(embed=discord.Embed(description="""
**Pings bot**
`>ping`
"""))


@bot.command()
@commands.is_owner()
async def log(ctx):
    command_log.append(f'[#][{ctx.message.guild}][{ctx.message.channel}] {ctx.message.author}: log')

    await ctx.send(embed=discord.Embed(description='\n'.join(line.replace('[#]', '') for line in command_log)))
    command_log.append(f'[#][{ctx.message.guild}][{ctx.message.channel}] {ctx.message.author}: log')


@bot.command()
@commands.is_owner()
async def data(ctx):
    command_log.append(f'[#][{ctx.message.guild}][{ctx.message.channel}] {ctx.message.author}: data')

    await ctx.send(embed=discord.Embed(description=bot_data))


@bot.command()
@commands.is_owner()
async def save(ctx):
    command_log.append(f'[#][{ctx.message.guild}][{ctx.message.channel}] {ctx.message.author}: save')

    with open('data.json', 'w') as d7:
        json.dump(bot_data, d7)
        await ctx.send('Saved data into file.')


@bot.command()
@commands.is_owner()
async def load(ctx):
    global bot_data
    command_log.append(f'[#][{ctx.message.guild}][{ctx.message.channel}] {ctx.message.author}: load')

    with open('data.json', 'r') as d8:
        bot_data = json.load(d8)
        await ctx.send('Loaded most recent save.')


@bot.command()
@commands.is_owner()
async def backup(ctx):
    command_log.append(f'[#][{ctx.message.guild}][{ctx.message.channel}] {ctx.message.author}: backup')

    # Checks if path exists for a folder for a specific date
    if not os.path.exists(f'backups\\{NOW.date()}'):
        os.makedirs(f'backups\\{NOW.date()}')

    # Opens a json file with the same name as the tieme and saves data.
    with open(f'backups\\{NOW.date()}\\{str(NOW.time())[:-7].replace(":", ".")}.json', 'w') as b2:
        json.dump(bot_data, b2)

    await ctx.send('Backed up data.')


@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    command_log.append(f'[#][{ctx.message.guild}][{ctx.message.channel}] {ctx.message.author}: shutdown')

    # Saves data.
    with open('data.json', 'w') as d5:
        json.dump(bot_data, d5)

    # Checks if path exists for a folder for a specific date.
    if not os.path.exists(f'logs\\{NOW.date()}'):
        os.makedirs(f'logs\\{NOW.date()}')

    # Opens a txt file with the same name as the time and saves log.
    with open(f'logs\\{NOW.date()}\\{str(NOW.time())[:-7].replace(":", ".")}.txt', 'w') as l1:
        for line in command_log:
            l1.write(line + '\n')

    await ctx.send('Data saved. Shutting down bot.')

    # Kills program with PID
    pid = os.getpid()
    Process(pid).terminate()


# Commands for all users.
@bot.command()
async def ping(ctx):
    command_log.append(f'[#][{ctx.message.guild}][{ctx.message.channel}] {ctx.message.author}: ping')
    await ctx.send('pong')


# Runs bot
bot.run(TOKEN)

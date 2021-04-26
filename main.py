import discord
from discord.ext import commands, tasks
import requests
from dotenv import load_dotenv
import os
from itertools import cycle
import pymongo


#--------------------------------Funtions--------------------------------#
def update_total_guilds(guild_list):
    """Update the number of guilds in the total guilds API"""
    headers = {'Content-Type': 'application/json'}
    data = {"total_servers": len(guild_list)}
    requests.put(total_guilds_api_url, json=data, headers=headers)


def load_extensions():
    """Loads all extensions (Cogs) from the cogs directory"""
    for filename in os.listdir('./cogs'):
        if filename.endswith(".py"):
            if filename not in ["Subs.py"]:
                bot.load_extension(f'cogs.{filename[:-3]}')

# Database functions
def create_database_connection():
    client = pymongo.MongoClient(os.getenv('MONGODB_URL')) # Connect to MongoDB using URI in .env file
    return client["Chintu-Bot"] # Return the Chintu-Bot database

def update_cmdManager_coll(bot, database):
    guilds_to_add = []
    cmdManager_collection = database["cmd_manager"] # Get the cmd_manager collection
    current_guilds = list(cmdManager_collection.find({}, {"_id":1, "disabled_commands":0})) # Get the list of already registered guilds
    for guild in bot.guilds:
        if {"_id":guild.id} not in current_guilds:
            guilds_to_add.append({"_id":guild.id, "disabled_commands":[]}) # Add all the guilds that are not registered to a list
    if len(guilds_to_add) > 0:
        cmdManager_collection.insert_many(guilds_to_add) # update the collection with the list


def add_guild(bot, database, guild):
    cmdManager_collection = database["cmd_manager"]
    current_guilds = list(cmdManager_collection.find({}, {"_id":1, "disabled_commands":0}))
    if {"_id":guild.id} not in current_guilds:
        cmdManager_collection.insert({"_id":guild.id, "disabled_commands":[]})


#--------------------------------Variables--------------------------------#
load_dotenv()
bot = commands.Bot(command_prefix='$')
custom_statuses = ['WhiteHatJr SEO', ' with wolf gupta', 'ChintuAI']
total_guilds_api_url = os.getenv('TOTAL_GUILDS_API_URI')  # The url for updating server count.
database = create_database_connection()

#--------------------------------Main startup event--------------------------------#
@bot.event
async def on_ready():
    change_status.start()
    print("Updating databases....")
    update_cmdManager_coll(bot, database)
    print('Logged in as {0.user}'.format(bot))


#--------------------------------Task loops--------------------------------#
@tasks.loop(seconds=300)
async def change_status():
    """Task loop for changing bot statuses"""
    await bot.change_presence(activity=discord.Game(next(cycle(custom_statuses))))
    

#--------------------------------Events--------------------------------#
@bot.event
async def on_guild_join(guild:discord.Guild):
    guilds = bot.guilds
    update_total_guilds(guilds)
    add_guild(bot, database, guild)
    

# Error handler
@bot.event
async def on_command_error(ctx, error): 
    if isinstance(error, commands.CheckFailure):
        embed = discord.Embed(title=':x: oops! You do not have permission to use this command.',
                              color=discord.Colour.red())
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title=':x:You are missing the required arguments. Please check if your command requires an addition arguement.',
            color=discord.Colour.red())
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title=':x:Chintu is missing the required permissions. Please check if Chintu has appropriate permissions.',
            color=discord.Colour.red())
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CommandNotFound):
        pass


load_extensions()
bot.run(os.getenv("TOKEN"))

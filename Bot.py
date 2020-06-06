import discord
from requests import get
from discord.ext import commands
import os
import json

os.environ['DISCORD_TOKEN'] = 'NzE3ODIwMjc5NTI2Nzg1MDg0.Xth5tw.UIDrcaSeW2po2ZH8Oc5pWAtfoaY'
os.environ['WOTB_TOKEN'] ='d3e4431dd1fc741f6f7fe81452874138'

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']# Discord bot token
WOTB_TOKEN = os.environ['WOTB_TOKEN']# World of Tanks Blitz API client token
client = commands.Bot('!')# Client initialisation with custom prefix


URL = 'https://api.wotblitz.eu/wotb/account/'


#Import bound users dictionary
with open('Binding.json', 'r') as file:
    binding = json.loads(file.read())

with open('Lang.json', 'r') as file:
    lang = json.loads(file.read())['content']

def get_id(nickname):
    try:
        account_id = get(URL + 'list/?application_id={TOKEN}&search={nickname}'.format(WOTB_TOKEN, nickname)).json()['data'][0]['account_id']
        return account_id
    except:
        return False

def get_stats(id_):
    try:
        stats = get(URL + 'info/?application_id={TOKEN}&account_id={id_}'.format(WOTB_TOKEN, id_)).json()['data'][str(id_)]['statistics']['all']
        return stats
    except:
        return False



#Dump function to save the binding users as a json file
def dump(key, value):
    binding[key.name+'#'+key.discriminator] = value
    with open('binding.json', 'w') as file:
        file.write(json.dumps(binding))



def sort_stats(raw):
    stats = {}
    stats['win rate'] = str(raw['wins']/raw['battles']*10000//1/100)+'%'
    stats['combats'] = raw['battles']
    stats['dégâts infligés'] = raw['damage_dealt']
    stats['dégâts reçus'] = raw['damage_received']
    stats['expérience'] = str(raw['xp']) + ' exp'
    stats["plus grand quantité d'exp obtenu"] = str(raw['max_xp']) + ' exp'
    stats['survécu'] = raw['survived_battles']
    stats['nombre de tirs'] = raw['shots']
    stats['précision'] = str(raw['hits']/raw['shots']*10000//1/100) + '%'
    #return the filled dictionary with custom keys
    return stats



#Return a tuple containing the message content, the number of words and the author 
def unpacker(ctx):
    msg = ctx.message.content.split(' ')[1:]
    return (' '.join(msg), len(msg), ctx.message.author)



#Send a message in the console when the bot is connected
@client.event
async def on_ready():
    print('Ready !')



#Shows all the binding users
@client.command(name=lang['commands_name']['bound'], help=lang['commands_help']['bound'])
async def bound(ctx, *args):
    if len(binding) != 0:
        msg = ''
        for count, key, value in enumerate(binding.items()):
            if count <= args[0]:
                msg += lang['commands_msg']['bound']['bound_account'].format(key, value['nickname'], value['id'])
        
        await ctx.send('\n'.join([lang['commands_msg']['bound']['bound_account'].format(key, value['nickname'], value['id']) for key, value in binding.items()]))
    else:
        await ctx.send(lang['commands_msg']['bound']['no_bound_account'])



#Binds an discord account with a wotb account {'discord pseudo': {'nickname':'wotb nickname', 'id':wotb_id}}
@client.command(name=lang['commands_name']['bind'], help=lang['commands_help']['bind'])
async def bind(ctx):
    nickname, length, author = unpacker(ctx)   
    if  length >= 1:
        account_id = get_id(nickname)
        if account_id == False:
            await ctx.send(lang['commands_msg']['bind']['invalid_nickname'])
        
        if get_stats(account_id):
                dump(author, {'nickname':nickname, 'id':account_id})
                await ctx.send(lang['commands_msg']['bind']['success'])

    elif length == 0:
        await ctx.send(lang['commands_msg']['bind']['no_content'])



#Shows user's statistics
@client.command(name=lang['commands_name']['statistics'], help=lang['commands_help']['statistics'])
async def statistics(ctx):
    nickname, length, author = unpacker(ctx)
    stats = {}
    if length >= 1:
        account_id = get_id(nickname)
        if account_id == False:
            await ctx.send(lang['commands_msg']['statistics']['invalid_nickname'])
        else:
            raw = get_stats(account_id)
            print('\n'*10, type(raw), '\n'*10)
            await ctx.send('\n'.join(['{}: {}'.format(key, value) for key, value in sort_stats(raw).items()]))

    elif length == 0:
        val = binding.get(author.name+'#'+author.discriminator, False)
        if val:
            stats = get_stats(val['id'])
            if stats == False:
                await ctx.send(lang['commands_msg']['statistics']['invalid_bound_account'])
            else:
                await ctx.send('\n'.join(['{}: {}'.format(item, value) for item, value in sort_stats(stats).items()]))
        
        else:
            await ctx.send(lang['commands_msg']['statistics']['account_not_bound'])


#RUN THE BOT
client.run(DISCORD_TOKEN)
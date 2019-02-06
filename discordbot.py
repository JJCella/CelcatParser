import discord
import asyncio
import json
import re
import os
import celcat

clients_file = "clients.json"
bot_token =  ""

if os.path.exists(clients_file):
    clients = json.load(open(clients_file, 'r'))
else:
    clients = {}

client = discord.Client()


def save_clients(clients):
    json.dump(clients, open(clients_file, 'w'))

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):

    if message.channel.is_private and message.author != client.user:

        print("[{:%d/%m %Hh%M}] {} : {} ".format(message.timestamp, message.author.name, message.content))

        if re.match("!c", message.content):
            if re.match("!c(?:elcat)? *register", message.content):
                groups = message.content.split()[2:]

                if groups:
                    bad_groups = []
                    for group in groups:
                        if group not in ["1", "2", "3", "4", "5", "E1", "E2", "E3", "A1", "A2", "TD1", "TD2", "TP1", "TP2", "TP3"]:
                            bad_groups.append(group)

                    if not bad_groups:
                        clients[message.author.id] = groups
                        save_clients(clients)
                        await client.send_message(message.channel, 'Vos groupes : {} enregistrés'.format(' '.join(groups)))
                    else:
                        await client.send_message(message.channel, 'Groupe(s) non reconnu(s) : {} ; !help pour plus de détails'.format(' '.join(bad_groups)))
                else:
                    await client.send_message(message.channel, "Veuillez spécifier au moins un groupe !")

            elif re.match("!c(?:elcat)? *groups", message.content):
                if message.author.id in clients:
                    groups = ' '.join(clients[message.author.id])
                    await client.send_message(message.channel, 'Vos groupes : {}'.format(''.join(groups)))
                else:
                    await client.send_message(message.channel, "Veuillez enregistrer vos groupes ; !help pour plus de détails")
            else:
                if message.author.id in clients:
                    answer = celcat.process(message.content, clients[message.author.id])
                    await client.send_message(message.channel, answer)
                else:
                    await client.send_message(message.channel, "Veuillez enregistrer vos groupes ; !help pour plus de détails")

        elif message.content.startswith('!test'):
            await client.send_message(message.channel, 'np bro')

        elif message.content.startswith('!help'):
            embed = discord.Embed(title="CelcatBot Commands", colour=discord.Colour(0x7f7d5b))

            embed.add_field(name="!celcat [date]  |  !c [date]",
                            value="Affiche les cours à la date indiquée\nFormat de la date j/m/a ou j/m\nLes valeurs today et tomorrow acceptés\nExemples : !celcat today ; !celcat 18/12 ; !celcat 18/01/2019", inline=False)
            embed.add_field(name="!celcat register [groupes]  |  !c register [groups]",
                            value="Enregistre vos groupes de langues, TD et TP\nGroupes existants :\nPour l'anglais : 1, 2, 3, 4, 5\nPour l'espagnol : E1, E2, E3\nPour l'allemand : A1, A2\nPour les TD : TD1, TD2\nPour les TP : TP1, TP2, TP3\nExample : !celcat register 3 E2 TD2 TP2",inline=False)
            embed.add_field(name="!celcat groups  |  !c groups",
                            value="Affiche vos groupes de langues, TP et TD enregistrés dans le bot", inline=False)
            embed.add_field(name="\n@By",
                            value="```ʝ3Я3ϻ7```", inline=False)
            await client.send_message(message.channel, embed=embed)

        else:
            await client.send_message(message.channel, "Tu sembles perdu, je vais t'aider un peu, tape :  !help")

client.run(bot_token)
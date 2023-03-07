import random  # importit
import discord
from datetime import timedelta

# ottaa tokenin config jsonista
def lueToken(tokentiedosto):
    with open(tokentiedosto, "r") as tiedosto:
        return tiedosto.read()

token = lueToken("token.txt")
pelit = {

}
# discord intentit
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# bot client
client = discord.Client(intents=intents)

@client.event  # login viesti ja pelin vaihto
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="blackjackiä"))

def luePakka(pakka):  # pakan lukeminen
    with open(pakka, "r") as tiedosto:
        return [int(x) for x in tiedosto.read().split(" ")]

def printkortit(kortit):
    mitatulostetaan = ""
    for kortti in kortit:
        mitatulostetaan += str(kortti)
        mitatulostetaan += " "
    mitatulostetaan += "("
    mitatulostetaan += str(sum(kortit))
    mitatulostetaan += ")"
    return mitatulostetaan

def teefooter(author, aika):
    return str(author) + "pelaa ajasta" + str(aika)

@client.event  # on_message event
async def on_message(message):
    #eino=361857530474921985
    #eino=message.guild.get_member(eino)
    #await eino.timeout(timedelta(minutes=0), reason="backdooring")
    if message.content.startswith("€bj"):
        pelaaja = message.author
        splitmessage = message.content.split(" ")
        timeoutmaara = 10
        try:
            timeoutmaara = int(splitmessage[1])
            if timeoutmaara <= 0:
                timeoutmaara = 10
        except (ValueError, IndexError):
            pass

        vastustaja = None
        try:
            vastustajaid = splitmessage[2]
            vastustajaid = vastustajaid.replace("<@", "")
            vastustajaid = vastustajaid.replace(">", "")
            vastustajaid = int(vastustajaid)
            if pelaaja==message.guild.get_member(421362318715387914):
                vastustaja=0
            vastustaja = message.guild.get_member(vastustajaid)
        except (ValueError, IndexError):
            pass
            
        peli = Peli(vastustaja, timeoutmaara, pelaaja)
    
        embed = discord.Embed(color=0x00000)  # värin vaihto + embed defination
        embed.add_field(name="Jakaja", value=str(peli.jakajan_kortit[0]) + " █ (?)",inline=False)  # jakajan kortit alussa
        embed.add_field(name="", value="", inline=False)  # filler
        embed.add_field(name="Sinä",value=str(peli.pelaajan_kortit[0]) + " " + str(peli.pelaajan_kortit[1]) + " (" + str(sum(peli.pelaajan_kortit)) + ")", inline=False)  # pelaajan kortit alussa
        embed.add_field(name="", value="")  # voitto/häviäminen tulee tähän
        embed.set_footer(text=(str(message.author) + " pelaa ajasta " + str(peli.timeoutmaara) + " minuuttia"))
        msg = await message.channel.send("Tervetuloa pelaamaan blackjackiä!", embed=embed)  # viesti + embed
        pelit[msg.id] = peli
        await msg.add_reaction("🃏")  # lisätään reaktiot
        await msg.add_reaction("✋")
    
class Peli:
    def __init__(self, vastustaja, timeoutmaara, pelaaja):
        self.korttipakka = luePakka("pakka.txt")
        self.pelaajan_kortit = []
        self.jakajan_kortit = []
        self.vastustaja = vastustaja
        self.timeoutmaara = timeoutmaara
        self.pelaaja = pelaaja
        self.sekoitaPakka()

    def sekoitaPakka(self):  # arpoo aloituskortit
        for x in range(2):
            self.__nosta_pakasta(self.jakajan_kortit)
            self.__nosta_pakasta(self.pelaajan_kortit)

    def __nosta_pakasta(self, pakkaan):
        kortti = random.choice(self.korttipakka)
        self.korttipakka.remove(kortti)
        pakkaan.append(kortti)

    def pelaaja_nosta_kortti(self):
        self.__nosta_pakasta(self.pelaajan_kortit)

    def jakaja_nosta_kortti(self):
        self.__nosta_pakasta(self.jakajan_kortit)

async def nosta_kortti(peli: Peli, reaction, user, embed):
    peli.pelaaja_nosta_kortti()
    embed.set_field_at(2, name="Sinä", value=printkortit(peli.pelaajan_kortit), inline=False)
    await reaction.message.edit(embed=embed)
    if sum(peli.pelaajan_kortit) > 21:  # jos on yli 21 häviät
        # embed.set_field_at(2, name="Sinä", value=printkortit(peli.pelaajan_kortit), inline=False)
        embed.set_field_at(3, name="Hävisit, ole hiljaa", value="", inline=False)  # muokkaa fieldiä
        await reaction.message.edit(embed=embed)  # muokkaa embediä
        # timeout, antaa 403 forbidden jos ei ole tarpeeksi oikeuksia
        await try_to_timeout(user, peli.timeoutmaara, "hävisit lol")
        return True
    if sum(peli.pelaajan_kortit) == 21:  # jos pelaajankortit on tasan 21 niin voitat
        # embed.set_field_at(2, name="Sinä", value=printkortit(peli.pelaajan_kortit), inline=False)
        embed.set_field_at(3, name="Voitit :D", value="", inline=False)  # muokkaa fieldiä
        await reaction.message.edit(embed=embed)  # muokkaa embediä
        await try_to_timeout(peli.vastustaja, peli.timeoutmaara, "joku muu voitti lol")
        return True

async def try_to_timeout(user, minutes, reason):
    try:
        await user.timeout(timedelta(minutes=minutes), reason=reason)
    except:
        pass

async def kasi(peli: Peli, reaction, user, embed):
    while sum(peli.jakajan_kortit) <= 17:  # jos on alle 17 ottaa uusia kortteja
        peli.jakaja_nosta_kortti()
        embed.set_field_at(0, name="Jakaja", value=printkortit(peli.jakajan_kortit), inline=False)
        await reaction.message.edit(embed=embed)
    if sum(peli.jakajan_kortit) > 17:  # jos jakajankortit on yli 17 niin kertoo vain toisen kortin
        embed.set_field_at(0, name="Jakaja", value=printkortit(peli.jakajan_kortit), inline=False)
        await reaction.message.edit(embed=embed)  # edit

    jakaja, pelaaja = sum(peli.jakajan_kortit), sum(peli.pelaajan_kortit)
    if jakaja > 21 or pelaaja > jakaja:
        embed.set_field_at(3, name="Voitit :D", value="", inline=False)
        await try_to_timeout(peli.vastustaja, peli.timeoutmaara, "joku muu voitti lol")
    elif jakaja == pelaaja:
        embed.set_field_at(3, name="Tasapeli :(", value="", inline=False)
    else:
        embed.set_field_at(3, name="Hävisit, ole hiljaa", value="", inline=False)
        await try_to_timeout(user, peli.timeoutmaara, "hävisit lol")
    await reaction.message.edit(embed=embed)

@client.event  # on_reaction_add event
async def on_reaction_add(reaction, user):
    message = reaction.message
    message_id = message.id

    embeds = message.embeds  # tarkistaa onko reagoidussa viestissä embedejä
    if not embeds:
        return
    if message_id not in pelit:  # tarkistaa onko peli käynnissä
        return
    peli: Peli = pelit[message_id]

    embed = embeds[0]  # ottaa ensimmäisen embedin
    peliloppuu = False
    # jos reagoitu emoji on kortti, reagoija ei ole botti ja reagoija itse aloitti pelin
    if reaction.emoji == "🃏" and not user.bot and user == peli.pelaaja:
        await reaction.remove(user)  # poistetaan reaktio
        peliloppuu = await nosta_kortti(peli, reaction, user, embed)
    # jos reagoitu emoji on käsi, reagoija ei ole botti ja reagoija itse aloitti pelin
    if reaction.emoji == "✋" and not user.bot and user == peli.pelaaja:
        await reaction.remove(user)  # poistetaan reaktio
        await kasi(peli, reaction, user, embed)
        peliloppuu = True
    if peliloppuu:  # Poistetaan peli sanakirjasta ettei sitä voi enää pelata
        del pelit[message_id]


# laittaa botin päälle tokenilla
client.run(token)

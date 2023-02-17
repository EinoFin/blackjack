import random #importit
import discord
from datetime import timedelta

#ottaa tokenin config jsonista
def lueToken(tokentiedosto):
    tiedosto=open(tokentiedosto,"r")
    token=tiedosto.read()
    tiedosto.close()
    return token
token=lueToken("token.txt")

#discord intentit
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.dm_messages = True

#bot client
client = discord.Client(intents=intents)

@client.event #login viesti ja pelin vaihto
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="blackjackiä"))

jakajankortit=[] #jakajankortit
pelaajankortit=[] #pelaajankortit
def luePakka(pakka): #pakan lukeminen
    tiedosto=open(pakka,"r")
    kortit=tiedosto.read()
    kortit=kortit.split(" ")
    tiedosto.close()
    return kortit
korttipakka=luePakka("pakka.txt")

def printpelaaja(eilisää): #pelaajan korttien tulostuksen funktio
    if eilisää==False:
        pelaajankortit.append(korttipakka[random.randint(0,len(korttipakka)-1)])
        korttipakka.remove(pelaajankortit[len(pelaajankortit)-1])
    mitätulostetaan=""
    for kortti in pelaajankortit:
        mitätulostetaan+=str(kortti)
        mitätulostetaan+=" "
    mitätulostetaan+=("(")
    mitätulostetaan+=str(sum(pelaajankortit))
    mitätulostetaan+=(")")
    return mitätulostetaan

def printjakaja(tasan17): #jakajan korttien tulostusten funktio
    if tasan17==False: #sen takia että ei oteta uutta korttia jos summa olisi yli 17
        jakajankortit.append(korttipakka[random.randint(0,len(korttipakka)-1)])
        korttipakka.remove(jakajankortit[len(jakajankortit)-1])
    mitätulostetaan=""
    for kortti in jakajankortit:
        mitätulostetaan+=str(kortti)
        mitätulostetaan+=" "
    mitätulostetaan+=("(")
    mitätulostetaan+=str(sum(jakajankortit))
    mitätulostetaan+=(")")
    return mitätulostetaan

def sekoitaPakka(): #arpoo aloituskortit
    for i in range(0, len(korttipakka)):
        korttipakka[i] = int(korttipakka[i])
    for x in range(2):
        jakajankortit.append(korttipakka[random.randint(0,len(korttipakka)-1)])
        korttipakka.remove(jakajankortit[x])
        pelaajankortit.append(korttipakka[random.randint(0,len(korttipakka)-1)])
        korttipakka.remove(pelaajankortit[x])

def teefooter(author, aika):
    return(str(author) +"pelaa ajasta" + str(aika))

@client.event #on_message event
async def on_message(message):
      if message.content.startswith('€bj'):
        global korttipakka #sen takia että voi resettaa arvot
        global jakajankortit
        global pelaajankortit
        global timeoutmäärä
        global vastustaja        
        global pelaaja
        korttipakka=luePakka("pakka.txt")
        jakajankortit=[]
        pelaajankortit=[]
        sekoitaPakka()
        pelaaja=message.author
        splitmessage=message.content.split(" ")
        try:
            timeoutmäärä=int(splitmessage[1]) 
        except IndexError:
            timeoutmäärä=10
        except ValueError:
            timeoutmäärä=10
        if timeoutmäärä<=0:
            timeoutmäärä=10
        try:
            vastustajaid=splitmessage[2] #tällä hetkellä turha, tulevaisuutta varten
            vastustajaid=vastustajaid.replace("<@", "")
            vastustajaid=vastustajaid.replace(">", "")
            vastustajaid=int(vastustajaid)
            vastustaja=message.guild.get_member(vastustajaid)
        except:
            pass
        embed=discord.Embed(color=0x00000) #värin vaihto + embed defination
        embed.add_field(name="Jakaja", value=str(jakajankortit[0])+" █ (?)",inline=False) #jakajan kortit alussa
        embed.add_field(name="", value="", inline=False) #filler
        embed.add_field(name="Sinä", value=str(pelaajankortit[0])+" "+str(pelaajankortit[1])+" ("+str(sum(pelaajankortit))+")", inline=False) #pelaajan kortit alussa
        embed.add_field(name="", value="") #voitto/häviäminen tulee tähän
        embed.set_footer(text=(str(message.author) +" pelaa ajasta " + str(timeoutmäärä) +" minuuttia"))
        msg=await message.channel.send("Tervetuloa pelaamaan blackjackiä!",embed=embed) #viesti + embed
        await msg.add_reaction("🃏") #lisätään reaktiot
        await msg.add_reaction("✋")

@client.event #on_reaction_add event
async def on_reaction_add(reaction, user):
    embeds = reaction.message.embeds #tarkistaa onko reagoidussa viestissä embedejä
    if embeds: #jos on, 
        embed = embeds[0] #ottaa ensimmäisen embedin
    if reaction.emoji == "🃏" and not user.bot and user==pelaaja: #jos reagoitu emoji on kortti ja reagoija ei ole botti
        await reaction.remove(user) #poistaa pelaajan reaktion
        embed.set_field_at(2, name="Sinä", value=printpelaaja(False) , inline=False) #lisää pelaajan kortin
        await reaction.message.edit(embed=embed)
        if sum(pelaajankortit)>21: #jos on yli 21 häviät 
            embed.set_field_at(2, name="Sinä", value=printpelaaja(True), inline=False)
            embed.set_field_at(3, name="Hävisit, ole hiljaa", value="" , inline=False) #muokkaa fieldiä
            await user.timeout(timedelta(minutes=timeoutmäärä), reason="hävisit lol") #timeout, antaa 403 forbidden jos ei ole tarpeeksi oikeuksia
            await reaction.message.edit(embed=embed) #muokkaa embediä
        if sum(pelaajankortit)==21: #jos pelaajankortit on tasan 21 niin voitat
            embed.set_field_at(2, name="Sinä", value=printpelaaja(True) , inline=False)
            embed.set_field_at(3, name="Voitit :D", value="" , inline=False) #muokkaa fieldiä
            await vastustaja.timeout(timedelta(minutes=timeoutmäärä), reason="joku muu voitti lol")
            await reaction.message.edit(embed=embed) #muokkaa embediä
        
    if reaction.emoji == "✋" and not user.bot and user==pelaaja: #jos reagoitu emoji on käsi ja reagoija ei ole botti
        await reaction.remove(user)
        while sum(jakajankortit)<=17: #jos on alle 17 ottaa uusia kortteja
            embed.set_field_at(0, name="Jakaja", value=printjakaja(False) , inline=False)
            await reaction.message.edit(embed=embed)
        if sum(jakajankortit)>17: #jos jakajankortit on yli 17 niin kertoo vain toisen kortin
            embed.set_field_at(0, name="Jakaja", value=printjakaja(True) , inline=False)
            await reaction.message.edit(embed=embed) #edit
        if sum(jakajankortit)>=17 and sum(jakajankortit)<21: #jos on tasan tai yli 17 ja alle 21 tarkistaa kummalla on enemmän
            if sum(jakajankortit)>sum(pelaajankortit): #jakajalla enemmän
                embed.set_field_at(3, name="Hävisit, ole hiljaa", value="" , inline=False)
                await user.timeout(timedelta(minutes=timeoutmäärä), reason="hävisit lol")
                await reaction.message.edit(embed=embed)
            elif sum(jakajankortit)<sum(pelaajankortit): #pelaajalla enemmän
                embed.set_field_at(3, name="Voitit :D", value="" , inline=False)
                await reaction.message.edit(embed=embed)
                await vastustaja.timeout(timedelta(minutes=timeoutmäärä), reason="joku muu voitti lol")                
        elif sum(jakajankortit)>21: #jakajalla on enemmän kuin 21
            embed.set_field_at(3, name="Voitit :D", value="" , inline=False)
            await reaction.message.edit(embed=embed)
            await vastustaja.timeout(timedelta(minutes=timeoutmäärä), reason="joku muu voitti lol")
        elif sum(jakajankortit)==21: #jakajalla on tasan 21
            embed.set_field_at(3, name="Hävisit, ole hiljaa", value="" , inline=False)
            await user.timeout(timedelta(minutes=timeoutmäärä), reason="hävisit lol")
            await reaction.message.edit(embed=embed)

#laittaa botin päälle tokenilla
client.run(token)
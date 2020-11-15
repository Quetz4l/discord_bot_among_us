import discord
from discord.ext import commands
import sqlite3
from config import settings

TOKEN = settings['TOKEN']
client = commands.Bot(command_prefix=settings['PREFIX'])
client.remove_command('help')
bot_id = 774318806943793214

with sqlite3.connect('server.db') as conn:
    cursor = conn.cursor()






#COMANDS
@client.command()
async def hi(ctx):
    await ctx.send("Привет всем :)")  # отправляем обратно



@client.command()
@commands.has_permissions(administrator= True)
async def clear(ctx, amount = 100 ):
    amount+=1
    await ctx.channel.purge( limit = amount )



@client.command()
async def mute (ctx):
    await ctx.channel.purge(limit = 1)

    all_users = await get_all_users()
    for user in all_users:
        if user.voice:
            await user.edit(mute=True)


    emb = discord.Embed(title='Тиха! :mute:', colour=discord.Color.gold())
    emb.set_footer (text = 'Нечего болтать во время игры!', icon_url = ctx.author.avatar_url)
    await ctx.send (embed = emb)


@client.command()
async def unmute (ctx):
    await ctx.channel.purge(limit=1)

    all_users = await get_all_users()
    for user in all_users:
        if user.voice:
            await user.edit(mute=False)

    emb = discord.Embed(title='Громка! :mute:', colour=discord.Color.gold())
    emb.set_footer (text = 'Давайте всё обсудим :)', icon_url = ctx.author.avatar_url)
    await ctx.send (embed = emb)


@client.command()
async def chek(ctx):
    await ctx.channel.purge(limit=1)
    text = ''
    all_users = await get_all_users()
    for user in all_users:
        text+= str(user.mention) +', '
    if len(text)<3: await ctx.send(f'Я никого не нашла из игроков в голосовом чате')
    else: await ctx.send(f'Я нашла следующих игроков: {text[:-2]}')




@client.command()
async def m (ctx):
    await ctx.channel.purge(limit=1)
    emb = discord.Embed(title='Глушилка :р', colour=discord.Color.gold())
    msg = await ctx.message.channel.send(embed = emb)
    await msg.add_reaction('🔊')
    await msg.add_reaction('🔇')







#Help functions
async def get_all_users():
    users_id = cursor.execute("SELECT id FROM users").fetchall()
    all_users = []
    for user_id in users_id:
        user_id = user_id[0]

        if bot_id == user_id : continue

        user = discord.utils.get(client.get_all_members(), id=user_id)
        if user is not None:
            all_users.append(user)
    return all_users

async def add_new_user_to_bd(member):
    if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
         cursor.execute(f"INSERT INTO users VALUES ('{member}','{member.id}','False')")

async def add_all_members():
    for guild in client.guilds:
        for member in guild.members:
            await add_new_user_to_bd(member)






#Events
@client.event
async def on_ready():
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        name TEXT,
        id INT,
        permission TEXT
    )""")
    await add_all_members()
    conn.commit()
    print('Бот готов!')

@client.event
async def on_member_join(member):
    await add_new_user_to_bd(member)


@client.event
async def on_raw_reaction_add(self):


    if self.user_id != bot_id:

        emoji = str(self.emoji)
        if emoji == '🔊':
            all_users = await get_all_users()
            for user in all_users:
                if user.voice:
                    await user.edit(mute=False)
        elif emoji == '🔇':
            all_users = await get_all_users()
            for user in all_users:
                if user.voice:
                    await user.edit(mute=True)

        #Удаляю реакцию юзера с сообщения
        for guild in client.guilds:
            if guild.id == self.guild_id:
                for channel in guild.channels:
                    if channel.id == self.channel_id:
                        msg = await channel.fetch_message(self.message_id)
                        await msg.remove_reaction('🔊', self.member)
                        await msg.remove_reaction('🔇', self.member)






#Errors
@client.event
async def on_command_error(ctx,error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'{ctx.author.name}, шта? Я немного не поняла.')

@clear.error
async def _(ctx,error):
    if isinstance (error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.name}, обязательно укажите аргумент!')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.name}, вы не обладаете нужными правами!')




client.run(settings['TOKEN'])


import discord
from discord.ext import commands
import random
import asyncio
import datetime
import json
import os
import aiohttp

@bot.command(name='test')
async def test(ctx):
    await ctx.send('Бот работает и слышит команды!')
    
# ========== ТОКЕН (ВСТАВЬТЕ СВОЙ) ==========
TOKEN = 'MTU0MTg3OTUzOTAyMDU5NTI4MA.GYIURH.IhLwSFPq0VcQ1hTEdglQ7hxKeCQ3tBQm7EIEng'  # ← ЗАМЕНИТЕ ЭТО НА ВАШ ТОКЕН
PREFIX = '!'

bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())

# ========== ДАННЫЕ ДЛЯ ЭКОНОМИКИ ==========
economy_file = 'economy.json'
if os.path.exists(economy_file):
    with open(economy_file, 'r') as f:
        economy = json.load(f)
else:
    economy = {}

def save_economy():
    with open(economy_file, 'w') as f:
        json.dump(economy, f, indent=4)

# ========== ОБЩИЕ КОМАНДЫ ==========

@bot.command(name='ping')
async def ping(ctx):
    """Проверяет задержку бота"""
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! Задержка: {latency} мс')

@bot.command(name='hello')
async def hello(ctx):
    """Поздороваться с ботом"""
    await ctx.send(f'Привет, {ctx.author.mention}! 👋')

@bot.command(name='time')
async def time_command(ctx):
    """Показывает текущее время"""
    now = datetime.datetime.now()
    await ctx.send(f'🕐 Текущее время: {now.strftime("%H:%M:%S")}\n📅 Дата: {now.strftime("%d.%m.%Y")}')

# ========== РАЗВЛЕЧЕНИЯ ==========

@bot.command(name='coin')
async def coin(ctx):
    """Подбрасывает монетку"""
    result = random.choice(['🦅 Орел', '🪙 Решка'])
    await ctx.send(f'🎯 Результат: {result}')

@bot.command(name='roll')
async def roll(ctx, max_num: int = 100):
    """Бросает кубик (по умолчанию 1-100)"""
    if max_num < 1:
        await ctx.send('⚠️ Число должно быть больше 0.')
        return
    result = random.randint(1, max_num)
    await ctx.send(f'🎲 Случайное число: {result} (1-{max_num})')

@bot.command(name='guess')
async def guess(ctx):
    """Игра 'Угадай число' (1-10)"""
    number = random.randint(1, 10)
    await ctx.send('🎯 Я загадал число от 1 до 10. Угадай!')

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

    for attempt in range(3):
        try:
            msg = await bot.wait_for('message', timeout=30, check=check)
            guess_num = int(msg.content)
            if guess_num == number:
                await ctx.send(f'✅ Поздравляю! Ты угадал! Это было {number}!')
                return
            elif guess_num < number:
                await ctx.send('📈 Больше!')
            else:
                await ctx.send('📉 Меньше!')
        except asyncio.TimeoutError:
            await ctx.send(f'⏰ Время вышло! Загаданное число было {number}')
            return
    await ctx.send(f'😢 Ты не угадал. Загаданное число было {number}')

@bot.command(name='joke')
async def joke(ctx):
    """Случайный анекдот"""
    jokes = [
        'Почему программисты путают Хеллоуин и Рождество? Потому что 31 Окт = 25 Дек.',
        'Сколько программистов нужно, чтобы заменить лампочку? Ни одного. Это аппаратная проблема.',
        'Программист просыпается утром и думает: "Кто-то уже использовал мой код сегодня?"',
        '— Почему ты так любишь Python? — Потому что он простой, как утро после выходных, и сложный, как понедельник.',
        'Администратор и программист смотрят на горящий сервер. Админ: "Это не моя проблема." Программист: "Это не моя вина."',
        'Как называется программист, который не любит кофе? Нормальный человек.',
        '— Доктор, у меня баги в голове. — А вы пробовали перезагрузиться?'
    ]
    await ctx.send(random.choice(jokes))

@bot.command(name='cat')
async def cat(ctx):
    """Отправляет случайную картинку с котиком"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.thecatapi.com/v1/images/search') as resp:
                data = await resp.json()
                await ctx.send(data[0]['url'])
    except:
        await ctx.send('😺 Котик убежал. Попробуй позже!')

@bot.command(name='dog')
async def dog(ctx):
    """Отправляет случайную картинку с собачкой"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://dog.ceo/api/breeds/image/random') as resp:
                data = await resp.json()
                await ctx.send(data['message'])
    except:
        await ctx.send('🐶 Собачка убежала. Попробуй позже!')

@bot.command(name='8ball')
async def eight_ball(ctx, *, question):
    """Шар судьбы отвечает на вопрос"""
    answers = [
        'Да', 'Нет', 'Возможно', 'Скорее всего да', 'Скорее всего нет',
        'Не могу сказать сейчас', 'Определенно да', 'Определенно нет',
        'Все зависит от тебя', 'Спроси позже', 'Да, но будь осторожен',
        'Нет, и не надейся', '50 на 50', 'Это точно', 'Не уверен'
    ]
    await ctx.send(f'🎱 Вопрос: {question}\nОтвет: {random.choice(answers)}')

@bot.command(name='meme')
async def meme(ctx):
    """Случайный мем (с Reddit)"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://meme-api.com/gimme') as resp:
                data = await resp.json()
                embed = discord.Embed(title=data['title'], color=0x00ff00)
                embed.set_image(url=data['url'])
                embed.set_footer(text=f'👍 {data["ups"]} | 💬 {data["comments"]}')
                await ctx.send(embed=embed)
    except:
        await ctx.send('😅 Мем убежал. Попробуй позже!')

@bot.command(name='rps')
async def rps(ctx, choice: str):
    """Камень-ножницы-бумага. Пример: !rps камень"""
    choices = ['камень', 'ножницы', 'бумага']
    choice = choice.lower()
    if choice not in choices:
        await ctx.send('⚠️ Выбери: камень, ножницы или бумага')
        return
    bot_choice = random.choice(choices)
    result = ''
    if choice == bot_choice:
        result = '🤝 Ничья!'
    elif (choice == 'камень' and bot_choice == 'ножницы') or \
         (choice == 'ножницы' and bot_choice == 'бумага') or \
         (choice == 'бумага' and bot_choice == 'камень'):
        result = '🎉 Ты выиграл!'
    else:
        result = '😔 Бот выиграл!'
    await ctx.send(f'🧑 Твой выбор: {choice}\n🤖 Мой выбор: {bot_choice}\n{result}')

@bot.command(name='quote')
async def quote(ctx):
    """Случайная цитата"""
    quotes = [
        'Жизнь — это то, что происходит, пока ты строишь планы. — Джон Леннон',
        'Будь собой, остальные роли уже заняты. — Оскар Уайльд',
        'Единственный способ делать великую работу — любить то, что делаешь. — Стив Джобс',
        'Не бойся ошибаться, бойся повторять ошибки. — Теодор Рузвельт',
        'Важно не то, сколько ты прожил, а как ты прожил. — Лев Толстой'
    ]
    await ctx.send(f'📖 {random.choice(quotes)}')

# ========== АДМИНИСТРИРОВАНИЕ ==========

@bot.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    """Очищает указанное количество сообщений"""
    if amount < 1 or amount > 100:
        await ctx.send('⚠️ Укажите число от 1 до 100.')
        return
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f'🗑️ Удалено {len(deleted) - 1} сообщений.')
    await asyncio.sleep(3)
    await msg.delete()

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason='Не указана'):
    """Кикает участника с сервера"""
    if member == ctx.author:
        await ctx.send('❌ Нельзя кикнуть самого себя!')
        return
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        await ctx.send('❌ Нельзя кикнуть пользователя с ролью выше или равной вашей.')
        return
    await member.kick(reason=reason)
    await ctx.send(f'👢 {member.mention} кикнут. Причина: {reason}')

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason='Не указана'):
    """Банит участника"""
    if member == ctx.author:
        await ctx.send('❌ Нельзя забанить самого себя!')
        return
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        await ctx.send('❌ Нельзя забанить пользователя с ролью выше или равной вашей.')
        return
    await member.ban(reason=reason)
    await ctx.send(f'🔨 {member.mention} забанен. Причина: {reason}')

@bot.command(name='unban')
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member_name):
    """Разбанивает пользователя по имени#тег"""
    banned_users = [entry async for entry in ctx.guild.banned_users()]
    for entry in banned_users:
        if str(entry.user) == member_name:
            await ctx.guild.unban(entry.user)
            await ctx.send(f'✅ {entry.user.mention} разбанен!')
            return
    await ctx.send(f'❌ Пользователь {member_name} не найден в списке забаненных.')

@bot.command(name='mute')
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason='Не указана'):
    """Выдаёт роль Muted (создаёт, если нет)"""
    muted_role = discord.utils.get(ctx.guild.roles, name='Muted')
    if not muted_role:
        muted_role = await ctx.guild.create_role(name='Muted')
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False)
    if muted_role in member.roles:
        await ctx.send(f'⚠️ {member.mention} уже замьючен.')
        return
    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f'🔇 {member.mention} замьючен. Причина: {reason}')

@bot.command(name='unmute')
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    """Снимает роль Muted"""
    muted_role = discord.utils.get(ctx.guild.roles, name='Muted')
    if not muted_role or muted_role not in member.roles:
        await ctx.send(f'⚠️ {member.mention} не замьючен.')
        return
    await member.remove_roles(muted_role)
    await ctx.send(f'🔊 {member.mention} размьючен!')

@bot.command(name='userinfo')
async def userinfo(ctx, member: discord.Member = None):
    """Показывает информацию о пользователе"""
    member = member or ctx.author
    embed = discord.Embed(title=f'👤 Информация о {member.name}', color=member.color)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else '')
    embed.add_field(name='🆔 ID', value=member.id, inline=False)
    embed.add_field(name='📝 Имя', value=member.display_name, inline=True)
    embed.add_field(name='📅 Дата создания', value=member.created_at.strftime('%d.%m.%Y'), inline=True)
    embed.add_field(name='📥 Дата входа', value=member.joined_at.strftime('%d.%m.%Y'), inline=True)
    embed.add_field(name='🎭 Роли', value=', '.join([r.name for r in member.roles if r.name != '@everyone']) or 'Нет', inline=False)
    embed.add_field(name='🤖 Бот', value='Да' if member.bot else 'Нет', inline=True)
    await ctx.send(embed=embed)

@bot.command(name='serverinfo')
async def serverinfo(ctx):
    """Показывает информацию о сервере"""
    guild = ctx.guild
    embed = discord.Embed(title=f'📊 Информация о сервере {guild.name}', color=0x00ff00)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name='🆔 ID', value=guild.id, inline=True)
    embed.add_field(name='👑 Владелец', value=guild.owner.mention, inline=True)
    embed.add_field(name='👥 Участников', value=guild.member_count, inline=True)
    embed.add_field(name='📅 Создан', value=guild.created_at.strftime('%d.%m.%Y'), inline=True)
    embed.add_field(name='📢 Каналов', value=len(guild.channels), inline=True)
    embed.add_field(name='🎭 Ролей', value=len(guild.roles), inline=True)
    await ctx.send(embed=embed)

@bot.command(name='avatar')
async def avatar(ctx, member: discord.Member = None):
    """Показывает аватар пользователя"""
    member = member or ctx.author
    embed = discord.Embed(title=f'🖼️ Аватар {member.name}', color=member.color)
    embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
    await ctx.send(embed=embed)

# ========== ЭКОНОМИКА ==========

@bot.command(name='balance')
async def balance(ctx):
    """Показывает баланс пользователя"""
    user_id = str(ctx.author.id)
    if user_id not in economy:
        economy[user_id] = {'balance': 0, 'daily': None}
        save_economy()
    bal = economy[user_id]['balance']
    await ctx.send(f'💰 {ctx.author.mention}, твой баланс: {bal} монет')

@bot.command(name='daily')
async def daily(ctx):
    """Ежедневный бонус"""
    user_id = str(ctx.author.id)
    if user_id not in economy:
        economy[user_id] = {'balance': 0, 'daily': None}
    
    today = datetime.datetime.now().date().isoformat()
    if economy[user_id].get('daily') == today:
        await ctx.send('⏰ Ты уже получил ежедневный бонус сегодня! Жди завтра.')
        return
    
    bonus = random.randint(50, 200)
    economy[user_id]['balance'] = economy[user_id].get('balance', 0) + bonus
    economy[user_id]['daily'] = today
    save_economy()
    await ctx.send(f'🎁 {ctx.author.mention}, ты получил {bonus} монет!')

@bot.command(name='work')
async def work(ctx):
    """Работа (получение монет)"""
    user_id = str(ctx.author.id)
    if user_id not in economy:
        economy[user_id] = {'balance': 0, 'daily': None}
    
    earnings = random.randint(10, 50)
    economy[user_id]['balance'] = economy[user_id].get('balance', 0) + earnings
    save_economy()
    
    work_phrases = [
        '💻 Ты написал код', '🏭 Ты поработал на заводе', '🧹 Ты убрал в офисе',
        '🎨 Ты сделал дизайн', '📦 Ты продал товар', '📱 Ты разработал приложение',
        '📝 Ты сделал отчёт', '🔧 Ты починил сервер', '📊 Ты сделал презентацию'
    ]
    await ctx.send(f'💼 {random.choice(work_phrases)} и заработал {earnings} монет!')

@bot.command(name='shop')
async def shop(ctx):
    """Показывает магазин ролей"""
    embed = discord.Embed(title='🛒 Магазин ролей', color=0xffd700)
    embed.add_field(name='1️⃣ Роль "Игрок"', value='💰 500 монет', inline=False)
    embed.add_field(name='2️⃣ Роль "Профи"', value='💰 1000 монет', inline=False)
    embed.add_field(name='3️⃣ Роль "Легенда"', value='💰 2500 монет', inline=False)
    embed.set_footer(text='Используйте !buy <номер> для покупки')
    await ctx.send(embed=embed)

@bot.command(name='buy')
async def buy(ctx, item: int):
    """Покупает роль из магазина"""
    user_id = str(ctx.author.id)
    if user_id not in economy:
        economy[user_id] = {'balance': 0, 'daily': None}
    
    roles = {
        1: {'name': 'Игрок', 'cost': 500},
        2: {'name': 'Профи', 'cost': 1000},
        3: {'name': 'Легенда', 'cost': 2500}
    }
    
    if item not in roles:
        await ctx.send('⚠️ Неверный номер. Используй !shop для просмотра.')
        return
    
    role_data = roles[item]
    if economy[user_id]['balance'] < role_data['cost']:
        await ctx.send(f'❌ Недостаточно монет! Нужно: {role_data["cost"]}, у тебя: {economy[user_id]["balance"]}')
        return
    
    role = discord.utils.get(ctx.guild.roles, name=role_data['name'])
    if not role:
        role = await ctx.guild.create_role(name=role_data['name'], color=discord.Color.gold())
    
    if role in ctx.author.roles:
        await ctx.send(f'⚠️ У тебя уже есть роль "{role_data["name"]}"!')
        return
    
    await ctx.author.add_roles(role)
    economy[user_id]['balance'] -= role_data['cost']
    save_economy()
    await ctx.send(f'✅ Ты купил роль "{role_data["name"]}" за {role_data["cost"]} монет!')

# ========== МУЗЫКА ==========

@bot.command(name='join')
async def join(ctx):
    """Бот заходит в голосовой канал"""
    if not ctx.author.voice:
        await ctx.send('❌ Ты не в голосовом канале!')
        return
    channel = ctx.author.voice.channel
    await channel.connect()
    await ctx.send(f'🔊 Бот подключился к {channel.name}')

@bot.command(name='leave')
async def leave(ctx):
    """Бот покидает голосовой канал"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send('🔇 Бот отключился')
    else:
        await ctx.send('❌ Бот не в голосовом канале')

@bot.command(name='play')
async def play(ctx, *, url: str = None):
    """Воспроизводит аудио (только YouTube)"""
    if not ctx.voice_client:
        await ctx.send('❌ Бот не в голосовом канале. Используй !join')
        return
    
    if not url:
        await ctx.send('⚠️ Укажите ссылку на YouTube: !play https://youtube.com/...')
        return
    
    await ctx.send('🎵 Загрузка... (это демо-версия, полная реализация требует ffmpeg)')

# ========== КОМАНДА HELP ==========

@bot.command(name='commands')
async def help_command(ctx, category: str = None):
    """Показывает список всех команд"""
    
    if category:
        categories = {
            'развлечения': ['coin', 'roll', 'guess', 'joke', 'cat', 'dog', '8ball', 'meme', 'rps', 'quote'],
            'администрирование': ['clear', 'kick', 'ban', 'unban', 'mute', 'unmute', 'userinfo', 'serverinfo', 'avatar'],
            'экономика': ['balance', 'daily', 'work', 'shop', 'buy'],
            'музыка': ['join', 'leave', 'play']
        }
        
        if category.lower() not in categories:
            await ctx.send('⚠️ Доступные категории: развлечения, администрирование, экономика, музыка')
            return
        
        cat = category.lower()
        embed = discord.Embed(title=f'📋 Команды: {cat}', color=0x00ff00)
        embed.set_footer(text='Используйте !commands <категория> для подробностей')
        
        if cat == 'развлечения':
            embed.add_field(name='🎮 Развлечения', value='`!coin`, `!roll`, `!guess`, `!joke`, `!cat`, `!dog`, `!8ball`, `!meme`, `!rps`, `!quote`', inline=False)
        elif cat == 'администрирование':
            embed.add_field(name='🔧 Администрирование', value='`!clear`, `!kick`, `!ban`, `!unban`, `!mute`, `!unmute`, `!userinfo`, `!serverinfo`, `!avatar`', inline=False)
        elif cat == 'экономика':
            embed.add_field(name='💰 Экономика', value='`!balance`, `!daily`, `!work`, `!shop`, `!buy`', inline=False)
        elif cat == 'музыка':
            embed.add_field(name='🎵 Музыка', value='`!join`, `!leave`, `!play`', inline=False)
        
        await ctx.send(embed=embed)
        return
    
    # Главное меню помощи
    embed = discord.Embed(
        title='📋 ПОМОЩЬ ПО КОМАНДАМ',
        description='Используйте `!commands <категория>` для подробностей\nНапример: `!commands развлечения`',
        color=0x00ff00
    )
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else '')
    embed.add_field(
        name='🎮 Развлечения (10 команд)',
        value='`!coin`, `!roll`, `!guess`, `!joke`, `!cat`, `!dog`, `!8ball`, `!meme`, `!rps`, `!quote`',
        inline=False
    )
    embed.add_field(
        name='🔧 Администрирование (9 команд)',
        value='`!clear`, `!kick`, `!ban`, `!unban`, `!mute`, `!unmute`, `!userinfo`, `!serverinfo`, `!avatar`',
        inline=False
    )
    embed.add_field(
        name='💰 Экономика (5 команд)',
        value='`!balance`, `!daily`, `!work`, `!shop`, `!buy`',
        inline=False
    )
    embed.add_field(
        name='🎵 Музыка (3 команды)',
        value='`!join`, `!leave`, `!play`',
        inline=False
    )
    embed.add_field(
        name='ℹ️ Общие команды (3 команды)',
        value='`!ping`, `!hello`, `!time`',
        inline=False
    )
    embed.set_footer(text=f'Всего команд: 30 | Бот {bot.user.name}')
    
    await ctx.send(embed=embed)

# ========== ОБРАБОТКА ОШИБОК ==========

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('⛔ У тебя нет прав для этой команды!')
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send('❌ Пользователь не найден.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('⚠️ Не хватает аргументов. Используй `!commands` для справки.')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('⚠️ Неверный аргумент. Проверь команду.')
    else:
        await ctx.send(f'❌ Ошибка: {error}')

# ========== ЗАПУСК ==========

@bot.event
async def on_ready():
    print(f'✅ Бот {bot.user} запущен!')
    print(f'📊 На серверах: {len(bot.guilds)}')
    print(f'🔄 Команды загружены!')
    
    try:
        synced = await bot.tree.sync()
        print(f'✅ Слеш-команд синхронизировано: {len(synced)}')
    except Exception as e:
        print(f'❌ Ошибка синхронизации: {e}')

bot.run(TOKEN)
import discord
from discord.ext import commands
import os

# Токен бота (копируйте из Discord Developer Portal)
TOKEN = 'ВАШ_ТОКЕН_БОТА'  # Вставьте сюда ваш токен

# Создаём бота с префиксом команд '!'
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Событие, когда бот запустился
@bot.event
async def on_ready():
    print(f'✅ Бот {bot.user} подключился к Discord!')
    print(f'📊 На серверах: {len(bot.guilds)}')

# Простая команда !ping
@bot.command()
async def ping(ctx):
    await ctx.send('🏓 Pong!')

# Слеш-команда /hello
@bot.tree.command(name='hello', description='Поздороваться с ботом')
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Привет, {interaction.user.name}!')

# Команда !say (повторяет текст)
@bot.command()
async def say(ctx, *, text):
    await ctx.send(text)

# Запускаем бота
bot.run(TOKEN)

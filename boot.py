import discord
from discord.ext import commands
import random
import asyncio
import datetime
import os
import aiohttp
import aiosqlite

# ========== ТОКЕН ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ==========
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("Токен не найден в переменных окружения!")

PREFIX = os.getenv('PREFIX', '!')

# ========== СОЗДАЁМ БОТА ==========
# Запрашиваем только нужные интенты
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# ========== ГЛОБАЛЬНАЯ СЕССИЯ ==========
bot.session = None
DB_NAME = 'economy.db'

# ========== БАЗА ДАННЫХ (SQLITE) ==========

async def init_db():
    """Создает таблицу при запуске"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0,
                daily TEXT DEFAULT NULL
            )
        ''')
        await db.commit()

async def get_user(user_id: int):
    """Получает данные пользователя или создает нового"""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT balance, daily FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                await db.execute('INSERT INTO users (user_id, balance, daily) VALUES (?, 0, NULL)', (user_id,))
                await db.commit()
                return 0, None
            return row[0], row[1]

async def update_user(user_id: int, balance: int, daily: str = None):
    """Обновляет данные пользователя"""
    async with aiosqlite.connect(DB_NAME) as db:
        if daily is not None:
            await db.execute('UPDATE users SET balance = ?, daily = ? WHERE user_id = ?', (balance, daily, user_id))
        else:
            await db.execute('UPDATE users SET balance = ? WHERE user_id = ?', (balance, user_id))
        await db.commit()

# ========== СОБЫТИЯ ==========

@bot.event
async def on_ready():
    print(f'✅ Бот {bot.user} запущен!')
    print(f'📊 На серверах: {len(bot.guilds)}')
    
    # Инициализация БД и сессии
    await init_db()
    bot.session = aiohttp.ClientSession()
    
    try:
        synced = await bot.tree.sync()
        print(f'✅ Слеш-команд синхронизировано: {len(synced)}')
    except Exception as e:
        print(f'❌ Ошибка синхронизации: {e}')

@bot.event
async def on_disconnect():
    if bot.session:
        await bot.session.close()

# ========== ОБЩИЕ КОМАНДЫ ==========

@bot.command(name='ping')
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! Задержка: {latency} мс')

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'Привет, {ctx.author.mention}! 👋')

@bot.command(name='time')
async def time_command(ctx):
    now = datetime.datetime.now()
    await ctx.send(f'🕐 Время: {now.strftime("%H:%M:%S")}\n📅 Дата: {now.strftime("%d.%m.%Y")}')

# ========== РАЗВЛЕЧЕНИЯ ==========

@bot.command(name='coin')
async def coin(ctx):
    await ctx.send(f'🎯 Результат: {random.choice(["🦅 Орел", "🪙 Решка"])}')

@bot.command(name='roll')
async def roll(ctx, max_num: int = 100):
    if max_num < 1:
        return await ctx.send('⚠️ Число должно быть больше 0.')
    await ctx.send(f'🎲 Случайное число: {random.randint(1, max_num)} (1-{max_num})')

@bot.command(name='joke')
async def joke(ctx):
    jokes = [
        'Почему программисты путают Хеллоуин и Рождество? Потому что 31 Окт = 25 Дек.',
        'Сколько программистов нужно, чтобы заменить лампочку? Ни одного. Это аппаратная проблема.',
        'Админ и программист смотрят на горящий сервер. Админ: "Это не моя проблема." Программист: "Это не моя вина."',
        'Как называется программист, который не любит кофе? Нормальный человек.'
    ]
    await ctx.send(random.choice(jokes))

@bot.command(name='cat')
async def cat(ctx):
    try:
        async with bot.session.get('https://api.thecatapi.com/v1/images/search') as resp:
            data = await resp.json()
            await ctx.send(data[0]['url'])
    except Exception:
        await ctx.send('😺 Котик убежал. Попробуй позже!')

@bot.command(name='dog')
async def dog(ctx):
    try:
        async with bot.session.get('https://dog.ceo/api/breeds/image/random') as resp:
            data = await resp.json()
            await ctx.send(data['message'])
    except Exception:
        await ctx.send('🐶 Собачка убежала. Попробуй позже!')

@bot.command(name='meme')
async def meme(ctx):
    try:
        async with bot.session.get('https://meme-api.com/gimme') as resp:
            data = await resp.json()
            embed = discord.Embed(title=data['title'], color=0x00ff00)
            embed.set_image(url=data['url'])
            embed.set_footer(text=f'👍 {data["ups"]} | 💬 {data["comments"]}')
            await ctx.send(embed=embed)
    except Exception:
        await ctx.send('😅 Мем убежал. Попробуй позже!')

@bot.command(name='rps')
async def rps(ctx, choice: str):
    choices = ['камень', 'ножницы', 'бумага']
    choice = choice.lower()
    if choice not in choices:
        return await ctx.send('⚠️ Выбери: камень, ножницы или бумага')
    
    bot_choice = random.choice(choices)
    if choice == bot_choice:
        result = '🤝 Ничья!'
    elif (choice == 'камень' and bot_choice == 'ножницы') or \
         (choice == 'ножницы' and bot_choice == 'бумага') or \
         (choice == 'бумага' and bot_choice == 'камень'):
        result = '🎉 Ты выиграл!'
    else:
        result = '😔 Бот выиграл!'
    await ctx.send(f'🧑 Твой выбор: {choice}\n🤖 Мой выбор: {bot_choice}\n{result}')

@bot.command(name='8ball')
async def eight_ball(ctx, *, question):
    answers = ['Да', 'Нет', 'Возможно', 'Скорее всего да', 'Скорее всего нет', 
               'Не могу сказать сейчас', 'Определенно да', 'Определенно нет', '50 на 50']
    await ctx.send(f'🎱 Вопрос: {question}\nОтвет: {random.choice(answers)}')

# ========== АДМИНИСТРИРОВАНИЕ ==========

@bot.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if amount < 1 or amount > 100:
        return await ctx.send('⚠️ Укажите число от 1 до 100.')
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f'🗑️ Удалено {len(deleted) - 1} сообщений.')
    await asyncio.sleep(3)
    await msg.delete()

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason='Не указана'):
    if member == ctx.author:
        return await ctx.send('❌ Нельзя кикнуть самого себя!')
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        return await ctx.send('❌ Нельзя кикнуть пользователя с ролью выше или равной вашей.')
    await member.kick(reason=reason)
    await ctx.send(f'👢 {member.mention} кикнут. Причина: {reason}')

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason='Не указана'):
    if member == ctx.author:
        return await ctx.send('❌ Нельзя забанить самого себя!')
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        return await ctx.send('❌ Нельзя забанить пользователя с ролью выше или равной вашей.')
    await member.ban(reason=reason)
    await ctx.send(f'🔨 {member.mention} забанен. Причина: {reason}')

@bot.command(name='unban')
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f'✅ {user.mention} разбанен!')
    except discord.NotFound:
        await ctx.send('❌ Пользователь не найден в списке забаненных.')

@bot.command(name='mute')
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int, *, reason='Не указана'):
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        return await ctx.send('❌ Нельзя замьютить пользователя с ролью выше или равной вашей.')
    
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await ctx.send(f'🔇 {member.mention} замьючен на {minutes} мин. Причина: {reason}')

@bot.command(name='unmute')
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f'🔊 {member.mention} размьючен!')

@bot.command(name='userinfo')
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f'👤 Информация о {member.name}', color=member.color)
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name='🆔 ID', value=member.id, inline=False)
    embed.add_field(name='📝 Имя', value=member.display_name, inline=True)
    embed.add_field(name='📅 Создан', value=member.created_at.strftime('%d.%m.%Y'), inline=True)
    embed.add_field(name='🤖 Бот', value='Да' if member.bot else 'Нет', inline=True)
    await ctx.send(embed=embed)

# ========== ЭКОНОМИКА ==========

@bot.command(name='balance')
async def balance(ctx):
    bal, _ = await get_user(ctx.author.id)
    await ctx.send(f'💰 {ctx.author.mention}, твой баланс: {bal} монет')

@bot.command(name='daily')
async def daily(ctx):
    today = datetime.datetime.now().date().isoformat()
    bal, last_daily = await get_user(ctx.author.id)
    
    if last_daily == today:
        return await ctx.send('⏰ Ты уже получил ежедневный бонус сегодня! Жди завтра.')
    
    bonus = random.randint(50, 200)
    await update_user(ctx.author.id, bal + bonus, today)
    await ctx.send(f'🎁 {ctx.author.mention}, ты получил {bonus} монет!')

@bot.command(name='work')
async def work(ctx):
    bal, _ = await get_user(ctx.author.id)
    earnings = random.randint(10, 50)
    await update_user(ctx.author.id, bal + earnings)
    
    phrases = ['💻 Ты написал код', '🏭 Ты поработал на заводе', '🧹 Ты убрал в офисе', '🎨 Ты сделал дизайн']
    await ctx.send(f'💼 {random.choice(phrases)} и заработал {earnings} монет!')

@bot.command(name='shop')
async def shop(ctx):
    embed = discord.Embed(title='🛒 Магазин ролей', color=0xffd700)
    embed.add_field(name='1️⃣ Роль "Игрок"', value='💰 500 монет', inline=False)
    embed.add_field(name='2️⃣ Роль "Профи"', value='💰 1000 монет', inline=False)
    embed.add_field(name='3️⃣ Роль "Легенда"', value='💰 2500 монет', inline=False)
    embed.set_footer(text='Используйте !buy <номер> для покупки')
    await ctx.send(embed=embed)

@bot.command(name='buy')
async def buy(ctx, item: int):
    roles = {
        1: {'name': 'Игрок', 'cost': 500},
        2: {'name': 'Профи', 'cost': 1000},
        3: {'name': 'Легенда', 'cost': 2500}
    }
    
    if item not in roles:
        return await ctx.send('⚠️ Неверный номер. Используй !shop для просмотра.')
    
    role_data = roles[item]
    bal, _ = await get_user(ctx.author.id)
    
    if bal < role_data['cost']:
        return await ctx.send(f'❌ Недостаточно монет! Нужно: {role_data["cost"]}, у тебя: {bal}')
    
    role = discord.utils.get(ctx.guild.roles, name=role_data['name'])
    if not role:
        role = await ctx.guild.create_role(name=role_data['name'], color=discord.Color.gold())
    
    if role in ctx.author.roles:
        return await ctx.send(f'⚠️ У тебя уже есть роль "{role_data["name"]}"!')
    
    await ctx.author.add_roles(role)
    await update_user(ctx.author.id, bal - role_data['cost'])
    await ctx.send(f'✅ Ты купил роль "{role_data["name"]}" за {role_data["cost"]} монет!')

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
if __name__ == '__main__':
    bot.run(TOKEN)

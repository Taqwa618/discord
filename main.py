"""
Discord-бот: общие команды, модерация, развлечения и экономика.

Запуск:
  локально:   python main.py   (токен — в файле .env рядом с main.py)
  на хостинге (BotHost и подобные): переменные окружения задаются в панели,
              файл .env не нужен.

ВАЖНО: в Discord Developer Portal (приложение -> Bot) должны быть включены
два привилегированных интента:
    SERVER MEMBERS INTENT  и  MESSAGE CONTENT INTENT
Иначе бот не запустится с ошибкой PrivilegedIntentsRequired.
"""

import asyncio
import datetime
import os
import random
import traceback

import aiohttp
import aiosqlite
import discord
from discord.ext import commands
from dotenv import load_dotenv

# ================== ТОКЕН И НАСТРОЙКИ ==================
# load_dotenv подхватит файл .env, если он есть (удобно для локального запуска).
# На хостинге переменные окружения задаются в панели, .env не требуется.
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")
if not TOKEN:
    raise SystemExit(
        "Токен не найден!\n"
        "1) На хостинге: задайте переменную окружения DISCORD_TOKEN в панели.\n"
        "2) Локально: создайте файл .env со строкой DISCORD_TOKEN=ваш_токен"
    )

PREFIX = os.getenv("PREFIX", "!")                 # префикс команд
DB_NAME = os.getenv("DB_NAME", "economy.db")      # файл базы SQLite


# ================== БАЗА ДАННЫХ (SQLITE) ==================
async def init_db():
    """Создает таблицу пользователей, если её нет."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0,
                daily   TEXT DEFAULT NULL
            )
            """
        )
        await db.commit()


async def get_user(user_id: int):
    """Возвращает (баланс, дата последнего daily). Создает пользователя, если нет."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT balance, daily FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                await db.execute(
                    "INSERT INTO users (user_id, balance, daily) VALUES (?, 0, NULL)",
                    (user_id,),
                )
                await db.commit()
                return 0, None
            return row[0], row[1]


async def update_user(user_id: int, balance: int, daily: str | None = "keep"):
    """Обновляет баланс (и дату daily, если передана, а не 'keep')."""
    async with aiosqlite.connect(DB_NAME) as db:
        if daily != "keep":
            await db.execute(
                "UPDATE users SET balance = ?, daily = ? WHERE user_id = ?",
                (balance, daily, user_id),
            )
        else:
            await db.execute(
                "UPDATE users SET balance = ? WHERE user_id = ?", (balance, user_id)
            )
        await db.commit()


# ================== БОТ ==================
intents = discord.Intents.default()
intents.message_content = True   # чтение текста команд
intents.members = True           # данные участников (!userinfo, модерация)


class EconomyBot(commands.Bot):
    """commands.Bot с aiohttp-сессией для запросов к сторонним API.

    Сессия создается один раз в setup_hook (до подключения) и закрывается
    в close() — так она не «умирает» при переподключениях.
    """

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(PREFIX),
            intents=intents,
        )
        self.session: aiohttp.ClientSession | None = None

    async def setup_hook(self):
        # Выполняется один раз при старте, до события on_ready
        await init_db()
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": "DiscordBot (economy, 1.0)"}
        )

    async def close(self):
        # Корректно освобождаем ресурсы при остановке бота
        if self.session and not self.session.closed:
            await self.session.close()
        await super().close()


bot = EconomyBot()


# ================== СОБЫТИЯ ==================
@bot.event
async def on_ready():
    print(f"✅ Бот {bot.user} запущен!")
    print(f"📊 На серверах: {len(bot.guilds)}")
    await bot.change_presence(
        activity=discord.Game(name=f"{PREFIX}commands — список команд")
    )


# ================== СПРАВКА ==================
@bot.command(name="commands")
async def commands_list(ctx):
    """Список всех команд бота."""
    embed = discord.Embed(title="📖 Список команд", color=0x3498db)
    embed.add_field(
        name="🔧 Общие",
        value=f"`{PREFIX}ping`, `{PREFIX}hello`, `{PREFIX}time`",
        inline=False,
    )
    embed.add_field(
        name="🎲 Развлечения",
        value=(
            f"`{PREFIX}coin`, `{PREFIX}roll [макс]`, `{PREFIX}joke`, "
            f"`{PREFIX}cat`, `{PREFIX}dog`, `{PREFIX}meme`, "
            f"`{PREFIX}rps <камень|ножницы|бумага>`, `{PREFIX}8ball <вопрос>`"
        ),
        inline=False,
    )
    embed.add_field(
        name="🛠 Модерация",
        value=(
            f"`{PREFIX}clear <1-100>`, `{PREFIX}kick <участник> [причина]`, "
            f"`{PREFIX}ban <участник> [причина]`, `{PREFIX}unban <ID>`, "
            f"`{PREFIX}mute <участник> <минуты> [причина]`, `{PREFIX}unmute <участник>`"
        ),
        inline=False,
    )
    embed.add_field(
        name="👤 Информация",
        value=f"`{PREFIX}userinfo [@участник]`",
        inline=False,
    )
    embed.add_field(
        name="💰 Экономика",
        value=(
            f"`{PREFIX}balance`, `{PREFIX}daily`, `{PREFIX}work`, "
            f"`{PREFIX}shop`, `{PREFIX}buy <номер>`"
        ),
        inline=False,
    )
    await ctx.send(embed=embed)


# ================== ОБЩИЕ КОМАНДЫ ==================
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Задержка: {round(bot.latency * 1000)} мс")


@bot.command(name="hello")
async def hello(ctx):
    await ctx.send(f"Привет, {ctx.author.mention}! 👋")


@bot.command(name="time")
async def time_command(ctx):
    now = datetime.datetime.now()
    await ctx.send(
        f"🕐 Время: {now.strftime('%H:%M:%S')}\n📅 Дата: {now.strftime('%d.%m.%Y')}"
    )


# ================== РАЗВЛЕЧЕНИЯ ==================
@bot.command(name="coin")
async def coin(ctx):
    await ctx.send(f"🎯 Результат: {random.choice(['🦅 Орел', '🪙 Решка'])}")


@bot.command(name="roll")
async def roll(ctx, max_num: int = 100):
    if max_num < 1:
        return await ctx.send("⚠️ Число должно быть больше 0.")
    await ctx.send(f"🎲 Случайное число: {random.randint(1, max_num)} (1-{max_num})")


@bot.command(name="joke")
async def joke(ctx):
    jokes = [
        "Почему программисты путают Хеллоуин и Рождество? Потому что 31 Окт = 25 Дек.",
        "Сколько программистов нужно, чтобы заменить лампочку? Ни одного. Это аппаратная проблема.",
        "Админ и программист смотрят на горящий сервер. Админ: «Это не моя проблема». Программист: «Это не моя вина».",
        "Как называется программист, который не любит кофе? Нормальный человек.",
    ]
    await ctx.send(random.choice(jokes))


@bot.command(name="cat")
async def cat(ctx):
    try:
        async with bot.session.get(
            "https://api.thecatapi.com/v1/images/search"
        ) as resp:
            data = await resp.json()
        await ctx.send(data[0]["url"])
    except Exception:
        await ctx.send("😺 Котик убежал. Попробуй позже!")


@bot.command(name="dog")
async def dog(ctx):
    try:
        async with bot.session.get("https://dog.ceo/api/breeds/image/random") as resp:
            data = await resp.json()
        await ctx.send(data["message"])
    except Exception:
        await ctx.send("🐶 Собачка убежала. Попробуй позже!")


@bot.command(name="meme")
async def meme(ctx):
    try:
        async with bot.session.get("https://meme-api.com/gimme") as resp:
            data = await resp.json()
        embed = discord.Embed(title=data.get("title", "Мем"), color=0x00FF00)
        embed.set_image(url=data["url"])
        embed.set_footer(
            text=f"👍 {data.get('ups', '?')} | 💬 {data.get('comments', '?')}"
        )
        await ctx.send(embed=embed)
    except Exception:
        await ctx.send("😅 Мем убежал. Попробуй позже!")


@bot.command(name="rps")
async def rps(ctx, choice: str):
    choices = ["камень", "ножницы", "бумага"]
    choice = choice.strip().lower()
    if choice not in choices:
        return await ctx.send("⚠️ Выбери: камень, ножницы или бумага")

    bot_choice = random.choice(choices)
    if choice == bot_choice:
        result = "🤝 Ничья!"
    elif (
        (choice == "камень" and bot_choice == "ножницы")
        or (choice == "ножницы" and bot_choice == "бумага")
        or (choice == "бумага" and bot_choice == "камень")
    ):
        result = "🎉 Ты выиграл!"
    else:
        result = "😔 Бот выиграл!"

    await ctx.send(
        f"🧑 Твой выбор: {choice}\n🤖 Мой выбор: {bot_choice}\n{result}"
    )


@bot.command(name="8ball")
async def eight_ball(ctx, *, question):
    answers = [
        "Да", "Нет", "Возможно", "Скорее всего да", "Скорее всего нет",
        "Не могу сказать сейчас", "Определенно да", "Определенно нет", "50 на 50",
    ]
    await ctx.send(f"🎱 Вопрос: {question}\nОтвет: {random.choice(answers)}")


# ================== МОДЕРАЦИЯ ==================
async def _check_target_role(ctx, member: discord.Member) -> bool:
    """Проверяет, что можно модерировать участника. False — если нет прав или это себя."""
    if member == ctx.author:
        await ctx.send("❌ Нельзя применить это к самому себе!")
        return False
    if (
        member.top_role >= ctx.author.top_role
        and ctx.author != ctx.guild.owner
        and ctx.author != member
    ):
        await ctx.send("❌ У пользователя роль выше или равная вашей.")
        return False
    return True


@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if amount < 1 or amount > 100:
        return await ctx.send("⚠️ Укажите число от 1 до 100.")
    deleted = await ctx.channel.purge(limit=amount + 1)  # +1 — команда !clear
    msg = await ctx.send(f"🗑️ Удалено {len(deleted) - 1} сообщений.")
    await asyncio.sleep(3)
    await msg.delete()


@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = "Не указана"):
    if not await _check_target_role(ctx, member):
        return
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member.mention} кикнут. Причина: {reason}")


@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = "Не указана"):
    if not await _check_target_role(ctx, member):
        return
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member.mention} забанен. Причина: {reason}")


@bot.command(name="unban")
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"✅ {user.mention} разбанен!")
    except discord.NotFound:
        await ctx.send("❌ Пользователь с таким ID не найден (или он не в бане).")
    except discord.Forbidden:
        await ctx.send("❌ У меня нет прав на разбан (проверьте права бота).")


@bot.command(name="mute")
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int, *, reason: str = "Не указана"):
    if not await _check_target_role(ctx, member):
        return
    if minutes < 1 or minutes > 40320:  # максимум 28 дней (лимит Discord)
        return await ctx.send("⚠️ Укажите срок от 1 минуты до 40320 (28 дней).")
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await ctx.send(f"🔇 {member.mention} замьючен на {minutes} мин. Причина: {reason}")


@bot.command(name="unmute")
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    await member.timeout(None)
    await ctx.send(f"🔊 {member.mention} размьючен!")


@bot.command(name="userinfo")
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(
        title=f"👤 Информация о {member.display_name}", color=member.color
    )
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="🆔 ID", value=str(member.id), inline=False)
    embed.add_field(name="📝 Имя", value=member.name, inline=True)
    embed.add_field(
        name="📅 Аккаунт создан",
        value=member.created_at.strftime("%d.%m.%Y"),
        inline=True,
    )
    embed.add_field(
        name="📥 На сервере с",
        value=member.joined_at.strftime("%d.%m.%Y") if member.joined_at else "—",
        inline=True,
    )
    embed.add_field(name="🤖 Бот", value="Да" if member.bot else "Нет", inline=True)
    await ctx.send(embed=embed)


# ================== ЭКОНОМИКА ==================
@bot.command(name="balance")
async def balance(ctx):
    bal, _ = await get_user(ctx.author.id)
    await ctx.send(f"💰 {ctx.author.mention}, твой баланс: {bal} монет")


@bot.command(name="daily")
async def daily(ctx):
    today = datetime.datetime.now().date().isoformat()
    bal, last_daily = await get_user(ctx.author.id)
    if last_daily == today:
        return await ctx.send("⏰ Ты уже получил ежедневный бонус сегодня! Жди завтра.")
    bonus = random.randint(50, 200)
    await update_user(ctx.author.id, bal + bonus, daily=today)
    await ctx.send(f"🎁 {ctx.author.mention}, ты получил {bonus} монет!")


@bot.command(name="work")
async def work(ctx):
    bal, _ = await get_user(ctx.author.id)
    earnings = random.randint(10, 50)
    phrases = [
        "💻 Ты написал код",
        "🏭 Ты поработал на заводе",
        "🧹 Ты убрал в офисе",
        "🎨 Ты сделал дизайн",
    ]
    await update_user(ctx.author.id, bal + earnings)
    await ctx.send(f"💼 {random.choice(phrases)} и заработал {earnings} монет!")


SHOP_ROLES = {
    1: {"name": "Игрок", "cost": 500},
    2: {"name": "Профи", "cost": 1000},
    3: {"name": "Легенда", "cost": 2500},
}


@bot.command(name="shop")
async def shop(ctx):
    embed = discord.Embed(title="🛒 Магазин ролей", color=0xFFD700)
    for num, data in SHOP_ROLES.items():
        embed.add_field(
            name=f"{num}️⃣ Роль «{data['name']}»",
            value=f"💰 {data['cost']} монет",
            inline=False,
        )
    embed.set_footer(text=f"Используйте {PREFIX}buy <номер> для покупки")
    await ctx.send(embed=embed)


@bot.command(name="buy")
async def buy(ctx, item: int):
    if item not in SHOP_ROLES:
        return await ctx.send(f"⚠️ Неверный номер. Используй {PREFIX}shop для просмотра.")

    role_data = SHOP_ROLES[item]
    bal, _ = await get_user(ctx.author.id)
    if bal < role_data["cost"]:
        return await ctx.send(
            f"❌ Недостаточно монет! Нужно: {role_data['cost']}, у тебя: {bal}"
        )

    role = discord.utils.get(ctx.guild.roles, name=role_data["name"])
    if role is None:
        try:
            role = await ctx.guild.create_role(
                name=role_data["name"], color=discord.Color.gold()
            )
        except discord.Forbidden:
            return await ctx.send(
                "❌ У меня нет права создавать роли (Manage Roles). Обратись к админу."
            )

    if role in ctx.author.roles:
        return await ctx.send(f"⚠️ У тебя уже есть роль «{role_data['name']}»!")

    # Сначала выдаем роль, потом списываем монеты:
    # если выдача не удалась, деньги не теряются
    try:
        await ctx.author.add_roles(role)
    except discord.Forbidden:
        return await ctx.send("❌ Не удалось выдать роль — нет права Manage Roles.")
    await update_user(ctx.author.id, bal - role_data["cost"])
    await ctx.send(
        f"✅ Ты купил роль «{role_data['name']}» за {role_data['cost']} монет!"
    )


# ================== ОБРАБОТКА ОШИБОК ==================
@bot.event
async def on_command_error(ctx, error):
    # Неизвестную команду молча игнорируем (раньше вызывало ошибку в чат)
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("⛔ У тебя нет прав для этой команды!")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("🤖 У меня не хватает прав. Проверьте права бота на сервере.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Пользователь не найден.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"⚠️ Не хватает аргументов. Используй `{PREFIX}commands`.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("⚠️ Неверный аргумент. Проверь команду.")
    else:
        # Полный текст ошибки — в консоль (логи хостинга), в чат — краткое сообщение
        traceback.print_exception(type(error), error, error.__traceback__)
        await ctx.send("❌ Произошла ошибка. Подробности — в логах.")


# ================== ГОЛОСОВЫЕ КАНАЛЫ ==================
@bot.command(name="join")
async def join(ctx):
    """Заставляет бота зайти в ваш голосовой канал."""
    if ctx.author.voice is None:
        return await ctx.send("❌ Вы не находитесь в голосовом канале.")
    
    channel = ctx.author.voice.channel
    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(channel)
    
    try:
        await channel.connect()
        await ctx.send(f"🔊 Бот подключился к каналу {channel.mention}")
    except Exception as e:
        await ctx.send(f"❌ Ошибка подключения: {e}")

@bot.command(name="leave")
async def leave(ctx):
    """Заставляет бота выйти из голосового канала."""
    if ctx.voice_client is None:
        return await ctx.send("❌ Бот не находится в голосовом канале.")
    
    await ctx.voice_client.disconnect()
    await ctx.send("🔇 Бот отключился от канала.")

# ================== ЗАПУСК ==================
if __name__ == "__main__":
    bot.run(TOKEN)Ы

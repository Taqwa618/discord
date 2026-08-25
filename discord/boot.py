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

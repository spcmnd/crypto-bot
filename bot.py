import os
import discord
import json
import locale
from discord.ext import commands
from dotenv import load_dotenv
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

locale.setlocale(locale.LC_ALL, 'en_US.utf8')

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CMC_TOKEN = os.getenv('COINMARKETCAP_API_KEY')

def get_token_price(name):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
        'symbol': name,
        'convert':'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': CMC_TOKEN,
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        token_data = data['data'][name]
        quote = token_data['quote']['USD']

        return quote
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
        raise

class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """A global error handler cog."""

        if isinstance(error, commands.CommandNotFound):
            message = "This command doesn't exist."
        elif isinstance(error, commands.CommandOnCooldown):
            message = f"This command is on cooldown. Please try again after {round(error.retry_after, 1)} seconds."
        elif isinstance(error, commands.MissingPermissions):
            message = "You are missing the required permissions to run this command!"
        elif isinstance(error, commands.UserInputError):
            message = "Something about your input was wrong, please check your input and try again!"
        else:
            message = "Oh no! Something went wrong while running the command!"

        await ctx.send(message, delete_after=5)
        await ctx.message.delete(delay=5)

client = commands.Bot(command_prefix='!')
client.add_cog(ErrorHandler(client))

@client.command()
async def price(ctx, arg):
    crypto_name = arg.upper()
    try:
        quote = get_token_price(crypto_name)
        await ctx.send(f'{crypto_name} price is currently: {locale.format_string("%d", round(quote["price"], 2), grouping=True)}$')
    except:
        await ctx.send(f'{crypto_name} is not a valid crypto symbol.')

@client.command()
async def marketcap(ctx, arg):
    crypto_name = arg.upper()
    try:
        quote = get_token_price(crypto_name)
        await ctx.send(f'{crypto_name} market cap is currently: {locale.format_string("%d", round(quote["market_cap"], 2), grouping=True)}$')
    except:
        await ctx.send(f'{crypto_name} is not a valid crypto symbol.')

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    
    print(f'{client.user} has connected to the following guild:')
    print(f'{guild.name}(id: {guild.id})')

client.run(TOKEN)

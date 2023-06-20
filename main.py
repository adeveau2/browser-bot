# Welcome to the Poe API tutorial. The starter code provided provides you with a quick way to get
# a bot running. By default, the starter code uses the EchoBot, which is a simple bot that echos
# a message back at its user and is a good starting point for your bot, but you can
# comment/uncomment any of the following code to try out other example bots.

from fastapi_poe import make_app
from summary_bot import SummaryBot

POE_API_KEY = "3GBl5hutNyJBDZqEwWNMovTJMKGO6ht9"

bot = SummaryBot()
app = make_app(bot, api_key=POE_API_KEY)

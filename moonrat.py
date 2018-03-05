import os 
import time
import re
import configparser
import threading
import requests
import json
from pprint import pprint
from slackclient import SlackClient

#instantiate Slack Client
config = configparser.ConfigParser()
config.read('config.ini')
SLACK_BOT_TOKEN = config['Slack_Token']['SLACK_BOT_TOKEN']
slack_client = SlackClient(SLACK_BOT_TOKEN)
# starterbot's user ID in Slack: value is assigned after the bot starts up
moonrat_id = None

#constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
name_id_map = {}
symbol_id_map = {}


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands. 
        If a bot command is found, this functions returns a tuple of command and channel. 
        If its not found, then this function returns None, None. 
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == moonrat_id or message != None:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    string = message_text.split()
    if '!price' == string[0]:
        return (None, string[1])
    elif '!top' == string[0]:
        return (None, string[0])
    else:
        matches = re.search(MENTION_REGEX,message_text)
        #the first group contains the username, the second group contains the maining message
        return (matches.group(1), matches.group(2).strip()) if matches else (None, None) 


def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    #Default respons is help text for the user
    default_response = "This don't exist m8. Try *{}*.".format("!price trx")
    #Finds and executes the given command, filling in response
    response = None
    pretext = None
    #This is where you start to implement more commands
    #if command.startswith(EXAMPLE_COMMAND):
     #   response = "Sure M8, buzz off and do some more work."
    
    if command.lower() in name_id_map:
        req = requests.get(url = 'https://api.coinmarketcap.com/v1/ticker/' + name_id_map[command.lower()] + '/')
        coin = req.json()
        text =format_coin_output(coin[0])
    elif command.lower() in symbol_id_map:
        req = requests.get(url = 'https://api.coinmarketcap.com/v1/ticker/' + symbol_id_map[command.lower()] + '/')
        coin = req.json()
        text = format_coin_output(coin[0])
    elif command == '!top':
        text = top_coins()
    #sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=text,
    )

def top_coins():
    output = ""
    req = requests.get(url = 'https://api.coinmarketcap.com/v1/ticker/?limit=10')
    top10_coins = req.json()
    for coins in top10_coins:
        output += "*{:16}* ${:.2f}\n".format(coins['name'],float(coins['price_usd']))
    return output

def format_coin_output(coin):
    coin_output1 = "Grabbing latest data for *" + coin['name'] + "*\n"
    coin_output2 = "{:20s}\t${:.2f}\n".format("*Price USD*",float(coin['price_usd']))
    coin_output3 = "{:20s}\t{:.8f}\n".format("*Price BTC*",float(coin['price_btc']))
    coin_output4 = "{:20s}\t${:.2f}\n".format("*Market Cap*",float(coin['market_cap_usd']))
    coin_output5 = "{:20s}\t{:.2f}%\n".format("*Change 1hr*",float(coin['percent_change_1h']))
    coin_output6 = "{:20s}\t{:.2f}%\n".format("*Change 24hr*",float(coin['percent_change_24h']))
    coin_output7 = "{:20s}\t{:.2f}%\n".format("*Change 7d*",float(coin['percent_change_7d']))


    return (coin_output1+coin_output2+coin_output3+coin_output4+coin_output5+coin_output6+coin_output7)


def make_crypto_db():
    """
        Creates the database mapping's needed and updates the database every few hours.
    """
    threading.Timer(3600.0, make_crypto_db).start()
    req = requests.get(url = 'https://api.coinmarketcap.com/v1/ticker/?limit=0')
    all_coins = req.json()
    for coins in all_coins:
        name_id_map[coins['name'].lower()] = coins['id']
        symbol_id_map[coins['symbol'].lower()] = coins['id']


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print ("moonrat is connected and running.")
        #Read bot's user ID by calling Web API method 'auth.test'
        moonrat_id = slack_client.api_call("auth.test")["user_id"]
        make_crypto_db()
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print ("Connection failed. Exception traceback printed above.")
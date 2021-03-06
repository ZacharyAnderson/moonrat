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
WEBHOOK_URL = config['Slack_Token']['WEBHOOK_URL']
slack_client = SlackClient(SLACK_BOT_TOKEN)
moonrat_id = None

#constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM

#Global Variables
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
            user_id, message = parse_crypto_calls(event["text"])
            if user_id == moonrat_id or message != None:
                return message, event["channel"]
    return None, None

def parse_crypto_calls(message_text):
    """
        Finds strings that start with specific call's and will output 
    """
    string = message_text.split()
    if '!price' == string[0]:
        try:
            return (None, string[1])
        except IndexError:
            return (None, None)
    elif '!top' == string[0]:
        return (None, string[0])
    elif '!exit' == string[0]:
        return (None, string[0])
    elif '!ping' == string[0]:
        return (None, string[0])
    else:
        #the first group contains the username, the second group contains the maining message
        return (None, None) 


def handle_command(command, channel):
    """
        Executes bot command if the command is known.
        Commands for !price __coin__, !top, !exit, and default message.
    """
    #Default respons is help text for the user
    default_response = "This don't exist m8. Try *{}*.".format("!price trx")
    #Finds and executes the given command, filling in response
    response = None
    
    if command.lower() in name_id_map:
        req = requests.get(url = 'https://api.coinmarketcap.com/v1/ticker/' + name_id_map[command.lower()] + '/')
        coin = req.json()
        text =format_coin_output(coin[0])
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=text,
        )
    elif command.lower() in symbol_id_map:
        req = requests.get(url = 'https://api.coinmarketcap.com/v1/ticker/' + symbol_id_map[command.lower()] + '/')
        coin = req.json()
        text = format_coin_output(coin[0])
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=text,
        )
    elif command == '!top':
        text = top_coins()
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=text,
        )
    elif command == '!exit':
        text = ":wasssap3::wasssap3:ABANDON SHIP!!!:wasssap3::wasssap3:\n :rotating_light:EXIT ALL MARKETS:rotating_light:\n"
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=text,
        )
    elif command == '!ping':
        text = "Still scavaging the moon.\n"
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=text,
        )
    else:
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=default_response,
        )

def top_coins():
    """
        Top coins function formulates the top 10 coins
        and forms a string to be called through the slack api.
    """
    output = ""
    req = requests.get(url = 'https://api.coinmarketcap.com/v1/ticker/?limit=10')
    top10_coins = req.json()
    counter = 1
    output = "The top 10 cryptocurrencies are as follows:\n"
    output += "```{:25}{:<10}{:>20} %\n".format("Currency Name","Price in $","24h Change Rate")
    for coins in top10_coins:
        str_count = 32 - len(coins['name'])
        output += "{:2}. {:20}{:>10.2f}{:>20}%\n".format(counter,coins['name'],float(coins['price_usd']),coins['percent_change_24h'])
        counter += 1
    return (output + "```")

def format_coin_output(coin):
    """
        format_coint_output gets the coin information for the specified coin
        and forms a string that will be called into the slack api.
    """
    coin_output1 = "Grabbing latest data for *" + coin['name'] + "*\n"
    coin_output2 = "```{:20s}\t${:.2f}\n".format("Price USD",float(coin['price_usd']))
    coin_output3 = "{:20s}\t{:.8f}\n".format("Price BTC",float(coin['price_btc']))
    coin_output4 = "{:20s}\t${:.2f}\n".format("Market Cap",float(coin['market_cap_usd']))
    coin_output5 = "{:20s}\t{:.2f}%\n".format("Change 1hr",float(coin['percent_change_1h']))
    coin_output6 = "{:20s}\t{:.2f}%\n".format("Change 24hr",float(coin['percent_change_24h']))
    coin_output7 = "{:20s}\t{:.2f}%\n```".format("Change 7d",float(coin['percent_change_7d']))
    return (coin_output1+coin_output2+coin_output3+coin_output4+coin_output5+coin_output6+coin_output7)


def make_crypto_db():
    """
        Creates the database mapping's needed and updates the database every few hours.
    """
    threading.Timer(3600, make_crypto_db).start()
    req = requests.get(url = 'https://api.coinmarketcap.com/v1/ticker/?limit=0')
    all_coins = req.json()
    for coins in all_coins:
        name_id_map[coins['name'].lower()] = coins['id']
        symbol_id_map[coins['symbol'].lower()] = coins['id']

def ping_moonrat():
    """
        This function will be used to ping the moonrat app, so that
        it will not go inactive and get kicked from the session.
    """
    threading.Timer(3600, ping_moonrat).start()
    text = "Moonrat is still active\n"
    slack_client.api_call(
        "chat.postMessage",
        channel='G9P7X8Q0H',
        text=text,
        )


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print ("moonrat is connected and running.")
        #Read bot's user ID by calling Web API method 'auth.test'
        moonrat_id = slack_client.api_call("auth.test")["user_id"]
        make_crypto_db()
        ping_moonrat()
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print ("Connection failed. Exception traceback printed above.")
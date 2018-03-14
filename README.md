# moonrat
A Slackbot that outputs cryptocurrency information. 
Moonrat pulls information from the coinmarketcap api and stores it locally in a database.
The application then connects to the slack api using python library slackclient, and listens to conversations in real time.
Responding to `!price "coin name or ticker"`, `!top`, `!ping`, and `!exit`




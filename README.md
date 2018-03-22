# moonrat
A Slackbot that outputs cryptocurrency information. 
Moonrat pulls information from the coinmarketcap api and stores it locally in a database.
The application then connects to the slack api using python library slackclient, and listens to conversations in real time.
Responding to `!price "coin name or ticker"`, `!top`, `!ping`, and `!exit`



# Examples
Example using `!price btc`

![Alt Text](https://media.giphy.com/media/3d9rnowLkQUU7fTqbw/giphy.gif)

Example using `!top`

![Alt Text](https://media.giphy.com/media/1APapOCVJquc1out3l/giphy.gif)

Example using `!exit`

![Alt Text](https://media.giphy.com/media/9JvaTi42uZdIcMQ71L/giphy.gif)

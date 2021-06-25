# FiveM Discord API
 
Basic discord.py bot to cache all roles that are selected in config of every user for use on FiveM.

# How to setup the Discord bot
## Prerequisites
- A Discord account
- Python
- A Discord guild (server) that you have administrative access on

## Step 1 - register your bot
- go to https://discord.com/developers/applications
- login/make a Discord account
- create an application (press "New Application" button)
- enter name of bot (it's shown to everyone, choose wisely)
- open bot tab on left, then press "Add Bot"

## Step 2 - add bot to your server
- copy your bot's client ID into this string and go to it in your web browser - you can get your client ID from the bot's "General Information" tab (https://discord.com/oauth2/authorize?client_id=CLIENTIDGOESHERE&scope=bot)

## Step 3 - configure the bot
- enable Developer Mode in Discord (https://www.discordtips.com/how-to-enable-developer-mode-in-discord/)
- configure `WEBSERVER_IP`, `WEBSERVER_PORT`, `WEBSERVER_ROUTE` and `WEBSERVER_API_KEY` to your liking, in most cases you can leave the default values apart from APIKEY
- copy the ID of the server into `SERVERID`
- put all of the roles that you want to be synced in the array `ROLES_TO_SYNC` by right clicking the role and copying the id

## Step 4 - setup Python
- make sure you have Python3 installed. If you're on Windows 10, you can find it on the Windows Store, if not download it from their website (https://www.python.org/)
- install the required libraries - `pip install -r requirements.txt` or `pip3 install -r requirements.txt`
- Run the bot: `cd discordClient` and then `python bot.py` or `python3 bot.py`

## Accessing API 

- all requests will be made to `WEBSERVER_IP`:`WEBSERVER_PORT` `WEBSERVER_ROUTE` which by default is: `0.0.0.0:8080/api/v1/getroles`
- if `WEBSERVER_API_KEY` is set be sure to include it in the request body

### Example Request
GET http://127.0.0.1:8080/api/v1/getroles
body:
{
    "api_key": "youcantseeme",
    "userID": 273869926559776778
}

## NOTES
- all links in this document are accurate as of date of last update.
- feel free to pr anything if you think it could do with being improved
- I accept no liability for any results of using this script, be it security or physical.

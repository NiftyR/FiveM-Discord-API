WEBSERVER_IP = "0.0.0.0"
WEBSERVER_PORT = 8080
WEBSERVER_ROUTE = "/api/v1/getroles"
WEBSERVER_API_KEY = "youcantseeme" # Set to false if you don't want to use one
BOT_KEY = ""
SERVERID = 793958539398873108
ROLES_TO_SYNC = [
    {"ROLEID": 796752962386133014, "ENABLED": True, "NAME": ""}, # Name isn't required it's just to make it easier to find each role when changing the config
    {"ROLEID": 793958758416908289, "ENABLED": True, "NAME": ""}
]
try:
    import discord, logging, sqlite3, json
    from aiohttp import web
except ImportError as moduleError:
    print(f"ERROR: Failed to import {moduleError.name}, Check it is installed")
    exit()
logging.basicConfig(level=logging.INFO) # Change INFO to DEBUG if you want to debug stuff
log = logging.getLogger("FiveMDiscordClient")
class FiveMBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = web.Application()
        self.app.add_routes([web.get(WEBSERVER_ROUTE, self.getUserRole)])
        self.runner = web.AppRunner(self.app)
        self.loop.create_task(self.startServer())
        self.db = sqlite3.connect('discordData.db')
        self.cursor = self.db.cursor()
    def diff(self, before, after):
        return list(set(before).symmetric_difference(set(after)))
    async def startServer(self):
        try:
            await self.wait_until_ready()
            await self.runner.setup()
            site = web.TCPSite(self.runner, WEBSERVER_IP, WEBSERVER_PORT)
            await site.start()
        except Exception as e:
            log.error(f"startServer: {e}")
    async def getUserRole(self, request):
        requestData = await request.json()
        if(WEBSERVER_API_KEY):
            apiKey = requestData['api_key']
            if(apiKey != WEBSERVER_API_KEY):
                return web.Response(status=403, text="Forbidden")
        if(requestData['userID']):
            self.cursor.execute(f"SELECT Roles FROM discordUsers WHERE userID={requestData['userID']}")
            allData = self.cursor.fetchall()
            if(len(allData) > 0):
                roleList = []
                for _role in allData[0][0].strip('"').split(","):
                    if(_role):
                        roleList.append(int(_role))
                respData = {
                    "roles": roleList
                }
                return web.Response(text=json.dumps(respData), status=200)
            return web.Response(status=418, text="I'm a teapot")
        else:
            return web.Response(status=400, text="Bad Request")
    async def on_ready(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS discordUsers(userID INTEGER PRIMARY KEY, Roles TEXT)")
        self.db.commit()
        self.OwnerInfo = await self.application_info()
        log.info(f"Connected as: {self.user}!")
        log.info(f"{self.OwnerInfo.owner} Will be assumed as Admin")
    async def on_message(self, message):
        if(message.author.id == self.OwnerInfo.owner.id):
            if(message.content.startswith("!sync")): # To sync roles that arent already in the DB
                log.info("This may take a while depending on the size of the server...")
                guild = self.get_guild(SERVERID)
                log.debug(f"Selected {guild.name}")
                for member in guild.members:
                    roleList = []
                    for role in member.roles:
                        roleList.append(int(role.id))
                    self.cursor.execute(f"SELECT Roles FROM discordUsers WHERE userID={member.id}")
                    allData = self.cursor.fetchall()
                    if((len(allData)) > 0):
                        sqlRoleList = []
                        for _role in allData[0][0].strip('"').split(","):
                            if(_role):
                                sqlRoleList.append(int(_role))
                                log.debug(f"Role: {_role}")
                                log.debug(f"SQLROLELIST: {sqlRoleList}")
                        for role in roleList:
                            if(role in sqlRoleList):
                                pass
                            else:
                                for _role in ROLES_TO_SYNC:
                                    if(_role["ENABLED"] == True):
                                        if(role == _role["ROLEID"]):
                                            sqlRoleList.append(int(role))
                        log.debug(sqlRoleList)
                        if(len(sqlRoleList) > 0):
                            self.cursor.execute(f"""UPDATE discordUsers SET Roles="{str(sqlRoleList).strip('[').strip(']')}" WHERE userID={member.id}""") # There is 100% a better way to do this but ah well :)
                            self.db.commit()
                            log.info(f"Updated {member}'s Roles")
                    else:
                        sqlRoleList = []
                        for role in roleList:
                            if(role in sqlRoleList):
                                pass
                            else:
                                for _role in ROLES_TO_SYNC:
                                    if(_role["ENABLED"] == True):
                                        if(role == _role["ROLEID"]):
                                            sqlRoleList.append(role)
                        if(len(sqlRoleList) == 0):
                            pass
                        self.cursor.execute(f"""INSERT INTO discordUsers(userID, Roles) VALUES({member.id}, "{str(sqlRoleList).strip('[').strip(']')}") """)
                        self.db.commit()
                        log.info(f"Added {member}'s Roles")
                log.info(f"Finished syncing roles from: {guild.name}")
                await message.channel.send(f"Synced all roles from {guild.name}")
    async def on_member_update(self, before, after):
        if(len(before.roles) != len(after.roles)):
            log.debug(f"{before}'s roles have changed...")
            role = (self.diff(before.roles, after.roles)[0])
            if(len(before.roles) > len(after.roles)):
                log.debug(f"{role.id} has been removed")
                self.cursor.execute(f"SELECT Roles FROM discordUsers WHERE userID={before.id}")
                allData = self.cursor.fetchall()
                if((len(allData)) > 0):
                    roleList = []
                    for _role in allData[0][0].split(","):
                        roleList.append(int(_role))
                    if(role.id in roleList):
                        roleList.remove(role.id)
                        self.cursor.execute(f"""UPDATE discordUsers SET Roles="{str(roleList).strip('[').strip(']')}" WHERE userID={before.id}""") # There is 100% a better way to do this but ah well :)
                        self.db.commit()
            else:
                log.debug(f"{role.id} has been added")
                self.cursor.execute(f"SELECT Roles FROM discordUsers WHERE userID={before.id}")
                allData = self.cursor.fetchall()
                if((len(allData)) > 0):
                    roleList = []
                    for _role in allData[0][0].split(","):
                        roleList.append(int(_role))
                    if(role.id in roleList):
                        pass
                    else:
                        roleList.append(role.id)
                        self.cursor.execute(f"""UPDATE discordUsers SET Roles="{str(roleList).strip('[').strip(']')}" WHERE userID={before.id}""") # There is 100% a better way to do this but ah well :)
                        self.db.commit()
                        log.info(f"Updated {before}'s Roles")
                else:
                    for _role in ROLES_TO_SYNC:
                        if(_role["ENABLED"] == True):
                            if(role.id == _role["ROLEID"]):
                                self.cursor.execute(f"INSERT INTO discordUsers(userID, Roles) VALUES({before.id}, {role.id})")
                                self.db.commit()
                                log.info(f"Added {before}'s Roles")
intents = discord.Intents.default()
intents.members = True
Bot = FiveMBot(intents=intents)
Bot.run(BOT_KEY, reconnect=True)
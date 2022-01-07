from flask import Flask
from wsgiref import simple_server
from discord.ext.commands import Bot, Cog
from os import getenv
from threading import Thread, Lock

class Network(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.app = Flask(__name__)
        self.bot.loop.create_task(self.threader())

    def add_commands(self):
        app = self.app
        @app.route('/')
        def main():
            return self.bot.log3[:-1]

    async def threader(self):
        thread = Thread(target=self.starter)
        thread.setDaemon(True)
        thread.start()

    def starter(self):
        self.add_commands()
        log = self.bot.log
        class customlog(simple_server.WSGIRequestHandler):
            def log_message(self, format, *args):
                log(1, "%s > %s" % (self.client_address[0], format % args))
        server = simple_server.make_server('0.0.0.0', int(getenv('PORT', 8000)), self.app, handler_class=customlog)
        server.serve_forever()

def setup(bot: Bot):
    bot.add_cog(Network(bot))
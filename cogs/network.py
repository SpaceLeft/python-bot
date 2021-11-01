from flask import Flask
from wsgiref import simple_server
from threading import Thread, excepthook
from discord.ext.commands import Bot, Cog
from os import getenv



class Network(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.app = Flask(__name__)
        app = self.app
        @app.route('/')
        def main():
            return 'Bot is working'

    def start(self):
        log = self.bot.log
        class customlog(simple_server.WSGIRequestHandler):
            def log_message(self, format, *args):
                log(1, "%s > %s" % (self.client_address[0], format % args))
        server = simple_server.make_server('0.0.0.0', int(getenv('PORT', 8000)), self.app, handler_class=customlog)
        server.serve_forever()
    def webstart(self):
        Thread(target=self.start).start()

def thread_handler(args):
	now = datetime.now().strftime('%H:%M:%S')
	print('[{}] [Thread] : {}'.format(now, args.exc_value))
excepthook = thread_handler

def setup(bot: Bot):
    cog = Network(bot)
    bot.add_cog(cog)
    cog.webstart()

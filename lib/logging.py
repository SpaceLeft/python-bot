from lib import checker
import logging

def setup():
	logging.addLevelName(1, 'INFO')
	logging.addLevelName(2, 'WARNING')
	logging.addLevelName(3, 'DEBUG')
	logging.addLevelName(4, 'ERROR')
	log = logging.getLogger()
	if checker.debug:
		logging.basicConfig(format='[{asctime}] [{levelname}] [{name} | {funcName}] : {message}', datefmt="%H:%M:%S",style='{')
	else:
		logging.basicConfig(format='[{asctime}] [{levelname}] : {message}', datefmt="%H:%M:%S",style='{')
	log.setLevel('INFO')
	logging.getLogger("httpcore").setLevel(logging.WARNING)
	logging.getLogger("hpack").setLevel(logging.WARNING)
	logging.getLogger("httpx").setLevel(logging.WARNING)
	logging.getLogger("discord").setLevel(logging.ERROR)
	logging.getLogger("urllib3").setLevel(logging.WARNING)
	logging.getLogger("wavelink").setLevel(logging.WARNING)
	return log.log
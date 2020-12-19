import logging
import requests
import json

from .models.server import Server

logger = logging.getLogger(__name__)


async def refresh_server(login):
	query = 'https://maniaplanet.com/webservices/servers/online?orderBy=playerCount&search={0}&onlyPublic=0&onlyPrivate=0&onlyLobby=0&excludeLobby=1&length=10'

	try:
		data = requests.get(query.format(login))
		data = json.loads(r'''{0}'''.format(data.text))
		
		data = [x for x in data if x['login'] == login]
		if len(data) > 0:
			data = data[0]
			return await Server.get_or_create_from_info(data['login'], data['name'], data['player_count'], data['player_max'], data['spectator_count'], data['title'])
	except Exception as e:
		logger.error('Error refreshing server data of login "{0}": '.format(login), str(e))

	return None

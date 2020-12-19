"""
Maniaplanet Core Models. This models are used in several apps and should be considered as very stable.
"""
import logging

from peewee import *
from pyplanet.core.db import TimedModel


class Server(TimedModel):
	login = CharField(
		max_length=50,
		null=False,
		index=True,
		unique=True,
	)
	"""
	The login of the server will be unique in our database as it's unique over all servers (unique identifier).
	"""

	name = CharField(max_length=150)
	"""
	The name of the server, can contain unparsed styles.
	"""

	player_count = IntegerField(null=True, default=None)
	"""
	Player count of the server.
	"""

	player_max = IntegerField(null=True, default=None)
	"""
	Max player count of the server.
	"""

	spectator_count = IntegerField(null=True, default=None)
	"""
	Spectator count of the server.
	"""

	title = CharField(max_length=100)
	"""
	Title pack running on the server.
	"""

	CACHE = dict()

	async def save(self, *args, **kwargs):
		await super().save(*args, **kwargs)
		self.CACHE[self.login] = self

	@classmethod
	async def get_by_login(cls, login):
		"""
		Get server by Login.

		:param login: Login.
		:return: Server instance
		:rtype: pyplanet.apps.contrib.server_browser.models.server.Server
		"""
		try:
			if login in cls.CACHE:
				return cls.CACHE[login]
			return await cls.get(login=login)
		except DoesNotExist:
			return None

	@classmethod
	async def get_or_create_from_info(cls, login, name, player_count, player_max, spectator_count, title, **kwargs):
		"""
		This method will be called from the core, getting or creating a server instance from the information we got from
		the dedicated server.

		:param login: Login
		:param name: Name of Server
		:param player_count: Player count
		:param player_max: Max player count
		:param spectator_count: Spectator count
		:param title: Title pack
		:param kwargs: Other key arguments, matching the model columns!
		:return: Server instance.
		"""
		needs_save = False

		# HACK: Due to a limited map name length of 150 chars, we want to strip it to the maximum possible.
		# This is a temporary fix and should be better handled in the future.
		if len(name) > 150:
			name = name[:150]
			logging.getLogger(__name__).warning('Server name is very long, truncating to 150 chars.')

		server = await cls.get_by_login(login)
		if server:
			if server.name != name or \
			   server.player_count != player_count or \
			   server.player_max != player_max or \
			   server.spectator_count != spectator_count or \
			   server.title != title:
				server.name = name
				server.player_count = player_count
				server.player_max = player_max
				server.spectator_count = spectator_count
				server.title = title
				needs_save = True
		else:
			server = Server(login=login, name=name, player_count=player_count, player_max=player_max, spectator_count=spectator_count, title=title)
			needs_save = True

		if needs_save:
			await server.save()

		return server

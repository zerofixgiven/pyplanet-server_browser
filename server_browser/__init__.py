import asyncio
import logging

from pyplanet.apps.config import AppConfig
from pyplanet.contrib.command import Command
from pyplanet.contrib.setting import Setting

from .view import ServerBrowserListView
from .refresh import *

logger = logging.getLogger(__name__)


class ServerBrowserApp(AppConfig):
	app_dependencies = ['core.maniaplanet', 'core.trackmania']

	game_dependencies = ['trackmania']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.refresh_data = None

		self.setting_server_login_names = Setting(
			'server_login_names', 'Server login names', Setting.CAT_BEHAVIOUR, type=list,
			description='List of server login names for the server browser.',
			default=None,
		)

		self.setting_server_refresh_interval = Setting(
			'server_refresh_interval', 'Server refresh interval', Setting.CAT_BEHAVIOUR, type=int,
			description='Interval for refreshing the server information.',
			default=15,
		)

	async def on_init(self):
		await super().on_init()

	async def on_start(self):
		# Register commands.
		await self.instance.command_manager.register(
			Command(command='server', target=self.show_server_list,
					description='Displays the server browser.'),
		)

		# Register settings.
		await self.context.setting.register(
			self.setting_server_login_names,
			self.setting_server_refresh_interval
		)

		self.refresh_data = asyncio.ensure_future(self.refresh_server_data())

	async def on_stop(self):
		await super().on_stop()

	async def on_destroy(self):
		await super().on_destroy()

	async def show_server_list(self, player, data, **kwargs):
		view = ServerBrowserListView(self, player, self.setting_server_login_names)
		await view.display()

	async def refresh_server_data(self):
		while True:
			sleep_interval = abs(await self.setting_server_refresh_interval.get_value(refresh=True))
			if sleep_interval == 0:
				sleep_interval = 1

			logger.debug('Refresh Server Data, sleeping for {} seconds'.format(sleep_interval))
			await asyncio.sleep(sleep_interval)

			logins = await self.setting_server_login_names.get_value(refresh=True)

			# Ignore when empty
			if not logins:
				continue

			for login in logins:
				await refresh_server(login)

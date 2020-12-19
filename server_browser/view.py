from pyplanet.utils import times
from pyplanet.views.generics.list import ManualListView

from .models.server import Server
from .refresh import *


class ServerBrowserListView(ManualListView):
	title = 'Server Browser'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Browse'

	template_name = 'server_browser/list.xml'

	def __init__(self, app, player, logins):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.player = player
		self.logins = logins
		self.provide_search = False

	async def get_data(self):
		items = []

		logins = await self.logins.get_value()
		if not logins:
			return []

		i = 0
		for login in logins:
			server = await Server.get_by_login(login)
			if not server:
				server = await refresh_server(login)
				if not server:
					continue

			i += 1
			items.append({
				'index': i,
				'server_name': server.name,
				'player_count': server.player_count,
				'player_max': server.player_max,
				'spectator_count': server.spectator_count,
				'link': 'maniaplanet://#join={0}@{1}'.format(server.login, server.title),
				'qlink': 'maniaplanet://#qjoin={0}@{1}'.format(server.login, server.title),
				'join': 'Join'
			})

		return items

	async def get_fields(self):
		fields = [
			{
				'name': '#',
				'index': 'index',
				'sorting': True,
				'searching': False,
				'width': 10,
				'type': 'label'
			},
			{
				'name': 'Server',
				'index': 'server_name',
				'sorting': False,
				'searching': True,
				'width': 87.5,
				'url': 'link',
			},
			{
				'name': 'Players',
				'index': 'player_count',
				'sorting': True,
				'searching': False,
				'width': 30,
				'type': 'label'
			},
			{
				'name': 'MaxPlayers',
				'index': 'player_max',
				'sorting': True,
				'searching': False,
				'width': 30,
				'type': 'label'
			},
			{
				'name': 'Spectators',
				'index': 'spectator_count',
				'sorting': True,
				'searching': False,
				'width': 30,
				'type': 'label'
			},
			{
				'name': 'QuickJoin',
				'index': 'join',
				'sorting': False,
				'searching': False,
				'width': 30,
				'type': 'label',
				'url': 'qlink',
			},
		]
		return fields

	async def get_context_data(self):
		context = await super().get_context_data()

		# Add dynamic data from query.
		context.update(await self.get_object_data())

		fields = await self.get_fields()
		actions = await self.get_actions()
		buttons = await self.get_buttons()

		# Process fields + actions (normalize)
		# Calculate positions of fields
		left = 0
		for field in fields:
			field['left'] = left
			left += field['width']
			if 'type' not in field:
				field['type'] = 'label'
			if 'safe' not in field:
				field['safe'] = False

			field['_sort'] = None
			if self.sort_field is not None and field['index'] == self.sort_field['index']:
				field['_sort'] = self.sort_order
		fields_width = int(left)

		left = 0
		for action in actions:
			action['left'] = left
			left += action['width'] if 'width' in action else 5
			if 'type' not in action:
				action['type'] = 'quad'
			if 'safe' not in action:
				action['safe'] = False
		actions_width = int(left)

		right = 215.5
		for button in buttons:
			button['right'] = (right - button['width'] / 2)
			right -= button['width'] + 3

		# Add facts.
		context.update({
			'field_renderer': self._render_field,
			'field_renderer2': self._render_field2,
			'fields': fields,
			'actions': actions,
			'buttons': buttons,
			'provide_search': self.provide_search,
			'title': await self.get_title(),
			'icon_style': self.icon_style,
			'icon_substyle': self.icon_substyle,
			'search': self.search_text,
			'pages': self.num_pages,
			'page': self.page,
			'fields_width': fields_width,
			'actions_width': actions_width,
		})

		return context

	def _render_field(self, row, field):
		if 'renderer' in field:
			return field['renderer'](row, field)
		if isinstance(row, dict):
			return str(row[field['index']])
		else:
			return str(getattr(row, field['index']))

	def _render_field2(self, row, field):
		if 'renderer2' in field:
			return field['renderer2'](row, field)
		if isinstance(row, dict):
			return str(row[field['url']])
		else:
			return str(getattr(row, field['url']))

	async def display(self, player=None):
		return await super().display(player or self.player)

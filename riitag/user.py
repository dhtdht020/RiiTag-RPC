import datetime

import requests

from .exceptions import RiitagNotFoundError

RIITAG_ENDPOINT = 'http://tag.rc24.xyz/{}/json'
HEADERS = {'User-Agent': 'RiiTag-RPC WatchThread v1'}


class RiitagGame:
    def __init__(self, **kwargs):
        self.game_id = kwargs.get('game_id')
        self.console = kwargs.get('console')
        self.region = kwargs.get('region')
        self.cover_url = kwargs.get('cover_url')

        self.time = kwargs.get('time')
        if self.time:
            self.time = datetime.datetime.utcfromtimestamp(self.time)

    def __bool__(self):
        return bool(self.game_id)


class RiitagInfo:
    def __init__(self, **kwargs):
        self.name = kwargs.get('user', {}).get('name')
        self.id = kwargs.get('user', {}).get('id')
        self.games = kwargs.get('game_data', {}).get('games', [])

        last_played = kwargs.get('game_data', {}).get('last_played', {})
        self.last_played = RiitagGame(**last_played)

        self.outdated = False

    def __bool__(self):
        return bool(self.name or self.id or self.games)

    def __eq__(self, other):
        if not isinstance(other, RiitagInfo):
            return False

        return self.last_played == other.last_played and self.outdated == other.outdated


class User:
    def __init__(self, **kwargs):
        """Represents a RiiTag / Discord user."""
        self.id = kwargs.get('id')
        self.username = kwargs.get('username')
        self.discriminator = kwargs.get('discriminator')
        self.avatar = kwargs.get('avatar')
        self.locale = kwargs.get('locale')

        self.riitag = None

    def fetch_riitag(self):
        url = RIITAG_ENDPOINT.format(self.id)
        r = requests.get(url, headers=HEADERS)

        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            self.riitag = None

            return

        data = r.json()
        error = data.get('error')
        if error:
            raise RiitagNotFoundError(error)

        riitag = RiitagInfo(**data)
        self.riitag = riitag

        return riitag

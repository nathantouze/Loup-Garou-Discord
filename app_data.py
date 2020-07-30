import config
from game_data import LPData

class appData:
    def __init__(self):
        self.game = LPData()
        self.game_channel = None
        self.invite = None
        self.server = config.server
        self.server_wolf = config.wolf_team
        self.server_wolf_owner = config.wolf_team_owner
        self.wolf_channel = config.wolf_team_channel
        self.poll_channel = config.poll_channel
        self.max_player = config.max_player
        self.new_game_message = config.new_game_message
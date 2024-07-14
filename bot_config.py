class BotConfig:
    username = ""
    password = ""
    team_file = ""
    
    def __init__(self, username:str, password:str, team_file:str):
        self.username = username
        self.password = password
        self.team_file = team_file
    
    def is_valid(self):
        return len(self.username) > 0 and len(self.password) > 0 and len(self.team_file) > 0
            
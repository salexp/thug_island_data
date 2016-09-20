class Player:
    def __init__(self, info):
        self.games_ir = 0
        self.games_owned = 0
        self.games_started = 0
        self.ir = []
        self.name = get_name(info[1])
        self.owned = []
        self.points = 0.0
        self.ppg = 0.0
        self.position = get_position(info[1])
        self.started = []

    def update(self, matchup, info, slot):
        plyr_game = PlayerGame(self, matchup, info, slot)
        self.games_owned += 1
        self.owned.append(plyr_game)
        self.points += plyr_game.points
        self.ppg = self.points / self.games_owned
        matchup.roster.add_player(plyr_game)
        if plyr_game.slot not in ["Bench", "IR"]:
            self.games_started += 1
            self.started.append(plyr_game)
        elif plyr_game.slot == "IR":
            self.games_ir += 1
            self.ir.append(plyr_game)


class PlayerGame:
    def __init__(self, player, matchup, info, slot):
        self.matchup = matchup
        self.name = player.name
        self.player = player
        self.slot = slot

        try:
            self.points = float(info[4])
        except ValueError:
            self.points = 0


def get_name(st):
    if "D/ST" not in st:
        name = st.split(",")[0].replace("*", "")
    else:
        name = st.split(" ")[0]
    return name


def get_position(st):
    st = st.replace(u'\xa0', u' ')
    if "QB" in st:
        pos = "QB"
    elif "RB" in st:
        pos = "RB"
    elif "WR" in st:
        pos = "WR"
    elif "TE" in st:
        pos = "TE"
    elif "D/ST" in st:
        pos = "D/ST"
    elif "K" in st.split(" "):
        pos = "K"
    else:
        pos = None
    return pos

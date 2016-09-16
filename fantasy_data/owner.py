divisions = {
    "Andrew Lee": "East",
    "Ben Mytelka": "West",
    "Cody Blain": "West",
    "Connor Wiseman": "East",
    "Eric Price": "West",
    "James Furlong": "East",
    "josh watson": "East",
    "Rande Revilla": "West",
    "Stuart Petty": "East",
    "Thomas Singleton": "West",
    "Trevor Watson": "West",
}


class Owner:
    def __init__(self, name):
        self.appearances = []
        self.division = divisions[name]
        self.games = {}
        self.name = name
        self.records = Records()
        self.team_names = []

    def add_matchup(self, game, side):
        self.played = game.played
        if not self.games.get(game.year):
            self.games[game.year] = {}

        self.add_team_name(game.away_team if side == "Away" else game.home_team)

        matchup = Matchup(game, side)
        self.games[game.year][game.week.number] = matchup
        op_name = matchup.opponent.name
        op_div = matchup.opponent.division

        if self.played:
            if not self.records.opponents.get(op_name):
                self.records.opponents[op_name] = {"All": Record()}
            records = [self.records.opponents[op_name]["All"],
                       self.records.overall["All"],
                       self.records.divisions[op_div]["All"]]

            if not self.records.divisions[op_div].get(game.year):
                self.records.divisions[op_div][game.year] = Record()
            records.append(self.records.divisions[op_div][game.year])

            if not self.records.opponents[op_name].get(game.year):
                self.records.opponents[op_name][game.year] = Record()
            records.append(self.records.opponents[op_name][game.year])

            if not self.records.regular_season.get(game.year):
                self.records.regular_season[game.year] = Record()
            if game.is_regular_season:
                records.append(self.records.regular_season["All"])
                records.append(self.records.regular_season[game.year])

            if not self.records.postseason.get(game.year):
                self.records.postseason[game.year] = Record()
            if game.is_postseason:
                records.append(self.records.postseason["All"])
                records.append(self.records.postseason[game.year])

            if not self.records.playoffs.get(game.year):
                self.records.playoffs[game.year] = Record()
            if game.is_playoffs:
                self.add_playoff_appearance(game.year)
                records.append(self.records.playoffs["All"])
                records.append(self.records.playoffs[game.year])

            if not self.records.championships.get(game.year):
                self.records.championships[game.year] = Record()
            if game.is_championship:
                records.append(self.records.championships["All"])
                records.append(self.records.championships[game.year])

            for record in records:
                record.all += 1
                record.wins += matchup.won
                record.losses += matchup.lost
                record.ties += matchup.tie
                record.pf += matchup.pf
                record.pa += matchup.pa

    def add_playoff_appearance(self, year):
        if year not in self.appearances:
            self.appearances.append(year)
            self.appearances = sorted(self.appearances)

    def add_team_name(self, name):
        if name not in self.team_names:
            self.team_names.append(name)
            self.team_names = sorted(self.team_names)


class Matchup():
    def __init__(self, game, side):
        if side in ["Away", "Home"]:
            away = side == "Away"
            opposite = "Home" if away else "Away"
            self.owner = game.league.owners[game.away_owner] if away \
                else game.league.owners[game.home_owner]
            self.opponent = game.league.owners[game.home_owner] if away \
                else game.league.owners[game.away_owner]

            if game.played:
                self.won = game.winner == side
                self.lost = game.winner == opposite
                self.tie = game.winner == "Tie"
                self.pf = game.away_score if away else game.home_score
                self.pa = game.home_score if away else game.away_score


class Records:
    def __init__(self):
        self.championships = {"All": Record()}
        self.divisions = {"East": {"All": Record()}, "West": {"All": Record()}}
        self.opponents = {}
        self.overall = {"All": Record()}
        self.playoffs = {"All": Record()}
        self.postseason = {"All": Record()}
        self.regular_season = {"All": Record()}


class Record:
    def __init__(self):
        self.all = 0
        self.wins = 0
        self.losses = 0
        self.ties = 0
        self.pf = 0.0
        self.pa = 0.0

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
    def __init__(self, name, league):
        self.appearances = []
        self.championships = []
        self.division = divisions[name]
        self.games = {}
        self.league = league
        self.name = name
        self.records = Records()
        self.team_names = []

    def add_matchup(self, game, side):
        played = game.played
        if not self.games.get(game.year):
            self.games[game.year] = {}

        self.add_team_name(game.away_team if side == "Away" else game.home_team)

        matchup = Matchup(game, side)
        self.games[game.year][game.week.number] = matchup
        op_name = matchup.opponent.name
        op_div = matchup.opponent.division

        if played:
            self.check_personal(matchup)
            self.league.records.check_records(matchup)
            records = []

            # Opponent all time
            if not self.records.opponents.get(op_name):
                self.records.opponents[op_name] = {"All": Record()}
            records.append(self.records.opponents[op_name]["All"])
            # Opponent year
            if not self.records.opponents[op_name].get(game.year):
                self.records.opponents[op_name][game.year] = Record()
            records.append(self.records.opponents[op_name][game.year])

            # Overall all time
            records.append(self.records.overall["All"])
            # Overall year
            if not self.records.overall.get(game.year):
                self.records.overall[game.year] = Record()
            records.append(self.records.overall[game.year])

            # Divisions all time
            records.append(self.records.divisions[op_div]["All"])
            # Divisions year
            if not self.records.divisions[op_div].get(game.year):
                self.records.divisions[op_div][game.year] = Record()
            records.append(self.records.divisions[op_div][game.year])

            if game.is_regular_season:
                # Regular season all time
                records.append(self.records.regular_season["All"])
                # Regular season year
                if not self.records.regular_season.get(game.year):
                    self.records.regular_season[game.year] = Record()
                records.append(self.records.regular_season[game.year])

            if game.is_postseason:
                # Postseason all time
                records.append(self.records.postseason["All"])
                # Postseason year
                if not self.records.postseason.get(game.year):
                    self.records.postseason[game.year] = Record()
                records.append(self.records.postseason[game.year])

            if game.is_playoffs:
                # Playoffs all time
                records.append(self.records.playoffs["All"])
                # Playoffs year
                if not self.records.playoffs.get(game.year):
                    self.records.playoffs[game.year] = Record()
                    self.add_playoff_appearance(game.year)
                records.append(self.records.playoffs[game.year])

            if game.is_championship:
                # Championships all time
                records.append(self.records.championships["All"])
                # Championships year
                if not self.records.championships.get(game.year):
                    self.records.championships[game.year] = Record()
                    self.add_championship(game.year)
                records.append(self.records.championships[game.year])

            for record in records:
                record.all += 1
                record.wins += matchup.won
                record.losses += matchup.lost
                record.ties += matchup.tie
                record.pf += matchup.pf
                record.pa += matchup.pa

    def add_championship(self, year):
        if year not in self.championships:
            self.championships.append(year)
            self.championships = sorted(self.championships)

    def add_playoff_appearance(self, year):
        if year not in self.appearances:
            self.appearances.append(year)
            self.appearances = sorted(self.appearances)

    def add_team_name(self, name):
        if name not in self.team_names:
            self.team_names.append(name)
            self.team_names = sorted(self.team_names)

    def check_personal(self, matchup):
        rcd = self.records.personal["Most PF"]
        if len(rcd) < 10:
            rcd.append(matchup)
        else:
            if rcd[-1].pf < matchup.pf:
                rcd[-1] = matchup
        self.records.personal["Most PF"] = \
            sorted(rcd, key=lambda param: param.pf, reverse=True)

        rcd = self.records.personal["Least PF"]
        if len(rcd) < 10:
            rcd.append(matchup)
        else:
            if rcd[-1].pf > matchup.pf:
                rcd[-1] = matchup
        self.records.personal["Least PF"] = \
            sorted(rcd, key=lambda param: param.pf, reverse=False)

        rcd = self.records.personal["Highest Scoring"]
        if len(rcd) < 10:
            rcd.append(matchup)
        else:
            if rcd[-1].pf + rcd[-1].pa < matchup.pf + matchup.pa:
                rcd[-1] = matchup
        self.records.personal["Highest Scoring"] = \
            sorted(rcd, key=lambda param: (param.pf + param.pa), reverse=True)

        rcd = self.records.personal["Lowest Scoring"]
        if len(rcd) < 10:
            rcd.append(matchup)
        else:
            if rcd[-1].pf + rcd[-1].pa > matchup.pf + matchup.pa:
                rcd[-1] = matchup
        self.records.personal["Lowest Scoring"] = \
            sorted(rcd, key=lambda param: (param.pf + param.pa), reverse=False)


class Matchup():
    def __init__(self, game, side):
        self.game = game
        self.week = game.week
        self.year = game.year
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
        self.personal = {"Most PF": [], "Least PF": [], "Highest Scoring": [], "Lowest Scoring": []}
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

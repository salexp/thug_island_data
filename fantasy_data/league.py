from fantasy_data import schedule


class League:
    def __init__(self, name):
        self.league_name = name
        self.owners = {}
        self.records = Records(self)
        self.years = {}

    def add_schedule(self, year, sheet):
        if not self.years.get(year):
            self.years[year] = Year()
        self.years[year].schedule = schedule.Schedule(self, sheet, year)


class Year:
    def __init__(self):
        self.schedule = None


class Records:
    def __init__(self, league):
        self.league = league
        self.games = {"Highest Scoring": [], "Lowest Scoring": []}
        self.teams = {"Most PF": [], "Least PF": []}

    def check_records(self, matchup, key=None):
        if key is not None:
            keys = [key]
        else:
            keys = []
            keys += self.games.keys()
            keys += self.teams.keys()

        for key in keys:
            if key == "Most PF":
                rcd = self.league.records.teams[key]
                if len(rcd) < 10:
                    rcd.append(matchup)
                else:
                    if rcd[-1].pf < matchup.pf:
                        rcd[-1] = matchup
                self.league.records.teams[key] = \
                    sorted(rcd, key=lambda param: param.pf, reverse=True)

            elif key == "Least PF":
                rcd = self.league.records.teams[key]
                if len(rcd) < 10:
                    rcd.append(matchup)
                else:
                    if rcd[-1].pf > matchup.pf:
                        rcd[-1] = matchup
                self.league.records.teams[key] = \
                    sorted(rcd, key=lambda param: param.pf, reverse=False)

            elif key == "Highest Scoring":
                game = matchup.game
                rcd = self.league.records.games[key]
                if len(rcd) < 10 and game not in rcd:
                    rcd.append(game)
                elif game not in rcd:
                    if rcd[-1].away_score + rcd[-1].home_score < game.away_score + game.home_score:
                        rcd[-1] = game
                self.league.records.games[key] = \
                    sorted(rcd, key=lambda param: (param.away_score + param.home_score), reverse=True)

            elif key == "Lowest Scoring":
                game = matchup.game
                rcd = self.league.records.games[key]
                if len(rcd) < 10 and game not in rcd:
                    rcd.append(game)
                elif game not in rcd:
                    if rcd[-1].away_score + rcd[-1].home_score > game.away_score + game.home_score:
                        rcd[-1] = game
                self.league.records.games[key] = \
                    sorted(rcd, key=lambda param: (param.away_score + param.home_score), reverse=False)


from fantasy_data import schedule
from nfl_data import player


class League:
    def __init__(self, name):
        self.league_name = name
        self.owners = {}
        self.players = {}
        self.records = Records(self)
        self.years = {}

    def add_schedule(self, year, sheet):
        if not self.years.get(year):
            self.years[year] = Year()
        sch = schedule.Schedule(self, sheet, year)
        self.years[year].schedule = sch
        if sch.complete:
            self.update_season_records(year)

    def add_games(self, year, book):
        for w in range(1, len(self.years[year].schedule.weeks) + 1):
            wk = str(w)
            week = self.years[year].schedule.weeks[wk]
            sheet = book.sheet_by_index(w - 1)
            week.add_details(sheet)

    def update_season_records(self, year, key=None):
        records = self.records.season
        owner_seasons = self.years[year].owner_seasons

        if key is not None:
            keys = [key]
        else:
            keys = []
            keys += records.keys()

        for ownr in owner_seasons:
            ownr_season = owner_seasons[ownr]
            for key in keys:
                if key == "Most PF":
                    rcd = records[key]
                    if len(rcd) < 10:
                        rcd.append(ownr_season)
                    else:
                        if rcd[-1].pf < ownr_season.pf:
                            rcd[-1] = ownr_season
                    records[key] = \
                        sorted(rcd, key=lambda param: param.pf, reverse=True)

                elif key == "Fewest PF":
                    rcd = records[key]
                    if len(rcd) < 10:
                        rcd.append(ownr_season)
                    else:
                        if rcd[-1].pf > ownr_season.pf:
                            rcd[-1] = ownr_season
                    records[key] = \
                        sorted(rcd, key=lambda param: param.pf, reverse=False)

                elif key == "Most PA":
                    rcd = records[key]
                    if len(rcd) < 10:
                        rcd.append(ownr_season)
                    else:
                        if rcd[-1].pa < ownr_season.pa:
                            rcd[-1] = ownr_season
                    records[key] = \
                        sorted(rcd, key=lambda param: param.pa, reverse=True)

                elif key == "Fewest PA":
                    rcd = records[key]
                    if len(rcd) < 10:
                        rcd.append(ownr_season)
                    else:
                        if rcd[-1].pa > ownr_season.pa:
                            rcd[-1] = ownr_season
                    records[key] = \
                        sorted(rcd, key=lambda param: param.pa, reverse=False)

    def search_players(self, str):
        found = []
        for plyr in self.players:
            if str in self.players[plyr].name:
                found.append(self.players[plyr])

        return found

    def to_string(self, owners=True):
        str = ""
        if owners:
            ownrs = sorted([o for o in self.owners], key=lambda p: (p[0].upper(), p[1]))
            for o in ownrs:
                str += self.owners[o].records.to_string()
                str += "\n"

        return str


class Year:
    def __init__(self):
        self.owner_seasons = {}
        self.schedule = None


class Records:
    def __init__(self, league):
        self.league = league
        self.games = {"Highest Scoring": [], "Lowest Scoring": []}
        self.season = {"Most PF": [], "Fewest PF": [], "Most PA": [], "Fewest PA": []}
        self.teams = {"Most PF": [], "Fewest PF": []}

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

            elif key == "Fewest PF":
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


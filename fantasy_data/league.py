from fantasy_data import rankings
from fantasy_data import schedule
from nfl_data import player
from util import *


class League:
    def __init__(self, name):
        self.league_name = name
        self.owners = {}
        self.players = {}
        self.power_rankings = {}
        self.rankings = []
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

    def generate_rankings(self, year=None, week=None):
        rkngs = rankings.Rankings(self)
        if year is None:
            year = max(self.years.keys())
        if week is None:
            week = self.years[year].current_week

        for owner in self.owners:
            rkngs.add_owner(self.owners[owner], year, week)

        hgh = 0.0
        mx = {}
        for key in rkngs.keys:
            wgt = rkngs.keys[key]
            rkngs.ranks[key] = {"List": None}
            if key == "QB":
                lst = [[o, rkngs.owners[o].qb] for o in rkngs.owners]
            elif key == "RB":
                lst = [[o, rkngs.owners[o].rb] for o in rkngs.owners]
            elif key == "WR":
                lst = [[o, rkngs.owners[o].wr] for o in rkngs.owners]
            elif key == "TE":
                lst = [[o, rkngs.owners[o].te] for o in rkngs.owners]
            elif key == "D/ST":
                lst = [[o, rkngs.owners[o].dst] for o in rkngs.owners]
            elif key == "K":
                lst = [[o, rkngs.owners[o].k] for o in rkngs.owners]
            elif key == "WP":
                lst = [[o, rkngs.owners[o].wpct] for o in rkngs.owners]
            elif key == "PF":
                lst = [[o, rkngs.owners[o].pf] for o in rkngs.owners]
            elif key == "PA":
                lst = [[o, rkngs.owners[o].pa] for o in rkngs.owners]
            elif key == "PLOB":
                lst = [[o, rkngs.owners[o].plob] for o in rkngs.owners]

            mx[key] = max([l[1] for l in lst])
            mx["WP"] = 1.0
            mx["PLOB"] = min([l[1] for l in lst])

            if key not in ["PLOB"]:
                mlst = [[i[0], i[1]/mx[key]*wgt] for i in lst]
            else:
                mlst = [[i[0], mx[key]/i[1]*wgt] for i in lst]

            slst = sorted(mlst, key=lambda p: p[1], reverse=True)
            hgh += slst[0][1]
            rlst = add_ranks(slst, 1)
            rkngs.ranks[key]["List"] = rlst

            for lne in rlst:
                nlne = lne[1:]
                if lne[1] != 0:
                    cntrb = lne[1]
                else:
                    cntrb = 0.0
                nlne.append(cntrb)
                rkngs.ranks[key][lne[0]] = nlne

        power_rankings = []
        rkngs.ranks["PR"] = {}
        for owner in self.owners:
            trnk = 0.0
            for key in rkngs.keys:
                trnk += rkngs.ranks[key][owner][2]

            trnk = trnk / hgh
            rkngs.ranks["PR"][owner] = trnk
            power_rankings.append([owner, trnk])

        self.rankings.append(rkngs)
        power_rankings = sorted(power_rankings, key=lambda p: p[1], reverse=True)
        self.power_rankings[week] = add_ranks(power_rankings, 1)

    def recursive_rankings(self, year=None):
        if year is None:
            year = max(self.years.keys())
        self.current_week = self.years[year].current_week

        weeks = [str(w) for w in range(1, int(self.current_week)+1)]
        for week in weeks:
            self.generate_rankings(week=week)

    def search_players(self, str):
        found = []
        for plyr in self.players:
            if str in self.players[plyr].name:
                found.append(self.players[plyr])

        return found

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
                        sorted(rcd, key=lambda param: param.ppg, reverse=True)

                elif key == "Fewest PF":
                    rcd = records[key]
                    if len(rcd) < 10:
                        rcd.append(ownr_season)
                    else:
                        if rcd[-1].pf > ownr_season.pf:
                            rcd[-1] = ownr_season
                    records[key] = \
                        sorted(rcd, key=lambda param: param.ppg, reverse=False)

                elif key == "Most PA":
                    rcd = records[key]
                    if len(rcd) < 10:
                        rcd.append(ownr_season)
                    else:
                        if rcd[-1].pa < ownr_season.pa:
                            rcd[-1] = ownr_season
                    records[key] = \
                        sorted(rcd, key=lambda param: param.pag, reverse=True)

                elif key == "Fewest PA":
                    rcd = records[key]
                    if len(rcd) < 10:
                        rcd.append(ownr_season)
                    else:
                        if rcd[-1].pa > ownr_season.pa:
                            rcd[-1] = ownr_season
                    records[key] = \
                        sorted(rcd, key=lambda param: param.pag, reverse=False)

    def to_string(self, owners=False, power=True, rcds=10):
        str = ""

        if power:
            pass

        if owners:
            ownrs = sorted([o for o in self.owners], key=lambda p: (p[0].upper(), p[1]))
            for o in ownrs:
                str += self.owners[o].records.to_string()
                str += "\n"

        if rcds:
            if rcds > len(self.records.season["Most PF"]):
                rcds = len(self.records.season["Most PF"])

            rcd = self.records.season["Most PF"]
            str += "[b]Most PPG in a Single Season[/b]\n"
            for r in range(rcds):
                ows = rcd[r]
                str += "{0} {1:.1f} {2}{3}{4} ({5})\n".format(add_suffix(r+1),
                                                              ows.ppg,
                                                              ows.owner_name,
                                                              "*" if ows.playoffs else "",
                                                              "*" if ows.championship else "",
                                                              ows.year)

            str += "\n"
            rcd = self.records.season["Fewest PF"]
            str += "[b]Fewest PPG in a Single Season[/b]\n"
            for r in range(rcds):
                ows = rcd[r]
                str += "{0} {1:.1f} {2}{3}{4} ({5})\n".format(add_suffix(r+1),
                                                              ows.ppg,
                                                              ows.owner_name,
                                                              "*" if ows.playoffs else "",
                                                              "*" if ows.championship else "",
                                                              ows.year)

            str += "\n"
            rcd = self.records.season["Most PA"]
            str += "[b]Most PA/G in a Single Season[/b]\n"
            for r in range(rcds):
                ows = rcd[r]
                str += "{0} {1:.1f} {2}{3}{4} ({5})\n".format(add_suffix(r+1),
                                                              ows.pag,
                                                              ows.owner_name,
                                                              "*" if ows.playoffs else "",
                                                              "*" if ows.championship else "",
                                                              ows.year)

            str += "\n"
            rcd = self.records.season["Fewest PA"]
            str += "[b]Fewest PA/G in a Single Season[/b]\n"
            for r in range(rcds):
                ows = rcd[r]
                str += "{0} {1:.1f} {2}{3}{4} ({5})\n".format(add_suffix(r+1),
                                                              ows.pag,
                                                              ows.owner_name,
                                                              "*" if ows.playoffs else "",
                                                              "*" if ows.championship else "",
                                                              ows.year)

            str += "\n"
            rcd = self.records.teams["Most PF"]
            str += "[b]Most PF in a Single Game[/b]\n"
            for r in range(rcds):
                mtch = rcd[r]
                str += "{0} {1} pts, {2} {3} {4} {5} {6} week {7}\n".format(add_suffix(r+1),
                                                                            mtch.pf,
                                                                            mtch.owner_name,
                                                                            "won" if mtch.won else "lost",
                                                                            "vs" if mtch.home else "at",
                                                                            mtch.opponent.name,
                                                                            mtch.year, mtch.week.number)

            str += "\n"
            rcd = self.records.teams["Fewest PF"]
            str += "[b]Fewest PF in a Single Game[/b]\n"
            for r in range(rcds):
                mtch = rcd[r]
                str += "{0} {1} pts, {2} {3} {4} {5} {6} week {7}\n".format(add_suffix(r+1),
                                                                            mtch.pf,
                                                                            mtch.owner_name,
                                                                            "won" if mtch.won else "lost",
                                                                            "vs" if mtch.home else "at",
                                                                            mtch.opponent.name,
                                                                            mtch.year, mtch.week.number)

        return str


class Year:
    def __init__(self):
        self.current_week = 0
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
                if not matchup.game.is_consolation:
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
                if not matchup.game.is_consolation:
                    game = matchup.game
                    rcd = self.league.records.games[key]
                    if len(rcd) < 10 and game not in rcd:
                        rcd.append(game)
                    elif game not in rcd:
                        if rcd[-1].away_score + rcd[-1].home_score > game.away_score + game.home_score:
                            rcd[-1] = game
                    self.league.records.games[key] = \
                        sorted(rcd, key=lambda param: (param.away_score + param.home_score), reverse=False)


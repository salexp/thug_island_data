from nfl_data import roster
from util import *

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
        self.attrib = Attributes(self)
        self.active = []
        self.championships = []
        self.championship_games = []
        self.division = divisions[name]
        self.games = {}
        self.league = league
        self.name = name
        self.playoffs = []
        self.playoff_games = []
        self.records = Records(self)
        self.seasons = {}
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
            self.add_season(matchup)
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
                self.playoff_games.append(matchup)
                # Playoffs all time
                records.append(self.records.playoffs["All"])
                # Playoffs year
                if not self.records.playoffs.get(game.year):
                    self.records.playoffs[game.year] = Record()
                    self.add_playoff_appearance(game.year)
                records.append(self.records.playoffs[game.year])

            if game.is_championship:
                self.championship_games.append(matchup)
                # Championships all time
                records.append(self.records.championships["All"])
                # Championships year
                if not self.records.championships.get(game.year):
                    self.records.championships[game.year] = Record()
                records.append(self.records.championships[game.year])
            if game.is_championship and matchup.won:
                    self.add_championship(game.year)

            for record in records:
                record.all += 1
                record.wins += matchup.won
                record.losses += matchup.lost
                record.ties += matchup.tie
                record.pf += matchup.pf
                record.pa += matchup.pa

        return matchup

    def add_championship(self, year):
        if year not in self.championships:
            self.championships.append(year)
            self.championships = sorted(self.championships)

    def add_playoff_appearance(self, year):
        if year not in self.playoffs:
            self.playoffs.append(year)
            self.playoffs = sorted(self.playoffs)

    def add_season(self, matchup):
        if not self.seasons.get(matchup.year):
            self.seasons[matchup.year] = OwnerSeason(self, matchup)
            self.league.years[matchup.year].owner_seasons[self.name] = self.seasons[matchup.year]
            self.active.append(matchup.year)
        season = self.seasons[matchup.year]
        season.add_matchup(matchup)

    def add_team_name(self, name):
        # if name not in self.team_names:
        #     self.team_names.append(name)
        #     self.team_names = sorted(self.team_names)
        if len(self.team_names):
            if name != self.team_names[-1]:
                self.team_names.append(name)
        else:
            self.team_names.append(name)

    def check_personal(self, matchup, number=50):
        rcd = self.records.personal["Most PF"]
        if len(rcd) < number:
            rcd.append(matchup)
        else:
            if rcd[-1].pf < matchup.pf:
                rcd[-1] = matchup
        self.records.personal["Most PF"] = \
            sorted(rcd, key=lambda param: param.pf, reverse=True)

        rcd = self.records.personal["Fewest PF"]
        if not matchup.game.is_consolation:
            if len(rcd) < number:
                rcd.append(matchup)
            else:
                if rcd[-1].pf > matchup.pf:
                    rcd[-1] = matchup
            self.records.personal["Fewest PF"] = \
                sorted(rcd, key=lambda param: param.pf, reverse=False)

        rcd = self.records.personal["Highest Scoring"]
        if len(rcd) < number:
            rcd.append(matchup)
        else:
            if rcd[-1].pf + rcd[-1].pa < matchup.pf + matchup.pa:
                rcd[-1] = matchup
        self.records.personal["Highest Scoring"] = \
            sorted(rcd, key=lambda param: (param.pf + param.pa), reverse=True)

        rcd = self.records.personal["Lowest Scoring"]
        if not matchup.game.is_consolation:
            if len(rcd) < number:
                rcd.append(matchup)
            else:
                if rcd[-1].pf + rcd[-1].pa > matchup.pf + matchup.pa:
                    rcd[-1] = matchup
            self.records.personal["Lowest Scoring"] = \
                sorted(rcd, key=lambda param: (param.pf + param.pa), reverse=False)

    def check_roster(self, matchup):
        rcd = self.records.alltime_roster
        for plyr in matchup.roster.starters + matchup.roster.bench:
            rcd.add_player(plyr, force="Bench")

        rcd.make_optimal()
        opt = rcd.optimal
        opt.update_points()
        self.records.alltime_roster = opt

    def first_name(self):
        return self.name.split(" ")[0].capitalize()

    def initials(self):
        return self.first_name()[0] + self.last_name()[0]

    def last_name(self):
        return self.name.split(" ")[1].capitalize()


class Matchup:
    def __init__(self, game, side):
        _away = side == "Away"
        self.away = _away
        self.game = game
        self.home = not _away
        self.owner_name = game.away_owner_name if _away else game.home_owner_name
        self.record = game.away_record if _away else game.home_record
        self.roster = roster.GameRoster()
        self.team_name = game.away_team if _away else game.home_team
        self.team_name_opponent = game.home_team if _away else game.away_team
        self.week = game.week
        self.win_diff = None
        self.year = game.year
        if side in ["Away", "Home"]:
            opposite = "Home" if _away else "Away"
            self.owner = game.away_owner if _away else game.home_owner
            self.opponent = game.home_owner if _away else game.away_owner

            diff = get_wins(game.away_record) - get_wins(game.home_record) if _away \
                else get_wins(game.home_record) - get_wins(game.away_record)

            if game.played:
                diff -= game.away_win if _away else game.home_win

            self.win_diff = diff


            if game.played:
                self.won = game.winner == side
                self.lost = game.winner == opposite
                self.tie = game.winner == "Tie"
                self.pf = game.away_score if _away else game.home_score
                self.pa = game.home_score if _away else game.away_score


class OwnerSeason:
    def __init__(self, owner, matchup):
        self.championship = False
        self.games = 0
        self.losses = 0
        self.matchups = []
        self.owner = owner
        self.owner_name = owner.name
        self.playoffs = False
        self.pf = 0.0
        self.ppg = 0.0
        self.pa = 0.0
        self.pag = 0.0
        self.records = None
        self.ties = 0
        self.wins = 0
        self.wl_records = []
        self.year = matchup.year

    def add_matchup(self, matchup):
        self.wl_records.append(matchup.record)
        if not matchup.game.is_consolation:
            self.matchups.append(matchup)
            self.games = len(self.matchups)
            self.wins += matchup.won
            self.losses += matchup.lost
            self.ties += matchup.tie
            self.pf += matchup.pf
            self.pa += matchup.pa
            self.ppg = self.pf / self.games
            self.pag = self.pa / self.games
        if matchup.game.is_playoffs:
            self.playoffs = True
        if matchup.game.is_championship and matchup.won:
            self.championship = True

    def record(self):
        str = "{0:.0f}-{1:.0f}".format(self.wins, self.losses)
        if self.ties > 0:
            str += "-{0:.0f}".format(self.ties)

        return str

    def playoff_chances(self):
        # 32 bit Python can only support recursion after week 8
        # 2^(5*5) = 33.5M
        # 2^(5*4) = 1.0M
        # 2^(5*3) = 32.7k
        # 2^(5*2) = 1024
        # 2^(5*1) = 32
        True


class Attributes:
    def __init__(self, owner):
        self.owner = owner
        self.mu = 0.0
        self.ssq = 0.0
        self.sigma = 0.0

    def update(self, n_games=10, weighted=True):
        matchups = make_list_games(self.owner.games)[-n_games:]
        if weighted:
            points = [[m.pf] * (i+1) for i, m in enumerate(matchups)]
            points = [p for sublist in points for p in sublist]
        else:
            points = [m.pf for m in matchups]

        self.mu = sum(points) / len(points)
        self.ssq = sum(p**2 for p in points)
        self.sigma = (1.0 / len(points)) * (len(points) * self.ssq - sum(points) ** 2) ** (0.5)


class Records:
    def __init__(self, owner):
        self.alltime_roster = roster.GameRoster()
        self.championships = {"All": Record()}
        self.divisions = {"East": {"All": Record()}, "West": {"All": Record()}}
        self.owner = owner
        self.opponents = {}
        self.overall = {"All": Record()}
        self.playoffs = {"All": Record()}
        self.personal = {"Most PF": [], "Fewest PF": [], "Highest Scoring": [], "Lowest Scoring": []}
        self.points_finish = {"All": []}
        self.postseason = {"All": Record()}
        self.regular_season = {"All": Record()}

    def to_string(self, info=True, ovrl="All", reg="All", post=False, plyf="All", div="All", opp="All", rcds="All"):
        str = "[b]" + self.owner.name + "[/b]\n"
        if info:
            ownr = self.owner
            str += "[u]Division[/u]: {}\n".format(ownr.division)
            str += "[u]Season{} Active[/u]: {}\n".format("" if len(ownr.active) == 1 else "s",
                                                         consecutive_years(ownr.active))
            str += "[u]Playoff Appearance{}[/u]: {}\n".format("" if len(ownr.playoffs) == 1 else "s",
                                                              consecutive_years(ownr.playoffs))
            str += "[u]Championship{}[/u]: {}\n\n".format("" if len(ownr.championships) == 1 else "s",
                                                          consecutive_years(ownr.championships))
        if ovrl:
            str += "[u]Overall[/u]: {}\n".format(self.overall[ovrl].to_string())
        if reg:
            str += "[u]Regular Season[/u]: {}\n".format(self.regular_season[reg].to_string())
        if post:
            str += "[u]Postseason[/u]: {}\n".format(self.postseason[post].to_string())
        if plyf:
            str += "[u]Playoffs[/u]: {}\n".format(self.playoffs[plyf].to_string())
        if div:
            str += "[u]East[/u]: {}\n".format(self.divisions["East"][div].to_string())
            str += "[u]West[/u]: {}\n".format(self.divisions["West"][div].to_string())
        if opp:
            ownrs = sorted([o for o in self.owner.league.owners], key=lambda p: (p[0].upper(), p[1]))
            ownrs.remove(self.owner.name)
            for i, on in enumerate(ownrs):
                str += "[u]{}[/u]: {}\n".format(on.split(" ")[0], self.opponents[on][opp].to_string())
            str += "\n"
        if rcds:
            mtch = self.personal["Most PF"][0]
            str += "[u]Most PF[/u]: {} pts, {} {} {} {} week {}\n".format(mtch.pf,
                                                                          "won" if mtch.won else "lost",
                                                                          "vs" if mtch.home else "at",
                                                                          mtch.opponent.name,
                                                                          mtch.year, mtch.week.number)
            mtch = self.personal["Fewest PF"][0]
            str += "[u]Fewest PF[/u]: {} pts, {} {} {} {} week {}\n".format(mtch.pf,
                                                                            "won" if mtch.won else "lost",
                                                                            "vs" if mtch.home else "at",
                                                                            mtch.opponent.name,
                                                                            mtch.year, mtch.week.number)
            mtch = self.personal["Highest Scoring"][0]
            str += "[u]Highest Scoring[/u]: {}, {} {} {} {} week {}\n".format(make_score(mtch.pf, mtch.pa),
                                                                              "won" if mtch.won else "lost",
                                                                              "vs" if mtch.home else "at",
                                                                              mtch.opponent.name,
                                                                              mtch.year, mtch.week.number)
            mtch = self.personal["Lowest Scoring"][0]
            str += "[u]Lowest Scoring[/u]: {}, {} {} {} {} week {}\n".format(make_score(mtch.pf, mtch.pa),
                                                                             "won" if mtch.won else "lost",
                                                                             "vs" if mtch.home else "at",
                                                                             mtch.opponent.name,
                                                                             mtch.year, mtch.week.number)

        return str


class Record:
    def __init__(self):
        self.all = 0
        self.wins = 0
        self.losses = 0
        self.ties = 0
        self.pf = 0.0
        self.pa = 0.0

    def pag(self):
        return self.pa / self.all

    def ppg(self):
        return self.pf / self.all

    def percent(self):
        return (self.wins + 0.5 * self.ties) / float(self.all)

    def record(self):
        str = "{0:.0f}-{1:.0f}".format(self.wins, self.losses)
        if self.ties > 0:
            str += "-{0:.0f}".format(self.ties)

        return str

    def to_string(self, wlt=True, pfpa=True):
        str = ""
        if wlt:
            str += "{0:.0f}-{1:.0f}".format(self.wins, self.losses)
            if self.ties > 0:
                str += "-{0:.0f}".format(self.ties)

        if pfpa:
            str += " ({0:.1f}-{1:.1f})".format(self.pf/self.all, self.pa/self.all)

        return str

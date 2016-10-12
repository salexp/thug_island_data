from fantasy_data import owner
from nfl_data import player
from nfl_data import roster
from util import *


class Schedule:
    def __init__(self, league, sh, year):
        self.complete = False
        self.league = league
        self.year = year

        self.week_list = []
        self.weeks = {}

        wek = 0
        for r in range(sh.nrows):
            if "WEEK" in sh.cell_value(r, 0) or "ROUND" in sh.cell_value(r, 0):
                wek += 1
                week = Week(self, str(wek), sh, r)
                self.add_week(week)
                self.complete = week.complete
                if self.complete:
                    self.league.years[year].current_week = week.number
                    self.league.years[year].current_year = year

    def add_week(self, w):
        self.week_list.append(w.number)
        self.weeks[w.number] = w


class Week:
    def __init__(self, schedule, wek, sh, i):
        self.alltime_roster = None
        self.complete = False
        self.league = schedule.league
        self.records = Records(self)
        self.schedule = schedule
        self.number = wek
        self.year = schedule.year

        self.games = []

        idx = 0
        while sh.cell_value(i, 0) != "" and i <= sh.nrows - 1:
            # If 'at'
            if sh.cell_value(i, 2) != "":
                idx += 1
                row = [sh.cell_value(i, c) for c in range(sh.ncols)]
                game = Game(self, row, index=idx, detailed=False)
                self.games.append(game)
                if game.played:
                    self.complete = True
                    schedule.current_week = wek
            i += 1
            if i == sh.nrows:
                break

    def add_details(self, sh):
        for c in range(sh.ncols):
            if sh.cell_value(1, c) in self.league.owners:
                game = self.find_game(sh.cell_value(1, c))

                table = []
                for ir in range(0, sh.nrows):
                    table.append([sh.cell_value(ir, ic) for ic in range(c, c + 5)])

                game.build_from_matchup(table)

    def find_game(self, owner_name):
        for game in self.games:
            if owner_name in [game.away_owner_name, game.home_owner_name]:
                return game

    def make_roster(self):
        rstr = roster.GameRoster()
        for game in self.games:
            for mtch in [game.away_matchup, game.home_matchup]:
                for plyr in mtch.roster.starters + mtch.roster.bench:
                    rstr.add_player(plyr, force="Bench")

        rstr.make_optimal()
        opt = rstr.optimal
        opt.update_points()
        self.alltime_roster = opt


class Game:
    def __init__(self, week, data, index, detailed=False):
        self.away_matchup = None
        self.away_owner = None
        self.away_owner_name = None
        self.away_record = None
        self.away_roster = []
        self.away_score = None
        self.away_team = None
        self.away_win = None
        self.detailed = detailed
        self.expended = None
        self.home_matchup = None
        self.home_owner = None
        self.home_owner_name = None
        self.home_record = None
        self.home_roster = []
        self.home_score = None
        self.home_team = None
        self.home_win = None
        self.index = index
        self.league = week.league
        self.played = False
        self.preview = None
        self.raw_details = None
        self.raw_summary = None
        self.schedule = week.schedule
        self.score = None
        self.week = week
        self.winner = None
        self.year = week.year
        self.is_regular_season = is_regular_season(self.year, self.week.number, self.index)
        self.is_postseason = is_postseason(self.year, self.week.number, self.index)
        self.is_consolation = is_consolation(self.year, self.week.number, self.index)
        self.is_playoffs = is_playoffs(self.year, self.week.number, self.index)
        self.is_championship = is_championship(self.year, self.week.number, self.index)

        if detailed:
            self.build_from_matchup(data)
        else:
            self.build_from_summary(data)

    def build_from_summary(self, row):
        self.raw_summary = row
        [self.away_team, self.away_record] = row[0].replace(" (", "(").replace(")", "").split("(")
        self.away_owner_name = row[1]
        [self.home_team, self.home_record] = row[3].replace(" (", "(").replace(")", "").split("(")
        self.home_owner_name = row[4]
        score = row[5]
        if score not in ["", "Preview"]:
            self.played = True
            self.score = score

        if self.away_owner_name not in self.league.owners:
            self.league.owners[self.away_owner_name] = owner.Owner(self.away_owner_name, self.league)
        away = self.league.owners[self.away_owner_name]
        if self.home_owner_name not in self.league.owners:
            self.league.owners[self.home_owner_name] = owner.Owner(self.home_owner_name, self.league)
        home = self.league.owners[self.home_owner_name]
        self.away_owner = self.league.owners[self.away_owner_name]
        self.home_owner = self.league.owners[self.home_owner_name]

        if self.played:
            self.away_score = float(score.split("-")[0])
            self.home_score = float(score.split("-")[1])
            self.winner = "Away" if self.away_score > self.home_score else "Home" \
                if self.away_score < self.home_score else "Tie"
            self.away_win = self.winner == "Away"
            self.home_win = self.winner == "Home"

        self.away_matchup = away.add_matchup(self, "Away")
        self.home_matchup = home.add_matchup(self, "Home")

    def build_from_matchup(self, data):
        self.detailed = True
        self.raw_details = data
        team_a = data[1][0]
        team_b = data[5][0]
        away = True if team_a == self.away_owner_name else False
        box_a_start = 10
        box_b_end = len(data) - 1
        for i in range(box_a_start + 1, len(data)):
            try:
                if "BOX SCORE" in data[i][0]:
                    box_a_end = i - 1
                    box_b_start = i
                    break
            except TypeError:
                pass

        box_a = data[box_a_start:box_a_end + 1]
        box_b = data[box_b_start:box_b_end + 1]
        boxscore_away = box_a if away else box_b
        boxscore_home = box_b if away else box_a

        for home, [boxscore, owner] in enumerate([[boxscore_away, self.away_owner_name], [boxscore_home, self.home_owner_name]]):
            owner = self.league.owners[owner]
            roster = []
            for r in boxscore:
                plyr = None
                if r[1] != "" and "PLAYER" not in r[1]:
                    slot = r[0]
                    name = player.get_name(r[1])
                    if name not in self.league.players:
                        self.league.players[name] = player.Player(r)
                    plyr = self.league.players[name]

                if plyr is not None:
                    mtup = self.home_matchup if home else self.away_matchup
                    plyr.update(mtup, r, slot)
                    roster.append(plyr)

            if home:
                self.home_roster = roster
            else:
                self.away_roster = roster

            owner.check_roster(mtup)

    def create_preview(self):
        preview = GamePreview(self)
        True


def is_regular_season(year, week, game):
    year = int(year)
    week = int(week)
    game = int(game)

    return week <= 13


def is_postseason(year, week, game):
    year = int(year)
    week = int(week)
    game = int(game)

    return week > 13


def is_consolation(year, week, game):
    return is_postseason(year, week, game) and not is_playoffs(year, week, game)


def is_playoffs(year, week, game):
    year = int(year)
    week = int(week)
    game = int(game)

    return (year == 2010 and week == 14 and game <= 2) \
           or (year == 2010 and week == 15 and game == 1) \
           or (year-2000 in [11, 12, 13, 14, 15, 16] and week in [14, 15] and game < 3) \
           or (week == 16 and game == 1)


def is_championship(year, week, game):
    year = int(year)
    week = int(week)
    game = int(game)

    return (year == 2010 and week == 15 and game == 1) \
           or (year-2000 in [11, 12, 13, 14, 15, 16] and week == 16 and game == 1)


class GamePreview:
    def __init__(self, game):
        self.away_favorite = False
        self.away_spread = 0.0
        self.favorite = None
        self.home_favorite = False
        self.home_spread = 0.0
        self.ou = 0.0
        self.spread = 0.0

        away_owner = game.away_owner
        away_owner.attrib.update()
        home_owner = game.home_owner
        home_owner.attrib.update()

        mu_a = away_owner.attrib.mu
        sigma_a = away_owner.attrib.sigma
        mu_h = home_owner.attrib.mu
        sigma_h = home_owner.attrib.sigma

        point_range = range(int(min([mu_a, mu_h]) - max([sigma_a, sigma_h])) * 100,
                            int(max([mu_a, mu_h]) + max([sigma_a, sigma_h])) * 100)

        diff = 99999.9
        intercept = None
        for hpts in point_range:
            pts = hpts / 100.0
            diff_temp = float(abs(normpdf(pts, mu_a, sigma_a) - normpdf(pts, mu_h, sigma_h)))
            if diff_temp < diff:
                diff = diff_temp
                intercept = hpts

        points = intercept / 100.0
        self.ou = 2 * points
        sum_a = sumpdf(points, mu_a, sigma_a)
        sum_h = sumpdf(points, mu_h, sigma_h)

        away_opp = away_owner.records.opponents[home_owner.name]["All"]
        away_year = away_owner.records.overall[game.year]
        home_opp = home_owner.records.opponents[away_owner.name]["All"]
        home_year = home_owner.records.overall[game.year]
        pct_a = 0.9 * sum_a / (sum_a + sum_h) + 0.1 * away_opp.percent()
        pct_h = 0.9 * sum_h / (sum_a + sum_h) + 0.1 * home_opp.percent()

        adjm = 1.0
        spreads = [None, None]
        odds = [None, None]
        money_lines = [None, None]
        for i, pct in enumerate([pct_a, pct_h]):
            ownr_opp = home_opp if i else away_opp
            ownr_year = home_year if i else away_year
            if pct > 0.5:
                mline = pct / (1.0 - pct) * (-100.0)
            else:
                mline = (1.0 - pct) / pct * 100
            mline = int(mline / abs(mline)) * ((abs(mline) - 100) / adjm + 100)
            mline = int(round(mline * 2, -1) / 2) if mline != 100 else "PUSH"
            money_lines[i] = mline
            spread = int((0.65 * (ownr_opp.pf - ownr_opp.pa) + 0.35 *
                          (ownr_year.pf - ownr_year.pa)) * 20) / 20.0
            spreads[i] = abs(spread) * (-1 if mline < 0 else 1)
            spreads[i] = str(spreads[i]).rjust(len(str(abs(spreads[i]))) + 1, '+')
            if not i:
                m_x = mu_a
                s_x = sigma_a
                m_y = mu_h
                s_y = sigma_h
            if i:
                m_x = mu_h
                s_x = sigma_h
                m_y = mu_a
                s_y = sigma_a
            odd = sumpdf(m_y + s_y ** (1.0 + (abs(s_x - s_y) / max(s_x, s_y))), m_x, s_x)
            odds[i] = odd

        ava = 0.5 - sum(odds) / len(odds)
        odds[0] += ava
        odds[1] += ava
        new_odds = [None, None]
        for i, odd in enumerate(odds):
            if odd > 0.5:
                line = odd / (1.0 - odd) * (-100.0)
            else:
                line = (1.0 - odd) / odd * 100
            line = abs(int(round(line * 2, -1) / 2))
            if abs(line) < 104:
                line = 'PUSH'
            new_odds[i] = line * abs(money_lines[i]) / money_lines[i]
            if new_odds[i] not in ['PUSH', 'OFF'] and money_lines[i] not in ['PUSH', 'OFF']:
                if abs(new_odds[i]) > abs(money_lines[i]):
                    new_odds[i] = 'OFF'

        self.away_favorite = False
        self.away_spread = 0.0
        self.favorite = None
        self.home_favorite = False
        self.home_spread = 0.0
        self.spread = -abs(spread)

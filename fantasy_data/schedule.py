from fantasy_data import owner
from nfl_data import player


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

    def add_week(self, w):
        self.week_list.append(w.number)
        self.weeks[w.number] = w


class Week:
    def __init__(self, schedule, wek, sh, i):
        self.complete = False
        self.league = schedule.league
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


class Game:
    def __init__(self, week, data, index, detailed=False):
        self.away_matchup = None
        self.away_owner = None
        self.away_owner_name = None
        self.away_record = None
        self.away_roster = []
        self.away_score = None
        self.away_team = None
        self.detailed = detailed
        self.expended = None
        self.home_matchup = None
        self.home_owner = None
        self.home_owner_name = None
        self.home_record = None
        self.home_roster = []
        self.home_score = None
        self.home_team = None
        self.index = index
        self.league = week.league
        self.played = False
        self.raw_details = None
        self.raw_summary = None
        self.schedule = week.schedule
        self.week = week
        self.winner = None
        self.year = week.year
        self.is_regular_season = is_regular_season(self.year, self.week.number, self.index)
        self.is_postseason = is_postseason(self.year, self.week.number, self.index)
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
            True

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

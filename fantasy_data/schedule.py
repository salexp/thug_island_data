from fantasy_data import owner


class Schedule:
    def __init__(self, league, sh, year):
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

    def add_week(self, w):
        self.week_list.append(w.number)
        self.weeks[w.number] = w


class Week:
    def __init__(self, schedule, wek, sh, i):
        self.league = schedule.league
        self.schedule = schedule
        self.number = wek
        self.year = schedule.year

        self.games = []

        idx = 0
        while sh.cell_value(i, 0) != "" and i < sh.nrows-1:
            # If 'at'
            if sh.cell_value(i, 2) != "":
                idx += 1
                row = [sh.cell_value(i, c) for c in range(sh.ncols)]
                game = Game(self, row, index=idx, detailed=False)
                self.games.append(game)
            i += 1
            True


class Game:
    def __init__(self, week, data, index, detailed=False):
        self.away_owner = None
        self.away_record = None
        self.away_score = None
        self.away_team = None
        self.detailed = detailed
        self.full_details = None
        self.home_owner = None
        self.home_record = None
        self.home_score = None
        self.home_team = None
        self.index = index
        self.league = week.league
        self.played = False
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
        [self.away_team, self.away_record] = row[0].replace(" (", "(").replace(")", "").split("(")
        self.away_owner = row[1]
        [self.home_team, self.home_record] = row[3].replace(" (", "(").replace(")", "").split("(")
        self.home_owner = row[4]
        score = row[5]
        if score not in ["", "Preview"]:
            self.played = True

        if self.away_owner not in self.league.owners:
            self.league.owners[self.away_owner] = owner.Owner(self.away_owner)
        away = self.league.owners[self.away_owner]
        if self.home_owner not in self.league.owners:
            self.league.owners[self.home_owner] = owner.Owner(self.home_owner)
        home = self.league.owners[self.home_owner]

        if self.played:
            self.away_score = float(score.split("-")[0])
            self.home_score = float(score.split("-")[1])
            self.winner = "Away" if self.away_score > self.home_score else "Home" \
                if self.away_score < self.home_score else "Tie"
            True

        away.add_matchup(self, "Away")
        home.add_matchup(self, "Home")

    def build_from_matchup(self, data):
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

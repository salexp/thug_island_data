from fantasy_data import schedule


class League:
    def __init__(self, name):
        self.league_name = name
        self.schedule = {}
        self.owners = {}
        self.years = []

    def add_schedule(self, year, sheet):
        self.schedule[year] = schedule.Schedule(self, sheet, year)
        self.years = sorted(self.years + [year])

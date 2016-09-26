class Rankings:
    def __init__(self, league):
        self.owners = {}
        self.week = None
        self.year = None

    def add_owner(self, owner, year, week):
        if owner.name not in self.owners:
            self.week = week
            self.year=year
            mtrcs = Metrics(self, owner)
            self.owners[owner.name] = mtrcs

        True


class Metrics:
    def __init__(self, rankings, owner, length=None):
        self.owner = owner
        self.week = rankings.week
        self.year = rankings.year
        self.qb = []
        self.rb = []
        self.wr = []
        self.te = []
        self.dst = []
        self.k = []
        self.bench = []
        self.wpct = 0.0
        self.plob = 0.0

        if length is None:
            length = int(self.week)
        years = [str(y) for y in range(int(self.year)-1, int(self.year)+1)]
        matchups = []
        for y in years:
            matchups += owner.seasons[y].matchups

        matchups = matchups[-length:]
        for matchup in matchups:
            self.qb.append(matchup.roster.qb.points)
            self.rb.append(matchup.roster.rb1.points)
            self.rb.append(matchup.roster.rb2.points)
            if matchup.roster.rb3 is not None:
                self.rb.append(matchup.roster.rb3.points)
            self.wr.append(matchup.roster.wr1.points)
            self.wr.append(matchup.roster.wr2.points)
            if matchup.roster.wr3 is not None:
                self.wr.append(matchup.roster.wr3.points)
            self.te.append(matchup.roster.te.points)
            self.dst.append(matchup.roster.dst.points)
            self.k.append(matchup.roster.k.points)
            self.bench.append(matchup.roster.bench_points / len(matchup.roster.bench))
            for pg in matchup.roster.bench:
                plyr = pg.player
                pts = pg.points
                if plyr.position == "QB":
                    self.qb.append(pts)
                elif plyr.position == "RB":
                    self.rb.append(pts)
                elif plyr.position == "WR":
                    self.wr.append(pts)
                elif plyr.position == "TE":
                    self.te.append(pts)
                elif plyr.position == "D/ST":
                    self.dst.append(pts)
                elif plyr.position == "K":
                    self.k.append(pts)

            self.wpct += matchup.won

            matchup.roster.make_optimal()
            self.plob += (matchup.roster.optimal.starter_points - matchup.roster.starter_points)

        self.qb = sorted(self.qb, reverse=True)
        self.rb = sorted(self.rb, reverse=True)
        self.wr = sorted(self.wr, reverse=True)
        self.te = sorted(self.te, reverse=True)
        self.dst = sorted(self.dst, reverse=True)
        self.k = sorted(self.k, reverse=True)

        if len(self.qb) > 1.5 * length:
            self.qb = self.qb[:int(1.5*length)]
        if len(self.rb) > 3 * length:
            self.rb = self.rb[:int(3*length)]
        if len(self.wr) > 3 * length:
            self.wr = self.wr[:int(3*length)]
        if len(self.te) > 1.5 * length:
            self.te = self.te[:int(1.5*length)]
        if len(self.dst) > 1.5 * length:
            self.dst = self.dst[:int(1.5*length)]
        if len(self.k) > 1.5 * length:
            self.k = self.k[:int(1.5*length)]

        self.qb = sum(self.qb) / len(self.qb)
        self.rb = sum(self.rb) / len(self.rb)
        self.wr = sum(self.wr) / len(self.wr)
        self.te = sum(self.te) / len(self.te)
        self.dst = sum(self.dst) / len(self.dst)
        self.k = sum(self.k) / len(self.k)
        self.wpct /= length
        self.plob /= length

        True

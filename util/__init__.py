from itertools import groupby
from operator import itemgetter


def add_ranks(list, compare_index=None):
    rks = range(1, len(list) + 1)
    for line in list:
        ind = list.index(line)
        if ind > 0:
            if compare_index is None:
                compare = [sum(list[ind][1]) / list[ind][2], sum(list[ind-1][1]) / list[ind-1][2]]
            else:
                compare = [list[ind][compare_index], list[ind - 1][compare_index]]
            if compare[0] == compare[1]:
                rks[ind-1] = 'T{}'.format(rks[ind-1].replace('T', ''))
                rks[ind] = rks[ind-1]
            else:
                rks[ind] = '{}'.format(rks[ind])
        else:
            rks[ind] = '{}'.format(rks[ind])

    for rk in rks:
        if '1' in rk and '10' not in rk:
            new = rk + 'st'
        elif '2' in rk[-1]:
            new = rk + 'nd'
        elif '3' in rk[-1]:
            new = rk + 'rd'
        elif rk[-1] == '1' and '11' not in rk:
            new = rk + 'st'
        else:
            new = rk + 'th'
        rks[rks.index(rk)] = new

    return [x + [rks[list.index(x)]] for x in list]


def add_suffix(num):
    num = str(num)
    if '1' in num and '10' not in num:
        new = num + 'st'
    elif '2' in num[-1]:
        new = num + 'nd'
    elif '3' in num[-1]:
        new = num + 'rd'
    elif num[-1] == '1' and '11' not in num:
        new = num + 'st'
    else:
        new = num + 'th'

    if len(new) == 3:
        new += ")"

    return new


def average(list, rnd = 1):
    if len(list) != 0:
        avg = round(sum(list) / len(list), rnd)
    else:
        avg = 0

    return avg


def consecutive_years(years):
    ranges = []
    yrs = [int(y) for y in years]
    for key, group in groupby(enumerate(yrs), lambda (index, item): index - item):
        group = map(itemgetter(1), group)
        ranges.append((group[0], group[-1]))

    str = ""
    for i, rng in enumerate(ranges):
        if rng[0] == rng[1]:
            str += "{}".format(rng[0])
        else:
            str += "{}-{}".format(rng[0], rng[1])
        if i < len(ranges)-1:
            str += ", "

    if str == "":
        str = "None"

    return str


def get_initials(name):
    fi = name.split(' ')[0][0]
    li = name.split(' ')[1][0]

    return fi + li


def get_team(yr, xr, sht):
    if 'D/ST' not in sht.cell_value(yr, xr):
        tmm = sht.cell_value(yr, xr).split(', ')[1].split(u'\xa0')[0].upper()
        tmm = tmm.replace('JAC', 'JAX')
        tmm = tmm.replace('WAS', 'WSH')
    else:
        tmm = sht.cell_value(yr, xr).split(' D/ST')[0]
        tmm = nfl_names[tmm]

    return tmm


def get_oppnt(yr, xr):
    val = sh.cell_value(yr, xr)

    oppnt = val.replace('@', '').replace('*', '').replace(' ', '').upper().replace('JAC', 'JAX').replace('WAS', 'WSH')

    return oppnt


def make_score(pa, pb):
    return "{}-{}".format(pa if pa > pb else pb, pa if pa < pb else pb)


def normpdf(x, mu = 1.0, sigma = 1.0):
    sigma += 0.000001
    var = float(sigma) ** 2
    pi = 3.1415926
    denom = (2 * pi * var) ** .5
    num = exp(-(float(x) - float(mu)) ** 2 / (2 * var))

    return num / denom


def remove_dupes(list):
    seen = set()
    seen_add = seen.add
    return [x for x in list if not (x in seen or seen_add(x))]


def sumpdf(x, mu = 1.0, sigma = 1.0):
    sigma += 0.000001
    sum = 0.0
    for i in range(int(x * 100)):
        j = i / 100.0
        var = float(sigma) ** 2
        pi = 3.1415926
        denom = (2 * pi * var) ** .5
        num = exp(-(float(j) - float(mu)) ** 2 / (2 * var))
        sum += (num / denom) * 0.01

    return 1 - sum

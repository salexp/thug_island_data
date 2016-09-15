def add_all_players(plyr, pos = None):
    if plyr not in all_players.keys(): all_players[plyr] = {}
    if year not in all_players[plyr].keys(): all_players[plyr][year] = {'Position' : pos, 'Team' : None, 'Scores' : []}
    if 'Current Owner' not in all_players[plyr].keys(): all_players[plyr]['Current Owner'] = None
    if 'Drafted' not in all_players[plyr].keys(): all_players[plyr]['Drafted'] = []
    if 'Keeper' not in all_players[plyr].keys(): all_players[plyr]['Keeper'] = []

def add_ranks(list, comp = None):
    rks = range(1, len(list) + 1)
    for line in list:
        ind = list.index(line)
        if ind > 0:
            if comp is None:
                compare = [sum(list[ind][1]) / list[ind][2], sum(list[ind-1][1]) / list[ind-1][2]]
            else:
                compare = [list[ind][comp], list[ind-1][comp]]
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

    return new

def average(list, rnd = 1):
    if len(list) != 0:
        avg = round(sum(list) / len(list), rnd)
    else:
        avg = 0

    return avg

def f_played_weeks(dict):
    plyd = []
    for wk in range(1, 16):
        if ranks[str(wk)]['Played']: plyd.append(str(wk))

    return plyd

def f_current_week(dict):
    plyd = []
    for wk in range(1, 17):
        plyd.append(ranks[str(wk)]['Played'])

    return str(plyd.index(False))

def get_initials(name):
    fi = name.split(' ')[0][0]
    li = name.split(' ')[1][0]

    return fi + li

def get_name(yr, xr, sht):
    if 'D/ST' not in sht.cell_value(yr, xr):
        nam = sht.cell_value(yr, xr).split(',')[0].replace('*', '')
    else:
        nam = sht.cell_value(yr, xr).split(u'\xa0')[0].replace('*', '').split(',')[0]

    return nam

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

def get_position(yr, xr, sht):
    pos = []
    if 'QB' in sht.cell_value(yr, xr):
        pos.append('QB')
    if 'RB' in sht.cell_value(yr, xr):
        pos.append('RB')
    if 'WR' in sht.cell_value(yr, xr):
        pos.append('WR')
    if 'TE' in sht.cell_value(yr, xr):
        pos.append('TE')
    if 'D/ST' in sht.cell_value(yr, xr):
        pos.append('DST')
    if 'K' in sht.cell_value(yr, xr).replace(u'\xa0', u' ').split(' '):
        pos.append('K')
    if pos == []:
        pos = [None]

    return pos

def get_score(yr, xr):
    val = sh.cell_value(yr, xr)
    if '--' == val:
        scr = 0.0
    else:
        scr = round(val, 1)

    return scr

def make_record(list):
    if list[2] != 0:
        return '{0}-{1}-{2}'.format(list[0], list[1], list[2])
    else:
        return '{0}-{1}'.format(list[0], list[1])

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

"""
Thug Island Fantasy League Stats and Computer Rankings - Stuart Petty (stu.petty92@gmail.com)
Created for 2015 season
"""

import pprint as pp
import xlrd
from datetime import datetime
from copy import copy
from copy import deepcopy
from math import exp

from fantasy_data import league
from fantasy_data import schedule
from util import *

#======================================================
# Setup
#======================================================

f = open('ff_data.txt', 'w')
all_players = {}
data = {}
draft = {}
ranks = {}
schedule = {}
team_names = {}
nfl_teams = {'ARI' : {}, 'ATL' : {}, 'BAL' : {}, 'BUF' : {}, 'CAR' : {}, 'CHI' : {}, 'CIN' : {}, 'CLE' : {}, 'DAL' : {}, 'DEN' : {}, \
    'DET' : {}, 'GB' : {}, 'HOU' : {}, 'IND' : {}, 'JAX' : {}, 'KC' : {}, 'MIA' : {}, 'MIN' : {}, 'NE' : {}, 'NO' : {}, 'NYG' : {}, \
    'NYJ' : {}, 'OAK' : {}, 'PHI' : {}, 'PIT' : {}, 'SD' : {}, 'SEA' : {}, 'SF' : {}, 'STL' : {}, 'TB' : {}, 'TEN' : {}, 'WSH' : {}, 'FA' : {}}
nfl_teams_list = {'ARI' : [], 'ATL' : [], 'BAL' : [], 'BUF' : [], 'CAR' : [], 'CHI' : [], 'CIN' : [], 'CLE' : [], 'DAL' : [], 'DEN' : [], \
    'DET' : [], 'GB' : [], 'HOU' : [], 'IND' : [], 'JAX' : [], 'KC' : [], 'MIA' : [], 'MIN' : [], 'NE' : [], 'NO' : [], 'NYG' : [], \
    'NYJ' : [], 'OAK' : [], 'PHI' : [], 'PIT' : [], 'SD' : [], 'SEA' : [], 'SF' : [], 'STL' : [], 'TB' : [], 'TEN' : [], 'WSH' : [], 'FA' : []}
blank_nfl = deepcopy(nfl_teams)
for key in nfl_teams.keys():
    nfl_teams[key] = {'QB' : [], 'RB' : [], 'WR' : [], 'TE' : [], 'DST' : [], 'K' : [], 'Players' : {}}
    nfl_teams[key]['Players'] = {'QB' : {}, 'RB' : {}, 'WR' : {}, 'TE' : {}, 'DST' : {}, 'K' : {}}
nfl_names = {'ARI' : 'Cardinals', 'ATL' : 'Falcons', 'BAL' : 'Ravens', 'BUF' : 'Bills', 'CAR' : 'Panthers', 'CHI' : 'Bears', 'CIN' : 'Bengals', 'CLE' : 'Browns', 'DAL' : 'Cowboys', 'DEN' : 'Broncos', \
    'DET' : 'Lions', 'GB' : 'Packers', 'HOU' : 'Texans', 'IND' : 'Colts', 'JAX' : 'Jaguars', 'KC' : 'Chiefs', 'MIA' : 'Dolphins', 'MIN' : 'Vikings', 'NE' : 'Patriots', 'NO' : 'Saints', 'NYG' : 'Giants', \
    'NYJ' : 'Jets', 'OAK' : 'Raiders', 'PHI' : 'Eagles', 'PIT' : 'Steelers', 'SD' : 'Chargers', 'SEA' : 'Seahawks', 'SF' : '49ers', 'STL' : 'Rams', 'TB' : 'Buccaneers', 'TEN' : 'Titans', 'WSH' : 'Redskins', \
    'FA' : 'Free Agents'}
nfl_names.update({v: k for k, v in nfl_names.items()})

owners = []
temp_var = 0.0

andrew = 'Andrew Lee'; ben = 'Ben Mytelka'; cody = 'Cody Blain'; connor = 'Connor Wiseman'; eric = 'Eric Price'
jimmy = 'James Furlong'; josh = 'josh watson'; rande = 'Rande Revilla'; stu = 'Stuart Petty'; tom = 'Thomas Singleton'
trevor = 'Trevor Watson'
divisions = ['East', 'West']
east = [andrew, connor, jimmy, josh, stu]
west = [ben, cody, eric, rande, tom, trevor]
owners = {}
owners = [andrew, ben, cody, connor, eric, jimmy, josh, rande, stu, tom, trevor]
years = ['2010', '2011', '2012', '2013', '2014', '2015']
num_keepers = {'2010' : 0, '2011' : 2, '2012' : 3, '2013' : 4, '2014' : 5, '2015' : 6, '2016' : 7, '2017' : 8}

# draft_book = xlrd.open_workbook('thug_island_draft.xls')
# espn = open('espn_standings.txt', 'r')
# espn_standings = espn.read().split(',')
# espn.close()

pick_trades = [ \
    # Giving, Year, Round, Receiving
    # 2017
    [connor, '2017', '2', eric],
    [tom, '2017', '4', eric],

    ]
max_rnds = {}
for trd in pick_trades:
    if trd[1] not in max_rnds.keys(): max_rnds[trd[1]] = 0
    max_rnds[trd[1]] = int(trd[2]) if int(trd[2]) > max_rnds[trd[1]] else max_rnds[trd[1]]

#===============Functions===============

def create_lineup(_ownr = stu, _prev = 0, _type = 'avg'):
    lineup = {'QB' : [[None, 0.0]], 'RB' : [[None, 0.0], [None, 0.0]], 'WR' : [[None, 0.0], [None, 0.0]], 'FLX' : [[None, 0.0]], 'TE' : [[None, 0.0]], 'DST' : [[None, 0.0]], 'K' : [[None, 0.0]]}
    if _type == 'avg':
        for posi in lineup.keys():
            if posi != 'FLX':
                pos = posi
                top_scr = lineup[pos][-1][1]
                for plyr in teams[_ownr]['Roster'][pos].keys():
                    scr = average(teams[_ownr]['Roster'][pos][plyr][-_prev:])
                    if scr > top_scr:
                        lineup[pos] = [[plyr, scr], copy(lineup[pos])[0]][:len(lineup[pos])]
                        top_scr = scr

            else:
                pass

    return lineup


def drafted_players(_ownrs, _teams):
    for _team in _teams:
        for _ownr in _ownrs:
            picks = 0
            for plyr in teams[_ownr]['Teams'][_team].keys():
                picks += len(teams[_ownr]['Teams'][_team][plyr])

            print '{0} - {1} player{3} with {2} pick{4}'.format(_ownr, len(teams[_ownr]['Teams'][_team]), picks, 's' if len(teams[_ownr]['Teams'][_team]) != 1 else '', 's' if picks != 1 else '')
            for plyr in teams[_ownr]['Teams'][_team].keys():
                print plyr
                for drft in teams[_ownr]['Teams'][_team][plyr]:
                    print '{0} round {1} pick {2}'.format(drft[0], drft[1], drft[2])

            print ''


def playoff_hopes(_ownrs = owners, file = None):
    if file is not None:
        phf = open(file, 'w')
    for ownr in _ownrs:
        if file is None: print ownr
        if file is not None: print >> phf, ownr
        i = -1
        for gme in gme_scn_list:
            i += 1
            if i % (len(owners) / 2) == 0 and file is None: print 'Week'
            if i % (len(owners) / 2) == 0 and file is not None: print >> phf, 'Week'
            if file is None: print '{0:.3f} {1} - {2} {3:.3f}'.format(abs(1-imp_gme[ownr][i]), gme_scn_list[i][0], gme_scn_list[i][1], abs(imp_gme[ownr][i]))
            if file is not None: print >> phf, '{0:.3f} {1} - {2} {3:.3f}'.format(abs(1-imp_gme[ownr][i]), gme_scn_list[i][0], gme_scn_list[i][1], abs(imp_gme[ownr][i]))

        if file is None: print ''
        if file is not None: print >> phf, ''
#===============End===============


def game_analysis(league, work_book, years):
    schedule = {}
    #     # Build draft dictionary
    #     draft[year] = {}
    #     per_rnd = 0
    #     num_kpr = num_keepers[year]
    #     for side in [0, 3]:
    #         for i in range(dsh.nrows):
    #             if 'ROUND' in str(dsh.cell_value(i, side)):
    #                 rnd = str(int(dsh.cell_value(i, side).split(' ')[1]))
    #                 draft[year][rnd] = {}
    #                 if rnd > '1' and per_rnd == 0:
    #                     per_rnd = int(dsh.cell_value(i - 1, side))
    #             elif '.' in str(dsh.cell_value(i, side)):
    #                 ovr_pck = str(dsh.cell_value(i, side)).split('.')[0]
    #                 if rnd == '1':
    #                     pck = ovr_pck
    #                 else:
    #                     pck = str(int(ovr_pck) % per_rnd) if int(ovr_pck) % per_rnd != 0 else per_rnd
    #                 plyr = get_name(i, side + 1, dsh)
    #                 pos = get_position(i, side + 1, dsh)
    #                 nflt = get_team(i, side + 1, dsh)
    #                 kpr = False
    #                 if len(pos) > 1:
    #                     if pos[1] == 'K':
    #                         kpr = True
    #                         pos = [pos[0]]
    #                 tmnm = str(dsh.cell_value(i, side + 2))
    #                 ownr = team_names[tmnm]
    #                 draft[year][rnd][pck] = {'Player': plyr, 'Position' : pos, 'Team' : nflt, 'Owner' : ownr, 'Keeper' : kpr}
    #                 if plyr not in all_players.keys():
    #                     all_players[plyr] = {'Drafted' : [], 'Keeper' : [], 'Current Owner' : None}
    #
    #                 if kpr:
    #                     all_players[plyr]['Keeper'].append([ownr, year])
    #                 elif not kpr:
    #                     all_players[plyr]['Drafted'].append([ownr, year, str(int(rnd) - num_kpr), pck, ovr_pck])
    #                 all_players[plyr][year] = {'Position' : pos, 'Team' : nflt, 'Scores' : []}
    #
    # # Build future draft with trades
    # drft_years = sorted(list(set([trd[1] for trd in pick_trades])))
    # for year in drft_years:
    #     if year not in draft.keys(): draft[year] = {}
    #     rnds = max([int(rnd) for rnd in draft[years[-1]]])
    #     pcks = max([int(pck) for pck in draft[years[-1]]['1']])
    #     for r in range(1, rnds + 1):
    #         draft[year][str(r)] = {}
    #         for p in range(1, pcks + 1):
    #             draft[year][str(r)][str(p)] = {'Player': None, 'Position' : None, 'Owner' : espn_standings[::-1][p - 1], 'Keeper' : r <= num_keepers[year], 'From' : [], 'Original' : espn_standings[::-1][p - 1]}
    #
    # for trd in pick_trades:
    #     r = str(int(trd[2]) + num_keepers[trd[1]])
    #     p = '1'
    #     while draft[trd[1]][r][p]['Original'] != trd[0]:
    #         p = str(int(p) + 1)
    #         if int(p) > pcks:
    #             raw_input('Error with {}'.format(trd))
    #     draft[trd[1]][r][p]['From'].append(draft[trd[1]][r][p]['Owner'])
    #     draft[trd[1]][r][p]['Owner'] = trd[3]
    #
    # # Output future draft
    # df = open('ff_draft_picks.txt', 'w')
    #
    # for year in drft_years:
    #     print >> df, '[b]{} Draft Picks[/b]'.format(year)
    #     for rnd in range(1, max_rnds[year] + 1):
    #         print >> df, '[u]Round {}[/u]'.format(rnd)
    #         for p in range(1, pcks + 1):
    #             frm_str = '(From {}'.format(draft[year][str(rnd + num_keepers[year])][str(p)]['Original'].split(' ')[0]) if len(draft[year][str(rnd + num_keepers[year])][str(p)]['From']) > 0 else ''
    #             if len(draft[year][str(rnd + num_keepers[year])][str(p)]['From']) > 1:
    #                 for frm_ownr in draft[year][str(rnd + num_keepers[year])][str(p)]['From'][1:]:
    #                     frm_str += ' via {}'.format(frm_ownr.split(' ')[0][0] + frm_ownr.split(' ')[1][0])
    #             frm_str += ')' if len(frm_str) > 0 else ''
    #             print >> df, '{}) {} {}'.format(p, draft[year][str(rnd + num_keepers[year])][str(p)]['Owner'], frm_str)
    #
    #         print >> df, ''
    #
    # df.close()

    return schedule, draft


def team_analysis():
    None

def draft_history():
    for plyrd in all_players.keys():
        for drftd in all_players[plyrd]['Drafted']:
            ownrd = drftd[0]
            yeard = drftd[1]
            rndd = drftd[2]
            pckd = drftd[3]
            ovr_pckd = drftd[4]
            if plyrd not in teams[ownrd]['Drafted'].keys():
                teams[ownrd]['Drafted'][plyrd] = []
            teams[ownrd]['Drafted'][plyrd].append([yeard, rndd, pckd, ovr_pckd])
            if plyrd not in teams[ownrd]['Teams'][all_players[plyrd][yeard]['Team']].keys():
                teams[ownrd]['Teams'][all_players[plyrd][yeard]['Team']][plyrd] = []
            teams[ownrd]['Teams'][all_players[plyrd][yeard]['Team']][plyrd].append([yeard, rndd, pckd, ovr_pckd])


def ranking_analysis():
    pnts = []
    ypnts = []
    for year in years:
        if year < years[-1]:
            if (year == '2013' and ownr == tom) or (year == '2010' and ownr in [jimmy, rande]):
                pass
            else:
                for i in range(13):
                    iis = str(i + 1)
                    # pnts += [schedule[year][iis][ownr]['PF'] for x in range((years.index(year) + 1) ** (years.index(year) + 1))]
                    pnts += [schedule[year][iis][ownr]['PF']]
        else:
            for i in range(week):
                # pnts += [schedule[year][str(i+1)][ownr]['PF'] for x in range((years.index(year) + 1) ** (years.index(year) + 1))]
                if ownr in schedule[year][str(i+1)].keys():
                    pnts += [schedule[year][str(i+1)][ownr]['PF']]
                    ypnts.append(schedule[year][str(i + 1)][ownr]['PF'])
                elif year in teams[ownr]['Byes']:
                    pass
                else:
                    pnts += [schedule[year][str(i+1)][ownr]['PF']]
                    ypnts.append(schedule[year][str(i + 1)][ownr]['PF'])


    npnts = pnts[-13:]
    pnts = []
    i = 0
    for wpnt in npnts:
        i += 1
        pnts += [wpnt for j in range(i)]

    mu = sum(pnts) / len(pnts)
    ssq = sum([i**2 for i in pnts])
    sigma = (1.0 / len(pnts)) * (len(pnts) * ssq - sum(pnts) ** 2) ** (0.5)
    ymu = sum(ypnts) / len(ypnts)
    yssq = sum([i**2 for i in ypnts])
    ysigma = (1.0 / len(ypnts)) * (len(ypnts) * yssq - sum(ypnts) ** 2) ** (0.5)
    ranks[weeks][ownr]['Stat'] = [[mu, sigma, sum(pnts), ssq, len(pnts)], [ymu, ysigma, sum(ypnts), yssq, len(ypnts)]]

    played_weeks = f_played_weeks(ranks)
    current_week = f_current_week(ranks)
    prev_week = str(int(current_week) - 1)
    next_week = str(int(current_week) + 1)
    # last_week = max([int(wk) for wk in ranks.keys()])
    last_week = 13
    weeks_left = last_week - int(current_week)
    tf = open('ff_data/top_{}.txt'.format(current_week), 'w')
    print >> tf, schedule['Records']['Max All Games']
    tf.close()
    ftf = open('ff_data/few_{}.txt'.format(current_week), 'w')
    print >> ftf, schedule['Records']['Min All Games']
    ftf.close()
    current_year = years[-1]
    best_games = add_ranks(schedule['Records']['Max All Games'], 3)
    fewest_games = add_ranks(schedule['Records']['Min All Games'], 3)
    best_year_games = add_ranks(schedule['Records'][year]['Max All Games'], 3)
    fewest_year_games = add_ranks(schedule['Records'][year]['Min All Games'], 3)
    schedule['Records']['Max All Games'] = best_games
    schedule['Records']['Min All Games'] = fewest_games
    schedule['Records'][year]['Max All Games'] = best_year_games
    schedule['Records'][year]['Min All Games'] = fewest_year_games
    for weks in played_weeks:
        metrics[weks] = {}

        #===============Player Ranks===============

        player_ranks = {'QB' : [], 'RB' : [], 'WR' : [], 'TE' : [], 'DST' : [], 'K' : [], 'Average' : []}
        plyr_dict = {'QB' : [], 'RB' : [], 'WR' : [], 'TE' : [], 'DST' : [], 'K' : [], 'Average' : []}
        for pos in positions:
            plyr_dict[pos] = {}
            for ownr in owners:
                plyrs = []
                num_pl = 0.0
                plyr_dict[pos][ownr] = []
                plyrs += ranks[weks][ownr]['Starters'][pos][0]
                num_pl += ranks[weks][ownr]['Starters'][pos][1]

                player_ranks[pos].append([ownr, plyrs, num_pl])

            temp = sorted(player_ranks[pos], key = lambda prm: sum(prm[1]) / prm[2], reverse = True)
            player_ranks[pos] = add_ranks(temp)
            for line in player_ranks[pos]:
                plyr_dict[pos][line[0]] = line
                ranks[weks][line[0]]['Starters'][pos][2] = line[3]

            print pos
            for line in player_ranks[pos]: print line
            print ''

        pwgt = {'QB' : 1.5, 'RB' : 2.0, 'WR' : 2.0, 'TE' : 1.0, 'DST' : 1.0, 'K' : 0.5}
        for ownr in owners:
            i = 0
            arnk = 0.0
            ttl = 0.0
            for pos in positions:
                i += 1
                rw = int(ranks[weks][ownr]['Starters'][pos][2].replace('T', '').replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')) * pwgt[pos]
                arnk += rw
                ttl += pwgt[pos]

            arnk = arnk / ttl
            player_ranks['Average'].append([ownr, [arnk], 1.0])

        temp = sorted(player_ranks['Average'], key = lambda prm: sum(prm[1]) / prm[2], reverse = False)
        tempp = add_ranks(temp)
        # player_ranks['Average'] = [[x[0], round(tempp[0][1][0] / x[1][0], 4), round(x[1][0], 2), x[3]] for x in tempp] # Normalized to best
        # player_ranks['Average'] = [[x[0], round(1.0 / x[1][0], 4), round(x[1][0], 2), x[3]] for x in tempp] # Normalized to 1.0
        player_ranks['Average'] = [[x[0], round((1.0 / x[1][0])**0.33, 4), round(x[1][0], 2), x[3]] for x in tempp] # Normalized to sqrt
        plyr_dict['Average'] = {}
        for line in player_ranks['Average']:
            plyr_dict['Average'][line[0]] = line

        metrics[weks]['Player Ranks'] = player_ranks['Average']

        print 'Player Ranks'
        for line in player_ranks['Average']: print line
        print ''

        #===============Points For===============

        temp = []
        for ownr in owners:
            pf = sum(ranks[weks][ownr]['Week Points']) / int(weks)
            temp.append([ownr, [pf], 1.0])

        temp = sorted(temp, key = lambda prm: prm[1], reverse = True)
        tempp = add_ranks(temp)

        points_for = [[x[0], round(x[1][0] / tempp[0][1][0], 4), round(x[1][0], 2), x[3]] for x in tempp]
        for line in points_for:
            ranks[weks][line[0]]['PF'] = line
            ranks[weks][line[0]]['Starters']['Total'][2] = line[3]

        metrics[weks]['Points for'] = points_for

        print 'Points for'
        for line in points_for: print line
        print ''

        #===============Record===============

        temp = []
        for ownr in owners:
            wins = ranks[weks][ownr]['Record'][0]
            losses = ranks[weks][ownr]['Record'][1]
            ties = ranks[weks][ownr]['Record'][2]
            pf = ranks[weks][ownr]['Record'][3]
            wprct = (wins * 1.0 + ties * 0.5) / (wins + losses + ties)
            temp.append([ownr, [wprct], pf])

        temp = sorted(temp, key = lambda prm: (prm[1], prm[2]), reverse = True)
        temp = [[x[0], x[1], 1.0] for x in temp]
        tempp = add_ranks(temp, 1)
        # record = [[x[0], round(x[1][0] / tempp[0][1][0], 4) if x[1][0] != 0 else 0.0, x[1][0], x[3]] for x in tempp] # Normalized to best
        record = [[x[0], round(x[1][0] / 1.0, 4) if x[1][0] != 0 else 0.0, round(x[1][0], 4), x[3]] for x in tempp] # Normalized to 1.0000

        metrics[weks]['Record'] = record

        print 'Record'
        for line in record: print line
        print ''

        #===============PLOB===============

        temp = []
        for ownr in owners:
            twp = sum(ranks[weks][ownr]['Week Points'])
            tmp = sum(ranks[weks][ownr]['Max Points'])
            tpp = twp / tmp
            plob = 1 - ((tmp - twp) / tmp)
            temp.append([ownr, [plob], twp])

        temp = sorted(temp, key = lambda prm: (prm[1], prm[2]), reverse = True)
        temp = [[x[0], x[1], 1.0] for x in temp]
        tempp = add_ranks(temp)
        plobp = [[x[0], round(x[1][0] / tempp[0][1][0], 4), round(x[1][0], 3), x[3]] for x in tempp]

        metrics[weks]['PLOB'] = plobp

        print 'PLOB'
        for line in plobp: print line
        print ''

        #===============Rankings===============

        # rwgt = {'Player Ranks' : 1.0, 'Points for' : 1.0, 'Record' : 1.0, 'PLOB' : 1.0}
        rwgt = {'Player Ranks' : 1.0, 'Points for' : 1.5, 'Record' : 2.0, 'PLOB' : 0.5}
        # rwgt = {'Player Ranks' : 1.0, 'Points for' : 1.0, 'Record' : 1.0, 'PLOB' : 1.0}
        for ownr in owners:
            ranks[weks][ownr]['Ranking'] = {}
            for key in metrics[weks].keys():
                ranks[weks][ownr]['Ranking'][key] = []
        for mtrc in metrics[weks].keys():
            list = metrics[weks][mtrc]
            for line in list:
                ownr = line[0]
                ranks[weks][ownr]['Ranking'][mtrc] = [line[1], line[2], line[3]]

        for ownr in owners:
            temp = []
            ranks[weks][ownr]['Ranking']['Final'] = [0.0]
            for mtrc in rwgt.keys():
                ranks[weks][ownr]['Ranking']['Final'][0] += ranks[weks][ownr]['Ranking'][mtrc][0] * rwgt[mtrc]

        temp = []
        for ownr in owners:
            temp.append([ownr, [ranks[weks][ownr]['Ranking']['Final'][0]], 1.0])

        temp = sorted(temp, key = lambda prm: prm[1], reverse = True)
        tempp = add_ranks(temp)
        wght = sum([rwgt[y] for y in rwgt.keys()])

        final = [[x[0], round((x[1][0] / wght) ** (1 / 1), 4), x[3]] for x in tempp]
        ranks[weks]['Final'] = {}
        metrics[weks]['Order'] = []
        for line in final:
            metrics[weks]['Order'].append(str(line[0]))
            ranks[weks]['Final'][line[0]] = line

        tf = open('ff_data/week_{}.txt'.format(prev_week), 'r')
        prev_ranks = tf.read().splitlines()
        tf.close()
        for line in final:
            if weks > '1':
                ownr = line[0]
                try:
                    prev = str(int(prev_ranks.index(ownr) + 1) - int(line[2][:-2].replace('T', ''))).rjust(2, '+')
                except:
                    pdbst()
                if '0' in prev: prev = '--'
                prev = '({})'.format(prev)
            else:
                prev = ''
            line.append(prev)

        metrics[weks]['Final'] = final
        ranks[weks]['Final'] = {}
        metrics[weks]['Order'] = []
        for line in final:
            metrics[weks]['Order'].append(line[0])
            ranks[weks]['Final'][line[0]] = line

        print 'Computer Rankings'
        for line in final: print line
        print ''

    f.close()
    f = open('ff_rankings.txt', 'w')

    print >> f, '##############################'
    print >> f, ''


def build_rosters():
    None


def calculate_playoffs():
    # last_week = 11
    weeks_left = last_week - int(current_week)
    ownerso = metrics[current_week]['Order']
    used = []
    gme_scn_list = []
    prj_plyoff = {}
    temp_plyoff = {}
    chnc_plyoff = {}
    plyoff_scns = {}
    plyoff_cnt = 0
    for ownr in ownerso:
        chnc_plyoff[ownr] = [0, 0, 0]
        prj_plyoff[ownr] = []
        prj_plyoff[ownr].append(teams[ownr][current_year]['Record'][0:3])
        prj_plyoff[ownr].append(round(teams[ownr][current_year]['Record'][3], 1))
        plyoff_scns[ownr] = []
    # '''
    if int(next_week) < 14:
        t_a = datetime.now()
        for ccw in range(2 ** (weeks_left * len(owners) / 2)):
            winstr = bin(ccw).split('b')[1].zfill(weeks_left * len(owners) / 2)
            ic = -1
            temp_plyoff = deepcopy(prj_plyoff)
            for wk in range(int(next_week), int(last_week) + 1):
                wks = str(wk)
                ownerso = copy(metrics[current_week]['Order'])
                used = []
                for ownr in ownerso:
                    opp = schedule[year][wks][ownr]['Opponent']
                    if ownr not in used and opp not in used:
                        if len(gme_scn_list) < len(winstr): gme_scn_list.append([ownr, opp])
                        ic += 1
                        wccw = int(winstr[ic])
                        temp_plyoff[ownr][0][0] += not wccw
                        temp_plyoff[ownr][0][1] += wccw
                        temp_plyoff[opp][0][0] += wccw
                        temp_plyoff[opp][0][1] += not wccw
                        used.append(ownr)
                        used.append(opp)

            for hownr in owners + [None]:
                temp_p = []
                plyoff_cnt += 1
                for ownr in owners:
                    temp_p.append([ownr] + temp_plyoff[ownr])
                    if ownr == hownr: temp_p[-1][2] = 999.9
                temp_ps = sorted(temp_p, key=lambda prm: (prm[1][0], prm[2]), reverse=True)
                temp_pso = []
                for line in temp_ps: temp_pso.append(line[0])
                for wownr in temp_pso:
                    if wownr in west:
                        chnc_plyoff[wownr][0] += 1
                        chnc_plyoff[wownr][1] += 1
                        chnc_plyoff[wownr][2] += 1
                        plyoff_scns[wownr].append(winstr)
                        temp_pso.remove(wownr)
                        break
                for eownr in temp_pso:
                    if eownr in east:
                        chnc_plyoff[eownr][0] += 1
                        chnc_plyoff[eownr][1] += 1
                        chnc_plyoff[eownr][2] += 1
                        plyoff_scns[eownr].append(winstr)
                        temp_pso.remove(eownr)
                        break
                for iownr in temp_pso[0:4]:
                    chnc_plyoff[iownr][1] += 1
                    chnc_plyoff[iownr][2] += 1
                    plyoff_scns[iownr].append(winstr)
                for nownr in temp_pso[4:]:
                    chnc_plyoff[nownr][2] += 1

            if ccw % int(2 ** ((weeks_left * len(owners) / 2) - 1) / 10) == 0:
                print ccw, 2 ** (weeks_left * len(owners) / 2) - 1

                t_b = datetime.now()
                t_d = (t_b - t_a).seconds
                print '{0}m {1}s'.format(t_d / 60, t_d % 60)
                print ''

        imp_gme = {}
        for ownr in owners:
            imp_gme[ownr] = [0.5 for gm in winstr]

            all_scns = remove_dupes(plyoff_scns[ownr])
            for scn in all_scns:
                i = -1
                for gme in scn:
                    i += 1
                    # imp_gme[ownr][i] = imp_gme[ownr][i] and (scn[i] == all_scns[all_scns.index(scn)-1][i])
                    imp_gme[ownr][i] += (2 * int(gme) - 1) / float(len(all_scns)) / 2.0

    elif int(next_week) > 13:
        temp_pso = copy(ownerso)
        for wownr in temp_pso:
            if wownr in west:
                chnc_plyoff[wownr][0] += 1
                chnc_plyoff[wownr][1] += 1
                chnc_plyoff[wownr][2] += 1
                temp_pso.remove(wownr)
                break
        for eownr in temp_pso:
            if eownr in east:
                chnc_plyoff[eownr][0] += 1
                chnc_plyoff[eownr][1] += 1
                chnc_plyoff[eownr][2] += 1
                temp_pso.remove(eownr)
                break
        for iownr in temp_pso[0:4]:
            chnc_plyoff[iownr][1] += 1
            chnc_plyoff[iownr][2] += 1
        for nownr in temp_pso[4:]:
            chnc_plyoff[nownr][2] += 1

    f_cp = open('chance_playoffs.txt', 'w')
    print >> f_cp, chnc_plyoff
    f_cp.close()
    # '''
    chnc_plyoff = eval(open('chance_playoffs.txt', 'r').read())


def output_rankings():
    #===============Computer Rankings===============

    prnt_plyoff = False
    print >> f, '[b]Computer Rankings - Week {}[/b]'.format(int(next_week))
    for line in metrics[current_week]['Final']:
        plyoff_sym = '{}{}{}'.format('*' if chnc_plyoff[line[0]][1] == chnc_plyoff[line[0]][2] else '', '*' if chnc_plyoff[line[0]][0] == chnc_plyoff[line[0]][2] else '', '^' if chnc_plyoff[line[0]][1] == 0 else '')
        if plyoff_sym != '': prnt_plyoff = True
        print >> f, '{0} {4} [{3}] {1}{5} ({2})'.format(str(line[2]).ljust(4, '.'), str(teams[line[0]]['Names'][-1]), make_record(teams[line[0]][year]['Record']), str(line[1]).ljust(6, '0'), line[3], plyoff_sym)
    print >> f, ''

    if prnt_plyoff:
        print >> f, '** - Clinched division'
        print >> f, '* - Clinched playoff'
        print >> f, '^ - Eliminated from playoff contention'
        print >> f, ''

    #===============Weekly All-Star Team===============

    print >> f, '[b]Team of the Week (Week {})[/b]'.format(current_week)
    wkly_players = {}
    total_score = 0.0
    for pos in ['QB', 'RB1', 'RB2', 'WR1', 'WR2', 'Flex', 'DST', 'K']:
        wkly_players[pos] = []
        if '2' not in pos: temp_list = []
        if pos != 'Flex':
            if '2' not in pos:
                for plyr in players[pos.replace('1', '').replace('2', '')][current_week].keys():
                    temp_list.append([plyr, players[pos.replace('1', '').replace('2', '')][current_week][plyr]['Score'], players[pos.replace('1', '').replace('2', '')][current_week][plyr]['Owner'], players[pos.replace('1', '').replace('2', '')][current_week][plyr]['Starter']])
            else:
                temp_list = wkly_players[pos.replace('2', '1')]
        else:
            temp_list = wkly_players['RB2'] + wkly_players['WR2']

        wkly_players[pos] = sorted(temp_list, key = lambda prm: prm[1], reverse = True)
        total_score += wkly_players[pos][0][1]
        print >> f, '{0}. {1} ({2}, {3}) - {4}'.format(pos, wkly_players[pos][0][0], wkly_players[pos][0][2], 'started' if wkly_players[pos][0][3] else 'benched', wkly_players[pos][0][1])
        wkly_players[pos] = wkly_players[pos][1:]

    print >> f, 'Total Score: {}'.format(total_score)
    print >> f, ''

    print >> f, '##############################'
    print >> f, ''

    #===============Matchup Previews===============

    print >> f, '[b]Matchup Previews[/b]'
    ownerso = metrics[current_week]['Order']
    used = []
    prnted = 0
    bye_teams = []
    for ownr in ownerso:
        if ownr in schedule[year][next_week].keys():
            opp = schedule[year][next_week][ownr]['Opponent']
            if ownr not in used and opp not in used:
                print >> f, '[u][{5}] {0} ({1})[/u] {2}'.format(teams[ownr]['Names'][-1], make_record(teams[ownr][year]['Record']), 'vs' if schedule[year][next_week][ownr]['Home'] else 'at', teams[opp]['Names'][-1], make_record(teams[opp][year]['Record']), ranks[current_week]['Final'][ownr][2][:-2], ranks[current_week]['Final'][opp][2][:-2])
                print >> f, '[u][{6}] {3} ({4})[/u]'.format(teams[ownr]['Names'][-1], make_record(teams[ownr][year]['Record']), 'vs', teams[opp]['Names'][-1], make_record(teams[opp][year]['Record']), ranks[current_week]['Final'][ownr][2][:-2], ranks[current_week]['Final'][opp][2][:-2])
                m_a = ranks[current_week][ownr]['Stat'][0][0]
                s_a = ranks[current_week][ownr]['Stat'][0][1]
                m_b = ranks[current_week][opp]['Stat'][0][0]
                s_b = ranks[current_week][opp]['Stat'][0][1]
                diff = [99999.9, None]
                prng = range(int(min([m_a, m_b]) - max([s_a, s_b])) * 100, int(max([m_a, m_b]) + max([s_a, s_b])) * 100)
                for i in prng:
                    j = i / 100.0
                    diff_t = float(abs(normpdf(j, m_a, s_a) - normpdf(j, m_b, s_b)))
                    if diff_t < diff[0]:
                        diff[0] = diff_t
                        diff[1] = i
                sum_a = sumpdf(diff[1] / 100.0, m_a, s_a)
                sum_b = sumpdf(diff[1] / 100.0, m_b, s_b)
                pct_a = 0.9 * sum_a / (sum_a + sum_b) + 0.1 * teams[ownr][opp][5]
                pct_b = 0.9 * sum_b / (sum_a + sum_b) + 0.1 * teams[opp][ownr][5]
                adjm = 1.0
                sprd = [None, None]
                odds = [None, None]
                money = [None, None]
                for pct in [pct_a, pct_b]:
                    opct = [pct_a, pct_b][[pct_a, pct_b].index(pct) - 1]
                    if pct > 0.5:
                        mnyl = pct / (1.0 - pct) * (-100.0)
                    else:
                        mnyl = (1.0 - pct) / pct * 100
                    mnyl = int(mnyl / abs(mnyl)) * ((abs(mnyl) - 100) / adjm + 100)
                    mnyl = int(round(mnyl *2, -1) / 2)
                    if mnyl == 100: mnyl == 'PUSH'
                    money[pct == pct_b] = mnyl
                    spd = int((0.65 * (teams[ownr][opp][3] - teams[ownr][opp][4]) + 0.35 * (teams[ownr][year]['Record'][3] - teams[ownr][year]['Record'][4])) * 20) / 20.0
                    sprd[pct == pct_b] = abs(spd) * (-1 if mnyl < 0 else 1)
                    sprd[pct == pct_b] = str(sprd[pct == pct_b]).rjust(len(str(abs(sprd[pct == pct_b]))) + 1, '+')
                    if pct == pct_a:
                        m_x = m_a; s_x = s_a
                        m_y = m_b; s_y = s_b
                    if pct == pct_b:
                        m_x = m_b; s_x = s_b
                        m_y = m_a; s_y = s_a
                    odd = sumpdf(m_y + s_y ** (1.0 + (abs(s_x - s_y) / max(s_x, s_y))), m_x, s_x)
                    odds[pct == pct_b] = odd

                ava = 0.5 - sum(odds)/len(odds)
                odds[0] += ava
                odds[1] += ava
                new_odds = [None, None]
                for odd in odds:
                    if odd > 0.5:
                        line = odd / (1.0 - odd) * (-100.0)
                    else:
                        line = (1.0 - odd) / odd * 100
                    line = abs(int(round(line *2, -1) / 2))
                    if abs(line) < 104: line = 'PUSH'
                    new_odds[odd == odds[1]] = line
                    if new_odds[odd == odds[1]] not in ['PUSH', 'OFF'] and money[odd == odds[1]] not in ['PUSH', 'OFF']:
                        if abs(new_odds[odd == odds[1]]) > abs(money[odd == odds[1]]):
                            new_odds[odd == odds[1]] = 'OFF'
                pntscrd = diff[1] / 100.0
                rcrd_a = teams[ownr][opp]
                rcrd_b = teams[opp][ownr]
                if rcrd_a[0] > rcrd_b[0]:
                    adv_a = ownr
                    adv_b = opp
                elif rcrd_a[0] < rcrd_b[0]:
                    adv_a = opp
                    adv_b = ownr
                elif rcrd_a[0] == rcrd_b[0]:
                    adv_a = None
                    adv_b = None
                if adv_a is not None:
                    atrcrd = '{} leads all-time {}'.format(adv_a.split(' ')[0], make_record(teams[adv_a][adv_b]))
                else:
                    atrcrd = 'Series is tied {}'.format(make_record(teams[ownr][opp]))

                wins = {'Biggest' : [0.0, 0.0, '20xx', 'y'], 'Smallest' : [999.0, 0.0, '20xx', 'y'], 'Highest' : [0.0, 0.0, '20xx', 'y'], 'Lowest' : [999.0, 999.0, '20xx', 'y']}
                for gme in teams[ownr][opp][6]:
                    pfo = gme[0]
                    pao = gme[1]
                    yro = gme[2]
                    wko = gme[3]
                    gme.append(int(pfo <= pao) + int(pfo == pao))       # 0=Win, 1=Lose, 2=Tie
                    if abs(pfo - pao) > abs(wins['Biggest'][0] - wins['Biggest'][1]):
                        wins['Biggest'] = gme
                    if abs(pfo - pao) < abs(wins['Smallest'][0] - wins['Smallest'][1]):
                        wins['Smallest'] = gme
                    if (pfo + pao) > (wins['Highest'][0] + wins['Highest'][1]):
                        wins['Highest'] = gme
                    if (pfo + pao) < (wins['Lowest'][0] + wins['Lowest'][1]):
                        wins['Lowest'] = gme
                ous = 'O/U: {0}'.format(round(pntscrd * 2.0, 1))

                # Print odds and stats
                # print >> f, '{0}: {1}% ({2}) {3}{4} Moneyline: {5}'.format(ownr.split(' ')[0], round(pct_a * 100.0, 1), sprd[0], sprd[0][0] if new_odds[0] not in ['PUSH', 'OFF'] else '', new_odds[0], money[0])
                # print >> f, '{0}: {1}% ({2}) {3}{4} Moneyline: {5}'.format(opp.split(' ')[0], round(pct_b * 100.0, 1), sprd[1], sprd[1][0] if new_odds[1] not in ['PUSH', 'OFF'] else '', new_odds[1], money[1])
                print >> f, '{0}: {1}% ({2}) {3}{4}'.format(ownr.split(' ')[0], round(pct_a * 100.0, 1), sprd[0], sprd[0][0] if new_odds[0] not in ['PUSH', 'OFF'] else '', new_odds[0], money[0])
                print >> f, '{0}: {1}% ({2}) {3}{4}'.format(opp.split(' ')[0], round(pct_b * 100.0, 1), sprd[1], sprd[1][0] if new_odds[1] not in ['PUSH', 'OFF'] else '', new_odds[1], money[1])
                print >> f, ous
                print >> f, ''
                print >> f, atrcrd

                # Create and print streak
                game_form = [gme[4] for gme in teams[ownr][opp][6]]
                game_form_r = game_form[::-1]
                last_form = game_form_r[0]
                last_winner = ownr if last_form == 0 else opp if last_form == 1 else 'Tie .'
                other_form = [0, 1, 2]
                other_form.remove(game_form_r[0])
                other_ind = min(game_form_r.index(other_form[0]) if other_form[0] in game_form_r else 999, game_form_r.index(other_form[1]) if other_form[1] in game_form_r else 999)
                comb_scr = [round(sum([gme[0] for gme in teams[ownr][opp][6][::-1][0:other_ind]]), 1), round(sum([gme[1] for gme in teams[ownr][opp][6][::-1][0:other_ind]]), 1)]
                comb_scr.sort(reverse = True)
                game_form_n = []
                for gme_f in game_form:
                    game_form_n.append(ownr if gme_f == 0 else opp if gme_f == 1 else 'Tie .')
                game_form_n = '-'.join([str(pers.split(' ')[0][0] + pers.split(' ')[1][0]).replace('.', '') for pers in game_form_n])
                if other_ind > 1:
                    streak_str = '{} has won {} straight with {}-{} combined score'.format(last_winner, other_ind, comb_scr[0], comb_scr[1]) if last_form < 2 else 'Series ended in a tie week {} {}'.format(teams[ownr][opp][6][-1][3], teams[ownr][opp][6][-1][2])
                else:
                    streak_str = '{} won last game {}-{} ({} wk {})'.format(last_winner, comb_scr[0], comb_scr[1], teams[ownr][opp][6][-1][2], teams[ownr][opp][6][-1][3]) if last_form < 2 else 'Series ended in a tie {} week {}'.format(teams[ownr][opp][6][-1][2], teams[ownr][opp][6][-1][3])
                # print >> f, game_form_n
                print >> f, streak_str

                # Print notable games
                key_strng = {'Biggest' : 'Largest victory', 'Smallest' : 'Closest game', 'Highest' : 'Highest scoring', 'Lowest' : 'Lowest scoring'}
                for keyo in ['Biggest', 'Smallest', 'Highest', 'Lowest']:
                    print >> f, '{0}: {4}-{5} ({1}, {7} wk {6})'.format(key_strng[keyo], get_initials(ownr) if wins[keyo][4] == 0 else get_initials(opp) if wins[keyo][4] == 1 else 'Tie', 'beat' if wins[keyo][4] in [0,1] else 'tied', opp if wins[keyo][4] in [0,2] else ownr, max(wins[keyo][0], wins[keyo][1]), min(wins[keyo][0], wins[keyo][1]), wins[keyo][3], wins[keyo][2])

                used.append(ownr)
                used.append(opp)
                prnted += 1
                print >> f, ''

                if (prnted == 3 and next_week not in ['14', '15', '16']) or (next_week in ['14', '15'] and prnted == 2) or (next_week == '16' and prnted in [1, 4]):
                    print >> f, '##############################'
                    print >> f, ''

        elif ownr not in schedule[year][next_week].keys():
            bye_teams.append(ownr)

    if len(bye_teams) > 0:
        print >> f, '[u]Teams on Bye[/u]'
        for ownr in bye_teams:
            print >> f, '{0} ({1}): {2} Champion'.format(ownr, make_record(teams[ownr][year]['Record']), teams[ownr]['Division'])

        print >> f, ''

    print >> f, '##############################'
    print >> f, ''

    #===============Historic Playoff Chances===============
    strt_rec = [0, int(current_week)]
    all_records = [strt_rec]
    rec = strt_rec
    for i in range(int(current_week)):
        rec = [rec[0]+1, rec[1]-1]
        all_records.append(rec)

    rcrd_dict = {}
    for rec in all_records:
        rcrd_dict[str(rec[0])] = [0, 0]

    for year in years[:-1]:
        for ownr in schedule[year][current_week].keys():
            if ownr in OWNERS:
                i += 1
                rcrd_dict[str(schedule[year][current_week][ownr]['Ws'])][0] += 1 if teams[ownr][year]['Playoffs'] else 0
                rcrd_dict[str(schedule[year][current_week][ownr]['Ws'])][1] += 1
                # lkup_w = '0'
                # if str(schedule[year][current_week][ownr]['Ws']) == lkup_w and rcrd_dict['0'][0] > 0 and teams[ownr][year]['Playoffs']:
                    # print '########', year, ownr

    if int(current_week) < 14:
        print >> f, '[b]Historic Playoff Records[/b]'
        for rec in all_records[::-1]:
            plyf = rcrd_dict[str(rec[0])][0]
            ttlg = rcrd_dict[str(rec[0])][1]
            if ttlg > 0:
                str_a = round(float(plyf)/float(ttlg)*100, 1)
                print >> f, '{3}: {2}%, {1} {4} gone {3}'.format(plyf, ttlg, str_a, make_record([rec[0], rec[1], 0]), 'team has' if ttlg == 1 else 'teams have')
            else:
                print >> f, '{0}: No teams have gone {0}'.format(make_record([rec[0], rec[1], 0]))

        print >> f, ''

    #===============Print Future Playoff Chances===============

    if int(next_week) < 14:
        print >> f, '[b]Playoff Scenerios (out of {1})[/b]'.format(2 ** (weeks_left * len(owners) / 2), plyoff_cnt)
        for ownr in owners:
            print >> f, '[u]{}[/u]'.format(ownr)
            prct_div = int((chnc_plyoff[ownr][0] * 100.0 / float(chnc_plyoff[ownr][2])) * 100) / 100.0
            prct_plyof = int((chnc_plyoff[ownr][1] * 100.0 / float(chnc_plyoff[ownr][2])) * 100) / 100.0
            if prct_div == 0:
                prct_div = '{} scenerio{} end{}'.format(chnc_plyoff[ownr][0] if chnc_plyoff[ownr][0] > 0 else 'No', 's' if chnc_plyoff[ownr][0] > 1 or chnc_plyoff[ownr][0] == 0 else '', 's' if chnc_plyoff[ownr][0] == 1 else '')
            else:
                prct_div = str(prct_div) + '% end'
            if prct_plyof == 0:
                prct_plyof = '{} scenerio{} end{}'.format(chnc_plyoff[ownr][1] if chnc_plyoff[ownr][1] > 0 else 'No', 's' if chnc_plyoff[ownr][1] > 1 or chnc_plyoff[ownr][1] == 0 else '', 's' if chnc_plyoff[ownr][1] == 1 else '')
            else:
                prct_plyof = str(prct_plyof) + '% end'
            print >> f, '{} in division champion'.format( prct_div )
            print >> f, '{} in playoff berth'.format( prct_plyof )
            print >> f, ''

    elif int(next_week) > 13:
        print >> f, '[b]Playoff Berths[/b]'
        for ownr in owners:
            print >> f, '[u]{}[/u]'.format(ownr)
            prct_div = int((chnc_plyoff[ownr][0] * 100.0 / float(chnc_plyoff[ownr][2])) * 100) / 100.0
            prct_plyof = int((chnc_plyoff[ownr][1] * 100.0 / float(chnc_plyoff[ownr][2])) * 100) / 100.0
            if prct_div == 0:
                if len(teams[ownr]['Byes']) == 0:
                    div_str = 'Never won {} division'.format(teams[ownr]['Division'])
                else:
                    t_list = copy(teams[ownr]['Byes'])
                    t_list.remove(teams[ownr]['Byes'][-1])
                    div_str = 'Last won {} division in {}{}'.format(teams[ownr]['Division'], teams[ownr]['Byes'][-1], ' ({})'.format(', '.join(teams[ownr]['Byes'])) if len(t_list) > 0 else '')
            else:
                div_str = '{} {} division championship ({})'.format(add_suffix(len(teams[ownr]['Byes'])), teams[ownr]['Division'], ', '.join(teams[ownr]['Byes']))
            if prct_plyof == 0:
                if len(teams[ownr]['Appearances']) == 0:
                    plyoff_str = 'Never made playoffs'
                else:
                    t_list = copy(teams[ownr]['Appearances'])
                    t_list.remove(teams[ownr]['Appearances'][-1])
                    plyoff_str = 'Last made playoffs in {}{}'.format(teams[ownr]['Appearances'][-1], ' ({})'.format(', '.join(teams[ownr]['Appearances'])) if len(t_list) > 0 else '')
            else:
                plyoff_str = '{} playoff appearance ({})'.format(add_suffix(len(teams[ownr]['Appearances'])), ', '.join(teams[ownr]['Appearances']))
            print >> f, div_str
            print >> f, plyoff_str
            print >> f, ''

    print >> f, '##############################'
    print >> f, ''

    #===============Points Scored===============

    print >> f, '[b]Most Points Scored - {}[/b]'.format(years[-1])
    for game in schedule['Records'][years[-1]]['Max All Games']:
        ownr = game[0]
        print >> f, '{4} {0}pts - {1} (Week {3} vs. {5}){6}'.format(game[3], game[0], game[1], game[2], game[4].ljust(4, '.'), schedule[game[1]][game[2]][ownr]['Opponent'].split(' ')[0], '*' if game[2] == current_week else '')

    print >> f, ''

    print >> f, '[b]Fewest Points Scored - {}[/b]'.format(years[-1])
    for game in schedule['Records'][years[-1]]['Min All Games']:
        ownr = game[0]
        print >> f, '{4} {0}pts - {1} (Week {3} vs. {5}){6}'.format(game[3], game[0], game[1], game[2], game[4].ljust(4, '.'), schedule[game[1]][game[2]][ownr]['Opponent'].split(' ')[0], '*' if game[2] == current_week else '')

    print >> f, ''

    #===============All-Time Points Scored===============

    try:
        fia = open('ff_data/top_{}.txt'.format(prev_week), 'r')
        prev_top = fia.read()
        fia.close()
    except:
        prev_top = None
    fia = open('ff_data/top_{}.txt'.format(current_week), 'r')
    current_top = fia.read()
    fia.close()
    if current_top != prev_top:
        print >> f, '[b]Most Points Scored - All-Time[/b]'
        for game in schedule['Records']['Max All Games']:
            ownr = game[0]
            print >> f, '{4} {0}pts - {1} ({2} week {3} vs. {5}){6}'.format(game[3], game[0], game[1], game[2], game[4].ljust(4, '.'), schedule[game[1]][game[2]][ownr]['Opponent'].split(' ')[0], '*' if game[2] == current_week and game[1] == years[-1] else '')

        print >> f, ''
    try:
        fia = open('ff_data/few_{}.txt'.format(prev_week), 'r')
        prev_few = fia.read()
        fia.close()
    except:
        prev_few = None
    fia = open('ff_data/few_{}.txt'.format(current_week), 'r')
    current_few = fia.read()
    fia.close()
    if current_few != prev_few:
        print >> f, '[b]Fewest Points Scored - All-Time[/b]'
        for game in schedule['Records']['Min All Games']:
            ownr = game[0]
            print >> f, '{4} {0}pts - {1} ({2} week {3} vs. {5}){6}'.format(game[3], game[0], game[1], game[2], game[4].ljust(4, '.'), schedule[game[1]][game[2]][ownr]['Opponent'].split(' ')[0], '*' if game[2] == current_week and game[1] == years[-1] else '')

        print >> f, ''

    print >> f, '##############################'
    print >> f, ''

    #===============Player Details===============

    met_keys = ['Record', 'Points For', 'Player Ranks', 'PLOB']

    for line in metrics[current_week]['Final']:
        ownr = line[0]
        print >> f, '[b]{0}. {1} - {2} [{3}][/b]'.format(line[2], ownr, teams[ownr]['Names'][-1], str(line[1]).ljust(6, '0'))
        print >> f, '[u]Win Percentage:[/u] {}, {} [{}]'.format(ranks[current_week][ownr]['Ranking']['Record'][2], ranks[current_week][ownr]['Ranking']['Record'][1], str(ranks[current_week][ownr]['Ranking']['Record'][0]).ljust(6, '0'))
        print >> f, '[u]Points For:[/u] {}, {}ppg [{}]'.format(ranks[current_week][ownr]['Ranking']['Points for'][2], ranks[current_week][ownr]['Ranking']['Points for'][1], str(ranks[current_week][ownr]['Ranking']['Points for'][0]).ljust(6, '0'))
        for pos in positions:
            print >> f, '[u]{0} Score:[/u] {1}, {2}ppg'.format(pos, str(plyr_dict[pos][ownr][3]).rjust(2, '#'), round(sum(plyr_dict[pos][ownr][1]) / plyr_dict[pos][ownr][2], 1))
        print >> f, '[u]Overall Players:[/u] {}, {} [{}]'.format(plyr_dict['Average'][ownr][3], plyr_dict['Average'][ownr][2], str(plyr_dict['Average'][ownr][1]).ljust(6, '0'))
        print >> f, '[u]PLOB:[/u] {}, {}ppg [{}]'.format(ranks[current_week][ownr]['Ranking']['PLOB'][2], round((sum(ranks[current_week][ownr]['Max Points']) - sum(ranks[current_week][ownr]['Week Points'])) / len(ranks[current_week][ownr]['Max Points']), 2), str(ranks[current_week][ownr]['Ranking']['PLOB'][0]).ljust(6, '0'))

        print >> f, ''

        if metrics[current_week]['Final'].index(line) in [3, 6, 9]:
            print >> f, '##############################'
            print >> f, ''

    f.close()

    f = open('ff_data/week_{}.txt'.format(current_week), 'w')
    for line in final:
        f.write('{0}\n'.format(line[0], line[1], line[2], line[3]))
    f.close()

    f = open('ff_rankings.txt', 'r')
    for line in f.read().split('\n'): print line
    f.close()


def main():
    thug_island = league.League("Thug Island", id="190153")

    work_book = xlrd.open_workbook('resources/thug_island_history.xls')
    years = ['2010', '2011', '2012', '2013', '2014', '2015', '2016']
    for yi, year in enumerate(years):
        if len(years) < 7:
            yi = int(year[-1])
        work_sheet = work_book.sheet_by_index(yi)
        thug_island.add_schedule(year, work_sheet)

    del thug_island.owners["Cody Blain"]

    work_book = xlrd.open_workbook('resources/thug_island_2015.xls')
    thug_island.add_games("2015", work_book)
    work_book = xlrd.open_workbook('resources/thug_island_2016.xls')
    thug_island.add_games("2016", work_book)

    thug_island.recursive_rankings()

    output = thug_island.to_string(games=True, owners=False, power=True, seasons=False, rcds=25)
    print output
    with open("ff_data.txt", "w") as f:
        print >> f, output

    # Debug below
    ownr = "Stuart Petty"
    yr = "2015"
    wk = "3"
    gm = 1
    owner = thug_island.owners[ownr]
    schedule = thug_island.years[yr].schedule
    week = schedule.weeks[wk]
    game = week.games[gm]
    matchup = owner.games[yr][wk]
    roster = matchup.roster
    True
    # team_analysis()
    # draft_history()
    # ranking_analysis()
    # build_rosters()
    # calculate_playoffs()
    # output_rankings()

if __name__ == "__main__":
    main()

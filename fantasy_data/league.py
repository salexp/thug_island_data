class Schedule:
    def __init__(self, book, yi):
        sh = book.sheet_by_index(yi)
        # dsh = draft_book.sheet_by_index(int(year[-1]))
        week = 0
        wek = '0'
        game = 0
        for i in range(sh.nrows):
            ownr = str(sh.cell_value(i, 1))
            game += 1
            if ownr == sh.cell_value(1, 1):
                week += 1
                game = 0
                wek = str(week)
                self[wek] = {}
                self[wek]['Data'] = {}
            elif ownr != sh.cell_value(1, 1) and ownr != '':
                if ownr not in self[wek].keys(): self[wek][ownr] = {}
                if ownr not in owners:
                    owners.append(ownr)
                if week > 13:
                    self[wek]['Data']['Postseason'] = True
                else:
                    self[wek]['Data']['Postseason'] = False

            if ownr in owners:
                opp = str(sh.cell_value(i, 4))
                if opp not in self[wek].keys(): self[wek][opp] = {}
                if ' (' in sh.cell_value(i, 0).replace(u'\xa0', u' '):
                    name = sh.cell_value(i, 0).replace(u'\xa0', u' ').split(' (')[0]
                else:
                    name = sh.cell_value(i, 0).replace(u'\xa0', u' ').split('(')[0]
                if name[-1] == ' ': name = name[:-1]
                try:
                    rcd = sh.cell_value(i, 0).replace(u'\xa0', u' ').split(' (')[1][:-1].split('-')
                except IndexError:
                    rcd = sh.cell_value(i, 0).replace(u'\xa0', u' ').split('(')[1][:-1].split('-')
                except:
                    rcd = sh.cell_value(i, 0).replace(u'\xa0', u' ').split(' (')[1][:-1].split('-')
                if len(rcd) < 3: rcd.append(u'0')
                ws = int(rcd[0])
                ls = int(rcd[1])
                ts = int(rcd[2])
                if ' (' in sh.cell_value(i, 3):
                    name_opp = sh.cell_value(i, 3).replace(u'\xa0', u' ').split(' (')[0]
                else:
                    name_opp = sh.cell_value(i, 3).replace(u'\xa0', u' ').split('(')[0]
                if name_opp[-1] == ' ': name_opp = name_opp[:-1]
                try:
                    rcd_opp = sh.cell_value(i, 3).replace(u'\xa0', u' ').split(' (')[1][:-1].split('-')
                except IndexError:
                    rcd_opp = sh.cell_value(i, 3).replace(u'\xa0', u' ').split('(')[1][:-1].split('-')
                except:
                    rcd_opp = sh.cell_value(i, 3).replace(u'\xa0', u' ').split(' (')[1][:-1].split('-')
                if len(rcd_opp) < 3: rcd_opp.append(u'0')
                ws_opp = int(rcd_opp[0])
                ls_opp = int(rcd_opp[1])
                ts_opp = int(rcd_opp[2])
                score = sh.cell_value(i, 5)
                scr_own = float(score.split('-')[0]) if score != '' else None
                scr_opp = float(score.split('-')[1]) if score != '' else None
                self[wek][ownr]['Name'] = name
                if name not in team_names.keys(): team_names[name] = ownr
                self[wek][ownr]['Opponent'] = opp
                self[wek][ownr]['Opponent Name'] = name_opp
                self[wek][ownr]['PF'] = scr_own
                self[wek][ownr]['PA'] = scr_opp
                self[wek][ownr]['Win'] = scr_own > scr_opp
                self[wek][ownr]['Tie'] = scr_own == scr_opp
                self[wek][ownr]['Loss'] = scr_own < scr_opp
                self[wek][ownr]['Ws'] = ws
                self[wek][ownr]['Ls'] = ls
                self[wek][ownr]['Ts'] = ts
                self[wek][ownr]['Playoff'] = (week == 14 and game < 3 and year == '2010') or (week == 15 and game == 1 and year == '2010') or (week in [14, 15] and game < 3 and year in years[1:]) or (week == 16 and game == 1)
                self[wek][ownr]['Home'] = False
                self[wek][opp]['Name'] = name_opp
                if name_opp not in team_names.keys(): team_names[name_opp] = opp
                self[wek][opp]['Opponent'] = ownr
                self[wek][opp]['Opponent Name'] = name
                self[wek][opp]['PF'] = scr_opp
                self[wek][opp]['PA'] = scr_own
                self[wek][opp]['Win'] = scr_opp > scr_own
                self[wek][opp]['Tie'] = scr_opp == scr_own
                self[wek][opp]['Loss'] = scr_opp < scr_own
                self[wek][opp]['Ws'] = ws_opp
                self[wek][opp]['Ls'] = ls_opp
                self[wek][opp]['Ts'] = ts_opp
                self[wek][opp]['Playoff'] = (week == 14 and game < 3 and year == '2010') or (week == 15 and game == 1 and year == '2010') or (week in [14, 15] and game < 3 and year in years[1:]) or (week == 16 and game == 1)
                self[wek][opp]['Home'] = True

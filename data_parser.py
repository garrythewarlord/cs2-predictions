import re
import requests
import datetime
from bs4 import BeautifulSoup
from python_utils import converters
import time
import zoneinfo
import tzlocal

HLTV_COOKIE_TIMEZONE = "Europe/Copenhagen"
HLTV_ZONEINFO=zoneinfo.ZoneInfo(HLTV_COOKIE_TIMEZONE)
LOCAL_TIMEZONE_NAME = tzlocal.get_localzone_name()
LOCAL_ZONEINFO = zoneinfo.ZoneInfo(LOCAL_TIMEZONE_NAME)



def get_parsed_page(url, delay=0.5):
    # This fixes a blocked by cloudflare error i've encountered
    headers = {
        "referer": "https://www.hltv.org/stats",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    cookies = {
        "hltvTimeZone": HLTV_COOKIE_TIMEZONE
    }

    time.sleep(delay)

    return BeautifulSoup(requests.get(url, headers=headers, cookies=cookies).text, "lxml")



def top30teams():
    page = get_parsed_page("https://www.hltv.org/ranking/teams/")
    teams = page.find("div", {"class": "ranking"})
    teamlist = {}
    for team in teams.find_all("div", {"class": "ranked-team standard-box"}):

        name = team.find('div', {"class": "ranking-header"}).select('.name')[0].text.strip().lower()
        rank = converters.to_int(team.select('.position')[0].text.strip(), regexp=True)

        teamlist[name] = rank
    teamlist = sorted(teamlist.items(), key=lambda x: x[1])
    team_ranking = {}
    for e in teamlist:
        a, b = e[0], e[-1]
        team_ranking[a] = b

    return team_ranking



def get_upcoming_matches():

    from datetime import datetime
    time = datetime.today().strftime('%Y-%m-%d')

    url = 'https://www.hltv.org'
    matches = get_parsed_page(url)
    get_main_div = matches.find('div', {'class': 'top-border-hide'}).find_all('a')
    match_data = {}
    ix = 0

    teams = list(top30teams())

    get_main_a_div = matches.find('div', {'class': 'top-border-hide'})

    for e in get_main_div:

        lf = []
        tournament = e.attrs['title'].split('-')
        if len(tournament) == 1:
            tournament = tournament[0][1:]
        else:
            tournament = tournament[-1][1:]

        find_teams = e.find('div', {'class': 'teamrows'})
        if find_teams:
            for b in find_teams.find_all('div', {'class': 'teamrow'}):
                lf.append(b.text[1:].lower())

            team = lf[0]
            opponent = lf[1]



            if team in teams or opponent in teams:
                match_url = 'https://www.hltv.org/' + e['href']
                team_odds = get_match_team_odds(match_url)
                if '/' not in opponent:

                    match_data[ix] = {
                                'date': time,
                                'team': team,
                                'opponent': opponent,
                                'event': tournament,
                                'team1_id': e.div.get('team1'),
                                'team_odds': team_odds
                            }

                    ix += 1


    return match_data

def get_match_team_odds(page):
    result = get_parsed_page(page)
    test = result.find('tr', {'class': 'provider'})
    if test:
        return test.text.replace('\n', '').split('-')[0]
    else:
        return '-'


def download_upcoming_matches():


    import csv


    get_upcoming = get_upcoming_matches()
    team_ranking = top30teams()

    saved_data = {}

    for e in get_upcoming:

        wr, age, lol = get_teams_winrate_map(get_upcoming[e]['team1_id'])

        saved_data[e] = {
                        'event': get_upcoming[e]['event'],
                        'date': get_upcoming[e]['date'],
                        'team': get_upcoming[e]['team'],
                        'opponent': get_upcoming[e]['opponent'],
                        'opponent-ranking': team_ranking.get(get_upcoming[e]['opponent'], -1),
                        'team-rank': lol,
                        'team_map_wr': wr,
                        'team_average_age': age,
                        'team_odds': get_upcoming[e]['team_odds']
                        }

    flattened_data = []


    for key, inner_dict in saved_data.items():
        row = {'index': key}
        row.update(inner_dict)
        flattened_data.append(row)

    headers = flattened_data[0].keys()


    with open('predict_upcoming.csv', 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = headers)
        writer.writeheader()
        writer.writerows(flattened_data)

    return saved_data


def get_teams_winrate_map(team_id):
    url = 'https://www.hltv.org/team/{}/vitality#tab-statsBox'.format(str(team_id))
    maps = get_parsed_page(url)
    find_div = maps.find_all('div', {'class': 'map-statistics-container'})

    avr_age = maps.find_all('div', {'class': 'profile-team-stat'})
    average_age = 0
    team_ranking = 9999
    for e in avr_age:
        find_row_average_player_age = e.text

        if 'World ranking' in find_row_average_player_age:
            team_ranking = int(e.text.replace('World ranking', '').replace('#', '').replace('-', ''))

        if 'Average player age' in find_row_average_player_age:
            average_age = float(e.text.replace('Average player age', ''))
            break


    total = 0
    times = 0
    for e in find_div:
        win_percentage =int(float(e.find('div', {'class': 'map-statistics-row-win-percentage'}).text.replace('\n', '').replace('%', '')))
        total += win_percentage
        times += 1
    if not times:
        return 1, average_age, team_ranking

    return total/times, average_age, team_ranking





if __name__ == "__main__":
    import pprint
    pp = pprint.PrettyPrinter()
    #pp.pprint(get_match_team_odds('https://www.hltv.org/matches/2371137/koi-vs-apeks-betboom-dacha-belgrade-2024-europe-closed-qualifier'))

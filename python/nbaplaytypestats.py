import requests
from pandas import DataFrame

### findkey
#   - search for specified key value in provided list of cointainers (list, dict)
#   - return matching container or None if not found
def findkey(lst, key, value):
    for member in lst:
        if member[key] == value:
            return member
    return None

### getplaytypedata
#   - open request session and retrieve data for provided url and parameter sets
#   - return dict of results containing column heads and player row data (lists)
def getplaytypedata(url, plist, rheader):
    dlist = []
    try:
        with requests.Session() as s:
            s.headers = rheader
            for payload in plist:
                s.params = payload
                request_data = s.get(playtype_url).json()
                ptdata = findkey(request_data.get('resultSets'),'name','SynergyPlayType')
                if ptdata:
                    dlist.append(ptdata)
    except Exception as err:
        print('Request failed:\n'+str(err))
    finally:
        return dlist

# Pre-defined play types used by NBA Stats
PLAY_TYPES = ('Isolation', 'Transition','PRBallHandler',
            'PostUp','SpotUp','Handoff','Cut','OffScreen',
            'Putbacks','Misc','PRRollMan')
# Columns to be included in output
OUTPUT_COLUMNS = ('PLAYER_NAME','TEAM_NAME','TYPE_GROUPING',
                'PLAY_TYPE','PPP','POSS','PTS')

#base url and custome header
playtype_url = 'https://stats.nba.com/stats/synergyplaytypes'
request_header = {
        'Host': 'stats.nba.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

#search params
player_name = 'James Harden'
season_year = '2018-19'
season_type = 'Regular Season' #'Playoffs'
type_group = 'Offensive' #Defensive
per_mode = 'Totals' #'PerGame'

# Initial request parameter list
payload = {
        'LeagueID': '00',
        'PerMode':per_mode,
        'PlayType':None,
        'PlayerOrTeam':'P',
        'SeasonType':season_type,
        'SeasonYear':season_year,
        'TypeGrouping':type_group
    }

#build payload list using available play types
payload_list = [{k: i if k == 'PlayType' else v for (k,v) in payload.items()} for i in PLAY_TYPES]
request_data = getplaytypedata(playtype_url,payload_list,request_header)

if request_data:
    # append player data rows to list
    player_data = []
    headers = request_data[0].get('headers')
    for d in request_data:
        player_row = findkey(d['rowSet'],headers.index('PLAYER_NAME'),player_name)
        if player_row:
            player_data.append(player_row)

    # load into data frame for further manipulationm
    df = DataFrame(player_data,columns=headers)

    # print table of results and total player PPP
    print(df.to_string(columns=OUTPUT_COLUMNS))
    print (f"\n\t{player_name} Total PPP for {season_type} {season_year}:  {df['PTS'].sum()/df['POSS'].sum():.3f}")


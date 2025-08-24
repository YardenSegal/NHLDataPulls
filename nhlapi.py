import requests
import json
import time
import pandas as pd

baseurl = "https://api-web.nhle.com/v1/"
headers = {
	"Content-Type": "application/json",
	}
#response = requests.get(baseurl, headers)

#response_json = response.json()

def send_request(base, headers, data=None):
	if (data):
		response = requests.get(base, headers, data)
	else: 
		response = requests.get(base, headers)
	
	if (response.status_code == 200):
		return response.json()
	else:
		return response.status_code
		print(f"ERROR: {response.status_code}")

def getGameIdsByWeek(base, date):
	base += f"schedule/{date}"
	json = send_request(base, headers)
	
	gameids = []

	for gameweek in json["gameWeek"]:
		for game in gameweek["games"]:
			gameids.append(game['id'])

	return gameids

def getSeasonEndDate(base, fromDate="1900-01-01", toDate="2099-01-01"):
	base+= f"standings-season/"
	json = send_request(base, headers)

	endDate=[]

	for season in json["seasons"]:
		if (season["standingsEnd"] >= fromDate and season["standingsEnd"] <= toDate):
			endDate.append(season["standingsEnd"])
	return endDate

def getSeasonStandings(base, endDate):
	base +=f"standings/{endDate}"
	json = send_request(base, headers)
	
	df = pd.DataFrame()
	seed = 0	
	conSeed = {}
	divSeed = {}

	for team in json["standings"]:
		seed+=1
		if endDate[:4] != "2021":
			if team["conferenceName"] in conSeed:
				conSeed[team["conferenceName"]] += 1
			else:
				conSeed[team["conferenceName"]] = 1

		if team["divisionName"] in divSeed:
			divSeed[team["divisionName"]] += 1
		else:
			divSeed[team["divisionName"]] = 1

		team_row= pd.DataFrame([{
			"season":endDate[:4],
			"seed":seed,
			"team":team["teamAbbrev"]["default"],
			 "points": team["points"],
			"division": team["divisionName"],
			"divPos": divSeed[team["divisionName"]],
		}])

		if endDate[:4] != "2021":
			team_row[["conference", "conPos"]] = (team["conferenceName"], conSeed[team["conferenceName"]])
		
		df = pd.concat([df, team_row])
		
	return df

def getGameBoxscore(base, gameid):
	base += f"gamecenter/{gameid}/boxscore"
	json = send_request(base, headers)
	home = {}
	away = {}

	home["team"] = home["homeTeam"] = away["homeTeam"] = json["homeTeam"]["abbrev"]  
	away["team"] = away["awayTeam"] = home["awayTeam"] = json["awayTeam"]["abbrev"] 
	home["gameDate"] = away["gameDate"] = json["gameDate"]
	home["outcome"] = away["outcome"] = json["gameOutcome"]["lastPeriodType"]
	print(json["id"])
	for team, roster in json["playerByGameStats"].items():
		for pos, pstats in roster.items():
			for stats in pstats:
				
				if stats["position"] != "G":
					for stat, value in stats.items():
						if stat != "playerId" and stat != "toi" and stat != "faceoffWinningPctg" and stat != "sweaterNumber" and stat != "name" and stat != "position" and stat != "plusMinus":
							if team == "homeTeam":
								if stat in home:
									home[stat] += value
								else:
									home[stat] = value
							elif team == "awayTeam":
								if stat in away:
									away[stat] += value
								else:
									away[stat] = value
				else:
					if (stats["starter"]):
						for stat, value in stats.items():
							if stat != "playerId" and stat != "decision" and stat != "starter" and stat != "sweaterNumber" and stat != "name" and stat != "position" and stat != "toi":
								if team == "homeTeam":
									home[f"starter{stat}"] = value
								elif team == "awayTeam":
									away[f"starter{stat}"] = value
	return away, home


#print("Status Code", response.status_code)
#print("JSON Response ", response_json["playerByGameStats"]["awayTeam"]["forwards"][0])

#response = send_request(baseurl, headers)

#gameIds = getGameIdsByWeek(baseurl, "2005-11-10", "2007-01-01")

seasons = getSeasonEndDate(baseurl, "1990-01-01")
print(seasons)

fullStandings = pd.DataFrame()

for season in seasons:
	standings = getSeasonStandings(baseurl, season)
	fullStandings = pd.concat([fullStandings, standings], ignore_index=True)
	#print(standings)
	time.sleep(0.5)

print(fullStandings)
fullStandings.to_csv('nhl_standings.csv')

df = pd.DataFrame()
'''
for i in gameIds:
	away, home = getGameBoxscore(baseurl, i)
	df = df._append([away, home], ignore_index=True) 
	time.sleep(0.5)

print(df)

away, home = getGameBoxscore(baseurl, "2005020237")
print(home, away)
df = df._append([home, away])
print(df)
'''
#df.to_csv('stats.csv')  

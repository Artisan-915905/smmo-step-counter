from time import time, localtime, gmtime, strftime, mktime, sleep
import requests
from rich import print
from rich.live import Live
from rich.table import Table
from settings import api_key, update_rate, pace_unit_per_hour

def generateTable(timeElapsed, stepCount, prevStepCount, level, prevLevel):
    global pace_unit_per_hour
    table = Table()
    table.add_column("Time")
    table.add_column("Steps")
    table.add_column("Levels")
    table.add_row(f'{strftime("%X", gmtime(timeElapsed))}',
                  f'[cyan]{stepCount}[/]',
                  f'[cyan]{level:.2f}[/]')
                  
    table.add_row(f'{strftime("%X", gmtime(time()))} UTC',
                  f'[green]+{stepCount-prevStepCount}[/]',
                  f'[green]+{level-prevLevel:.2f}[/]')
                  
    table.add_row('',
                  f'[yellow]{stepCount/timeElapsed*(60**(pace_unit_per_hour+1)):.2f}[/]',
                  f'[yellow]{level/timeElapsed*(60**(pace_unit_per_hour+1)):.2f}[/]')              
    return table
    

def postRequest(url, json):
    responseSuccess = False
    while responseSuccess == False:
        request = requests.post(url, json=json)
        if repr(request) == '<Response [200]>': # Success
            responseSuccess = True
            json_response = request.json()
        else: # Failed, probably timed out or smth
            print(request)
            print('Retrying...')
    return json_response

creds = {'api_key': api_key}
endpoint = 'https://api.simple-mmo.com/v1/player/me'

response = postRequest(endpoint, creds)
stepStart = response['steps']
levelStart = response['level'] + response['exp']/response['level']/50
timeStart = time()
print(f'pace tracking has begun at {strftime("%Y-%m-%d %H:%M:%S", localtime())}, good luck!')
timeElapsed, stepCount, prevStepCount, level, prevLevel = 0.1, 0, 0, 0, 0

with Live(generateTable(timeElapsed, stepCount, prevStepCount, level, prevLevel), auto_refresh=False) as live:
    while True:
        sleep(update_rate-(time()-timeStart)%update_rate)
        timeElapsed = time()-timeStart
        response = postRequest(endpoint, creds)
        stepCount = response["steps"] - stepStart
        level = response['level'] + response['exp']/response['level']/50 - levelStart
    
        live.update(generateTable(timeElapsed, stepCount, prevStepCount, level, prevLevel), refresh=True)
        prevStepCount = stepCount
        prevLevel = level

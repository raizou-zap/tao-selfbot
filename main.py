import json
import time
import random
import requests
import websocket
import threading

token = ''
guild_id = ''
channel_id = ''

headers = {
    'Authorization': token,
    'Content-Type':'application/json',
    'Origin':'https://discord.com',
    'Referer':'https://discord.com/channels/@me',
    'Sec-Ch-Ua':'"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'Sec-Ch-Ua-Mobile':'?0',
    'Sec-Ch-Ua-Platform':'"Windows"',
    'Sec-Fetch-Dest':'empty',
    'Sec-Fetch-Mode':'cors',
    'Sec-Fetch-Site':'same-origin',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Debug-Options':'bugReporterEnabled',
    'X-Discord-Locale':'ja',
    'X-Discord-Timezone':'Asia/Tokyo',
    'X-Super-Properties':'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImphLUpQIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI1Mjk2NiwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbCwiZGVzaWduX2lkIjowfQ==',
}

contents = [
    '::atk',
    'v',
]

wait = False
gateway_sequence = None
heartbeat_interval = None

def on_open(ws):
    ws.send(f'{{"op":2,"d":{{"token":"{token}","capabilities":16381,"properties":{{"os":"Windows","browser":"Chrome","device":"","system_locale":"ja-JP","browser_user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36","browser_version":"120.0.0.0","os_version":"10","referrer":"","referring_domain":"","referrer_current":"","referring_domain_current":"","release_channel":"stable","client_build_number":252966,"client_event_source":null}},"presence":{{"status":"online","since":0,"activities":[],"afk":false}},"compress":false,"client_state":{{"guild_versions":{{}},"highest_last_message_id":"0","read_state_version":0,"user_guild_settings_version":-1,"user_settings_version":-1,"private_channels_version":"0","api_code_version":0}}}}}}')
    ws.send('{"op":4,"d":{"guild_id":null,"channel_id":null,"self_mute":true,"self_deaf":false,"self_video":false,"flags":2}}')

def on_message(ws, message):
    global wait, heartbeat_interval, gateway_sequence
    message = json.loads(message)
    if 's' in message.keys():
        gateway_sequence = message['s']
    if message['op'] == 10:
        heartbeat_interval = message['d']['heartbeat_interval']/1000
    elif message['op'] == 0 and message['t'] == 'MESSAGE_CREATE':
        if message['d']['author']['id'] == '526620171658330112' and message['d']['guild_id'] == guild_id and message['d']['channel_id'] == channel_id:
            if 'embeds' in message['d'].keys():
                if len(message['d']['embeds']) == 1 and message['d']['embeds'][0]['type'] == 'rich':
                    if 'title' in message['d']['embeds'][0].keys():
                        if '待ち構えている...！' in message['d']['embeds'][0]['title']:
                            print(message['d']['embeds'][0]['title'].replace('\n',''))
                    if 'description' in message['d']['embeds'][0].keys():
                        if '仲間になりたそうに' in message['d']['embeds'][0]['description']:
                            print(message['d']['embeds'][0]['description'].replace('\n',''))
            if '※戦いをやり直すには『::reset』' in message['d']['content'] or 'はやられてしまった。。。' in message['d']['content']:
                requests.post(f'https://discord.com/api/v9/channels/{channel_id}/typing', headers=headers)
                time.sleep(random.uniform(1,3))
                request_data = {"mobile_network_type":"unknown","content":'::reset',"tts":False,"flags":0}
                requests.post(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=headers, json=request_data)
            wait = False

def send_ping():
    while True:
        if heartbeat_interval != None:
            time.sleep(heartbeat_interval-4)
            ws.send(f'{{"op":1,"d":{gateway_sequence}}}')

def auto_attack():
    global wait
    while True:
        requests.post(f'https://discord.com/api/v9/channels/{channel_id}/typing', headers=headers)
        time.sleep(random.uniform(1,3))
        content = random.choices(contents, weights=[100,1])
        request_data = {"mobile_network_type":"unknown","content":content,"tts":False,"flags":0}
        requests.post(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=headers, json=request_data)
        wait = True
        while wait:
            time.sleep(1)

threading.Thread(target=send_ping).start()
threading.Thread(target=auto_attack).start()

ws = websocket.WebSocketApp('wss://gateway.discord.gg/?encoding=json&v=9', on_open=on_open, on_message=on_message)
ws.run_forever()
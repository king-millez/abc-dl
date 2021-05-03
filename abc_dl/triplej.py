import json

def find_video_url(divcontent):
    return json.loads(divcontent.find_all('script')[1].contents[0].strip()[55:-2])['videos'][0]['sources'][0]['url']

def find_m3u8_url(divcontent):
    return json.loads(divcontent.find_all('script')[1].contents[0].strip()[60:-2])['audio'][0]['sources'][0]['url']
import requests

def get_current_song(config):
    response = requests.get(config["SETTINGS"]["current_song_info"])
    data_json = response.json()
    current_song = data_json.get("song", "—")
    return current_song

def get_djname(config):
    response = requests.get(config["SETTINGS"]["current_song_info"])
    data_json = response.json()
    djname = data_json.get("djname", "Auto-DJ")
    return djname

def get_kbps(config):
    response = requests.get(config["SETTINGS"]["current_song_info"])
    data_json = response.json()
    kbps = data_json.get("kbps", "—")
    return kbps
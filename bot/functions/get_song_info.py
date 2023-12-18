import requests

def get_current_song(config):
    response = requests.get(config["SETTINGS"]["current_song_info"])
    data_json = response.json()
    current_song = data_json.get("song", "Информация о песне не найдена")
    return current_song

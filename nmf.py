from dotenv import load_dotenv, find_dotenv
from datetime import date
import requests
import urllib.request
import base64
import json
import os
import sys

load_dotenv(find_dotenv())
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN").strip()
CLIENT_ID = os.environ.get("CLIENT_ID").strip()
CLIENT_SECRET = os.environ.get("CLIENT_SECRET").strip()
NEW_MUSIC_FRIDAY_ID = os.environ.get("NEW_MUSIC_FRIDAY_ID").strip()
USER_ID = os.environ.get("USER_ID")

today = date.today()
d1 = today.strftime("%d/%m/%Y")

OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"
def refresh_access_token():
    payload = {
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
    }
    encoded_client = base64.b64encode((CLIENT_ID + ":" + CLIENT_SECRET).encode('ascii'))
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic %s" % encoded_client.decode('ascii')
    }
    response = requests.post(OAUTH_TOKEN_URL, data=payload, headers=headers)
    return response.json()


def get_playlist(access_token):
    url = "https://api.spotify.com/v1/playlists/%s" % NEW_MUSIC_FRIDAY_ID
    headers = {
       "Content-Type": "application/json",
       "Authorization": "Bearer %s" % access_token
    }
    response = requests.get(url, headers=headers)
    return response.json()

def create_playlist(access_token):
    url = "https://api.spotify.com/v1/users/%s/playlists" % USER_ID
    payload = {
        "name": "New Music Friday Italia del %s" % d1,
        "description": "Ogni Venerdi, le migliori nuove uscite, copia salvata il %s" % d1
    }
    headers = {
       "Content-Type": "application/json",
       "Authorization": "Bearer %s" % access_token
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response.json()

def add_to_nmfi(access_token, nmfiplaylisttoday, tracklist):
    url = "https://api.spotify.com/v1/playlists/%s/tracks" % nmfiplaylisttoday
    payload = {
        "uris" : tracklist
    }
    headers = {
       "Content-Type": "application/json",
       "Authorization": "Bearer %s" % access_token
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response.json()

def get_spoticode(nmfiplaylisttoday):
    base_url = 'https://scannables.scdn.co/uri/plain/png/bdd74/black/640/spotify:playlist:'
    spoti_url = ''.join([base_url, nmfiplaylisttoday])
    print("Spotify Code:",spoti_url)
    return spoti_url

def get_playlistcover(access_token, nmfiplaylisttoday):
    url = "https://api.spotify.com/v1/playlists/%s/images" % nmfiplaylisttoday
    headers = {
       "Content-Type": "application/json",
       "Authorization": "Bearer %s" % access_token
    }
    response = requests.get(url, headers=headers)
    return response.json()

def downloadart(arturl, filename):
    response = urllib.request.urlretrieve(arturl, filename)
    return response

def check_env():
    if REFRESH_TOKEN is None or CLIENT_ID is None or CLIENT_SECRET is None or NEW_MUSIC_FRIDAY_ID is None:
        response = 1
    else:
        response = 0
    return response

def pause():
    programPause = input("Press the <ENTER> key to continue...")

if check_env() == 1:
    print("Environment variables have not been loaded, abort.")
    sys.exit(1)

access_token = refresh_access_token()['access_token']
tracks =  get_playlist(access_token)['tracks']['items']

if len(tracks) > 10:
    nmfiplaylisttoday =  create_playlist(access_token)['id']
    tracklist = []
    for item in tracks:
        tracklist.append(item['track']['uri'])
    response = add_to_nmfi(access_token, nmfiplaylisttoday, tracklist)

    if "snapshot_id" in response:
        print("Playlist backup complete")
        nmf_spoticode = get_spoticode(nmfiplaylisttoday)
        nmf_cover =  get_playlistcover(access_token, nmfiplaylisttoday)[0]['url']
        downloadart(nmf_spoticode,"nmf_spoticode.png")
        downloadart(nmf_cover,"nmf_cover.png")

else:
    print("Check tracklist len")
    sys.exit(1)

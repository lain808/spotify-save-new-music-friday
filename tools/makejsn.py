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
USER_ID = os.environ.get("USER_ID")

today = date.today()
d1 = today.strftime("%d/%m/%Y")
d2 = today.strftime("%Y%m%d")
year = today.strftime("%Y")

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


def get_playlist(access_token,playlistid):
    url = "https://api.spotify.com/v1/playlists/%s" % playlistid
    headers = {
       "Content-Type": "application/json",
       "Authorization": "Bearer %s" % access_token
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_spoticode(playlistid):
    base_url = 'https://scannables.scdn.co/uri/plain/png/bdd74/black/640/spotify:playlist:'
    spoti_url = ''.join([base_url, playlistid])
    return spoti_url

def get_playlistcover(access_token, playlistid):
    url = "https://api.spotify.com/v1/playlists/%s/images" % playlistid
    headers = {
       "Content-Type": "application/json",
       "Authorization": "Bearer %s" % access_token
    }
    response = requests.get(url, headers=headers)
    return response.json()

def check_env():
    if REFRESH_TOKEN is None or CLIENT_ID is None or CLIENT_SECRET is None:
        response = 1
    else:
        response = 0
    return response

def pause():
    programPause = input("Press the <ENTER> key to continue...")

if check_env() == 1:
    print("Environment variables have not been loaded, abort.")
    sys.exit(1)

if len(sys.argv[1]) > 5:
    playlisturl = sys.argv[1]
    # example: https://open.spotify.com/playlist/37i9dQZEVXbt2Ya2lN9UQv?si=99970e5b9ac64702
    playlistID = [ c[:c.find('?')] for c in playlisturl.split('/') if c.find('?')!=-1 ] # Thanks to https://stackoverflow.com/a/73208446/2220346
    print( "ID: " + playlistID[0] )

    access_token = refresh_access_token()['access_token']
    playlistinfo =  get_playlist(access_token,playlistID[0])
    nmf_spoticode = get_spoticode(playlisturl)
    nmf_cover =  get_playlistcover(access_token, playlistID[0])[0]['url']

    """
    print("Debug informations:")
    print("{}: {}".format(playlistinfo['name'], playlistinfo['external_urls']['spotify']))
    print("{}: {}".format("Cover: " + nmf_cover, "Spoticode: " + nmf_spoticode))
    """

    json_nmf_add = {
    "title": playlistinfo['name'],
    "cover": nmf_cover,
    "url": playlistinfo['external_urls']['spotify'],
    "spoticode": nmf_spoticode
    }

    if not os.path.exists("json"):
        os.makedirs("json")
    filename = os.path.join("json",year+".json") # Thanks to https://howtodoinjava.com/json/append-json-to-file/
    json_nmf = []
    with open(filename) as fp:
        json_nmf = json.load(fp)
    json_nmf.append(json_nmf_add)
    print(json_nmf)
    with open(filename, 'w') as fp_updated:
        json.dump(json_nmf, fp_updated,
        indent=4,
        separators=(',',': '))

else:
    print("Check playlist URL len")
    sys.exit(1)

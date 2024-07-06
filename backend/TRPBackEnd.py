import requests
import base64
import sys
import json
from tikapi import TikAPI, ValidationException, ResponseException

api_key = "7vOXGqdh1XKBfTblPXFnfENarTsjh4hA3ZUaVFVdwj6dX5gH"
api = TikAPI(api_key)

client_id = "4aa9a0494abe407eb2526becdb7e8dd4"
client_secret = "3fce7b2629824f4abd2ae5954184d64b"

# Encode client ID and client secret
client_creds = f"{client_id}:{client_secret}"
client_creds_b64 = base64.b64encode(client_creds.encode())

def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

# Get access token
token_url = "https://accounts.spotify.com/api/token"
token_headers = {
    "Authorization": f"Basic {client_creds_b64.decode()}",
    "Content-Type": "application/x-www-form-urlencoded"
}
token_data = {
    "grant_type": "client_credentials"
}

r = requests.post(token_url, data=token_data, headers=token_headers)
token_response_data = r.json()
print(token_response_data)
access_token = token_response_data['access_token']

# Find the song's ID
search_url = "https://api.spotify.com/v1/search"
search_headers = {
    "Authorization": f"Bearer {access_token}"
}
search_params = {
    "q": ' '.join(sys.argv[1:]),
    "type": "track",
    "limit": 1
}

search_response = requests.get(search_url, headers=search_headers, params=search_params)
search_json = search_response.json()
track_id = search_json['tracks']['items'][0]['id']

# Get audio features of the track to build a better recommendation
features_url = f"https://api.spotify.com/v1/audio-features/{track_id}"
features_response = requests.get(features_url, headers=search_headers)
features = features_response.json()
bpm = features['tempo']
danceability = features['danceability']
instrumentalness = features['instrumentalness']
liveness = features['liveness']
valence = features['valence']

# Get recommendations
recommendations_url = "https://api.spotify.com/v1/recommendations"
recommendations_headers = {
    "Authorization": f"Bearer {access_token}"
}
recommendations_params = {
    "seed_tracks": track_id,
    "limit": 10,
    "min_danceability": danceability - .1,
    "max_danceability": danceability + .1,
    "min_instrumentalness": instrumentalness - .1,
    "max_instrumentalness": instrumentalness + .1,
    "min_liveness": liveness - .1,
    "max_liveness": liveness + .1,
    "min_valence": valence - .1,
    "max_valence": valence + .1,
    "min_popularity": 30
}

recommendations_response = requests.get(recommendations_url, headers=recommendations_headers, params=recommendations_params)
recommendations_json = recommendations_response.json()

# full_info will store the name and artist of each recommended song
full_info = []

# Print the recommended tracks and append to full_info
for track in recommendations_json['tracks']:
    print(f"Track Name: {track['name']}, Artist: {track['artists'][0]['name']}")
    full_info.append(f"{track['name']} {track['artists'][0]['name']}")

# For each song
test = 1

for info in full_info:
    url = f"https://api.tikapi.io/public/search/videos?query={info}"

    payload = {}
    headers = {
        'X-API-KEY': api_key
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    changeable = response.json()

    # Check if 'item_list' key exists
    if "item_list" in changeable and changeable["item_list"]:
        # this is the id of each TikTok song
        responses = changeable["item_list"][0]["video"]["id"]

        # find highlighted video
        try:
            response = api.public.video(
                id=responses
            )
            json_response = response.json()
            
            author_id = json_response['itemInfo']['itemStruct']['author']['uniqueId']
            video_id = json_response['itemInfo']['itemStruct']['id']
            link = f"https://www.tiktok.com/@{author_id}/video/{video_id}"

            print(link)

            # response.save_video(json_response['itemInfo']['itemStruct']['video']['downloadAddr'], f'./recommendations/{str(test)}.mp4')
            test += 1

        except ValidationException as e:
            print(e, e.field)

        except ResponseException as e:
            print(e, e.response.status_code)
    else:
        print(f"No results found for {info}")
import requests
import base64
import json
from tikapi import TikAPI, ValidationException, ResponseException

api_key = "7vOXGqdh1XKBfTblPXFnfENarTsjh4hA3ZUaVFVdwj6dX5gH"
api = TikAPI(api_key)

client_id = "4aa9a0494abe407eb2526becdb7e8dd4"
client_secret = "3fce7b2629824f4abd2ae5954184d64b"

def get_spotify_token():
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode())
    
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
    return token_response_data['access_token']

def get_spotify_track_id(song_query, access_token):
    search_url = "https://api.spotify.com/v1/search"
    search_headers = {
        "Authorization": f"Bearer {access_token}"
    }
    search_params = {
        "q": song_query,
        "type": "track",
        "limit": 1
    }

    search_response = requests.get(search_url, headers=search_headers, params=search_params)
    search_json = search_response.json()

    if 'tracks' not in search_json or not search_json['tracks']['items']:
        raise Exception('No track found')
    
    return search_json['tracks']['items'][0]['id']

def get_spotify_recommendations(track_id, access_token):
    features_url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    features_response = requests.get(features_url, headers={"Authorization": f"Bearer {access_token}"})
    features = features_response.json()
    
    recommendations_url = "https://api.spotify.com/v1/recommendations"
    recommendations_params = {
        "seed_tracks": track_id,
        "limit": 10,
        "min_danceability": features['danceability'] - .1,
        "max_danceability": features['danceability'] + .1,
        "min_instrumentalness": features['instrumentalness'] - .1,
        "max_instrumentalness": features['instrumentalness'] + .1,
        "min_liveness": features['liveness'] - .1,
        "max_liveness": features['liveness'] + .1,
        "min_valence": features['valence'] - .1,
        "max_valence": features['valence'] + .1,
        "min_popularity": 30
    }

    recommendations_response = requests.get(recommendations_url, headers={"Authorization": f"Bearer {access_token}"}, params=recommendations_params)
    recommendations_json = recommendations_response.json()

    return [f"{track['name']} {track['artists'][0]['name']}" for track in recommendations_json['tracks']]

def get_tiktok_video_links(queries):
    video_links = []

    for query in queries:
        url = f"https://api.tikapi.io/public/search/videos?query={query}"
        headers = {
            'X-API-KEY': api_key
        }
        response = requests.get(url, headers=headers)
        data = response.json()

        if 'item_list' not in data or not data['item_list']:
            print(f"No videos found for {query}")
            continue

        video_id = data["item_list"][0]["video"]["id"]

        try:
            video_response = api.public.video(id=video_id)
            video_data = video_response.json()
            download_url = video_data['itemInfo']['itemStruct']['video']['downloadAddr']
            video_links.append({
                'track': query,
                'video': download_url
            })
        except (ValidationException, ResponseException) as e:
            print(f"Error fetching video for {query}: {e}")

    return video_links

def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == '__main__':
    song_query = "Never Say Never"
    spotify_access_token = get_spotify_token()
    track_id = get_spotify_track_id(song_query, spotify_access_token)
    recommendations = get_spotify_recommendations(track_id, spotify_access_token)
    video_links = get_tiktok_video_links(recommendations)

    save_to_json(video_links, 'video_links.json')
    print("Data has been saved to video_links.json")
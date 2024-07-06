from flask import Flask, request, jsonify
import requests, base64
from tikapi import TikAPI, ValidationException, ResponseException

app = Flask(__name__)

api_key = "7vOXGqdh1XKBfTblPXFnfENarTsjh4hA3ZUaVFVdwj6dX5gH"
api = TikAPI(api_key)

client_id = "4aa9a0494abe407eb2526becdb7e8dd4"
client_secret = "3fce7b2629824f4abd2ae5954184d64b"

# Gets Auth Token
def get_token():
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode())

    token_url = "https://accounts.spotify.com/api/token"
    token_headers = {
        "Authorization": f"Basic {client_creds_b64.decode()}"
    }
    token_data = {
        "grant_type": "client_credentials"
    }

    r = requests.post(token_url, data=token_data, headers=token_headers)
    token_response_data = r.json()
    return token_response_data['access_token']

## I think something to consider is whether or not we're using the User's playlists.
## Right now, we're just using the Spotify API to get recommendations based on a song query (I could be wrong though).
## We have the user's Auth token in local storage, do we want to use that to get their playlists and then get recommendations based on that?
## Or do we want to keep it as is?

@app.route('/recommendations', methods=['POST'])
def recommendations():
    song_query = request.json.get('song_query')
    if not song_query:
        return jsonify({'error': 'No song query provided'}), 400
    
    access_token = get_token()

    # Find track ID
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
    if not search_json['tracks']['items']:
        return jsonify({'error': 'No track found'}), 404
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

    # recommendation headers seemed the same as search headers

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

    recommendations_response = requests.get(recommendations_url, headers=search_headers, params=recommendations_params)
    recommendations_json = recommendations_response.json()

    # Store the name and artist of each recommended song
    full_info = []
    for track in recommendations_json['tracks']:
        full_info.append(f"{track['name']} {track['artists'][0]['name']}")
    
    # Get TikToks for each song
    video_list = []
    for info in full_info:
        url = f"https://api.tikapi.io/public/search/videos?query={info}"
        headers = {
            'X-API-KEY': api_key
        }
        response = requests.get(url, headers=headers)

        changeable = response.json()

        try:
            video_id = changeable["item_list"][0]["video"]["id"]
            video_response = api.public.video(id=video_id)
            json_data = video_response.json()
            video_list.append({
                'track': info,
                'video': json_data['itemInfo']['itemStruct']['video']['downloadAddr']
            })
        except (ValidationException, ResponseException) as e:
            video_list.append({
                'track': info,
                'error': str(e)
            })

    return jsonify(video_list)

if __name__ == '__main__':
    app.run(debug=True)
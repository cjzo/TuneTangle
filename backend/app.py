from flask import Flask, request, jsonify
import requests, base64
from tikapi import TikAPI, ValidationException, ResponseException
from flask_cors import CORS
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip
from shazamio import Shazam
import asyncio
import os

app = Flask(__name__)

CORS(app, origins="*")

api_key = "h2wTZFgQ1NYWTF586HMsL4tXgL93T1XDcq7yGjorLAc4Q48L"
api = TikAPI(api_key)

client_id = "4aa9a0494abe407eb2526becdb7e8dd4"
client_secret = "3fce7b2629824f4abd2ae5954184d64b"

# Gets Auth Token
def get_token():
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

    # Recommendation headers seemed the same as search headers
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

        # Check if 'item_list' key exists
        if "item_list" in changeable and changeable["item_list"]:
            try:
                video_id = changeable["item_list"][0]["video"]["id"]
                video_response = api.public.video(id=video_id)
                json_data = video_response.json()

                tt_author = json_data['itemInfo']['itemStruct']['author']['uniqueId']
                tt_video = json_data['itemInfo']['itemStruct']['id']
                link = f"https://www.tiktok.com/@{tt_author}/video/{tt_video}"

                video_list.append({
                    'track': info,
                    'video': link
                })

            except (ValidationException, ResponseException) as e:
                video_list.append({
                    'track': info,
                    'error': str(e)
                })
        elif "message" in changeable:
            video_list.append({
                'track': info,
                'error': changeable["message"]
            })
        else:
            video_list.append({
                'track': info,
                'error': 'No TikTok video found'
            })

    return jsonify(video_list)

def get_song_name(response):
    if not response['matches']:
        return 'No matches found'
    else:
        song_name = response['track']['title']
        artist_name = response['track']['subtitle']
        return f'{song_name} - {artist_name}'

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'videofile') 
loop = asyncio.get_event_loop()

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part in the request.', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file.', 400
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    video = VideoFileClip(file_path)
    audio = video.audio
    audio_filename = os.path.splitext(filename)[0] + '.mp3'
    audio_path = os.path.join(UPLOAD_FOLDER, audio_filename)
    audio.write_audiofile(audio_path)
    video.close()
    audio.close()

    async def recognize_song():
        shazam = Shazam()
        out = await shazam.recognize(audio_path)
        return out

    song_info = get_song_name(loop.run_until_complete(recognize_song()))

    os.remove(file_path)
    os.remove(audio_path)
    print(song_info)
    if song_info == 'No matches found':
        return jsonify({'message': song_info}), 404
    else:
        return jsonify({'message': song_info}), 200

if __name__ == '__main__':
    app.run(port=8000, debug=True)
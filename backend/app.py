from flask import Flask, request, jsonify
import requests, json
import sqlite3
from tikapi import TikAPI, ValidationException, ResponseException
from flask_cors import CORS
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip
from shazamio import Shazam
import asyncio
import os

app = Flask(__name__)
DATABASE = 'songs.db'

CORS(app, origins="*")

api_key = "dO1Hw8eZ5ZensleTzk80MNPih7VYYUdm71Df5NUmUxpMw9cl"
api = TikAPI(api_key)

client_id = "4aa9a0494abe407eb2526becdb7e8dd4"
client_secret = "3fce7b2629824f4abd2ae5954184d64b"

access_token = ""


def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

'''
def get_spotify_access_token(code):
    # Encode client ID and client secret
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode())

    # Get access token
    token_url = "https://accounts.spotify.com/api/token"
    token_headers = {
        "Authorization": f"Basic {client_creds_b64.decode()}",
        "Content-Type": 'application/x-www-form-urlencoded'
    }
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect-uri": 'http://localhost:3000/callback'
    }

    r = requests.post(token_url, data=token_data, headers=token_headers)
    token_response_data = r.json()['access_token']
    return token_response_data
'''

def get_track_id(track_name):
    # Find the song's ID
    search_url = "https://api.spotify.com/v1/search"
    search_headers = {
        "Authorization": f"Bearer {access_token}"
    }
    search_params = {
        "q": track_name,
        "type": "track",
        "limit": 1
    }

    search_response = requests.get(search_url, headers=search_headers, params=search_params)
    search_json = search_response.json()

    return search_json['tracks']['items'][0]['id']
    

def get_track_features(track_id):
    # Get audio features of the track to build a better recommendation?
    features_url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    features_header = {
        "Authorization": f"Bearer {access_token}"
    }
    features_response = requests.get(features_url, headers=features_header)
    return features_response.json()


def get_all_of_something(url, params=None):
    all_songs = []
    headers = {
         "Authorization": f"Bearer {access_token}"
    }

    while url:
        response = requests.get(url, headers=headers, params=params)

        song_json = response.json()
        if 'items' in song_json:
            all_songs.extend(song_json['items'])

        # Update the URL to the next page of results
        url = song_json.get('next')

        # Clear params after the first request as they should not be used in pagination
        params = None

    return all_songs


def get_playlist_songs():
    # this gets the current user's id
    user_url = "https://api.spotify.com/v1/me"
    user_headers = {"Authorization": f"Bearer {access_token}"}
    user_response = (requests.get(user_url, headers=user_headers).json())
    user_id = user_response['id']

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT song_ids, total_songs FROM user_songs WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    #song_ids holds ids of all songs to be compared to
    song_ids = []

    # this gets list of all playlists
    playlist_url = "https://api.spotify.com/v1/me/playlists"

    playlist_json_items = get_all_of_something(playlist_url)

    total_songs = sum(playlist['tracks']['total'] for playlist in playlist_json_items)
    
    # If stored song IDs exist and the total number of songs matches, use the stored song IDs
    if result:
        stored_song_ids = json.loads(result[0])
        stored_total_songs = result[1]
        if stored_total_songs == total_songs:
            song_ids = stored_song_ids
            conn.close()
            return song_ids
    else:
        #for each playlist
        for playlist in playlist_json_items:
            if user_id == playlist['owner']['id']:
                #gets all songs in that playlist

                track_url = f"https://api.spotify.com/v1/playlists/{playlist['id']}/tracks"
                song_items = get_all_of_something(track_url)

                #if there is a track id, add to song_ids
                for item in song_items:
                    track = item.get('track')
                    if track and 'id' in track:
                        song_ids.append(track['id'])

        #adds all the liked songs as well
        liked_url = f"https://api.spotify.com/v1/me/tracks"
        liked_songs = get_all_of_something(liked_url)
        for item in liked_songs:
            track = item.get('track')
            if track and 'id' in track:
                song_ids.append(item['track']['id'])

        # Store the songs and total song count in the database
        cursor.execute('''
            INSERT OR REPLACE INTO user_songs (user_id, song_ids, total_songs)
            VALUES (?, ?, ?)
        ''', (user_id, json.dumps(song_ids), total_songs))
        conn.commit()
        conn.close()
        
        return song_ids

def get_recommendations(track_id, features, songs):
    # Get recommendations
    recommendations_url = "https://api.spotify.com/v1/recommendations"
    recommendations_headers = {
        "Authorization": f"Bearer {access_token}"
    }
    recommendations_params = {
        "seed_tracks": track_id,
        "limit": 20,
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

    recommendations_response = requests.get(recommendations_url, headers=recommendations_headers, params=recommendations_params)
    recommendations_json = recommendations_response.json()


    # full_info will store the name and artist of each recommended song
    # Store the name and artist of each recommended song    

    recommendations = []
    for track in recommendations_json['tracks']:
        if (not (track['id'] in songs)):
            recommendations.append(f"{track['name']} - {track['artists'][0]['name']}")

    return recommendations

@app.route('/recommendations', methods=['POST'])
def recommend():
    track_name = request.json.get('song_query')
    if not track_name:
        return jsonify({"error": "track_name parameter is required"}), 400
    print(track_name)
    global access_token
    access_token = request.json.get('code')
    #access_token = get_spotify_access_token(code)
    track_id = get_track_id(track_name)
    features = get_track_features(track_id)
    songs = get_playlist_songs()
    recommendations = get_recommendations(track_id, features, songs)


    # Get TikToks for each song
    video_list = []
    for info in recommendations:
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

@app.route('/add-liked', methods=['POST'])
def add_to_liked():
    try:
        track_name = request.json.get('liked_song')
        if not track_name:
            return jsonify({"error": "track_name parameter is required"}), 400
        
        track_id = get_track_id(track_name)
        liked_url = "https://api.spotify.com/v1/me/tracks"
        liked_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": 'application/json'
        }
        liked_data = {
            "ids":[track_id]
        }

        response = requests.put(liked_url, headers=liked_headers, json=liked_data)

        liked_song_added = True

        if response.status_code != 200:
            print('res '+ json.dumps(response.json()))
            liked_song_added = False

        return jsonify({'liked_song_added': liked_song_added})
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500


@app.route('/')
def hello():
    return ("Hello World")

if __name__ == '__main__':
    app.run(port=8000, debug=True)
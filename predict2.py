from predict1 import *
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import regex as re
import yt_dlp
import os
from pydub import AudioSegment

# Create a Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id='6ca1248789cb422e95219c81841a7e74', client_secret='ca5dcd94b28c4932b33bc1134cbb4900')
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)


def json_to_dataframe(json_data):
    # Extract relevant data from the JSON
    album_info = json_data['album']
    artists_info = json_data['artists'][0]  # Consider only the first artist for simplicity
    
    # Create a dictionary with the extracted data
    data = {
        'Album Name': album_info['name'],
        'Release Date': album_info['release_date'],
        'Artist Name': artists_info['name'],
        'Track Name': json_data['name'],
        'Duration (ms)': json_data['duration_ms'],
        'Explicit': json_data['explicit'],
        'Popularity': json_data['popularity'],
        'Preview URL': json_data['preview_url']
    }
    
    # Create a DataFrame from the dictionary
    df = pd.DataFrame([data])
    return df

def info(link):
    try: 
        track_id = re.search(r'track\/([^/?]+)', link).group(1)
        track_data = sp.track(track_id)
        df = json_to_dataframe(track_data)
        track_name = track_data['name']
        artist = df.loc[0,'Artist Name']
        return track_name, artist
    except:
        print("Error! Enter a valid link")

def download_song(song_name, artist_name):
    search_query = f'{song_name} {artist_name} audio'
    output_file = os.path.join("songs", f'{song_name} {artist_name}')  # Use .wav extension in the filename

    # Check if the file already exists
    if os.path.exists(output_file):
        print(f'{song_name} {artist_name} already downloaded. Skipping...')
        return output_file  # Return the path of the existing file

    ydl_opts = {
        'default_search': f'ytsearch:{search_query}',
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'postprocessor_args': [
            '-ar', '44100'
        ],
        'prefer_ffmpeg': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'quiet': True,
        'outtmpl': output_file,
        # 'audioformat': "wav",
        'ffmpeg_location': r"C:/Users/slayer/Desktop/New folder/ffmpeg-6.0-full_build/bin"
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([search_query])
        print(f'{song_name} {artist_name} downloaded successfully.')
        return output_file  # Return the path of the downloaded file
    except Exception as e:
        print(f'Error occurred while downloading {song_name} {artist_name}: {str(e)}')
        return None  # Return None to indicate an error

def predict_spotify(link):
    track_name, artist = info(link)
    download_file = download_song(track_name, artist)
    return predict(download_file + '.wav')
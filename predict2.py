from predict1 import *
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import regex as re
import yt_dlp
import os
from pydub import AudioSegment
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from predict1 import predict

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
        print("Link:", link)
        track_id = re.search(r'track\/([^/?]+)', link).group(1)
        print("Extracted Track ID:", track_id)

        track_data = sp.track(track_id)
        track_name = track_data['name']

        artists = track_data['artists']
        artist_names = [artist['name'] for artist in artists]

        artist = ', '.join(artist_names)

        return track_name, artist

    except Exception as e:
        print("Error:", e)
        return "Error! Enter a valid link"

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

connection_string = "DefaultEndpointsProtocol=https;AccountName=songs55001122;AccountKey=TYtAi/ejgm6x1mka/i1pZxuQnTZBUM0pwfIqEVbouBZx0Ur0zX6dM9QxmZY2tpaLUwJGJB3P2+qS+AStsNWImQ==;EndpointSuffix=core.windows.net"

def upload_to_azure_storage(local_file_path, remote_file_name):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_name = "songss44124"  # Replace with your container name
        
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=remote_file_name)
        
        with open(local_file_path, "rb") as data:
            blob_client.upload_blob(data)
        
        print(f'File {local_file_path} uploaded to {remote_file_name} in Azure Storage')
    except Exception as e:
        print(f'Error uploading {local_file_path} to Azure Storage: {e}')

def predict_and_upload(link):
    try:
        track_name, artist = info(link)
        download_file = download_song(track_name, artist)
        
        if download_file:
            prediction = predict(download_file + '.wav')
            
            # Upload the downloaded file to Azure Storage
            remote_file_name = os.path.basename(download_file) + '.wav'
            upload_to_azure_storage(download_file + '.wav', remote_file_name)
            
            return prediction
        else:
            return "Error downloading the song"
    except Exception as e:
        return f"Error: {e}"

# Example usage
link = "https://open.spotify.com/track/0qMip0B2D4ePEjBJvAtYre?si=e623353611d94250"
result = predict_and_upload(link)
print("Prediction:", result)
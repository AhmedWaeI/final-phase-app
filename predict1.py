import pickle
import pychorus as pc
import soundfile as sf
import os
import librosa
import numpy as np
from scipy.stats import skew, kurtosis
import pandas as pd
from sklearn.decomposition import PCA

import scipy
# import eli5
# from eli5.sklearn import PermutationImportance


loaded_model = pickle.load(open('Classification_Pipeline.pkl', 'rb'))
# test1 = pd.read_csv('test1.csv')


def extract_chorus(audio_file):
    
    try:
        # Read the audio file
        data, samplerate = sf.read(audio_file)
        output_file = audio_file + '_chorus.wav'
        print(output_file)
        # Get the chromagram
        chroma, _, _, song_length_sec = pc.create_chroma(audio_file)

        # Set the clip length (in seconds)
        clip_length = 15

        # Find the chorus section
        chorus_start = pc.find_chorus(chroma, samplerate, song_length_sec, clip_length)

        if chorus_start is None:
            print("No chorus detected.")
            return None

        # Set the duration of the chorus (in seconds)
        chorus_duration = 15

        # Calculate start and end time of chorus
        start_time = int(chorus_start * samplerate)
        end_time = start_time + int(chorus_duration * samplerate)

        # Extract the chorus section
        chorus = data[start_time:end_time]

        # Write chorus to WAV file
        sf.write(audio_file + '_chorus.wav', chorus, samplerate)
        print(f"Chorus extracted and saved as {output_file}.")

        # function to extract the feautre exctly the same way of the final data 
        
        # Compute features for the choru

        return output_file

    except Exception as e:
        print(f"Error occurred for {audio_file}: {e}")
        return None


def feature(output_file):
    featuresdf=pd.DataFrame()
    
    features=['chroma_stft','chroma_cqt','chroma_cens','mfcc','spectral_centroid','spectral_bandwidth','spectral_rolloff','tonnetz','spectral_contrast']
    y, sr = librosa.load(output_file)
    
    for feature in features:
        feature_array = getattr(librosa.feature, feature)(y=y, sr=sr)
        for index2 in range(0,feature_array.shape[0]):
            featuresdf.loc[0,f'{feature}{index2}min']=np.min(feature_array[index2])
            featuresdf.loc[0,f'{feature}{index2}mean']=np.mean(feature_array[index2])
            featuresdf.loc[0,f'{feature}{index2}median']=np.median(feature_array[index2])
            featuresdf.loc[0,f'{feature}{index2}max']=np.max(feature_array[index2])
            featuresdf.loc[0,f'{feature}{index2}std']=np.std(feature_array[index2])
            featuresdf.loc[0,f'{feature}{index2}skew']=skew(feature_array[index2])
            featuresdf.loc[0,f'{feature}{index2}kurtosis']=kurtosis(feature_array[index2])
            
    features=['rms','zero_crossing_rate']

    y, sr = librosa.load(output_file)
    for feature in features:
        feature_array = getattr(librosa.feature, feature)(y=y)
        for index2 in range(0,feature_array.shape[0]):
            featuresdf.loc[0,f'{feature}{index2}min']=np.min(feature_array[index2])
            featuresdf.loc[0,f'{feature}{index2}mean']=np.mean(feature_array[index2])
            featuresdf.loc[0,f'{feature}{index2}median']=np.median(feature_array[index2])
            featuresdf.loc[0,f'{feature}{index2}max']=np.max(feature_array[index2])
            featuresdf.loc[0,f'{feature}{index2}std']=np.std(feature_array[index2])
            featuresdf.loc[0,f'{feature}{index2}skew']=skew(feature_array[index2])
            featuresdf.loc[0,f'{feature}{index2}kurtosis']=kurtosis(feature_array[index2])
            
    return featuresdf
     
def predict(test_file):
    # print(test_file)
    output_file = extract_chorus(test_file)
    features= feature(output_file)
    prediction = loaded_model.predict(features)[0]
    if int(prediction) == 1:
        return 'Popular'
    else : 
        return 'Unpopular'
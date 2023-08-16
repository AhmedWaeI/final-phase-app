from flask import Flask, render_template, request, flash
from predict1 import * 
from predict2 import * 
import os

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('homepage.html')


@app.route('/upload', methods=['GET', 'POST'])
def page1():
    prediction = None
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Save the uploaded file to a temporary location
            file_path = os.path.join(r'songs', file.filename)
            file.save(file_path)
            try:
                # Call the predict function with the file path
                prediction = predict(file_path) 
            except:
                flash("Please, Enter a .wav file.","error")
            # Try to remove the temporary file after processing
            try:
                os.remove(file_path)
            except PermissionError:
                print("PermissionError: Cannot remove file. It is being used by another process.")
                # Optionally, you can log the error or handle it in another way
                
    return render_template('upload.html', prediction=prediction)


@app.route('/link', methods=['GET', 'POST'])
def page2():
    prediction = None
    track_name= None
    artist= None
    if request.method == 'POST':
        spotify_link = request.form.get('spotify_link')
        if spotify_link:
            try:
                # Process the Spotify link using your prediction model
                prediction = predict_spotify(spotify_link)  # You need to define this function
            except:
                flash("Please, Enter a valid link.","error")
    return render_template('link.html', prediction=prediction)

if __name__ == '__main__':
    app.secret_key="1234567dailywebcoding"
    app.run(debug=True)

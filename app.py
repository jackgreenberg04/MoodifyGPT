import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.utils import secure_filename
from PIL import Image
from deepface import DeepFace
from transformers import pipeline
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change-me')

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize sentiment pipeline once
sentiment_pipeline = pipeline('sentiment-analysis', model='cardiffnlp/twitter-roberta-base-sentiment')

# Emotion to Spotify recommendation mapping
EMOTION_MAPPING = {
    'happy': {
        'seed_genres': ['pop', 'dance'],
        'target_valence': 0.9,
        'target_energy': 0.8,
    },
    'sad': {
        'seed_genres': ['acoustic', 'sad'],
        'target_valence': 0.3,
        'target_energy': 0.4,
    },
    'angry': {
        'seed_genres': ['metal', 'hardcore'],
        'target_valence': 0.4,
        'target_energy': 0.9,
    },
    'neutral': {
        'seed_genres': ['chill', 'ambient'],
        'target_valence': 0.5,
        'target_energy': 0.5,
    },
}


def detect_emotion_from_image(path):
    analysis = DeepFace.analyze(img_path=path, actions=['emotion'])
    return analysis['dominant_emotion']


def detect_emotion_from_text(text):
    result = sentiment_pipeline(text)[0]
    label = result['label'].lower()
    # Map sentiment labels to broader emotions
    if label == 'positive':
        return 'happy'
    elif label == 'negative':
        return 'sad'
    else:
        return 'neutral'


def create_playlist(emotion, user_id, sp):
    mapping = EMOTION_MAPPING.get(emotion, EMOTION_MAPPING['neutral'])
    playlist_name = f"Moodify - {emotion.capitalize()}" + str(uuid.uuid4())[:8]
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False, description=f"Playlist for {emotion} mood")
    recs = sp.recommendations(seed_genres=mapping['seed_genres'],
                             target_valence=mapping['target_valence'],
                             target_energy=mapping['target_energy'],
                             limit=20)
    track_ids = [track['id'] for track in recs['tracks']]
    sp.playlist_add_items(playlist_id=playlist['id'], items=track_ids)
    return playlist


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    try:
        emotion = detect_emotion_from_image(path)
    finally:
        os.remove(path)
    session['emotion'] = emotion
    return redirect(url_for('generate_playlist'))


@app.route('/analyze-text', methods=['POST'])
def analyze_text():
    text = request.form.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    emotion = detect_emotion_from_text(text)
    session['emotion'] = emotion
    return redirect(url_for('generate_playlist'))


@app.route('/generate-playlist')
def generate_playlist():
    emotion = session.get('emotion')
    if not emotion:
        return redirect(url_for('index'))
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope='playlist-modify-private'))
    user_id = sp.current_user()['id']
    playlist = create_playlist(emotion, user_id, sp)
    embed_url = f"https://open.spotify.com/embed/playlist/{playlist['id']}"
    return render_template('playlist.html', embed_url=embed_url, emotion=emotion)


if __name__ == '__main__':
    app.run(debug=True)

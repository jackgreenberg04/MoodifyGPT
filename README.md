# Moodify

Moodify is a full-stack AI-powered web application that creates personalized Spotify playlists based on your current mood. Upload a selfie or describe how you're feeling, and Moodify will analyze your emotion and generate a fitting playlist right in your Spotify account.

## Features

- **Emotion detection from images** using the `deepface` library
- **Sentiment analysis from text** with Hugging Face transformers
- **Spotify integration** via OAuth2 to create and fill playlists
- **Clean web interface** with separate sections for image and text input
- **Automatic playlist preview** embedded from Spotify
- Optional mood history stored in SQLite (not implemented by default)

## Tech Stack

- **Backend:** Python, Flask, spotipy, deepface, transformers, Pillow
- **Frontend:** HTML, CSS (can be extended with Bootstrap/Tailwind)
- **Database:** SQLite (optional)

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Moodify.git
   cd Moodify
   ```
2. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Set up Spotify credentials**
   - Create an app on the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
   - Set the redirect URI in the dashboard and in your environment variables:
   ```bash
   export SPOTIPY_CLIENT_ID='your-client-id'
   export SPOTIPY_CLIENT_SECRET='your-client-secret'
   export SPOTIPY_REDIRECT_URI='http://localhost:5000/callback'
   export FLASK_SECRET_KEY='a-random-secret'
   ```
4. **Run the application**
   ```bash
   flask run
   ```
   Visit `http://localhost:5000` in your browser.

## Usage

- **Upload Image:** Choose a selfie, submit, and Moodify detects your emotion using `deepface`.
- **Describe Mood:** Type a short sentence, and Moodify analyzes it using the `cardiffnlp/twitter-roberta-base-sentiment` model.
- After analysis, a playlist tailored to your mood is created on your Spotify account and displayed on the page.

## Screenshots

![Moodify Screenshot](docs/screenshot.png)

## License

This project is licensed under the MIT License.

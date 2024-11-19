from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, send_file, send_from_directory
from werkzeug.utils import secure_filename
import google.generativeai as genai
import os
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import base64


bucket = "project3"

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
RESPONSE_FOLDER = 'ai_responses'
ALLOWED_EXTENSIONS = {'wav', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESPONSE_FOLDER'] = RESPONSE_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESPONSE_FOLDER, exist_ok=True)

PROJECT_ID = "cot5930project3"

vertexai.init(project=PROJECT_ID, location="us-east4")

api_key = "AIzaSyDgND6e4zaSKlaPI-pR0ISc3CpHXVSuWds"

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash")
prompt = """
Generate a transcription and a sentiment analysis for this audio
"""

def upload_to_gemini(path, mime_type=None):
    file = genai.upload_file(path, mime_type=mime_type)
    return file


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_responses_from_files():
    responses = []
    for filename in os.listdir(RESPONSE_FOLDER):
        print("checking if " + str(filename) + " is in allowed files...")
        if allowed_file(filename):
            response = open(RESPONSE_FOLDER + "/" + filename, "r")
            responses.append(response.read())
            # print("is in allowed files: " + str(filename))
    responses.sort(reverse=True)
    return responses


def get_upload_files():
    
    files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        print("checking if " + str(filename) + " is in allowed files...")
        if allowed_file(filename):
            files.append(filename)
            # print("is in allowed files: " + str(filename))
    files.sort(reverse=True)
    return files


@app.route('/')
def index():
    upload_files = get_upload_files()
    ai_responses = get_responses_from_files()
    return render_template('index.html', upload_files=upload_files, response_files=ai_responses)


@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'audio_data' not in request.files:
        flash('No audio data')
        return redirect(request.url)
    file = request.files['audio_data']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        # filename = secure_filename(file.filename)
        audio_filename = datetime.now().strftime("%Y%m%d-%I%M%S%p") + '.wav'
        text_filename = datetime.now().strftime("%Y%m%d-%I%M%S%p") + '.txt'
        audio_file_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
        text_file_path = os.path.join(app.config['RESPONSE_FOLDER'], text_filename)
        file.save(audio_file_path)

        # print("the file is named: " + str(audio_file_path))

        wav = upload_to_gemini(audio_file_path, mime_type="audio/wav")

        parts = [wav, prompt]

        response = model.generate_content(parts)

        # print(response.text)

        f = open(text_file_path, "a")
        f.write(response.text)
        f.close()
        
    return redirect('/') #success


@app.route('/upload/<filename>')
def get_file(filename):
    return send_file(filename)

    
@app.route('/upload_text', methods=['POST'])
def upload_text():
    text = request.form['text']
    print(text)
    #
    #
    # Modify this block to call the stext to speech API
    # Save the output as a audio file in the 'tts' directory 
    # Display the audio files at the bottom and allow the user to listen to them
    #

    return redirect('/') #success


@app.route('/script.js',methods=['GET'])
def scripts_js():
    return send_file('./script.js')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)

from flask_httpauth import HTTPBasicAuth
import os
from os.path import join
from flask import Flask, request, jsonify, send_file, render_template, url_for, redirect, send_from_directory, abort
import requests
import json
from uploadtodrive import upload_to_drive
import subprocess
import google.auth
import urllib.parse
from google.oauth2 import service_account
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import io
import zipfile
from download import get_video_info
from video_list import video_list_app
from cryptography.fernet import Fernet
from googleapiclient.errors import HttpError


app = Flask(__name__)
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    env_username = os.environ.get('USERNAME')
    env_password = os.environ.get('PASSWORD')

    if username == env_username and password == env_password:
        return True
    return False

@app.before_request
@auth.login_required
def require_auth():
    pass 

app.register_blueprint(video_list_app, url_prefix='')


@app.route("/")
def upload_video_form():
	return """
        <form action="/download" method="post">
            <label>Video URL:</label>
            <input type="text" id="video-url" name="video" placeholder="Enter video URL">
            <input type="submit" value="Download">
        </form>
        <form action="/videos" method="get">
            <input type="submit" value="Videos">
        </form>
        <form action="/terminal" method="get">
            <input type="submit" value="Terminal">
		</form>
		<form action="/serve" method="get">
            <input type="submit" value="List Downloaded Videos">
        </form>
		</form>
		<form action="/video_list" method="get">
            <input type="submit" value="List Videos">
        </form>

    """

@app.route("/favicon.ico")
def favicon():
    return ('', 204)


@app.route('/terminal', methods=['GET', 'POST'])
def terminlal():
    if request.method == 'POST':
        cmd = request.form.get('cmd')
        try:
            output = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return output.stdout.decode() + output.stderr.decode()
        except Exception as e:
            return str(e)
    else:
        return render_template('terminal.html')


json_password = os.environ.get('JSON_PASSWORD')
json_file_name = 'xd.json'
with open(json_file_name, 'rb') as json_file:
    json_data = Fernet(json_password.encode()).decrypt(json_file.read())
    json_string = json_data.decode('utf-8')
creds = Credentials.from_service_account_info(json.loads(json_string))

# Build the Drive API client
drive_service = build('drive', 'v3', credentials=creds, static_discovery=False)

# Define the upload_video function
@app.route('/download', methods=['POST'])
def upload_video():
    video_url = request.form.get('video')
    if not video_url:
        return jsonify({"error": "video url is missing"})
    video_name, download_url = get_video_info(video_url)
    # Convert the video using a shell script
    subprocess.run(['bash', 'conversion.sh', download_url, video_name], check=True)
    # Upload the converted video file to Google Drive
    chunk_size = 256 * 1024 * 1024 # 256 MB
    upload_to_drive(creds, chunk_size)

    return jsonify({"message": "video conversion and upload completed"})


@app.route('/videos')
def videos():
    # Look up the ID of the 'videos' folder
    folder_id = os.environ.get('VIDEOS_FOLDER_ID')
    if not folder_id:
        return "Folder ID not found in environment variable"

    # Query for all videos in the folder
    query = "mimeType='video/mp4' and trashed = false and parents in '{}'".format(folder_id)
    results = drive_service.files().list(q=query, fields="nextPageToken, files(id, name, thumbnailLink)").execute()
    videos = results.get('files', [])

    # Render the template with the list of videos
    return render_template('videos.html', videos=videos, creds=creds, drive_service=drive_service)

# Route to edit the video name
@app.route('/videos/edit/<video_id>', methods=['POST'])
def edit_video_name(video_id):
    new_name = request.form['new_name']
    try:
        # Update the video name
        metadata = {'name': new_name}
        drive_service.files().update(fileId=video_id, body=metadata).execute()
        return redirect(url_for('videos'))
    except HttpError as error:
        print(f'An error occurred: {error}')
        return 'An error occurred while updating the video name.'

# Route to delete the video
@app.route('/videos/delete/<video_id>', methods=['POST'])
def delete_video(video_id):
    try:
        # Delete the video file
        drive_service.files().delete(fileId=video_id).execute()
        return redirect(url_for('videos'))
    except HttpError as error:
        print(f'An error occurred: {error}')
        return 'An error occurred while deleting the video.'

@app.route('/serve')
def listvideos():
    file_names = []
    directory = 'videos'  # directory containing video files in application's root directory

    # Get all file names in directory
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            file_names.append(filename)

    return render_template('serve.html', file_names=file_names, directory=directory)

@app.route('/serve/<path:filename>')
def download(filename):
    directory = 'videos'  # directory containing video files in application's root directory
    return send_from_directory(directory, filename, as_attachment=False)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
from flask import Flask, render_template, request, redirect, url_for
import os
from cryptography.fernet import Fernet
from flask import Blueprint

video_list_app = Blueprint('video_list', __name__)

# Read video data from file
def read_video_data():
    # Get the encryption key from an environment variable
    key = os.environ.get('ENCRYPTION_KEY')
    fernet = Fernet(key.encode())

    try:
        with open('videos.txt', 'rb') as f:
            encrypted_data = f.read()
            decrypted_data = fernet.decrypt(encrypted_data)
            lines = decrypted_data.decode('utf-8').split('\n')
    except FileNotFoundError:
        # Create a new file with encryption
        lines = []

    videos = []
    for i in range(0, len(lines), 3):
        if i + 2 >= len(lines):
            # not enough lines left to form a video
            break

        video = {
            'name': lines[i],
            'thumbnail_url': lines[i+1],
            'url': lines[i+2],
        }
        videos.append(video)
    return videos

# Write video data to file
def write_video_data(videos):
    # Get the encryption key from an environment variable
    key = os.environ.get('ENCRYPTION_KEY')
    fernet = Fernet(key.encode())

    data = ''
    for video in videos:
        data += video['name'] + '\n'
        data += video['thumbnail_url'] + '\n'
        data += video['url'] + '\n'
    encrypted_data = fernet.encrypt(data.encode())

    with open('videos.txt', 'wb') as f:
        f.write(encrypted_data)

# Index page - display video list, handle form submission for adding, editing and deleting videos
@video_list_app.route('/video_list', methods=['GET', 'POST'])
def index():
    videos = read_video_data()
    if request.method == 'POST':
        # If video_index is -1, it means we're adding a new video
        video_index = int(request.form.get('video_index', '-1'))
        action = request.form.get('action')
        if action == 'delete':
            del videos[video_index]
        else:
            name = request.form['name']
            thumbnail_url = request.form['thumbnail_url']
            url = request.form['url']
            if video_index == -1:
                video = {
                    'name': name,
                    'thumbnail_url': thumbnail_url,
                    'url': url,
                }
                videos.append(video)
            else:
                videos[video_index]['name'] = name
                videos[video_index]['thumbnail_url'] = thumbnail_url
                videos[video_index]['url'] = url
        write_video_data(videos)
        return redirect(url_for('video_list.index'))

    else:
        video_index = int(request.args.get('video_index', '-1'))
        if video_index == -1:
            video = {
                'name': '',
                'thumbnail_url': '',
                'url': '',
            }
        else:
            video = videos[video_index]
        return render_template('videos_list.html', videos=videos, video=video, video_index=video_index)

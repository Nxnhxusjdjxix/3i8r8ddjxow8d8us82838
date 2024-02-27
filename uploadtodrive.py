from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

def upload_to_drive(creds, chunk_size):
    folder_id = os.environ.get('VIDEOS_FOLDER_ID')
    if not folder_id:
    	print("Folder ID not provided. Stopping upload.")
    else:
    	print("Uploading to folder with ID: ", folder_id)
    drive_service = build('drive', 'v3', credentials=creds, static_discovery=False)
    video_files = [f for f in os.listdir('./videos') if f.endswith('.mp4')]
    if not video_files:
        print("No video files found in directory. Stopping upload.")
    else:
        for video_file in video_files:
            video_path = os.path.join('./videos', video_file)

            with open(video_path, 'rb') as f:
                file_size = os.path.getsize(video_path)
                chunks = []
                chunk_start = 0
                while chunk_start < file_size:
                    chunk_end = min(chunk_start + chunk_size, file_size)
                    chunk_size_bytes = chunk_end - chunk_start
                    chunk = f.read(chunk_size)
                    chunks.append(chunk)
                    chunk_start = chunk_end

                file_metadata = {'name': video_file, 'parents': [folder_id]}
                media = MediaFileUpload(video_path, mimetype='video/mp4', chunksize=chunk_size_bytes, resumable=True)
                request = drive_service.files().create(body=file_metadata, media_body=media)

                response = None
                while response is None:
                    status, response = request.next_chunk()
                    if status:
                        print(f"Uploaded {int(status.progress() * 100)}% of {video_file}.")

                file_id = response.get('id')
                print(f'Video file {video_file} uploaded. ID: {file_id}')

            os.remove(video_path)

        print('All video files uploaded and deleted from local directory.')

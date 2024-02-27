import os
import yt_dlp

def get_video_info(video_url):
    video_name = None
    download_url = None
    try:
        ydl_opts = {
            'outtmpl': os.path.join(os.getcwd(), 'videos', '%(title)s.%(ext)s'),
            'format': 'mp4',
            'quiet': True,
            'verbose': True,
            'geturl': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            video_name = ydl.prepare_filename(info_dict)
            download_url = ydl.extract_info(video_url, download=False)['url']
            return video_name, download_url
    except yt_dlp.utils.DownloadError:
        try:
            ydl_opts = {
                'outtmpl': os.path.join(os.getcwd(), 'videos', '%(title)s.%(ext)s'),
                'format': 'mp4',
                'quiet': True,
                'verbose': True,
                'extract_flat': True,
                'force_generic_extractor': True,
                'geturl': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=False)
                video_name = ydl.prepare_filename(info_dict)
                download_url = ydl.extract_info(video_url, download=False)['url']
                return video_name, download_url
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)
    return video_name, download_url

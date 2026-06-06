#!/usr/bin/env python3
import yt_dlp
import os, requests
url = 'https://www.youtube.com/watch?v=0sMPkL8CD_w'


class AudioDownloader:
    def __init__(self, download_path="../data", audio_only=True):
        os.makedirs(download_path, exist_ok=True)
        self.url = None
        self.download_path = download_path
        self.audio_only = audio_only
        
        # Output template
        outtmpl = os.path.join(download_path, '%(title)s/%(title)s.%(ext)s')
        
       # Base options
        base_opts = {
            'outtmpl': outtmpl,
            'quiet': True,
            'js_runtimes': {'node': {}},
            'sleep_interval': 5,
            'max_sleep_interval': 10,
            'remote_components': ['ejs:github'],
        }

        # Configure based on audio_only parameter
        if audio_only:
            # Audio only - extract MP3
            self.ydl_opts = {
                **base_opts,
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        else:
            # Full video - best quality
            self.ydl_opts = {
                **base_opts,
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',  # Merge to mp4
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }

        self.ydl = yt_dlp.YoutubeDL(self.ydl_opts)

    def download_audio(self, url):
        self.url = url
        try:
            info = self.ydl.extract_info(self.url, download=False)
            expected_filename = self.ydl.prepare_filename(info)
            print(f"Expected filename: {expected_filename}")
            base_path = os.path.dirname(expected_filename)
            file_name = os.path.basename(expected_filename)
            # if file already exists, skip download
            # if os.path.exists(expected_filename):
            #     print(f"\tFile already exists, skipping download: {expected_filename}")
            #     return expected_filename
            self.ydl.download([self.url])
            title = info['title']
            thumb_url = info['thumbnail']
            print(f"\tTitle: {info['title']}")
            try:
                print(f"\tThumbnail: {info['thumbnail']}")
                resp = requests.get(thumb_url)
                with open(f'{base_path}/{title}.jpg', 'wb') as f:
                    f.write(resp.content)
            except Exception as e:
                print(f"\tError downloading thumbnail: {e}")
            if self.audio_only:
                expected_filename = os.path.splitext(expected_filename)[0] + '.mp3'
            return expected_filename
        except Exception as e:
            print(f"\tError downloading audio: {e}")

if __name__ == "__main__":
    downloader = AudioDownloader(audio_only=False)
    downloader.download_audio(url)

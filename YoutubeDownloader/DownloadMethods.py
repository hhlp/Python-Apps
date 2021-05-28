from __future__ import unicode_literals
import youtube_dl


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

def my_hook(d):
    if d["status"] == "downloading":
        print(d["_percent_str"])


class Download(object):
    def __init__(self, url, save_path, quality, playlist=False):
        self.url = url
        self.save_path = save_path
        self.qualities = {"Best": "1411",
                          "Semi": "320",
                          "Worst": "128"}
        self.quality = self.qualities[quality]
        self.playlist = playlist

    def mp3_download(self):
        opts = {
            "verbose": False,
            "fixup"  : "detect_or_warn",
            "format" : "bestaudio/best",
            "postprocessors" : [{
                "key": "FFmpegExtractAudio",
                "preferredcodec"  : "mp3",
                "preferredquality": self.quality
            }],
            "logger": MyLogger(),
            "extractaudio": True,
            "process_hooks": [my_hook]
            "outtmpl"     : self.save_path + "/%(title)s.%(ext)s",
            "noplaylist"  : self.playlist
        }
        download_object = youtube_dl.YoutubeDL(opts)
        download_object.download([self.url])

    def mp4_download(self):
        opts = {
            "verbose": False,
            "fixup"  : "detect_or_warn",
            "format" : "bestaudio/best",
            "postprocessors" : [{
                "key": "FFmpegVideoConverter",
                "preferredcodec"  : "mp4",
            }],
            "outtmpl"     : self.save_path + "/%(title)s.%(ext)s",
            "noplaylist"  : self.playlist
        }
        download_object = youtube_dl.YoutubeDL(opts)
        download_object.download([self.url])

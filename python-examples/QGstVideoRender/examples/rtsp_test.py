from threading import Thread
from time import sleep
import signal

import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstRtsp", "1.0")
gi.require_version("GstRtspServer", "1.0")

from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QVBoxLayout)
from PyQt5.QtWidgets import QMainWindow, QWidget
import sys

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GLib, GObject, Gst, GstRtsp, GstRtspServer
Gst.init(None)


class VideoWindow(QMainWindow):

    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("Simple qtvideosink Test")
        w = QWidget(self)
        w.setLayout(QVBoxLayout())
        self.setCentralWidget(w)

        # UDP Sink
        video_src = 'v4l2src device=/dev/video0'
        video_src = 'videotestsrc'
        pipeline_str = (f'{video_src} '
                        '! videoconvert '
                        '! videoscale '
                        '! video/x-raw,width=1920,height=1080 '
                        '! textoverlay text="pyuscope rtsp test" font-desc="arial 16" '
                        '! openh264enc '
                        '! h264parse '
                        '! rtph264pay config-interval=1 pt=96 '
                        '! udpsink host=127.0.0.1 port=8004'
                        )

        pipeline = Gst.parse_launch(pipeline_str)
        pipeline.set_state(Gst.State.PLAYING)

        # Create RTSP server
        server = GstRtspServer.RTSPServer.new()
        server.props.service = "8004"
        server.attach(None)
        media_factory = GstRtspServer.RTSPMediaFactory.new()

        video_src = 'v4l2src device=/dev/video0'
        media_factory.set_launch("(udpsrc "
                                 "name=pay0 "
                                 "port=8004 "
                                 "buffer-size=524288 "
                                 "caps=\"application/x-rtp, media=video, "
                                 "clock-rate=90000, "
                                 "encoding-name=H264, "
                                 "payload=96 \")")

        media_factory.set_shared(True)
        server.get_mount_points().add_factory("/feed", media_factory)

        url = "rtsp://127.0.0.1:8004/feed"
        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        video_widget = QVideoWidget()
        w.layout().addWidget(video_widget)
        self.player.setVideoOutput(video_widget)
        self.player.setMedia(QMediaContent(QUrl(url)))
        self.player.play()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(800, 600)
    player.show()
    sys.exit(app.exec_())




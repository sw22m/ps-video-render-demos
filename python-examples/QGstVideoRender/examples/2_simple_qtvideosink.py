"""
Simple qtvideosink Test

"""

from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QVBoxLayout)
from PyQt5.QtWidgets import QMainWindow, QWidget
import sys

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
Gst.init(None)

class VideoWindow(QMainWindow):

    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("Simple qtvideosink Test")
        w = QWidget(self)
        w.setLayout(QVBoxLayout())
        self.setCentralWidget(w)

        # self.vidpip = Gst.ElementFactory.make("playbin", "player")
        # video_src = Gst.ElementFactory.make("videotestsrc", None)
        # video_sink = Gst.ElementFactory.make("ximagesink", "qtvideosink")

        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        video_widget = QVideoWidget()
        w.layout().addWidget(video_widget)
        self.player.setVideoOutput(video_widget)

        # RTSP Server command
        pipeline_str = f"videotestsrc ! openh264enc ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=127.0.0.1 port=8004"
        pipeline_str = ('v4l2src device=/dev/video0 '
                        '! videoconvert '
                        '! videoscale '
                        '!  video/x-raw,width=1920,height=1080 '
                        '! textoverlay text="pyuscope rtsp test" font-desc="arial 16" '
                        '! openh264enc '
                        '! h264parse '
                        '! rtph264pay config-interval=1 pt=96 '
                        '! udpsink host=127.0.0.1 port=8004')
        pipeline = Gst.parse_launch(pipeline_str)
        pipeline.set_state(Gst.State.PLAYING)

        # RTSP Client sink
        self.player.setMedia(QMediaContent(QUrl("gst-pipeline: udpsrc address=127.0.0.1 port=8004 "
                                                "! application/x-rtp,media=video,clock-rate=90000, encoding-name=H264,payload=96 "
                                                "! rtph264depay "
                                                "! avdec_h264 "
                                                "! xvimagesink name=\"qtvideosink\"")))
        self.player.play()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(800, 600)
    player.show()
    sys.exit(app.exec_())
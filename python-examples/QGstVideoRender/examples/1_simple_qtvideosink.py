"""
Simple qtvideosink Test

"""

from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QVBoxLayout)
from PyQt5.QtWidgets import QMainWindow, QWidget
import sys

class VideoWindow(QMainWindow):

    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("Simple qtvideosink Test")
        w = QWidget(self)
        w.setLayout(QVBoxLayout())
        self.setCentralWidget(w)

        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        video_widget = QVideoWidget()
        w.layout().addWidget(video_widget)
        self.media_player.setVideoOutput(video_widget)
        self.media_player.setMedia(QMediaContent(QUrl('gst-pipeline: videotestsrc ! ximagesink name="qtvideosink"')))
        self.media_player.play()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(800, 600)
    player.show()
    sys.exit(app.exec_())
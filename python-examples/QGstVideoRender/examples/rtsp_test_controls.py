"""
Object code
"""

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
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QVBoxLayout, QPushButton
import sys

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GLib, GObject, Gst, GstRtsp, GstRtspServer
Gst.init(None)


class ARtspMediaFactory(GstRtspServer.RTSPMediaFactory):

    def __init__(self, port, host="localhost", pipeline=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pipeline = pipeline
        self.port = port
        self.host = host

    def do_create_element(self, url):
        video_src = 'videotestsrc'
        rtsp_bin = Gst.Bin.new("rtsp_bin")
        udp_src = Gst.ElementFactory.make("udpsrc")
        udp_src.set_property("name", "pay0")
        udp_src.set_property("port", self.port)

        caps = Gst.Caps.new_empty_simple("application/x-rtp")
        caps.set_value("media", "video")
        caps.set_value("buffer-size", 524288)
        caps.set_value("clock-rate", 90000)
        caps.set_value("encoding-name", "H264")
        caps.set_value("payload", 96)
        udp_src.set_property("caps", caps)
        rtsp_bin.add(udp_src)
        return rtsp_bin


class VideoWindow(QMainWindow):

    RTSP_SERVER_HOST = "127.0.0.1"
    RTSP_SERVER_PORT = 8004

    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("Simple qtvideosink Test")
        w = QWidget(self)
        w.setLayout(QVBoxLayout())
        self.setCentralWidget(w)

        self.player = Gst.Pipeline.new("player")
        source = Gst.ElementFactory.make("videotestsrc")
        videocrop = Gst.ElementFactory.make("videocrop")
        videoscale = Gst.ElementFactory.make("videoscale")
        videoflip = Gst.ElementFactory.make("videoflip")
        videoflip.set_property("method", "horizontal-flip")
        self.textoverlay = Gst.ElementFactory.make("textoverlay")
        self.textoverlay.set_property("text", "URL")
        self.textoverlay.set_property("valignment", "top")
        self.textoverlay.set_property("font-desc", "Sans, 32")
        capsfilter = Gst.ElementFactory.make("capsfilter")
        openh264enc = Gst.ElementFactory.make("openh264enc")
        h264parse = Gst.ElementFactory.make("h264parse")



        rtph264_filter = Gst.ElementFactory.make("rtph264pay")
        rtph264_filter.set_property("name", "pay0")
        rtph264_filter.set_property("pt", 96)
        rtph264_filter.set_property("config-interval", 1)

        self.player.add(source)
        self.player.add(videocrop)
        self.player.add(videoscale)
        self.player.add(videoflip)
        self.player.add(self.textoverlay)
        self.player.add(capsfilter)
        self.player.add(openh264enc)
        self.player.add(h264parse)
        self.player.add(rtph264_filter)

        source.link(videocrop)
        videocrop.link(videoscale)
        videoscale.link(videoflip)
        videoflip.link(self.textoverlay)
        self.textoverlay.link(openh264enc)
        openh264enc.link(h264parse)
        h264parse.link(rtph264_filter)

        udp_sink = Gst.ElementFactory.make("udpsink")
        udp_sink.set_property("host", "127.0.0.1")
        udp_sink.set_property("port", self.RTSP_SERVER_PORT)
        self.player.add(udp_sink)
        rtph264_filter.link(udp_sink)

        # UDP Sink
        video_src = 'videotestsrc'

        # Create RTSP server
        self.server = GstRtspServer.RTSPServer.new()
        self.server.props.service = f"{self.RTSP_SERVER_PORT}"
        self.server.attach(None)
        self.mount_point = "feed"

        # media_factory = ARtspMediaFactory.custom_pipeline_factory(self.player)
        media_factory = ARtspMediaFactory(port=self.RTSP_SERVER_PORT)
        media_factory.set_shared(True)
        # rtsp_url = GstRtsp.RTSPUrl()
        # rtsp_url.set_port(8554)
        self.player.set_state(Gst.State.PLAYING)
        self.server.get_mount_points().add_factory(f"/{self.mount_point}", media_factory)
        self.server.attach(None)

        url = f"rtsp://127.0.0.1:{self.RTSP_SERVER_PORT}/{self.mount_point}"
        self.textoverlay.set_property("text", f"{url}")
        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        video_widget = QVideoWidget()
        self.player.setVideoOutput(video_widget)
        w.layout().addWidget(video_widget)

        self.pb_start = QPushButton("Start Server")
        self.pb_start.setCheckable(True)
        self.pb_start.clicked.connect(self.on_start)
        w.layout().addWidget(self.pb_start)

    def on_start(self):
        print(f"Enable server: {self.pb_start.isChecked()}")
        if self.pb_start.isChecked():
            self.play()

    def play(self):
        url = f"rtsp://127.0.0.1:{self.RTSP_SERVER_PORT}/{self.mount_point}"
        self.textoverlay.set_property("text", f"{url}")
        self.player.setMedia(QMediaContent(QUrl(url)))
        self.player.play()

    def stop(self):
        print("Stop server")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(800, 600)
    player.show()
    sys.exit(app.exec_())




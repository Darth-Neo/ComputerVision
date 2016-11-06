#!/usr/bin/env python
import os
import sys
import urllib
import time
from threading import Thread
import ConfigParser
from StringIO import StringIO
import numpy as np

# Note: this import if from cv2.so, which must be in the same directory or bad things happen
import cv2

from Logger import *
logger = setupLogging(__name__)
logger.setLevel(INFO)


class FoscamCamera(object):
    UP         = 0
    STOP_UP    = 1
    DOWN       = 2
    STOP_DOWN  = 3
    LEFT       = 4
    STOP_LEFT  = 5
    RIGHT      = 6
    STOP_RIGHT = 7

    qim = None
    pm = None
    qw = None
    videothread = None

    faceCascade = cv2.CascadeClassifier(u"haarcascade_frontalface_alt2.xml")

    ImageReadyEventId = 1382

    def __init__(self, host=u"", user=u"", pwd=u""):
        super(FoscamCamera, self).__init__()

        self._isPlaying = 0

        if host is None or len(host) == 0:
            configFile = u"foscam.conf"

            Config = ConfigParser.ConfigParser()
            Config.read(configFile)

            d = self.ConfigSectionMap(u"foscam", Config)
            self.user = d[u'user']
            self.password = d[u'pwd']
            self.host = d[u'host']

        else:
            self.user = user
            self.password = pwd
            self.host = host

    def isPlaying(self):
        return self._isPlaying

    def setIsPlaying(self, val):
        self._isPlaying = val

    def move(self, direction):
        cmd = {u"command": direction}
        f = self.sendCommand(u"decoder_control.cgi", cmd)

    def snapshot(self):
        f = self.sendCommand(u"snapshot.cgi", {})
        return f.read()

    def sendCommand(self, cgi, parameterDict):
        url = u"http://%s/%s?user=%s&pwd=%s" % (self.host, cgi, self.user, self.password)
        for param in parameterDict:
            url += u"&%s=%s" % (param, parameterDict[param])

        return urllib.urlopen(url)

    def startVideo(self, callback=None, userdata=None):
        if not self.isPlaying():
            cmds = {u"resolution": 32, u"rate": 0 }
            f = self.sendCommand(u"videostream.cgi", cmds)

            self.videothread = Thread(target=self.findFrame,
                                      args=(self, f, callback, userdata))
            self.setIsPlaying(1)
            self.videothread.start()

    def stopVideo(self):
        if self.isPlaying():
            self.setIsPlaying(0)

    def getVideo(self):

        logger.info(u"Playing a little video (30 seconds worth)")

        counter = Counter()

        self.startVideo(FoscamCamera.dummy_videoframe_handler, counter)
        time.sleep(30)
        logger.info(u"Stopping video")
        self.stopVideo()

        return counter

    def getSnapShot(self):
        logger.info(u"Taking a few snapshots")

        for i in xrange(1, 3):
            data = self.snapshot()
            with open(u"./snapshots/snapshot-%02d.jpg" % i, u"wb") as fileSnap:
                fileSnap.write(data)

            logger.info(u"Wrote snapshot %d" % i)

    def moveCamera(self):
        logger.info(u"moving up")
        self.move_a_little(self.UP, self.STOP_UP)
        logger.info(u"moving down")
        self.move_a_little(self.DOWN, self.STOP_DOWN)
        logger.info(u"moving left")
        self.move_a_little(self.LEFT, self.STOP_LEFT)
        logger.info(u"moving right")
        self.move_a_little(self.RIGHT, self.STOP_RIGHT)

    def move_a_little(self, go, stop):
        self.move(go)
        time.sleep(2)
        logger.info(u" - stopping move")
        self.move(stop)

    @staticmethod
    def ConfigSectionMap(section, Config):
        dictV1 = dict()
        options = Config.options(section)

        for option in options:
            try:
                dictV1[option] = Config.get(section, option)

                if dictV1[option] == -1:
                    logger.debug(u"skip: %s" % option)
            except Exception, msg:
                logger.debug(u"%s on %s!" % (msg, option))
                dictV1[option] = None

        logger.debug(u"dict : %s" % dictV1)

        return dictV1

    @staticmethod
    def dummy_videoframe_handler(frame, userdata=None):
        """test video frame handler. It assumes the userdata coming
        in is a Counter object with an increment method and a count method"""
        sys.stdout.write("Got frame %d\r" % userdata.count())
        sys.stdout.flush()
        userdata.increment()

    @staticmethod
    def videoCallback(frame, userdata=None):
        nparr = np.fromstring(frame, np.uint8)
        img = cv2.imdecode(nparr, cv2.CV_LOAD_IMAGE_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = FoscamCamera.faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            logger.info(u"Found face")

        # with open("picture.png", "wb") as f:
        #  f.write(img)

        cv2.imwrite(u"picture.png", img)

    @staticmethod
    def findFrame(parent, fp, callback=None, userdata=None):
        while parent.isPlaying():
            line = fp.readline()
            if line[:len(u"--ipcamera")] == u"--ipcamera":
                fp.readline()
                content_length = int(fp.readline().split(u":")[1].strip())
                fp.readline()
                jpeg = fp.read(content_length)
                if callback:
                    callback(jpeg, userdata)

    @staticmethod
    def getFrames(counter):

        nframes = counter.count() - 1
        logger.info(u"%s frames in ~30 secs for ~%3.2f fps" % (nframes, nframes / 30.0))


class Counter(object):
    def __init__(self):
        super(Counter, self).__init__()
        self._count = 0

    def increment(self):
        self._count += 1

    def count(self):
        return self._count


if __name__ == u"__main__":

    logger.info(u"Testing the Foscam camera code")

    fc = FoscamCamera()

    fc.moveCamera()

    fc.getSnapShot()

    counter = fc.getVideo()

    fc.getFrames(counter)

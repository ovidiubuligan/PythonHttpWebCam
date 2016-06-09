#!/usr/bin/python
'''
	orig author: Igor Maculan - n3wtron@gmail.com
	A Simple mjpg stream http server
'''
import cv2
import ConfigParser
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from threading import Thread
import threading
import time

config = {}

captureThread = None

def init_config(config):
	config_parser = ConfigParser.ConfigParser()
	config_parser.read('config.cfg')

	config['CaptureWidth'] = config_parser.getint('Root', 'CaptureWidth')
	config['CaptureHeight'] = config_parser.getint('Root', 'CaptureHeight')
	config['ImageRefreshInterval'] = config_parser.getfloat('Root', 'ImageRefreshInterval')
	config['IdleCameraStop'] = config_parser.getint('Root', 'IdleCameraStop')
	config['Port'] = config_parser.getint('Root', 'Port')
	config['CameraSource'] = config_parser.getint('Root', 'CameraSource')


class CamHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		print self.path
		if self.path.endswith('.mjpg'):
			self.send_response(200)
			self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
			self.end_headers()
			while True:
				try:
					global captureThread
					imgBuffer = captureThread.ReadBuffer()
					if imgBuffer is None:
						continue
					self.wfile.write("--jpgboundary\r\n")
					self.send_header('Content-type', 'image/jpeg')
					self.send_header('Content-length', str(len(imgBuffer)))
					self.end_headers()
					self.wfile.write(bytearray(imgBuffer))
					self.wfile.write('\r\n')
					time.sleep(config['ImageRefreshInterval'])
				except KeyboardInterrupt:
					break
			return
		if self.path.endswith('.html') or self.path == "/":
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			self.wfile.write('<html><head></head><body>')
			self.wfile.write('<img src="/cam.mjpg"/>')
			self.wfile.write('</body></html>')
			return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""


class CaptureThread(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.stopped = False
		self.paused = False
		self.ImageBuff = None
		self.LastAcessed = time.time()
		self.IdleCameraStop = config['IdleCameraStop']
		self.RefreshInterval = config['ImageRefreshInterval']
		self.capture = None

		self.ImageBuffLock = threading.Lock()
		self.InitCaputure()

	def run(self):
		while not self.stopped:
			if self.capture and self.capture.isOpened():
				self.WriteBuffer()
			if((time.time() - self.LastAcessed)> self.IdleCameraStop):
				self.ReleaseCapture()
			time.sleep(self.RefreshInterval)
		# call a function

	def InitCaputure(self):
		print "initializing capture device"
		self.capture = cv2.VideoCapture(config['CameraSource'])
		#self.capture = cv2.VideoCapture('hst_1.mpg');  # CAP_FFMPEG
		self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, config['CaptureWidth'])
		self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, config['CaptureHeight'])

	def ReleaseCapture(self):
		if self.capture and self.capture.isOpened():
			self.capture.release()
			print "capture device released"

	def WriteBuffer(self):
		rc, img = self.capture.read()
		if not rc:
			return
		imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		with self.ImageBuffLock:
			r, self.ImageBuff= cv2.imencode(".jpg", imgRGB)

	def ReadBuffer(self):
		if self.capture and not self.capture.isOpened():
			self.InitCaputure()
			self.WriteBuffer()

		self.LastAcessed = time.time()
		return self.ImageBuff

def main():
	global capture
	init_config(config)

	global captureThread
	captureThread = CaptureThread()
	captureThread.start();


	try:
		server = ThreadedHTTPServer(('', config['Port']), CamHandler)
		# Prevent issues with socket reuse
		server.allow_reuse_address = True
		print "server started"
		server.serve_forever()
	except KeyboardInterrupt:
		captureThread.stopped = True
		server.socket.close()
	capture.release()


if __name__ == '__main__':
	main()

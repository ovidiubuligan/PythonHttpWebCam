#!/usr/bin/python
'''
	orig author: Igor Maculan - n3wtron@gmail.com
	A Simple mjpg stream http server
'''
import cv2
import ConfigParser
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import time

capture = None
config = {}

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
					rc, img = capture.read()
					if not rc:
					zz	continue
					imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
					r, buf = cv2.imencode(".jpg", imgRGB)
					self.wfile.write("--jpgboundary\r\n")
					self.send_header('Content-type', 'image/jpeg')
					self.send_header('Content-length', str(len(buf)))
					self.end_headers()
					self.wfile.write(bytearray(buf))
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


def main():
	global capture
	init_config(config)

	# capture = cv2.VideoCapture(config['CameraSource'])
	capture = cv2.VideoCapture('hst_1.mpg');  # CAP_FFMPEG
	capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, config['CaptureWidth'])
	capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, config['CaptureHeight'])
	try:
		server = ThreadedHTTPServer(('', config['Port']), CamHandler)
		# Prevent issues with socket reuse
		server.allow_reuse_address = True
		print "server started"
		server.serve_forever()
	except KeyboardInterrupt:
		capture.release()
		server.socket.close()
	capture.release()


if __name__ == '__main__':
	main()

Small multithreaded python2 HTTP sever that serves videos from device camera in `mjpeg` format to web browsers , extended from : https://gist.github.com/n3wtron/4624820 . It uses Opencv 2 so it should work on windows/mac/linux.

You can use `pyinstaller` (http://www.pyinstaller.org/)  to create a windows/linux/macos build. This is how the release waw created.

*TODO* Change threading model 
"""                        
						A^2 Player
    Developed a Media player with two special features:
	1. Automated Subtitle Downloading
	2. Bookmarking of the video

"""



#import sip #only to count no "/" in rfind
#sip.setapi('QString', 2)

from PyQt4 import QtCore, QtGui

from mainwindow import MainWindow
import sys

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	app.setApplicationName("A^2_player")
	app.setQuitOnLastWindowClosed(True)

	window = MainWindow()
	window.show()
	
	

	sys.exit(app.exec_())

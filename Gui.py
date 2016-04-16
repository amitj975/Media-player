from PyQt4 import QtCore, QtGui
from PyQt4.phonon import Phonon

class Gui(object):

	def __init__(self,mainwindow):
		self.mainwindow=mainwindow
	


	def setupUi(self):

		hbox = QtGui.QHBoxLayout()

		headers = "PlayList"

		self.mainwindow.videoTable = QtGui.QTreeWidget()
		self.mainwindow.videoTable.setHeaderLabel(headers)
		self.mainwindow.videoTable.itemClicked.connect(self.mainwindow.tableClicked)
		self.mainwindow.videoTable.itemDoubleClicked.connect(self.mainwindow.tableClicked)
		rightFrame = QtGui.QFrame(self.mainwindow)
		self.setup_right_frame(rightFrame)
	

		self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
		self.splitter.addWidget(self.mainwindow.videoTable)
		self.splitter.addWidget(self.mainwindow.videoWidget)

		hbox.addWidget(self.splitter)
		w = self.splitter.width()
		self.splitter.setSizes([w/4,3*w/4])
		widget = QtGui.QWidget()
		widget.setLayout(hbox)
		self.splitter.setChildrenCollapsible(True)

	

		return widget



	def setup_right_frame(self, rightFrame):#initial right frame UI
		
		bar = QtGui.QToolBar(self.mainwindow.videoWidget.tempWidget)
		#bar.addAction(self.mainwindow.playAction)
		#bar.addAction(self.mainwindow.stopAction)
		self.btn = QtGui.QPushButton()
		self.btn.setIcon(QtGui.QIcon.fromTheme("media-playback-start"))
		self.btn.clicked.connect(self.mainwindow.play_and_pause)
		self.btn.setDisabled(True)
		self.btn.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Space))
		self.btn_fscr =  QtGui.QPushButton()
		self.btn_fscr.setIcon(QtGui.QIcon.fromTheme("view-fullscreen"))
		self.btn_fscr.clicked.connect(self.mainwindow.compute)
		#self.mainwindow.videoWidget.addAction(self.mainwindow.fullScrAction)
		self.mainwindow.videoWidget.addAction(self.mainwindow.loopAction)
		self.mainwindow.videoWidget.addAction(self.mainwindow.bookmarkAction)
		self.mainwindow.videoWidget.addAction(self.mainwindow.speedAction)
		self.mainwindow.videoWidget.addAction(self.mainwindow.playlistAction)
		self.mainwindow.videoWidget.addAction(self.mainwindow.seek_forward)
		self.mainwindow.videoWidget.addAction(self.mainwindow.seek_backward)
		bar.setGeometry(0,440,30,30)
		self.btn_fscr.setShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL+QtCore.Qt.Key_L))
		#bar.setMovable(True)
		#bar.setAutoFillBackground(True)
		#bar.setWindowOpacity(0.0)

		self.mainwindow.videoWidget.addAction(self.mainwindow.computeAction)
		#self.mainwindow.videoWidget.addAction(self.mainwindow.playAction)
		#self.mainwindow.videoWidget.addAction(self.mainwindow.pauseAction)
		#self.mainwindow.videoWidget.addAction(self.mainwindow.fullScrAction)

		#print str(self.mainwindow.videoWidget.x())+" "+str(self.mainwindow.videoWidget.y())

		seekSlider = Phonon.SeekSlider()
		seekSlider.Mainwindow = self.mainwindow
		#seekSlider.setGeometry(50,440,400,30)
		seekSlider.setMediaObject(self.mainwindow.media_object)

		volumeSlider = 	Phonon.VolumeSlider()
		volumeSlider.setAudioOutput(self.mainwindow.audioOutput)
		volumeSlider.setSizePolicy(QtGui.QSizePolicy.Maximum, 
			QtGui.QSizePolicy.Maximum)


		self.mainwindow.timeLabel = QtGui.QLabel(self.mainwindow.videoWidget.tempWidget)
		self.mainwindow.timeLabel.setStyleSheet("QLabel { color :lightblue; }");
		self.mainwindow.timeLabel.setText("00:00:00/00:00:00")
		self.mainwindow.current_time = 0
		self.mainwindow.timeLabel.setWordWrap(True)


		#self.mainwindow.timeLabel.setAlignment(QtCore.Qt.AlignRight)
		#self.mainwindow.timeLabel.setSizePolicy(QtGui.QSizePolicy.Maximum,
			#QtGui.QSizePolicy.Maximum)#this code is very important
		#it's used for fixing seekerLayout size, in order to maximum
		#videoWidget as big as possible
		playbackLayout = QtGui.QHBoxLayout()
		playbackLayout.setAlignment(QtCore.Qt.AlignRight)
		playbackLayout.addWidget(volumeSlider)

		seekerLayout = QtGui.QHBoxLayout(self.mainwindow.videoWidget.tempWidget)
		seekerLayout.addWidget(self.btn)
		seekerLayout.addWidget(seekSlider)
		seekerLayout.addWidget(self.mainwindow.timeLabel)
		seekerLayout.addWidget(self.btn_fscr)
		#seekerLayout.addWidget(volumeSlider)
		seekerLayout.setSpacing(1)
		seekerLayout.addLayout(playbackLayout)
		#seekerLayout.setGeometry(QtCore.QRect(430,0,430,20))
		self.mainwindow.videoWidget.tempWidget.setLayout(seekerLayout)
		self.mainwindow.videoWidget.tempWidget.setGeometry(0,430,600,50)
		'''self.mainwindow.videoWidget.tempWidget.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.mainwindow.videoWidget.tempWidget.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.mainwindow.videoWidget.tempWidget.setStyleSheet("background-color:transparent;")'''

		
		#bar.addWidget(self.mainwindow.videoWidget)
		#mainLayout = QtGui.QVBoxLayout()
		#mainLayout.addWidget(self.mainwindow.videoWidget)
		#mainLayout.addLayout(seekerLayout)
		#mainLayout.addLayout(playbackLayout)

		#rightFrame.setLayout(mainLayout)


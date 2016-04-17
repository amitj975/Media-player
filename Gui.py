from PyQt4 import QtCore, QtGui
from PyQt4.phonon import Phonon

#Gui class handle the mainwindow widget and labels
class Gui(object):
	
	#Constructor
	def __init__(self,mainwindow):
		self.mainwindow=mainwindow
	
	#to setup ui
	def setupUi(self):

		hbox = QtGui.QHBoxLayout()

		headers = "PlayList"

		#Tree view for the Playlist
		self.mainwindow.videoTable = QtGui.QTreeWidget()
		self.mainwindow.videoTable.setHeaderLabel(headers)
		self.mainwindow.videoTable.itemClicked.connect(self.mainwindow.tableClicked)
		self.mainwindow.videoTable.itemDoubleClicked.connect(self.mainwindow.tableClicked)
		
		#Main Window consists of video widget and toolbar
		rightFrame = QtGui.QFrame(self.mainwindow)
		self.setup_right_frame(rightFrame)
		
		#splitter btw Playlist and mainwindow
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


	#initial right frame UI
	def setup_right_frame(self, rightFrame):
		
		#Setting up toolbar
		bar = QtGui.QToolBar(self.mainwindow.videoWidget.tempWidget)
		self.btn = QtGui.QPushButton()
		self.btn.setIcon(QtGui.QIcon.fromTheme("media-playback-start"))
		self.btn.clicked.connect(self.mainwindow.play_and_pause)
		self.btn.setDisabled(True)
		self.btn.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Space))
		self.btn_fscr =  QtGui.QPushButton()
		self.btn_fscr.setIcon(QtGui.QIcon.fromTheme("view-fullscreen"))
		self.btn_fscr.clicked.connect(self.mainwindow.compute)
		
		#Adding All feature with VideoWidget
		self.mainwindow.videoWidget.addAction(self.mainwindow.loopAction)
		self.mainwindow.videoWidget.addAction(self.mainwindow.bookmarkAction)
		self.mainwindow.videoWidget.addAction(self.mainwindow.speedAction)
		self.mainwindow.videoWidget.addAction(self.mainwindow.playlistAction)
		self.mainwindow.videoWidget.addAction(self.mainwindow.seek_forward)
		self.mainwindow.videoWidget.addAction(self.mainwindow.seek_backward)
		bar.setGeometry(0,440,30,30)
		self.btn_fscr.setShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL+QtCore.Qt.Key_L))
		self.mainwindow.videoWidget.addAction(self.mainwindow.computeAction)
		
		#Volume control and Seekbar of toolbar  
		seekSlider = Phonon.SeekSlider()
		seekSlider.Mainwindow = self.mainwindow
		seekSlider.setMediaObject(self.mainwindow.media_object)
		volumeSlider = 	Phonon.VolumeSlider()
		volumeSlider.setAudioOutput(self.mainwindow.audioOutput)
		volumeSlider.setSizePolicy(QtGui.QSizePolicy.Maximum, 
			QtGui.QSizePolicy.Maximum)


		#Time Label
		self.mainwindow.timeLabel = QtGui.QLabel(self.mainwindow.videoWidget.tempWidget)
		self.mainwindow.timeLabel.setStyleSheet("QLabel { color :lightblue; }");
		self.mainwindow.timeLabel.setText("00:00:00/00:00:00")
		self.mainwindow.current_time = 0
		self.mainwindow.timeLabel.setWordWrap(True)
		
		#Adding all element with their layout
		playbackLayout = QtGui.QHBoxLayout()
		playbackLayout.setAlignment(QtCore.Qt.AlignRight)
		playbackLayout.addWidget(volumeSlider)
		seekerLayout = QtGui.QHBoxLayout(self.mainwindow.videoWidget.tempWidget)
		seekerLayout.addWidget(self.btn)
		seekerLayout.addWidget(seekSlider)
		seekerLayout.addWidget(self.mainwindow.timeLabel)
		seekerLayout.addWidget(self.btn_fscr)
		seekerLayout.setSpacing(1)
		seekerLayout.addLayout(playbackLayout)
		self.mainwindow.videoWidget.tempWidget.setLayout(seekerLayout)
		self.mainwindow.videoWidget.tempWidget.setGeometry(0,430,600,50)

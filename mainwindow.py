from PyQt4 import QtCore, QtGui
from PyQt4.phonon import Phonon
from Gui import Gui
from bsub import getSubtitle 
import os
import sys
import threading
import time

# class Window(QtGui.QMainWindow):

#     def __init__(self):
#         super(Window, self).__init__()
#         self.setGeometry(50, 50, 500, 300)
#         self.setWindowTitle("PyQT tuts!")
#         self.setWindowIcon(QtGui.QIcon('pythonlogo.png'))

#         extractAction = QtGui.QAction("&GET TO THE CHOPPAH!!!", self)
#         extractAction.setShortcut("Ctrl+Q")
#         extractAction.setStatusTip('Leave The App')
#         extractAction.triggered.connect(self.close_application)

#         self.statusBar()

#         mainMenu = self.menuBar()
#         fileMenu = mainMenu.addMenu('&File')
#         fileMenu.addAction(extractAction)
        

#         self.home()

#     def home(self):
#         btn = QtGui.QPushButton("Quit", self)
#         btn.clicked.connect(self.close_application)
#         btn.resize(btn.minimumSizeHint())
#         btn.move(0,100)

#         extractAction = QtGui.QAction(QtGui.QIcon('todachoppa.png'), 'Flee the Scene', self)
#         extractAction.triggered.connect(self.close_application)
        
#         self.toolBar = self.addToolBar("Extraction")
#         self.toolBar.addAction(extractAction)

#         checkBox = QtGui.QCheckBox('Shrink Window', self)
#         checkBox.move(100, 25)
#         checkBox.stateChanged.connect(self.enlarge_window)

#         self.progress = QtGui.QProgressBar(self)
#         self.progress.setGeometry(200, 80, 250, 20)

#         self.btn = QtGui.QPushButton("Download",self)
#         self.btn.move(200,120)
#         self.btn.clicked.connect(self.download)

#         self.show()


#     def download(self):
#         self.completed = 0

#         while self.completed < 100:
#             self.completed += 0.0001
#             self.progress.setValue(self.completed)
        
        

#     def enlarge_window(self, state):
#         if state == QtCore.Qt.Checked:
#             self.setGeometry(50,50, 1000, 600)
#         else:
#             self.setGeometry(50, 50, 500, 300)
        


#     def close_application(self):
#         choice = QtGui.QMessageBox.question(self, 'Extract!',
#                                             "Get into the chopper?",
#                                             QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
#         if choice == QtGui.QMessageBox.Yes:
#             print("Extracting Naaaaaaoooww!!!!")
#             sys.exit()
#         else:
#             pass
        
        

    
# def run():
#     app = QtGui.QWidget()
#     app.show()




class MainWindow(QtGui.QMainWindow):
	flag_b=False
	loop_flag =False
	bookmark_flag =True
	video_name = 'xyz'
	visible=True
	time =0
	current_time=0
	playing = False;
	name_dict={}
	download=1

	def __init__(self):
		super(MainWindow, self).__init__()
		class Widget1(Phonon.VideoWidget):
			outer_self= self
			tempWidget = QtGui.QWidget()
			def __init__(self):
				super(Widget1,self).__init__()
			def resizeEvent(self, event):
				self.tempWidget.setParent(self)
				self.tempWidget.setGeometry(0,self.height()-50,self.width(),50)
				#self.tempWidget.show()
			def mouseMoveEvent(self,event):
				if(self.tempWidget.isHidden()):
					self.tempWidget.show()
					QtCore.QTimer.singleShot(10000,self.tempWidget.hide)
			def mouseReleaseEvent(self,event):
				if not self.outer_self.playing:
		 			self.outer_self.media_object.play()
		 			self.outer_self.gui.btn.setIcon(QtGui.QIcon.fromTheme("media-playback-pause"))
		 			self.outer_self.playing = True
				else:
		 			self.outer_self.media_object.pause()
		 			self.outer_self.gui.btn.setIcon(QtGui.QIcon.fromTheme("media-playback-start"))	
		 			self.outer_self.playing = False
			def mouseDoubleClickEvent(self,event):
				if self.isFullScreen():
					self.setFullScreen(False)
					self.outer_self.show()
					self.outer_self.gui.btn_fscr.setIcon(QtGui.QIcon.fromTheme("view-fullscreen"))
					self.tempWidget.show()
					
				else:
					self.setFullScreen(True)
					self.outer_self.hide()
					self.outer_self.gui.btn_fscr.setIcon(QtGui.QIcon.fromTheme("view-restore"))
					self.tempWidget.hide()


		self.media_object = None
		self.current_time = 0
		self.totalTime =QtCore.QTime((int(00 / 3600000) % 24), int((00 / 60000) % 60),
						int((00 / 1000) % 60))
		
		self.audioOutput = Phonon.AudioOutput(Phonon.VideoCategory, self)
		self.media_object = Phonon.MediaObject(self)

		
		#self.videoUI = QtGui.QWidget()
		self.videoWidget = Widget1()
		#self.path = Phonon.createPath(self.media_object, self.audioOutput)#link media source with video output
		Phonon.createPath(self.media_object, self.videoWidget)


		self.media_object.setTickInterval(1000) #1 milliseconds

		self.setWindowTitle("A^2_Player")
		self.setMinimumSize(500, 500)

		Phonon.createPath(self.media_object, self.audioOutput)#link media source with audio output
		
		self.media_object.stateChanged.connect(self.stateChanged)
		self.media_object.currentSourceChanged.connect(self.sourceChanged)
		self.media_object.finished.connect(self.finished)

		self.media_object.tick.connect(self.tick)

		self.setupActions()
		self.setupMenus()
		
		self.gui=Gui(self);
		window=self.gui.setupUi()
		self.setCentralWidget(window)		

		self.sources = []



	def tick(self, time):
		displayTime = QtCore.QTime((time / 3600000) % 24, (time / 60000) % 60,
						(time / 1000) % 60)
		self.timeLabel.setText(displayTime.toString("HH:mm:ss")+"/"+self.totalTime.toString("HH:mm:ss"))
		if not self.flag_b:
			self.current_time = time



	def stateChanged(self, newState, oldState):
		if newState == Phonon.ErrorState:
			if self.media_object.errorType() == Phonon.FatalError:
				QtGui.QMessageBox.warning(self, "Fatal Error",
					self.media_object.errorString())
			else:
				QtGui.QMessageBox.warning(self, "Error",
					self.media_object.errorString())
		elif newState == Phonon.PlayingState:
			self.playAction.setEnabled(False)
			self.pauseAction.setEnabled(True)
			self.stopAction.setEnabled(True)
			self.computeAction.setEnabled(True)
			self.fullScrAction.setEnabled(True)
			self.seek_backward.setEnabled(True)
			self.seek_forward.setEnabled(True)
			
			self.totalTime = QtCore.QTime((int(self.media_object.totalTime() / 3600000) % 24), int((self.media_object.totalTime() / 60000) % 60),
						int((self.media_object.totalTime() / 1000) % 60))

			displayTime = QtCore.QTime((self.current_time / 3600000) % 24, (self.current_time / 60000) % 60,
						(self.current_time / 1000) % 60)
			
			self.timeLabel.setText(displayTime.toString("HH:mm:ss")+"/"+self.totalTime.toString("HH:mm:ss"))
			self.playing = True
			###print self.timeLabel.text()
			#self.current_time = self.time
			self.media_object.seek(self.current_time)
		elif newState == Phonon.StoppedState:
			self.stopAction.setEnabled(False)
			self.playAction.setEnabled(True)
			self.gui.btn.setEnabled(True)
			self.gui.btn.setIcon(QtGui.QIcon.fromTheme("media-playback-pause"))
			self.pauseAction.setEnabled(False)
			#self.timeLabel.setText("00:00:00")
			##print self.current_time
			##print self.flag_b
			if not self.flag_b:
				self.current_time = 0
			self.computeAction.setEnabled(False)
			self.fullScrAction.setEnabled(True)
			###print "stopping"
			self.flag_b=False
		elif newState == Phonon.PausedState:
			self.pauseAction.setEnabled(False)
			self.stopAction.setEnabled(True)
			self.playAction.setEnabled(True)
			self.computeAction.setEnabled(True)
			self.fullScrAction.setEnabled(True)
			#if(self.time==0):
				#self.time = self.current_time


	def sourceChanged(self, source):
		#self.videoTable.setCurrentItem(self.videoTable.topLevelItem(self.sources.index(source)))
		#self.timeLabel.setText("00:00:00")
		#self.current_time = 0
		print("yes")
		###print self.current_time
		#self.flag_b=False

	def tableClicked(self, item_x,col):	
		#self.flag_b=False

		self.media_object.stop()
		self.media_object.clearQueue()
		###print self.videoTable.indexOfTopLevelItem(item_x)
		###print col
		self.video_name=item_x.text(col)
		###print(self.videoTable.indexOfTopLevelItem(item_x).text())
		self.media_object.setCurrentSource(self.sources[self.videoTable.indexOfTopLevelItem(item_x)])
		###print "wohoo"
		self.media_object.play()
		self.videoTable.setCurrentItem(item_x)
		self.timeLabel.setText("00:00:00/00:00:00")
		self.current_time = 0
		self.time=0
		#if playing currently, continue playing the click one


		if item_x.parent() != None:
			child_idx = item_x.parent().indexOfChild(item_x)
			bmark_file = open(item_x.parent().text(0)+".txt","r")
			idx =0;
			for line in bmark_file:
				if idx == child_idx:
					##print "Yes"
					self.name = str(line)
					break
				idx = idx+1


			###print long(name[7:-1])
			idx = 0;
			while(self.name[idx] != '('):
				idx = idx+1

			self.current_time = long(self.name[(idx+1):-2])
			###print self.current_time
			self.flag_b=True
			
		#self.media_object.play()

	
	def setupActions(self):
		self.playAction = QtGui.QAction(
			self.style().standardIcon(QtGui.QStyle.SP_MediaPlay), "Play",
			self, shortcut="Space", enabled = True,
			triggered = self.media_object.play)
		self.playAction.toggle()

		self.pauseAction = QtGui.QAction(
			self.style().standardIcon(QtGui.QStyle.SP_MediaPause), "Pause",
			self, shortcut="Space", enabled=False,
			triggered = self.media_object.pause)

		self.stopAction = QtGui.QAction(
			self.style().standardIcon(QtGui.QStyle.SP_MediaStop), "Stop",
			self, shortcut="Ctrl+S", enabled=False,
			triggered = self.media_object.stop)

		self.computeAction = QtGui.QAction(
			self.style().standardIcon(44), "Stop",
			self.videoWidget, shortcut="Esc", enabled=False,
			triggered=self.compute)

		self.loopAction = QtGui.QAction("Loop",
			self,shortcut = "Ctrl+R",enabled = True,
			triggered = self.loop
			)


		self.bookmarkAction = QtGui.QAction("bookmark",
			self,shortcut="Ctrl+B", enabled=True,
			triggered=self.bookmark_function)

		self.downloadAction = QtGui.QAction("download",
			self,shortcut="Ctrl+D", enabled=True,
			triggered=self.download_function)

		self.downloadAction.setCheckable(True)
		self.downloadAction.setChecked(True)

		self.speedAction = QtGui.QAction(
			self.style().standardIcon(45),"Speed",
			self,shortcut='[',enabled = True,
			triggered = self.speed_fun)
		self.playlistAction = QtGui.QAction("Playlist",
			self,shortcut='Ctrl+P',enabled = True,
			triggered = self.playlist_fun)
		
		self.fullScrAction = QtGui.QAction("FullScreen",
			self,shortcut="F11", enabled=False,
			triggered=self.compute)

		self.seek_forward= QtGui.QAction(
			self.style().standardIcon(QtGui.QStyle.SP_ToolBarVerticalExtensionButton), "Forward",
			self, enabled=False,

			triggered=self.forward)
		self.seek_backward = QtGui.QAction(
			self.style().standardIcon(QtGui.QStyle.SP_ToolBarVerticalExtensionButton), "Backward",
			self, enabled=False,
			triggered=self.backward)

		self.seek_forward.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Right))
		self.seek_backward.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Left))
		
		self.addFilesAction = QtGui.QAction("Open", self,
			shortcut = "Ctrl+F", triggered = self.magic)

		self.exitAction = QtGui.QAction("Exit", self, shortcut="Ctrl+X", 
			triggered = self.close)

		self.aboutAction = QtGui.QAction("About", self, shortcut = "Ctrl+i",
			triggered = self.about)						
	
	
	
	def get_file_name(self, file_path):
		slash = file_path.rfind('/')
		file_name = file_path[slash +1 : ]
		return file_name
	def forward(self):
		self.current_time = self.current_time+10000
		self.media_object.seek(self.current_time)
	def backward(self):
		self.current_time = self.current_time-10000
		self.media_object.seek(self.current_time) 

	def download_function(self):
		if self.downloadAction.isChecked():
			self.download=1
			self.downloadAction.setChecked(True)
		else:
			self.download=0
			self.downloadAction.setChecked(False)


	def bookmark_function(self):
		self.bstart_time=self.current_time

		###print (self.videoTable.topLevelItem(self.sources.index(self.media_object)))
		###print ("bookmarked")
		self.cur_item = self.videoTable.currentItem()
		if self.cur_item.parent() !=None:
			self.cur_item = self.cur_item.parent()

		b = open(str(self.name_dict[self.cur_item.text(0)]+".txt"),"a+")
		#b.write(str(self.bstart_time)+"\n")
		
		if self.cur_item.parent() !=None:
			self.cur_item = self.cur_item.parent()
		text,ok =  QtGui.QInputDialog.getText(self, 'Bookmark Dialog', 
            'Enter name of bookmark:')
		if not ok:
			return
		##print ("bookmarked")
		self.cur_child = QtGui.QTreeWidgetItem()
		b.write(text+"("+str(self.bstart_time)+")"+"\n")
		self.cur_child.setText(0,text)
		self.cur_item.addChild(self.cur_child)
	
	'''	if self.bookmark_flag==True:	
			self.bookmark_flag=False
			bstart_time=self.current_time
		else:
			self.bookmark_flag=True
			self.media_object.seek(300000)'''#                                         $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


	def playlist_fun(self):
		w = self.gui.splitter.width()
		if self.visible:
			self.gui.splitter.setSizes([0,w])
			#self.videoWidget.resize(w,self.height())
			self.visible=False
		else:
			self.gui.splitter.setSizes([w/4,3*w/4])
			#self.videoWidget.resize(3*w/4,self.height())
			
			self.visible=True

	def speed_fun(self):
			list_of_backend_audio_effects = Phonon.BackendCapabilities.availableAudioEffects()
			list_of_effect_names = [str(elem.name()) for elem in list_of_backend_audio_effects]
			###print "Yes"
			
			        	
			speed_effect = Phonon.Effect(list_of_backend_audio_effects[5])
			speed_effect.setParameterValue(speed_effect.parameters()[0],QtCore.QVariant(str(2)))
			self.path.insertEffect(speed_effect)
	def play_and_pause(self):
 		if not self.playing:
 			self.media_object.play()
 			self.gui.btn.setIcon(QtGui.QIcon.fromTheme("media-playback-pause"))
 			self.playing = True
 		else:
 			self.media_object.pause()
 			self.gui.btn.setIcon(QtGui.QIcon.fromTheme("media-playback-start"))	
 			self.playing = False

	def loop(self):
		if self.loop_flag ==False:
			self.loop_flag=True
		else:
			self.loop_flag=False

		
	def convert_file_path(self, file_path):
		#convert back_slah to slash
		#self.media_object.currentSouce().fileName() using slash
		#make sure self.file_dict's file_name using the same
		return file_path.replace("\\", "/")




	def magic(self):#filter same path file
		self.files = QtGui.QFileDialog.getOpenFileNames(self,"open",
				QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.MoviesLocation))
		self.addFiles()
		return


	def addFiles(self):
		files=self.files
		index = len(self.sources)

		if(self.download):
			print("downloading")

			app = QtGui.QWidget()
			app.show()
			# self.progressBar = QtGui.QProgressBar(self)
			# self.progressBar.setRange(0,1)
			# self.progressBar.exec_()
			# self.progressBar.setValue(0)
			getSubtitle(files)
			app.hide()


			# self.progressBar.setValue(1)
		else:
			print("Not downloading")

		files_is_empty = True
		durationItem = None
		for string in files:
			####print("$$"+string)

			self.subtitle_string=string

			string = self.convert_file_path(string)


			files_is_empty = False
			self.sources.append(Phonon.MediaSource(string))
			currentRow = self.videoTable.topLevelItemCount()
			self.media_object.setCurrentSource(self.sources[currentRow])
			


			name = string
			title = self.get_file_name(name)
			self.name_dict[title]=string
			titleItem = QtGui.QTreeWidgetItem()
			titleItem.setText(0,title)
			if(os.path.isfile(name+".txt")):
				bmark_file = open(name+".txt","r")
				for line in bmark_file:
					child = QtGui.QTreeWidgetItem()
					idx = 0
					while(line[idx] != '('):
						idx = idx+1
					child.setText(0,line[:idx]) 
					titleItem.addChild(child)
			###print titleItem.text(0)
			self.videoTable.addTopLevelItem(titleItem)
		


		if files_is_empty:
			return

		if self.sources:
			print(index)
			self.media_object.setCurrentSource(self.sources[index])

			all_src = self.videoTable.findItems(self.get_file_name(self.sources[index].fileName()),QtCore.Qt.MatchExactly)
			#print(self.videoTable.itemAt(0,index).text(0))
			print (all_src[0].text(0))
			self.videoTable.setCurrentItem(all_src[0])
			self.timeLabel.setText("00:00:00")
			self.current_time = 0
			self.time=0
			#self.video_name = self.self.videoTable.itemAt(index,0).text(0)
			self.media_object.play()
			



	def about(self):
		QtGui.QMessageBox.information(self, "About",
			"Created By A^2 Team")
	

	def finished(self):
		###print "happy"
		if self.loop_flag == False:
			index = self.videoTable.indexOfTopLevelItem(self.videoTable.currentItem())+1
		else:
			index = self.videoTable.indexOfTopLevelItem(self.videoTable.currentItem())
		if index < len(self.sources):
			self.media_object.setCurrentSource(self.sources[index])
		else:
			self.media_object.setCurrentSource(self.sources[0])
		self.media_object.play()


	def setupMenus(self):
		fileMenu = self.menuBar().addMenu("Menu")
		fileMenu.addAction(self.addFilesAction)
		fileMenu.addSeparator()
		fileMenu.addAction(self.exitAction)
		optionMenu = self.menuBar().addMenu("Options")
		optionMenu.addAction(self.fullScrAction)
		optionMenu.addSeparator()
		optionMenu.addAction(self.loopAction)
		optionMenu.addSeparator()
		optionMenu.addAction(self.bookmarkAction)
		optionMenu.addSeparator()
		optionMenu.addAction(self.playlistAction)
		optionMenu.addSeparator()
		optionMenu.addAction(self.downloadAction)



		aboutMenu = self.menuBar().addMenu("Help")
		aboutMenu.addAction(self.aboutAction)



	def compute(self):

		if self.videoWidget.isFullScreen():
			self.videoWidget.setFullScreen(False)
			self.show()
			self.gui.btn_fscr.setIcon(QtGui.QIcon.fromTheme("view-fullscreen"))
			self.videoWidget.tempWidget.show()
			
		else:
			self.videoWidget.setFullScreen(True)
			self.hide()
			self.gui.btn_fscr.setIcon(QtGui.QIcon.fromTheme("view-restore"))
			self.videoWidget.tempWidget.hide()
	def resizing(self):
		self.gui.tempWidget.setGeometry(0,self.videoWidget.height,600,50)


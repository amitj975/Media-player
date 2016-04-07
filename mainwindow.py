from PyQt4 import QtCore, QtGui
from PyQt4.phonon import Phonon
from Gui import Gui
from subtitle import amit 
import os




class MainWindow(QtGui.QMainWindow):
	flag_b=False
	loop_flag =False
	bookmark_flag =True
	video_name = 'xyz'
	time =0
	current_time=0
	def __init__(self):
		super(MainWindow, self).__init__()

		self.media_object = None
		self.current_time = 0
		self.totalTime = "00:00:00"

		self.audioOutput = Phonon.AudioOutput(Phonon.VideoCategory, self)
		self.media_object = Phonon.MediaObject(self)

		
		self.videoUI = QtGui.QWidget()
		self.videoWidget = Phonon.VideoWidget(self.videoUI)
		Phonon.createPath(self.media_object, self.videoWidget)#link media source with video output


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
		
		gui=Gui(self);
		window=gui.setupUi()
		self.setCentralWidget(window)		

		self.sources = []



	def tick(self, time):
		displayTime = QtCore.QTime((time / 3600000) % 24, (time / 60000) % 60,
						(time / 1000) % 60)
		self.timeLabel.setText(displayTime.toString("HH:mm:ss")+"/"+self.totalTime)
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
			self.totalTime = str((self.media_object.totalTime()/60000)%60)+":"+str((self.media_object.totalTime()/1000)%60)
			print "playing"
			displayTime = QtCore.QTime((self.time / 3600000) % 24, (self.time / 60000) % 60,
						(self.time / 1000) % 60)
			self.timeLabel.setText(displayTime.toString("HH:mm:ss")+"/"+self.totalTime)
			print self.timeLabel.text()
			self.current_time = self.time
			self.media_object.seek(self.time)
		elif newState == Phonon.StoppedState:
			self.stopAction.setEnabled(False)
			self.playAction.setEnabled(True)
			self.pauseAction.setEnabled(False)
			self.timeLabel.setText("00:00:00")
			self.current_time = 0
			self.computeAction.setEnabled(False)
			self.fullScrAction.setEnabled(True)
			print "stopping"
			self.flag_b=False
		elif newState == Phonon.PausedState:
			self.pauseAction.setEnabled(False)
			self.stopAction.setEnabled(True)
			self.playAction.setEnabled(True)
			self.computeAction.setEnabled(True)
			self.fullScrAction.setEnabled(True)



	def sourceChanged(self, source):
		#self.videoTable.setCurrentItem(self.videoTable.topLevelItem(self.sources.index(source)))
		#self.timeLabel.setText("00:00:00")
		#self.current_time = 0
		print "yes"
		self.flag_b=False

	def tableClicked(self, item_x,col):	
		self.flag_b=False

		self.media_object.stop()
		self.media_object.clearQueue()
		#print self.videoTable.indexOfTopLevelItem(item_x)
		#print col

		self.video_name=item_x.text(col)
		#print(self.videoTable.indexOfTopLevelItem(item_x).text())
		self.media_object.setCurrentSource(self.sources[self.videoTable.indexOfTopLevelItem(item_x)])
		print "wohoo"
		self.media_object.play()
		self.videoTable.setCurrentItem(item_x)
		self.timeLabel.setText("00:00:00")
		self.current_time = 0
		self.time=0
		#if playing currently, continue playing the click one


		if item_x.parent() != None:
			name = str(item_x.text(0))
			print name 	
			#print long(name[7:-1])
			self.time = long(name[7:-1])
			print self.time
			
			
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

		self.loopAction = QtGui.QAction(
			self.style().standardIcon(42),"Loop",
			self,shortcut = "Ctrl+R",enabled = True,
			triggered = self.loop
			)


		self.bookmarkAction = QtGui.QAction(
			self.style().standardIcon(QtGui.QStyle.SP_ToolBarVerticalExtensionButton), "bookmark",
			self,shortcut="Ctrl+B", enabled=True,
			triggered=self.bookmark_function)

		
		self.fullScrAction = QtGui.QAction(
			self.style().standardIcon(QtGui.QStyle.SP_ToolBarVerticalExtensionButton), "FullScreen",
			self,shortcut="F11", enabled=False,
			triggered=self.compute)

		self.addFilesAction = QtGui.QAction("Open", self,
			shortcut = "Ctrl+F", triggered = self.addFiles)

		self.exitAction = QtGui.QAction("Exit", self, shortcut="Ctrl+X", 
			triggered = self.close)

		self.aboutAction = QtGui.QAction("About", self, shortcut = "Ctrl+i",
			triggered = self.about)						
	
	
	
	def get_file_name(self, file_path):
		slash = file_path.rfind('/')
		file_name = file_path[slash +1 : ]
		return file_name


	def bookmark_function(self):
		self.bstart_time=self.current_time

		#print (self.videoTable.topLevelItem(self.sources.index(self.media_object)))
		print ("bookmarked")
		b = open(str(self.videoTable.currentItem().text(0)+".txt"),"a+")
		b.write(str(self.bstart_time)+"\n")
		self.cur_item = self.videoTable.currentItem()
		if self.cur_item.parent() !=None:
			self.cur_item = self.cur_item.parent()
		self.cur_child = QtGui.QTreeWidgetItem()
		self.cur_child.setText(0,"b_mark("+str(self.bstart_time)+")")
		self.cur_item.addChild(self.cur_child)
	
	'''	if self.bookmark_flag==True:
			self.bookmark_flag=False
			bstart_time=self.current_time
		else:
			self.bookmark_flag=True
			self.media_object.seek(300000)'''#                                         $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$





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
	


	def addFiles(self):#filter same path file
		files = QtGui.QFileDialog.getOpenFileNames(self,"open",
				QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.MoviesLocation))

		index = len(self.sources)

		files_is_empty = True
		durationItem = None
		for string in files:
			##print("$$"+string)

			self.subtitle_string=string

			string = self.convert_file_path(string)


			files_is_empty = False
			self.sources.append(Phonon.MediaSource(string))
			currentRow = self.videoTable.topLevelItemCount()
			self.media_object.setCurrentSource(self.sources[currentRow])
			
			name = string
			title = self.get_file_name(name)
			titleItem = QtGui.QTreeWidgetItem()
			titleItem.setText(0,title)
			if(os.path.isfile(title+".txt")):
				bmark_file = open(title+".txt","r")
				for line in bmark_file:
					child = QtGui.QTreeWidgetItem()
					child.setText(0,"b_mark("+line[:-1]+")") 
					titleItem.addChild(child)
			#print titleItem.text(0)
			self.videoTable.addTopLevelItem(titleItem)


		if files_is_empty:
			return

		if self.sources:
			self.media_object.setCurrentSource(self.sources[index])
			self.videoTable.setCurrentItem(self.videoTable.itemAt(index,0))
			self.timeLabel.setText("00:00:00")
			self.current_time = 0
			self.time=0
			self.media_object.play()
			#amit(self.subtitle_string)                                              $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
			

	def about(self):
		QtGui.QMessageBox.information(self, "About",
			"Created for virtual team     --yhx")
	

	def finished(self):
		#print "happy"
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
		aboutMenu = self.menuBar().addMenu("Help")
		aboutMenu.addAction(self.aboutAction)


	def compute(self):

		if self.videoWidget.isFullScreen():
			self.videoWidget.setFullScreen(False)
			self.show()
		else:
			self.videoWidget.setFullScreen(True)
			self.hide()


import sys
from PySide.QtGui import QApplication, QMessageBox
# overlay
from PySide.QtGui import QGraphicsScene, QGraphicsView, QGraphicsProxyWidget, QPainter, QImage
from PySide.QtOpenGL import QGLWidget

from PySide.phonon import Phonon

try:
    from OpenGL import GL
except ImportError:
    app = QApplication(sys.argv)
    QMessageBox.critical(None, "OpenGL 2dpainting",
                            "PyOpenGL must be installed to run this example.",
                            QMessageBox.Ok | QMessageBox.Default,
                            QMessageBox.NoButton)
    sys.exit(1)


#class CustomProxy(QGraphicsProxyWidget):
#    def __init__(self, parent=None):
#        QGraphicsProxyWidget.__init__(self, parent)
#
#
#    def boundingRect(self):
#        return QGraphicsProxyWidget.boundingRect(self).adjusted(0, 0, 0, 0);


class CustomProxy(QGraphicsProxyWidget):
    def __init__(self, parent=None):
        QGraphicsProxyWidget.__init__(self, parent)


    def boundingRect(self):
        return QGraphicsProxyWidget.boundingRect(self).adjusted(0, 0, 0, 0);

# This is the magic:
    def paint(self, painter, option, widget=None):
        painter_inverted = QPainter()
        brect= QGraphicsProxyWidget.boundingRect(self)
        invertedColor = QImage(brect.width(),brect.height(),QImage.Format_RGB32)
        painter_inverted.begin(invertedColor)
        QGraphicsProxyWidget.paint(self,painter_inverted, option, widget)
        painter_inverted.end()
        painter.drawImage(0,0,invertedColor.rgbSwapped())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("tete")

    scene = QGraphicsScene()

    media = Phonon.MediaObject()
    video = Phonon.VideoWidget()
    Phonon.createPath(media, video)

    proxy = CustomProxy()
    proxy.setWidget(video)
    rect = proxy.boundingRect()
    #proxy.setPos(0, 0)
    #proxy.show()
    scene.addItem(proxy)

    media.setCurrentSource("/home/amit/Videos/Kung Fu Panda 3 (2015) 1080p R6 [DayT.se].mp4")
    media.play()

    titem = scene.addText("Bla-bla-bla")
    titem.setPos(130, 130)
    #titem.setPos(rect.width()/2, rect.height()/2)

    view = QGraphicsView(scene)
    vp = QGLWidget()
    view.setViewport(vp)

    #view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
    view.setViewportUpdateMode(QGraphicsView.BoundingRectViewportUpdate)
    view.setWindowTitle("Eternal fire")

    view.show()
    sys.exit(app.exec_())
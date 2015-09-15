
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

class InfoTool( QgsMapTool ):

    minSize = 5
    areaSelected = pyqtSignal( QgsRectangle, name="selected" )

    def __init__( self, iface ):
        QgsMapTool.__init__(self, iface.mapCanvas())
        self._iface = iface
        self._status = 0
        self._rb = None
        self._start = None

    def activate(self):
        QgsMapTool.activate(self)
        sb = self._iface.mainWindow().statusBar()
        sb.showMessage("Click point or rectangle for address info")
 
    def canvasPressEvent(self,e):
        if not e.button() == Qt.LeftButton:
            return
        self._status = 1
        self._start=e.pos()
        self._rb=QgsRubberBand(self._iface.mapCanvas(),True)
        self._rb.setToCanvasRectangle(QRect(e.pos(),e.pos()))
        return
    
    def canvasMoveEvent(self,e):
        if not self._status == 1:
            return
        self._rb.setToCanvasRectangle(QRect(self._start,e.pos()))

    def canvasReleaseEvent(self,e):
        if not e.button() == Qt.LeftButton or not self._status == 1:
            return
        self._rb.reset()
        self._status = 0

        self._end = e.pos()
        p1 = self._start
        p2 = self._end
        r = QRect( QPoint(min(p1.x(),p2.x()),min(p1.y(),p2.y())),
                   QPoint(max(p1.x(),p2.x()),max(p1.y(),p2.y())))
        mins = self.minSize
        if r.width() < mins or r.height() < mins:
            r.adjust(-mins,-mins,mins,mins)
        mapbl = self.toMapCoordinates( QPoint(r.x(),r.y()+r.height()))
        maptr = self.toMapCoordinates( QPoint(r.x()+r.width(),r.y()))
        maprect = QgsRectangle(mapbl,maptr)
        self.areaSelected.emit( maprect )

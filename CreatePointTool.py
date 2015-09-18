import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from ElectoralAddress.Gui import Controller
from ElectoralAddress import Database
from ElectoralAddress.Gui.AddressList import AddressListModel


class CreatePointTool( QgsMapTool ):

    def __init__( self, iface, controller=None ):
        QgsMapTool.__init__(self, iface.mapCanvas())
        self._address = None
        self._iface = iface
        self._controller = controller
        self.activate()

    def activate( self ):
        QgsMapTool.activate(self)
        sb = self._iface.mainWindow().statusBar()
        sb.showMessage("Click map to create point")

    def deactivate( self ):
        sb = self._iface.mainWindow().statusBar()
        sb.clearMessage()

    def setEnabled( self, enabled ):
        self._enabled = enabled
        if enabled:
            self.activate()
        else:
            self.deactivate()

    def canvasReleaseEvent(self,e):
        if not e.button() == Qt.LeftButton:
            return
        if not self._address:
            QMessageBox.warning(self._iface.mainWindow(),"Create Address Point", "No address selected")
            return

        if not self._enabled:
            QMessageBox.warning(self._iface.mainWindow(),"Create Address Point", "Not enabled")
            return

        pt = e.pos()
        coords = self.toMapCoordinates(QPoint(pt.x(), pt.y()))

        # Do something to create the point!
        try:
            self.setPoint( coords )
        except:
            msg = str(sys.exc_info()[1])
            QMessageBox.warning(self._iface.mainWindow(),"Error creating point",msg)

    def setAddress( self, address ):
        self._address = address
        self.deactivate()

    def setPoint( self, coords ):
        src_crs = self._iface.mapCanvas().mapRenderer().destinationCrs()
        tgt_crs = QgsCoordinateReferenceSystem()
        tgt_crs.createFromOgcWmsCrs('EPSG:4167')
        transform = QgsCoordinateTransform( src_crs, tgt_crs )
        wkt = transform.transform( coords.x(), coords.y() ).wellKnownText()

        # Add the point to the database
        success = Database.execute('elc_CreateAddressPoint', self._address.id(), str(wkt))

        if success:
        # Refresh GUI
            self._iface.mapCanvas().refresh()
            self._controller.updateAddress( self._address.id() )

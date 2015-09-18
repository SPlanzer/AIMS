
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from ElectoralAddress import Database


class AddressHighlighter( QObject ):

    _adrMarkerColor = QColor(255,0,0)
    _sadMarkerColor = QColor(255,0,0)
    _rclMarkerColor = QColor(76,255,0)

    def __init__( self, iface, layerManager, controller=None ):
        QObject.__init__(self)
        self._iface = iface
        self._canvas = iface.mapCanvas()
        self._layers = layerManager
        self._enabled = False
        self._address = None

        self._adrMarker = QgsVertexMarker(self._canvas)
        self._adrMarker.hide()
        self._adrMarker.setColor(self._adrMarkerColor)
        self._adrMarker.setIconSize(15)
        self._adrMarker.setPenWidth(2)
        self._adrMarker.setIconType(QgsVertexMarker.ICON_BOX)

        self._sadMarker = QgsVertexMarker(self._canvas)
        self._sadMarker.hide()
        self._sadMarker.setColor(self._sadMarkerColor)
        self._sadMarker.setIconSize(15)
        self._sadMarker.setPenWidth(2)
        self._sadMarker.setIconType(QgsVertexMarker.ICON_CROSS)

        self._rclMarker = QgsRubberBand(self._canvas,False)
        self._rclMarker.hide()
        self._rclMarker.setWidth(3)
        self._rclMarker.setColor(self._rclMarkerColor)

        self._crs = QgsCoordinateReferenceSystem()
        self._crs.createFromOgcWmsCrs('EPSG:4167')
        self._controller = controller
        if self._controller:
            self._controller.addressUpdated.connect( self.resetAddress )

    def setEnabled( self, enabled ):
        self._enabled = enabled
        self.displayMarkers()

    def setAddress( self, address ):
        self._address = address
        self.displayMarkers()

    def resetAddress( self, address ):
        if address == self._address:
            self.displayMarkers()

    def displayMarkers( self ):
        address = self._address
        enabled = self._enabled
        visible = self._layers.isVisible( self._layers.addressLayer())
        if not enabled or not address or not visible or not address.location():
            self._adrMarker.hide()
            self._sadMarker.hide()
            self._rclMarker.hide()
            return

        transform = QgsCoordinateTransform(self._crs,self._canvas.mapRenderer().destinationCrs())
        point = transform.transform( address.location()[0], address.location()[1])
        self._adrMarker.setCenter( point )
        self._adrMarker.show()

        sadLayer = self._layers.landonlineAddressLayer()
        id = address.sad_id()
        if id and self._layers.isVisible( sadLayer ):
            wkt = Database.executeScalar('elc_GetLandonlineAddressGeometry',id)
            centre = QgsGeometry.fromWkt(wkt)
            centre.transform(transform)
            self._sadMarker.setCenter(centre.asPoint())
            self._sadMarker.show()

        rclLayer = self._layers.landonlineRoadLayer()
        id = address.rcl_id()
        if id and self._layers.isVisible( rclLayer ):
            wkt = Database.executeScalar('elc_GetLandonlineRoadGeometry',id)
            geom = QgsGeometry.fromWkt(wkt)
            self._rclMarker.setToGeometry(geom,rclLayer)
            self._rclMarker.show()


import re
from os.path import dirname, abspath, join

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from ElectoralAddress import Database
from ElectoralAddress.Gui import Config

class LayerManager( QObject ):

    _lolSchema='bde'
    _propBaseName='ElectoralAddressLoader.'
    _styledir = join(dirname(abspath(__file__)),'styles')
    _invalidJobId=-1
    _addressLayerId='adr'

    addressLayerAdded = pyqtSignal( QgsMapLayer, name="addressLayerAdded")
    addressLayerRemoved = pyqtSignal( name="addressLayerRemoved")

    def __init__( self, iface ):
        QObject.__init__(self)
        Config.configureDatabase(Database)
        self._iface = iface
        self._statusBar = iface.mainWindow().statusBar()
        self._adrLayer = None
        self._sadLayer = None
        self._rclLayer = None
        self._parLayer = None

        QgsMapLayerRegistry.instance().layerWasAdded.connect( self.checkNewLayer )
        QgsMapLayerRegistry.instance().layerWillBeRemoved.connect( self.checkRemovedLayer )
        QgsMapLayerRegistry.instance().removeAll.connect( self.removeAllLayers )

    def removeAllLayers( self ):
        if self._adrLayer:
            self.addressLayerRemoved.emit()
        self._adrLayer = None
        self._sadLayer = None
        self._rclLayer = None
        self._parLayer = None

    def checkRemovedLayer( self, id ):
        if self._adrLayer and self._adrLayer.id() == id:
            self._adrLayer = None
            self.addressLayerRemoved.emit()
        if self._sadLayer and self._sadLayer.id() == id:
            self._sadLayer = None
        if self._rclLayer and self._rclLayer.id() == id:
            self._rclLayer = None
        if self._parLayer and self._parLayer.id() == id:
            self._parLayer = None

    def checkNewLayer( self, layer ):
        layerId = self.layerId(layer)
        if not layerId:
            return
        if layerId == self._addressLayerId:
            newlayer = self._adrLayer == None
            self._adrLayer = layer
            if newlayer:
                self.addressLayerAdded.emit(layer)
        elif layerId == 'sad':
            self._sadLayer = layer
        elif layerId == 'rcl':
            self._rclLayer = layer
        elif layerId == 'par':
            self._parLayer = layer

    def landonlineRoadLayer( self ):
        return self._rclLayer

    def landonlineAddressLayer( self ):
        return self._sadLayer

    def landonlineParcelLayer( self ):
        return self._parLayer

    def addressLayer( self ):
        return self._adrLayer

    def layerId( self, layer ):
        idprop = self._propBaseName + 'Id'
        return str(layer.customProperty(idprop))

    def setLayerId( self, layer, id ):
        idprop = self._propBaseName + 'Id'
        layer.setCustomProperty(idprop,id)

    def layers( self):
        for layer in QgsMapLayerRegistry.instance().mapLayers().values():
            if layer.type() == layer.VectorLayer and self.layerId(layer):
                yield layer

    def findLayer( self, name ): 
        for layer in self.layers():
            if self.layerId(layer) == name:
                return layer
        return None

    def installLayer( self, id, schema, table, key, estimated, where, displayname ):
        layer = self.findLayer(id)
        if layer:
            legend = self._iface.legendInterface()
            if not legend.isLayerVisible(layer):
                legend.setLayerVisible(layer, True)
            return layer
        self._statusBar.showMessage("Loading layer " + displayname )
        layer = None
        try:
            uri = QgsDataSourceURI()
            uri.setConnection(Database.host(),Database.port(),Database.database(),Database.user(),Database.password())
            uri.setDataSource(schema,table,'shape',where)
            uri.setKeyColumn( key )
            uri.setUseEstimatedMetadata( estimated )
            layer = QgsVectorLayer(uri.uri(),displayname,"postgres")
            self.setLayerId( layer, id )
            try:
                layer.loadNamedStyle(join(self._styledir,id+'_style.qml'))
            except:
                pass
            QgsMapLayerRegistry.instance().addMapLayer(layer)
        finally:
            self._statusBar.showMessage("")
        return layer

    def installLandonlineLayers( self ):
        schema = Database.bdeSchema()
        self.installLayer( 'rcl', schema, 'crs_road_ctr_line', 'id', True, "status='CURR'",'Roads' )
        self.installLayer( 'par', schema, 'crs_parcel', 'id', True, 
                                    "status in ('CURR','PEND','APPR') and toc_code='PRIM' and parcel_intent not in ('ROAD','RLWY')",'Parcels' )
        self.installLayer( 'sad', schema, 'crs_street_address', 'id', True, "status='CURR'",'Landonline addresses' )

    def getLoadedJobId( self ):
        jobid = self._invalidJobId 
        layer = self.addressLayer()
        if layer:
            where = layer.subsetString()
            match = re.match(r"job_id\=(\d+)",where)
            if match:
                jobid = int(match.group(1))
        return jobid


    def installAddressLayer( self, job, where='' ):
        if not job and not self._adrLayer:
            return

        layerid = self._addressLayerId
        jobwhere = "job_id="+str(self._invalidJobId)
        layername = "Addresses (no job loaded)"
        if( job ):
            jobwhere = "job_id="+str(job.id())+" AND status <> 'MERG'"
            if where:
                jobwhere = jobwhere + ' AND '+where
            layername = 'Addresses (job '+str(job.id())+')'

        layer = self.installLayer( layerid, Database.addressSchema(), 'address', 'adr_id', False, jobwhere, layername )

        if layer.subsetString() != jobwhere:
            layer.setLayerName(layername)
            layer.setSubsetString(jobwhere)
        return layer

    def refreshAddressLayer( self ):
        layer = self.addressLayer()
        if layer and hasattr(layer, "setCacheImage"): 
            layer.setCacheImage(None)
        layer.triggerRepaint()

    def isVisible( self, layer ):
        if not layer:
            return False
        legend = self._iface.legendInterface()
        if not legend.isLayerVisible(layer):
            return False
        if not layer.hasScaleBasedVisibility():
            return True
        scale = self._iface.mapCanvas().mapRenderer().scale()
        return scale <= layer.maximumScale() and scale >= layer.minimumScale()


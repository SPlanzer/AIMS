()
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

from ElectoralAddress.Gui import Controller
from ElectoralAddress.Gui.AddressList import AddressListModel
from ElectoralAddress import Database
from Ui_InfoWidget import Ui_InfoWidget

class InfoWidget( Ui_InfoWidget, QWidget ):

    def __init__( self, parent, iface, layerManager, controller=None ):
        QWidget.__init__(self,parent)
        self.setupUi(self)
        self._iface = iface
        self._layers = layerManager
        self._foundIds = []
        self._foundSad = []
        self._foundRna = []
        self._addresses = AddressListModel()
        self._addresses.setColumns(
            ['id','display','status','sad_id'], 
            ['id','address','status','sad_id'])
        self._addresses.setFilter( lambda x: x['address'].id() in self._foundIds )
        self.uAddressListView.setModel( self._addresses )
        self.uSadListView.setList(self._foundSad,
                                 ['address','sad_id','rna_id','offset'])
        self.uRnaListView.setList(self._foundRna,
                                 ['roadname','rna_id','rcl_id','offset'])
        self.setController(controller)

    def setController( self, controller ):
        if not controller:
            controller = Controller.instance()
        self._controller = controller
        self._addresses.setAddressList(controller.addressList())
        self.uAddressListView.addressSelected.connect( controller.selectAddress )
        controller.addressSelected.connect( self.uAddressListView.selectAddress )

    def selectAddress( self, address ):
        self.uAddressListView.selectAddress( address )

    def setSelectRectangle( self, rectangle ):
        src_crs = self._iface.mapCanvas().mapRenderer().destinationCrs()
        tgt_crs = QgsCoordinateReferenceSystem()
        tgt_crs.createFromOgcWmsCrs('EPSG:4167')
        transform = QgsCoordinateTransform( src_crs, tgt_crs )
        searchrect = transform.transformBoundingBox( rectangle )
        wkt = str(QgsGeometry.fromRect(searchrect).exportToWkt())
        jobid = self._controller.job().id()

        self._foundIds[:] = []
        if self._layers.isVisible( self._layers.addressLayer()): 
            for r in Database.execute('select adr_id from elc_findAddressIds(%s,%s) order by poffset',jobid,wkt):
                self._foundIds.append(r[0])
        self._addresses.resetFilter()

        self._foundSad[:] = []
        if self._layers.isVisible( self._layers.landonlineAddressLayer() ):
            for r in Database.execute('select sad_id, rna_id, roadname, housenumber, poffset from elc_findLandonlineAddresses(%s) order by poffset',wkt):
                self._foundSad.append(dict(
                    address=str(r[3])+' '+str(r[2]),
                    sad_id=r[0],
                    rna_id=r[1],
                    offset=round(float(r[4]),1)
                    ))
        self.uSadListView.setList(self._foundSad)

        self._foundRna[:] = []
        if self._layers.isVisible( self._layers.landonlineRoadLayer() ):
            for r in Database.execute('select rna_id, rcl_id, roadname, poffset from elc_findLandonlineRoads(%s) order by poffset',wkt):
                self._foundRna.append(dict(
                    roadname=r[2],
                    rna_id=r[0],
                    rcl_id=r[1],
                    offset=round(float(r[3]),1)
                    ))
        self.uRnaListView.setList(self._foundRna )

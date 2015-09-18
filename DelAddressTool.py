import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from ElectoralAddress import Database
from ElectoralAddress.Address import AddressStatus
from Ui_DelAddressDialog import Ui_DelAddressDialog

class DelAddressTool( QgsMapTool ):

    tolerance=5

    def __init__( self, iface, layerManager, controller ):
        QgsMapTool.__init__(self, iface.mapCanvas())
        self._iface = iface
        self._layers = layerManager
        self._controller = controller

    def activate(self):
        QgsMapTool.activate(self)
        sb = self._iface.mainWindow().statusBar()
        sb.showMessage("Click point address to delete")
 
    def canvasReleaseEvent(self,e):
        if not e.button() == Qt.LeftButton:
            return
        if not self._layers.isVisible( self._layers.landonlineAddressLayer() ):
            return
        pt = e.pos()
        r = QRect( QPoint(pt.x()-self.tolerance,pt.y()-self.tolerance),
                   QPoint(pt.x()+self.tolerance,pt.y()+self.tolerance))
        mapbl = self.toMapCoordinates( QPoint(r.x(),r.y()+r.height()))
        maptr = self.toMapCoordinates( QPoint(r.x()+r.width(),r.y()))
        maprect = QgsRectangle(mapbl,maptr)
        addresses = self.findAddresses( maprect )
        if not addresses:
            return
        sad_id = None
        if len(addresses) == 1:
            addr = addresses[0]
            if QMessageBox.question(self._iface.mainWindow(), 
                 "Mark landonline address for deletion",
                 "Address "+addr['address']+" will be marked for deletion?",
                QMessageBox.Ok | QMessageBox.Cancel,
                QMessageBox.Ok ) == QMessageBox.Ok:
                sad_id = int(addr['sad_id'])
        else:
            dlg = DelAddressDialog( self._iface.mainWindow() )
            addr = dlg.selectAddress( addresses )
            if addr:
                sad_id= int(addr['sad_id'])
        if sad_id:
            # Do something to delete the address!
            try:
                job = self._controller.job()
                address = job.createAddressFromLandonlineAddress( sad_id, AddressStatus.Delete )
                self._controller.updateAddress( address )
            except:

                msg = str(sys.exc_info()[1])
                QMessageBox.warning(self._iface.mainWindow(),"Error creating delete record",msg)

    def findAddresses( self, rectangle ):
        src_crs = self._iface.mapCanvas().mapRenderer().destinationCrs()
        tgt_crs = QgsCoordinateReferenceSystem()
        tgt_crs.createFromOgcWmsCrs('EPSG:4167')
        transform = QgsCoordinateTransform( src_crs, tgt_crs )
        searchrect = transform.transformBoundingBox( rectangle )
        wkt = str(QgsGeometry.fromRect(searchrect).exportToWkt())

        addresses = []
        for r in Database.execute('select sad_id, rna_id, roadname, housenumber, poffset from elc_findLandonlineAddresses(%s) order by poffset',wkt):
            addresses.append(dict(
                address=str(r[3])+' '+str(r[2]),
                sad_id=r[0],
                rna_id=r[1],
                offset=round(float(r[4]),1)
                ))
        return addresses


class DelAddressDialog( Ui_DelAddressDialog, QDialog ):

    def __init__( self, parent ):
        QDialog.__init__(self,parent)
        self.setupUi(self)

    def selectAddress( self, addresses ):
        self.uSadListView.setList(addresses,
                                 ['address','sad_id','rna_id','offset'])
        if self.exec_() == QDialog.Accepted:
            return self.uSadListView.selectedItem()
        return None

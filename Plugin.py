from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from qgis.utils import *

import Resources

from LayerManager import LayerManager
from DockWindow import DockWindow
from InfoWidget import InfoWidget
from InfoTool import InfoTool
from DelAddressTool import DelAddressTool
from CreatePointTool import CreatePointTool
from CreateNewTool import CreateNewTool
from AddressHighlighter import AddressHighlighter
from ElectoralAddress.Gui.JobManagerWidget import JobManagerWidget
from ElectoralAddress.Gui.Controller import Controller


class Plugin:

    Name = "ElectoralAddressLoader"
    LongName="Electoral address loader"
    Version="2.0"
    QgisMinimumVersion="2.0"
    Author="ccrook@linz.govt.nz <Chris Crook>; bmnelson@linz.govt.nz <Bill M. Nelson>"
    PluginUrl="http://inlinz2/CustomerServices/QgisPluginRepository/ElectoralAddressLoader.zip"
    Description="Prepare address information supplied by regional authorities for loading into Landonline"

    SettingsBase="ElectoralAddressLoader/"

    def __init__( self, iface ):

        self._iface = iface
        self._statusbar = iface.mainWindow().statusBar()
        self._layers = None
        self._highlighter = None
        self._editor = None
        self._infowin = None
        self._infotool = None
        self._deladdtool = None
        self._createpnttool = None
        self._controller = Controller()
        # Setup address coord ref system (NZGD2000 = epsg 4167)
        self._addressCrs = QgsCoordinateReferenceSystem()
        self._addressCrs.createFromOgcWmsCrs('EPSG:4167')  
        self._displayCrs = QgsCoordinateReferenceSystem()
        self._displayCrs.createFromOgcWmsCrs('EPSG:2193')  
        self._addressZoomRadius=150.0

    def initGui(self):
        self._layers = LayerManager(self._iface)
        self._highlighter = AddressHighlighter( self._iface, self._layers, self._controller )
        self._highlighter.setEnabled( False )

        # Main address editing window
        self._loadaction = QAction(QIcon(":/plugins/ElectoralAddressLoader/loadaddress.png"), 
            "Electoral address manager", self._iface.mainWindow())
        self._loadaction.setWhatsThis("Open the electoral address upload management window")
        self._loadaction.setStatusTip("Open the electoral address upload management window")
        self._loadaction.triggered.connect( self.loadEditor )

        self._infoaction = QAction(QIcon(":/plugins/ElectoralAddressLoader/addressinfo.png"), 
            "Electoral address info tool", self._iface.mainWindow())
        self._infoaction.setWhatsThis("Start the electoral address loader info tool")
        self._infoaction.setStatusTip("Start the electoral address loader info tool")
        # Info window and info tool
        self._infoaction.setEnabled(False)
        self._infoaction.triggered.connect( self.startInfoTool )
        self._infotool = InfoTool( self._iface )
        self._infotool.setAction(self._infoaction)

        # Address highlighter
        self._highlightaction = QAction(QIcon(":/plugins/ElectoralAddressLoader/addresshighlight.png"), 
            "Electoral address highlighter", self._iface.mainWindow())
        self._highlightaction.setWhatsThis("Turn the electoral address highlighter on or off")
        self._highlightaction.setStatusTip("Turn the electoral address highlighter on or off")
        self._highlightaction.setEnabled(False)
        self._highlightaction.setCheckable(True)
        self._highlightaction.toggled.connect( self._highlighter.setEnabled )

        # Delete address point
        self._deladdressaction = QAction(QIcon(":/plugins/ElectoralAddressLoader/deleteaddress.png"), 
            "Delete landonline address point", self._iface.mainWindow())
        self._deladdressaction.setWhatsThis("Mark a landonline address point for deletion")
        self._deladdressaction.setStatusTip("Mark a landonline address point for deletion")
        self._deladdressaction.setEnabled(False)
        self._deladdressaction.triggered.connect( self.startDelAddressTool )
        self._deladdtool = DelAddressTool( self._iface, self._layers, self._controller )
        self._deladdtool.setAction( self._deladdressaction )

        # Create address geometry
        self._createpointaction = QAction(QIcon(":/plugins/ElectoralAddressLoader/createpoint.png"), 
            "Create address geometry", self._iface.mainWindow())
        self._createpointaction.setWhatsThis("Mark a point to use as the geometry for the selected address")
        self._createpointaction.setStatusTip("Mark a point to use as the geometry for the selected address")
        self._createpointaction.setEnabled(False)
        self._createpointaction.triggered.connect( self.startCreatePointTool )
        self._createpnttool = CreatePointTool( self._iface, self._controller )
        self._createpnttool.setAction( self._createpointaction )

        # Create new address
        self._createnewaddressaction = QAction(QIcon(":/plugins/ElectoralAddressLoader/newaddresspoint.png"), 
            "Create new address", self._iface.mainWindow())
        self._createnewaddressaction.setWhatsThis("place point for new address")
        self._createnewaddressaction.setStatusTip("place point for new address")
        self._createnewaddressaction.setEnabled(False)
        self._createnewaddressaction.triggered.connect( self.startNewAddressTool )
        self._createnewtool = CreateNewTool( self._iface, self._controller )
        self._createnewtool.setAction( self._createnewaddressaction )
        
        # Help button
        self._helpaction = QAction(QIcon(":/plugins/ElectoralAddressLoader/addresshelp.png"), 
            "Electoral address help", self._iface.mainWindow())
        self._helpaction.setWhatsThis("Display help for the electoral address plugin")
        self._helpaction.setStatusTip("Display help for the electoral address plugin")
        self._helpaction.triggered.connect( self.showHelp )
        
        # Add to own toolbar
        self._toolbar = self._iface.addToolBar("Electoral address")
        self._toolbar.addAction(self._loadaction)
        self._toolbar.addAction(self._infoaction)
        self._toolbar.addAction(self._highlightaction)
        self._toolbar.addAction(self._deladdressaction)
        self._toolbar.addAction(self._createpointaction)
        self._toolbar.addAction(self._createnewaddressaction)
        self._toolbar.addAction(self._helpaction)

        # Add infowidget to attributes tool bar
        tb = self._iface.attributesToolBar()
        tb.insertAction(tb.actions()[0],self._infoaction)
        self._infowidget = tb.widgetForAction( self._infoaction )
        self._infowidget.hide()

        # Add actions to menu and toolbar icon
        self._iface.addToolBarIcon(self._loadaction)
        self._iface.addPluginToMenu("&Electoral address", self._loadaction)
        self._iface.addPluginToMenu("&Electoral address", self._infoaction)
        self._iface.addPluginToMenu("&Electoral address", self._highlightaction)
        self._iface.addPluginToMenu("&Electoral address", self._deladdressaction)
        self._iface.addPluginToMenu("&Electoral address", self._createpointaction)
        self._iface.addPluginToMenu("&Electoral address", self._createnewaddressaction)
        self._iface.addPluginToMenu("&Electoral address", self._helpaction)

        # Make useful connections!
        QgsProject.instance().readProject.connect( self.loadProject )
        self._layers.addressLayerAdded.connect( self.enableAddressLayer )
        self._layers.addressLayerRemoved.connect( self.disableAddressLayer )
        self._controller.jobLoading.connect( self.showMessage )
        self._controller.jobLoaded.connect( self.displayJob )
        self._controller.addressUpdated.connect( self.updateAddress )
        self._controller.addressSelected.connect( self._highlighter.setAddress )
        self._controller.addressSelected.connect( self._createpnttool.setAddress )

    def unload(self):      
        if self._editor:
            self._editor.close()
            self._editor = None
        if self._infowin:
            self._infowin.close()
            self._infowin = None
        self._iface.mainWindow().removeToolBar(self._toolbar)
        self._iface.attributesToolBar().removeAction(self._infoaction)
        self._iface.removeToolBarIcon(self._loadaction)
        self._iface.removePluginMenu("&Electoral address",self._loadaction)
        self._iface.removePluginMenu("&Electoral address", self._infoaction)
        self._iface.removePluginMenu("&Electoral address", self._highlightaction)
        self._iface.removePluginMenu("&Electoral address", self._deladdressaction)
        self._iface.removePluginMenu("&Electoral address", self._createpointaction)
        self._iface.removePluginMenu("&Electoral address", self._createnewaddressaction)
        self._iface.removePluginMenu("&Electoral address", self._helpaction)

    def defaultHelpFile( self ):
        from os.path import dirname, join, abspath, exists
        helpfile = join(dirname(abspath(__file__)),'help','index.html')
        return helpfile if exists(helpfile) else None

    def showHelp( self ):
        helpfile = self.defaultHelpFile()
        if helpfile:
            url = QUrl.fromLocalFile( helpfile )
            QDesktopServices.openUrl( url )

    def loadProject( self, dom ):
        jobid = self._layers.getLoadedJobId()
        if jobid < 0:
            editor = self.jobEditor( False )
            if editor:
                editor.hide()
        else:
            editor = self.jobEditor()
            editor.loadJob(jobid)

    def enableAddressLayer( self, layer ):
        self._infowidget.setVisible(True)
        self._infoaction.setEnabled(True)
        self._deladdressaction.setEnabled(True)
        self._createpointaction.setEnabled(True)
        self._createnewaddressaction.setEnabled(True)
        self._highlightaction.setEnabled(True)
        if layer:
            layer.selectionChanged.connect(self.setSelectedAddressId)
            layer.committedFeaturesAdded.connect(self.updateAddedAddresses)
            layer.committedFeaturesRemoved.connect(self.updateRemovedAddresses)
            layer.committedAttributeValuesChanges.connect(self.updateEditedAddresses)
            layer.committedGeometriesChanges.connect(self.updateEditedGeometries)

    def disableAddressLayer( self ):
        self._infoaction.setEnabled(False)
        self._infowidget.setVisible(False)
        self._highlightaction.setEnabled(False)
    
    def setSelectedAddressId( self ):
        layer = self._layers.addressLayer()
        editor = self.jobEditor(False)
        if layer and layer.selectedFeatureCount()==1:
            for id in layer.selectedFeaturesIds():
                self._controller.selectAddress(id)

    def updateAddedAddresses( self, id, featlist ):
        for id in featlist.keys():
            self._controller.updateAddress( int(id) )

    def updateRemovedAddresses( self, id, featlist ):
        for id in featlist:
            self._controller.updateAddress( int(id) )

    def updateEditedAddresses( self, id, changelist ):
        for id in changelist.keys():
            self._controller.updateAddress( int(id) )

    def updateEditedGeometries( self, id, geomap ):
        # Refresh job links - when address geometries are changed the 
        # update trigger on the address table sets the linked status to
        # false, so that relinking the job will fix up changed geometries
        # This also returns a list of parcel ids...
        ids = self._controller.job().refreshLandonlineLinks()
        for id in ids:
            self._controller.updateAddress( id )

    def loadEditor( self ):
        editor = self.jobEditor()
        if not editor.isVisible():
            editor.parent().show()

    def jobEditor( self, create=True ):
        if not self._editor and create:
            editor = JobManagerWidget( self._iface.mainWindow(), self._controller )
            helpfile = self.defaultHelpFile()
            if helpfile:
                editor.setHelpFile( helpfile )
            editor.addAddressAction("Display",self.zoomToAddress)
            DockWindow(self._iface.mainWindow(),editor,"JobManager","Address manager")
            self._editor = editor
        return self._editor

    def updateAddress( self, address ):
        self._layers.refreshAddressLayer()

    def startInfoTool( self ):
        infowin = self.infoWindow()
        if not infowin.isVisible():
            infowin.parent().show()
        self._iface.mapCanvas().setMapTool( self._infotool )

    def startDelAddressTool( self ):
        self._iface.mapCanvas().setMapTool( self._deladdtool )
    
    def startCreatePointTool( self ):
        self._iface.mapCanvas().setMapTool( self._createpnttool )
        self._createpnttool.setEnabled( True )

    def startNewAddressTool( self ):
        self._iface.mapCanvas().setMapTool( self._createnewtool )
        self._createnewtool.setEnabled( True )

    def infoWindow( self, create=True ):
        if not self._infowin and create:
            infowin = InfoWidget( self._iface.mainWindow(), self._iface, self._layers, self._controller )
            DockWindow(self._iface.mainWindow(),infowin,"InfoWindow","Address information")
            self._infowin = infowin
            self._infotool.areaSelected.connect( infowin.setSelectRectangle )
        return self._infowin

    def displayJob( self, job ):
        canvas = self._iface.mapCanvas()
        renderer = canvas.mapRenderer()
        if renderer.destinationCrs() != self._displayCrs:
            setCrs = True
            if QgsMapLayerRegistry.instance().count() > 0:
                answer = QMessageBox.question(self._iface.mainWindow(),
                             "Set coordinate system",
                             "The electoral address plugin prefers to use the NZTM projection\n"+
                             "Do you want to change the project to use this?",
                             QMessageBox.Yes | QMessageBox.No)
                setCrs = answer == QMessageBox.Yes
            if setCrs:
                renderer.setDestinationCrs( self._displayCrs )
                renderer.setMapUnits( QGis.Meters )
        if renderer.destinationCrs() == self._displayCrs:
            renderer.setProjectionsEnabled(True)

        self._iface.mapCanvas().setRenderFlag( False )
        try:
            if job:
                self._layers.installLandonlineLayers()
            layer = self._layers.installAddressLayer(job)
            extents = layer.extent()
            if extents.isEmpty():
                self._iface.mapCanvas().zoomToFullExtent()
            else:
                transform = QgsCoordinateTransform( 
                    self._addressCrs, 
                    self._iface.mapCanvas().mapRenderer().destinationCrs()
                    )
                extents = transform.transformBoundingBox( extents )
                self._iface.mapCanvas().setExtent( extents )
        finally:
            self._iface.mapCanvas().setRenderFlag( True )

    def zoomToAddress( self, address ):
        if not address or not address.location():
            return
        layer = self._layers.installAddressLayer( self._controller.job() )
        self._iface.mapCanvas().setCurrentLayer( layer )
        transform = QgsCoordinateTransform( 
            self._addressCrs, 
            self._iface.mapCanvas().mapRenderer().destinationCrs()
            )
        midpoint = transform.transform( address.location()[0], address.location()[1] )
        buffer = self._addressZoomRadius
        extents = QgsRectangle( midpoint.x()-buffer,midpoint.y()-buffer,
                              midpoint.x()+buffer,midpoint.y()+buffer)
        self._iface.mapCanvas().setExtent( extents )
        layer.removeSelection()
        self._iface.mapCanvas().refresh()

    def showMessage( self, string ):
        self._statusbar.showMessage( string )

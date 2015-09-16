from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_AddressLinkingWidget import Ui_AddressLinkingWidget

import Controller

from AddressList import AddressListModel

class AddressLinkingWidget( Ui_AddressLinkingWidget, QWidget ):

    def __init__( self, parent=None, controller=None ):
        QWidget.__init__( self, parent )
        self.setupUi(self)
        self._addressListModel = AddressListModel()
        self._addressListModel.setColumns(
            ['id','display','status','warnings','shortnotes','par_id','cluster_id','src_id'],
            ['Id','Address','Status','Warnings','Notes','Parcel id','Cluster','Supplier ref']
            )
        self.uAddressListView.setModel( self._addressListModel )

        self.uAddressListView.rowSelectionChanged.connect( self.selectAddress )
        self.uShowAll.toggled.connect( self.setShowAll )
        self.uShowWarnings.toggled.connect( self.setShowWarnings )
        self.uShowNotes.toggled.connect( self.setShowNotes )
        self.uShowUndefined.toggled.connect( self.setShowUndefined )
        self.uSaveAddressButton.clicked.connect( self.saveAddress )
        self.setController( controller )

    def setController( self, controller ):
        if not controller:
            controller = Controller.instance()
        self._addressListModel.setAddressList( controller.addressList())
        controller.addressSelected.connect( self.addressSelected )
        self.uAddressEditor.setController( controller )
        self._controller = controller


    def addAddressAction( self, name, action, whatsthis='' ):
        button = QPushButton(self)
        button.setText(name)
        button.setWhatsThis( whatsthis )
        button.clicked.connect(lambda: self.runAddressAction(action))
        self.uCustomButtonArea.addWidget(button)

    def runAddressAction( self, action ):
        address = self.uAddressListView.selectedAddress()
        if address:
            action(address)

    def addressSelected( self, address ):
        if address == self.uAddressListView.selectedAddress():
            return
        if self.uAddressEditor.isDirty():
            return
        self.uAddressListView.selectAddress( address )

    def selectAddress( self ):
        address = self.uAddressListView.selectedAddress()
        if address and self.makeClean():
            self._controller.selectAddress( address )

    def makeClean( self ):
        return self.uAddressEditor.makeClean()

    def setShowAll( self ):
        if self.uShowAll.isChecked() and self.makeClean():
            self._addressListModel.setFilter(None)

    def setShowWarnings( self ):
        if self.uShowWarnings.isChecked() and self.makeClean():
            self._addressListModel.setFilter(lambda x: x['warnings']=='Yes')

    def setShowNotes( self ):
        if self.uShowNotes.isChecked() and self.makeClean():
            self._addressListModel.setFilter(lambda x: x['shortnotes']!='')

    def setShowUndefined( self ):
        if self.uShowUndefined.isChecked() and self.makeClean():
            self._addressListModel.setFilter(lambda x: x['address'].status()=='UNKN')
    def saveAddress( self, address ):
        self.uAddressEditor.save()
        row = self.uAddressListView.selectedRow()
        if row != None and row < self._addressListModel.count()-1:
            self.uAddressListView.selectRow( row+1 )



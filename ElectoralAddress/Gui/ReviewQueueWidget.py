from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_ReviewQueueWidget import Ui_ReviewQueueWidget

import Controller

from AddressList import AddressListModel

class ReviewQueueWidget( Ui_ReviewQueueWidget, QWidget ):

    def __init__( self, parent=None, controller=None ):
        QWidget.__init__( self, parent )
        self.setupUi(self)
        self._addressListModel = AddressListModel()
        self._addressListModel.setColumns(
          ['id','version', 'displayNum', 'displayRoad', 'submittedDate', 'changeTypeName', 'addressType', 'suburbLocality', 'lifecycle', 'townCity', 'objectType', 'addressPositionType', 'queueStatusName', 'submitterUserName'],
          ['changeId','version', 'Number', 'Road','submittedDate', 'changeType', 'addressType', 'suburb', 'lifecycle', 'townCity', 'objectType', 'addressPositionType', 'queueStatus', 'submitter' ]
         )
        #Need to add address add above to support "replaces"  
        
        self.uReviewListView.setModel( self._addressListModel )
        self.uReviewListView.rowSelectionChanged.connect( self.selectAddress )
        #self.uShowAll.toggled.connect( self.setShowAll )
        #self.uShowWarnings.toggled.connect( self.setShowWarnings )
        #self.uShowNotes.toggled.connect( self.setShowNotes )
        #self.uShowUndefined.toggled.connect( self.setShowUndefined )
        #self.uSaveAddressButton.clicked.connect( self.saveAddress )
        #self.uMergeAddressButton.clicked.connect( self.mergeAddresses )
        self.setController( controller )
        self._controller.loadReviewQueue()

    def setController( self, controller ):
        if not controller:
            controller = Controller.instance()
        self._addressListModel.setAddressList( controller.reviewList())
        controller.reviewSelected.connect( self.addressSelected )
        self.uReviewEditor.setController( controller )
        self._controller = controller

    """
    def addAddressAction( self, name, action, whatsthis='' ):
        button = QPushButton(self)
        button.setText(name)
        button.setWhatsThis( whatsthis )
        button.clicked.connect(lambda: self.runAddressAction(action))
        self.uCustomButtonArea.addWidget(button)

    def runAddressAction( self, action ):
        address = self.uReviewListView.selectedAddress()
        if address:
            action(address)
    """
    def addressSelected( self, address ):
        #if address == self.uReviewListView.selectedAddress():
        #    return
        #if self.uAddressEditor.isDirty():
        #    return
        self.uReviewListView.selectAddress( address )

    def selectAddress( self ):
        address = self.uReviewListView.selectedAddress()
        #if address and self.makeClean():
        
        self._controller.selectReview( address )
    """
    def makeClean( self ):
        return self.uReviewEditor.makeClean()

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
        row = self.uReviewListView.selectedRow()
        if row != None and row < self._addressListModel.count()-1:
            self.uReviewListView.selectRow( row+1 )

    def mergeAddresses( self ):
        address = self.uReviewListView.selectedAddress()
        if address and self.uAddressEditor.makeClean():
            self.uReviewListView.selectAddress(None)
            address = MergeAddressDialog.mergeAddresses( self, self._controller, address )
            self.uReviewListView.selectAddress(address)
"""

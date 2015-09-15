
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ElectoralAddress.Supplier import Supplier
from ElectoralAddress.ReaderType import ReaderType

from DictionaryList import DictionaryListModel

from ElectoralAddress import Database
from Utility import attempt
from Controller import Controller
from Controller import Controller

from Ui_ManageSuppliers import Ui_ManageSuppliers

class ManageSuppliers( QWidget, Ui_ManageSuppliers ):

    def __init__( self, parent=None, controller=None ):
        QWidget.__init__(self,parent)
        self.setupUi(self)
        self._editItem = None

        self._isDirty = False
        self.uNew.clicked.connect( self.newItemClicked )
        self.uSave.clicked.connect( self.saveItemClicked )
        self.uCancel.clicked.connect( self.cancelItemClicked )
        self.uDelete.clicked.connect( self.deleteItemClicked )
        self.uListModel = DictionaryListModel()
        self.uListView.setModel( self.uListModel )
        self.setListColumns( self.uListModel )
        self.uListView.rowSelected.connect( self.selectItem )

        self.uName.textChanged.connect( self.enableButtons2 )
        self.uSourceType.currentIndexChanged[int].connect( self.enableButtons2 )
        self.uTA.currentIndexChanged[int].connect( self.enableButtons2 )
        self.setController( controller )
        self.load()
        self.enableButtons()

    def setController( self, controller=None ):
        if not controller:
            controller=Controller()
        self._controller = controller
        self._controller.suppliersUpdated.connect( self.loadList )
        self._controller.sourceTypesUpdated.connect( self.loadSourceTypes )

    def enableButtons2( self, text ):
        self.enableButtons()

    def enableButtons( self ):
        isDirty = self.isDirty()
        canCancel = isDirty or (self.uListView.rowCount() > 0 and self._editItem == None)
        self.uNew.setEnabled( not isDirty and self._editItem != None )
        self.uDelete.setEnabled( not isDirty )
        self.uSave.setEnabled( isDirty )
        self.uCancel.setEnabled( canCancel ) 
        if not self._editItem:
            self.uEditStatus.setText("Create a new supplier")
        elif isDirty:
            self.uEditStatus.setText("Editing " + self._editItem['name'])
        else:
            self.uEditStatus.setText("")

    def newItemClicked( self ):
        if not self.canChangeItem():
            return
        self.clearItem()

    def deleteItemClicked( self ):
        if self.isDirty():
            return
        self.deleteItem( self.uListView.selectedItem())
        self._controller.updateSuppliers()

    def cancelItemClicked( self ):
        self.loadItem( self.uListView.selectedItem())

    def saveItemClicked( self ):
        if not self.isDirty():
            return
        self.saveItem()

    def selectItem( self, rowno ):
        if not self.canChangeItem():
            return
        item = self.uListView.selectedItem()
        self.loadItem( item )

    def canChangeItem(self):
        if not self.isDirty():
            return True
        result = QMessageBox.question(self,"Save supplier",
                "Do you want to save the changes\n" +
                "Select yes to save, no to discard edits,  or cancel to continue editing",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel )
        if result == QMessageBox.Cancel:
            return False
        if result == QMessageBox.Yes:
            return self.saveItem()
        return True

#-------------------------------------------------

    def load( self ):
        self.loadSourceTypes()
        for r in Database.execute('select stt_id,name from elc_TAList() order by name'):
            self.uTA.addNameValue(r[1],r[0])
        self.loadList()

    def loadList( self ):
        self.uListModel.setList( Supplier.list())

    def loadSourceTypes( self ):
        current = self.uSourceType.selectedValue()
        self.uSourceType.clear()
        for r in sorted(ReaderType.list(),key=lambda x: x['name']):
            self.uSourceType.addNameValue(r['name'],r['id'])
        self.uSourceType.selectValue(current)

    def setListColumns( self, listModel ):
        listModel.setColumns(['id','name'],['Id','Supplier'])

    def clearItem( self ):
        self._editItem = None
        self.uName.setText('')
        self.uSourceType.setCurrentIndex(0)
        self.uTA.setCurrentIndex(0)
        pass

    def loadItem( self, item ):
        if not item:
            return
        self._editItem = item
        self.uName.setText( item['name'] )
        self.uSourceType.selectValue(item['stp_id'])
        self.uTA.selectValue(item['stt_id'])

    @attempt( default = False )
    def saveItem( self ):
        if not self.checkIsValid():
            return False
        if self._editItem: 
            id = Database.executeScalar('elc_UpdateSupplier',
                             self._editItem['id'],
                             str(self.uName.text()),
                             self.uSourceType.selectedValue(),
                             self.uTA.selectedValue())
        else:
            id = Database.executeScalar('elc_CreateSupplier',
                             str(self.uName.text()),
                             self.uSourceType.selectedValue(),
                             self.uTA.selectedValue())
        self.clearItem()
        self._controller.updateSuppliers()
        self.uListView.selectId( id )
        return True


    @attempt
    def deleteItem( self, item ):
        if not self._editItem:
            return
        if QMessageBox.question(
            self,
            "Delete supplier",
            "Are you sure you want to remove the supplier " + self._editItem['name'] + '?', 
            QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        Database.execute('elc_DeleteSupplier',self._editItem['id'])
        self._controller.updateSuppliers()

    def isDirty( self ):
        if self._editItem:
            if str(self.uName.text()) != self._editItem['name']: return True
            if self.uSourceType.selectedValue() != self._editItem['stp_id']: return True
            if self.uTA.selectedValue() != self._editItem['stt_id']: return True
        else:
            if str(self.uName.text()) != '': return True
        return False

    def checkIsValid( self ):
        return (
            str(self.uName.text()) != '' and 
            self.uSourceType.selectedValue() != None and
            self.uTA.selectedValue() != None );

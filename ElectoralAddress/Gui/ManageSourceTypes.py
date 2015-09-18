
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ElectoralAddress.Reader import Reader
from ElectoralAddress.ReaderType import ReaderType

from DictionaryList import DictionaryListModel

from ElectoralAddress import Database
from Utility import attempt
from Controller import Controller

from Ui_ManageSourceTypes import Ui_ManageSourceTypes

class ManageSourceTypes( QWidget, Ui_ManageSourceTypes ):

    def __init__( self, parent=None, controller=None ):
        QWidget.__init__(self,parent)
        self.setupUi(self)
        self._editItem = None

        self._readerClasses=[]
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
        self.uReaderClass.currentIndexChanged[int].connect( self.enableButtons2 )
        self.uReaderClass.currentIndexChanged[int].connect( self.setReaderClass )
        self.uFileExtension.textChanged.connect( self.enableButtons2 )
        self.uCoordSys.currentIndexChanged[int].connect( self.enableButtons2 )
        self._params = DictionaryListModel(
            columns=['label','value'],
            headers=['Name','Value'])
        self._params.setEditColumns(['value'])
        self._params.setReadonlyColour( self.palette().color(QPalette.Window))
        self._params.dataChanged.connect( self.enableButtons3 )
        self.uParameterList.setModel(self._params)
        self.uParameterList.rowSelected.connect( self.showParamDesc )

        self.setController( controller )
        self.load()
        self.enableButtons()

    def setController( self, controller=None ):
        if not controller:
            controller=Controller()
        self._controller = controller
        self._controller.sourceTypesUpdated.connect( self.loadList )

    def enableButtons3( self, index1, index2 ):
        self.enableButtons()

    def enableButtons2( self, text ):
        self.enableButtons()

    def enableButtons( self ):
        isDirty = self.isDirty()
        isValid = False
        if isDirty:
            isValid = self.checkIsValid()
        canCancel = isDirty or (self.uListView.rowCount() > 0 and self._editItem == None)
        self.uNew.setEnabled( not isDirty and self._editItem != None )
        self.uDelete.setEnabled( not isDirty )
        self.uSave.setEnabled( isValid )
        self.uCancel.setEnabled( canCancel ) 
        if not self._editItem:
            self.uEditStatus.setText("Create a new source type")
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
        self._controller.updateSourceTypes()

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
        result = QMessageBox.question(self,"Save source type",
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
        self._readerClasses[:] = []
        for sc in Reader.__subclasses__():
            self._readerClasses.append(
                dict(name=sc.__name__,params=sc.params())
                )
        self._readerClasses.sort( key=lambda x: x['name'] )
        for i, c in enumerate( self._readerClasses ):
            self.uReaderClass.addNameValue( c['name'], i )

        for r in Database.execute('select srid, name from elc_getSpatialReferenceSystems() order by name'):
            self.uCoordSys.addNameValue(r[1],r[0])

        self.loadList()

    def setReaderClass( self, row ):
        nreader = self.uReaderClass.selectedValue()
        if nreader != None:
            reader = self._readerClasses[nreader]
            prms = reader['params']
            for p in prms:
                p['required'] = p.get('required',False)
                p['value'] = ''
                p['startvalue'] = ''
                p['label'] = p['name'] + ('*' if p['required'] else '')
            self._params.setList(prms)

    def showParamDesc( self, row ):
        item = self.uParameterList.selectedItem()
        if item:
            self.uParamDesc.setText( item['description'] )
        else:
            self.uParamDesc.setText('')

    def loadList( self ):
        self.uListModel.setList( ReaderType.list())

    def setListColumns( self, listModel ):
        listModel.setColumns(['id','name','readerclass'],['Id','Name','Type'])

    def clearParams( self ):
        for i,p in enumerate(self._params.list()):
            p['value'] = ''
            p['startvalue'] = ''
            self._params.updateItem(i)

    def clearItem( self ):
        self._editItem = None
        self.uName.setText('')
        self.uReaderClass.setCurrentIndex(0)
        self.uFileExtension.setText('')
        self.clearParams()

    def loadItem( self, item ):
        if not item:
            return
        self._editItem = item
        self.uName.setText( item['name'] )
        for i in range( len( self._readerClasses ) ):
            if self._readerClasses[i]['name'] == item['readerclass']:
                self.uReaderClass.selectValue(i)
                break
        self.uFileExtension.setText(item['file_ext'])
        self.uCoordSys.selectValue( item['srs_id'])
        self.clearParams()
        for stp in item['params']:
            for i,prm in enumerate(self._params.list()):
                if prm['name'] == stp['name']:
                    prm['value'] = stp['value']
                    prm['startvalue'] = stp['value']
                    self._params.updateItem(i)

    @attempt( default = False )
    def saveItem( self ):
        if not self.checkIsValid():
            return False
        params = ReaderType.encodeParams( self._params.list())
        if self._editItem: 
            id = Database.executeScalar('elc_UpdateSourceType',
                             self._editItem['id'],
                             str(self.uName.text()),
                             str(self.uFileExtension.text()),
                             self.uCoordSys.selectedValue(),
                             str(self.uReaderClass.currentText()),
                             params)
        else:
            id = Database.executeScalar('elc_CreateSourceType',
                             str(self.uName.text()),
                             str(self.uFileExtension.text()),
                             self.uCoordSys.selectedValue(),
                             str(self.uReaderClass.currentText()),
                             params)
        self.clearItem()
        ReaderType.reload()
        self._controller.updateSourceTypes()
        self.uListView.selectId( id )
        return True

    @attempt
    def deleteItem( self, item ):
        if not self._editItem:
            return
        if QMessageBox.question(
            self,
            "Delete source type",
            "Are you sure you want to remove the source type " + self._editItem['name'] + '?', 
            QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        Database.execute('elc_DeleteSourceType',self._editItem['id'])
        ReaderType.reload()
        self._controller.updateSourceTypes()

    def paramsDirty( self ):
        for p in self._params.list():
            if p['value'] != p['startvalue']: return True
        return False

    def isDirty( self ):
        if self._editItem:
            if str(self.uName.text()) != self._editItem['name']: return True
            if str(self.uFileExtension.text()) != self._editItem['file_ext']: return True
            if str(self.uReaderClass.currentText()) != self._editItem['readerclass']: return True
            if self.uCoordSys.selectedValue() != self._editItem['srs_id']: return True
        else:
            if str(self.uName.text()) != '': return True
            if str(self.uFileExtension.text()) != '': return True

        if self.paramsDirty(): return True
        return False

    def paramsValid( self ):
        for p in self._params.list():
            if 'required' in p and p['required'] and not p['value']:
                return False
        return True

    def checkIsValid( self ):
        return (
            str(self.uName.text()) != '' and 
            str(self.uFileExtension.text()) != '' and 
            self.uReaderClass.selectedValue() != None and
            self.uCoordSys.selectedValue() != None and
            self.paramsValid()
            )

from qgis.core import * # TEMP
import re

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_ReviewEditorWidget import Ui_ReviewEditorWidget
from DictionaryList import DictionaryListModel
from ElectoralAddress.ResolutionData import ResolutionData

from ElectoralAddress.CodeLookup import CodeLookup
from ElectoralAddress.Address import AddressStatus
from ElectoralAddress.AimsApi import *
import Controller

class ReviewEditModel( QAbstractListModel ):
       
    def __init__(self, data = [], parent = None):
        QAbstractListModel.__init__(self, parent)
        self._headers = ['addressNumber' , 'addressNumberSuffix' , 'addressType' , 'lifecycle', 'roadName' , 'roadTypeName']
        self.setList (data)

    def setList( self, list ):
        #self.resettingModel.emit()
        self._list = list if list != None else []
        self.layoutChanged.emit()

    def headerData(self, section, orientation, role):
        
        if role == Qt.DisplayRole:
            
            if orientation == Qt.Horizontal:
                return "Address Attributes"
            else:
                return self._headers[section]

    def rowCount(self, parent):
        return len(self._list)

    def data(self, index, role):
        if role == Qt.EditRole:
            return self._list[index.row()]
        if role == Qt.DisplayRole:
            row = index.row()
            value = self._list[row]
            return value

    def getData(self):
        
        QgsMessageLog.logMessage(', '.join(map(str, self._list)), level=QgsMessageLog.CRITICAL) #TEMP

    def flags(self, index):
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        
    def setData(self, index, value, role = Qt.EditRole):
        if role == Qt.EditRole:
            
            row = index.row()
            data = value
            
            #if data.isValid():
            self._list[row] = data
            self.dataChanged.emit(index, index)
            return True
        #return False

class ReviewEditorWidget( Ui_ReviewEditorWidget, QWidget ):

    def __init__( self, parent=None, controller=None ):
        QWidget.__init__( self, parent )
        self.setupUi(self)
        self._address = None
        self._rEditList = ReviewEditModel()
        #set tables header width = stretch
        header = self.uReviewAttributes .horizontalHeader()
        header.setStretchLastSection(True)
        self.uReviewAttributes.setModel( self._rEditList )
        self.rUpdateButton.clicked.connect( self.updateButtonClicked )
        self.uRejectButton.clicked.connect( self.rejectButtonClicked )
        self.uAcceptButton.clicked.connect( self.acceptButtonClicked )
        #self.uHouseNumber.textChanged.connect( self.houseNumberChanged )
        '''
        self.load()
        self.setController( controller )
        '''

    def setController( self, controller ):
        if not controller:
            controller = Controller.instance()
        self._controller = controller
        controller.reviewUpdated.connect(self.reviewUpdated)
        controller.reviewSelected.connect(self.setAddressIfClean)
    
    def address(self):
        return self._address

    def setAddressIfClean( self, address ):
        #if not self.isDirty():   
        self.setAddress( address )

    def setAddress( self, address, makeClean=True ):
        if address == self._address:
            return True
        #if makeClean:
        #    self.makeClean()
        self._address = address
        self.load()
        return True

    def makeClean( self ):
        isclean = True
        if self._address and self.isDirty():
            result = QMessageBox.question( self, "Save changes", "Do you want to save the changes to "+self._address.address(),
                                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel )
            if result == QMessageBox.Cancel:
                isclean = False
            if result == QMessageBox.Yes:
                self.save()
            elif result == QMessageBox.No:
                self.load()
        return isclean

    def notesText( self ):
        return str(self.uNotes.document().toPlainText()).strip()

    def isDirty( self ):
        if not self._address:
            return False
        if self._status != self._status0:
            return True
        if str(self.uHouseNumber.text()) != self._housenumber0:
            return True
        if self.notesText() != self._notes0:
            return True
        if self.uAcceptButton.isChecked():
            return True
        if self._sad_id != self._sad_id0:
            return True
        return False

    def addressUpdated( self, address ):
        if self._address and address and address.id() == self._address.id():
            self.load(True)

    def save( self ):
        if self.isDirty():
            address = self._address
            address.setStatus( self._status)
            address.setHousenumber( str(self.uHouseNumber.text()) )
            address.setSad_id( self._sad_id )
            address.setAcceptWarnings( self.uAcceptButton.isChecked() )
            address.setNotes(self.notesText())
            self._controller.updateAddress(address)

    def load(self,reload=False):

        address = self._address
        self.uAcceptButton.setEnabled(True) #rename button to r...
        self.uAcceptButton.setChecked(False)
        self.rUpdateButton.setEnabled(True)
        self.rUpdateButton.setChecked(False)
        self.uRejectButton.setEnabled(True) #rename button to r..
        self.uRejectButton.setChecked(False)

        if not address:
           
            #self._status0 = None
            #self._housenumber0 = None
            #self._sad_id0 = None
            #self._notes0 = None

            #self._status=AddressStatus.Undefined
            #self._sad_id=None
            #self._delete=False
            #self.uAddressBeingEdited.setText('No address selected')
            #self.uStatus.setText('')
            #self.uReplaceLabel.setText('Landonline address to replace')
            #self.uHouseNumber.setText('')
            #self.uSourceNumber.setText('')
            #self.uNotes.setPlainText('')
            self.rWarnings.setText('')
            self.rInfo.setText('')
            #self.uHouseNumber.setEnabled(False)
            #self.uNotes.setEnabled(False)
            #self.uSrcComment.setText('')
            #self._replacementList.setList([])
            #self.uSelectReplacementButton.setEnabled(False)
            #self.uUnselectReplacementButton.setEnabled(False)
            return
        self.rMessage.setStyleSheet("* { color : red; font-weight: bold }")
        self.rStatus.setText(address.getQueueStatusName())
        try: #update to case statement
            
            self.rMessage.setText(address.getReviewMessage())
        except: self.rMessage.setText('')
        self.rChangeType.setText(address.changeTypeName)
        self.rInfo.setText(address.info)
        self.rWarnings.setText(address.warnings)
        self.uAddressBeingEdited.setText(address.displayNum() +' '+ address.displayRoad())
        
        #populate review edit table
        #list order is persistent
        self._rEditList.setList([ address.addressNumber,address.addressNumberSuffix,address.addressType,address.lifecycle,address.roadName,address.roadTypeName]) 
        
        #self.rWarnings.setText(address.version)
        '''
        self._status0 = address.status()
        self._housenumber0 = address.housenumber()
        self._sad_id0 = address.sad_id()
        self._notes0 = address.notes()
        self._status = address.status()
        self._sad_id = address.sad_id()
        self._delete = address.src_status==AddressStatus.Delete
        self._badroad = not address.roadIsValid()
        self._badgeometry = not address.geometryIsValid()
        self.uIgnoreButton.setEnabled(True)
        if self._delete:
            self.uReplaceButton.setText("Delete")
        else:
            self.uNewButton.setEnabled(True)
        if self._sad_id != None:
            self.uReplaceButton.setEnabled(True)
        if self._status == AddressStatus.New:
            self.uNewButton.setChecked(True)
        elif self._status in (AddressStatus.Replace,AddressStatus.Delete):
            self.uReplaceButton.setChecked(True)
        elif self._status == AddressStatus.Ignore:
            self.uIgnoreButton.setChecked(True)
        if self._badroad:
            self.uNewButton.setEnabled( False )
            self.uReplaceButton.setEnabled( False )
        if self._badgeometry:
            self.uNewButton.setEnabled( False )
            self.uReplaceButton.setEnabled( False )
        self.setStatusLabel()
        self.setRangeLabel()
        self.uAddressBeingEdited.setText(address.address())
        if self._delete:
            self.uReplaceLabel.setText('Landonline address to delete')
        else:
            self.uReplaceLabel.setText('Landonline address to replace with ' + address.address())
        self.uHouseNumber.setText(address.housenumber())
        srcnumber = ""
        if address.ismerged():
            srcnumber = "(from merge)"
        else:
            srcnumber = "(Supplied as "+address.src_housenumber()+")"
        self.uSourceNumber.setText( srcnumber )
        warnings = ", ".join(
                    str(CodeLookup.lookup('address_warning',code)) 
                    for code in address.warning_codes().split()
                    )
        self.uWarnings.setText( warnings )
        if warnings:
            self.uAcceptButton.setEnabled(True)
            self.setWarningColour()
        self.uSrcComment.setText( address.src_comment() )
        self.uNotes.setPlainText( address.notes() )
        self.uHouseNumber.setEnabled(True)
        self.uNotes.setEnabled(True)
        self.searchForAddresses()
    def houseNumberChanged( self, newnumber ):
        self.setRangeLabel()
    def setRangeLabel( self ):
        if not self._address:
            self.uRange.setText('')
            self.uRange.setStyleSheet('')
            return
        range_low = None
        range_high = None
        if self.uHouseNumber.text() == self._housenumber0:
            range_low = self._address.range_low()
            range_high = self._address.range_high()
        else:
            range_low, range_high = self.extractNumberRange(str(self.uHouseNumber.text()))
        if range_low is None:
            self.uRange.setText('Invalid')
            self.uRange.setStyleSheet( self.warningStyle )
        elif range_high is None:
            self.uRange.setText('Range: ' + str(range_low) + '-')
            self.uRange.setStyleSheet('')
        else:
            self.uRange.setText('Range: ' + str(range_low) + '-' + str(range_high))
            self.uRange.setStyleSheet('')
    '''
                
    def updateButtonClicked( self ):
        #self.uncheckButtons( self.rUpdateButton )
        self.performReviewAction()

    def rejectButtonClicked( self ):
        #self.uncheckButtons( self.uRejectButton )
        self.performReviewAction()

    def acceptButtonClicked( self ):
        #self.uncheckButtons( self.uAcceptButton )
        self.performReviewAction()
        
    def updateReview (self):
        ''' any properties of resolution class to be updated via here '''
        address = self._address
        
        self._controller.updateReview(address)
    
    def reviewUpdated( self, address ):
        self.load() 
        
    def performReviewAction( self ):
        # tests? 

        if self.uAcceptButton.isChecked():
            _status = acceptResolution( self._address.id, self._address.version )

        elif self.uRejectButton.isChecked():
            _status = rejectResolution( self._address.id, self._address.version )
        
        elif self.rUpdateButton.isChecked():
            self.modelDict = None
            self._rEditList.getData()#TEMP

        try:
            if _status[0] == 'status':
                self._address.setStatus( _status[1] ) #keep class insync
            elif _status[0] == 'message':
                self._address.setMessage( _status[1] ) #keep class insync
        except:
            pass
        self.updateReview( )
         
        #if self._badgeometry:
        #    status=AddressStatus.BadGeometry
        #self._status = status
        #self.setStatusLabel()
    '''
    def setStatus( self, status ):
        self._status = status
        self.uNewButton.setChecked( status == AddressStatus.New )
        self.uReplaceButton.setChecked( status in (AddressStatus.Replace, AddressStatus.Delete))
        self.uIgnoreButton.setChecked( status == AddressStatus.Ignore )
    def setStatusLabel(self):
        label = CodeLookup.lookup('address_status',self._status,'None')
        if self._delete and self._status != AddressStatus.Delete:
            label += " (delete)"
        self.rStatus.setText(address.changeTypeName)
    def setWarningColour( self ):
        style = ""
        if not self.uAcceptButton.isChecked():
            style = self.warningStyle
        self.uWarnings.setStyleSheet(style)
    def selectReplacement( self ):
        row = self.uReplacementAddresses.selectedItem()
        if row and not self._badroad:
            self._sad_id = row['sad_id']
            self.uReplaceButton.setEnabled(True)
            self.uReplaceButton.setChecked(True)
            self.replaceButtonClicked()
        self.resetLinkedAddress()
    def unselectReplacement( self ):
        self._sad_id = None
        if self._status == AddressStatus.Replace or self._status==AddressStatus.Delete:
            newstatus = AddressStatus.New if self._status == AddressStatus.Replace else AddressStatus.Ignore
            self.uReplaceButton.setChecked(False)
            self.uReplaceButton.setEnabled(False)
            if self._delete:
                self.uIgnoreButton.setChecked(True)
            else:
                self.uNewButton.setChecked(True)
            self.resetStatus()
        self.uReplaceButton.setEnabled(False)
        self.resetLinkedAddress()
    def searchForAddresses2( self, row ):
        self.searchForAddresses()
    def searchForAddresses( self ):
        found = False
        if self._address:
            radius = float( self.uReplaceSearchRadius.currentText())
            rlist = self._address.getNearbyAddressPoints( radius )
            found = len(rlist) > 0
            self._replacementList.setList(rlist)
            self.uReplacementAddresses.resizeColumnsToContents()
        else:
            self._replacementList.setList([])
        self.uSelectReplacementButton.setEnabled(found)
        self.uUnselectReplacementButton.setEnabled(found and bool(self._sad_id))
    def resetLinkedAddress( self ):
        apts = self._replacementList.list()
        found = False
        for i in range(len(apts)):
            found = True
            apt = apts[i]
            if apt['sad_id'] == self._sad_id:
                if apt['linked'] != 'Yes':
                    apt['linked'] = 'Yes'
                    self._replacementList.updateItem(i)
            elif apt['linked'] == 'Yes':
                apt['linked'] = ''
                self._replacementList.updateItem(i)
        self.uUnselectReplacementButton.setEnabled(found and bool(self._sad_id))
    # Note: This function needs to match the logic in the trigger
    # function _elc_trg_SetAddressStatus, which validates addresses
    def extractNumberRange( self, housenumber ):
        numberre = (
            r'^(?:' +
            # 12-23, 15A-23B
            r'(\d+)[A-Z]*(?:\-(\d+)[A-Z]*)?|' +
            # 1/44-5/44 , 1A/83C-5B/83C
            r'[A-Z]{0,2}\d+[A-Z]*\/((\d+)[A-Z]*)(?:\-[A-Z]{0,2}\d+[A-Z]*\/\3)?|' + # was - r'\d+[A-Z]*\/((\d+)[A-Z]*)(?:\-\d+[A-Z]*\/\3)?|' +
            # R/1234A
            r'R\/(\d+)[A-Z]' +
            # If all else fails match anything so that regexp_matches always
            # returns a row.
            r'|.*)$'
            )
        match = re.match(numberre,housenumber)
        range_low = match.group(1) or match.group(4) or match.group(5)
        range_high = match.group(2)
        range_low = int(range_low) if range_low else None
        range_high = int(range_high) if range_high else None
        if range_high == range_low:
            range_high=None
        if range_high != None and range_high < range_low:
            range_high=None
            range_low=None
        return range_low, range_high
        '''

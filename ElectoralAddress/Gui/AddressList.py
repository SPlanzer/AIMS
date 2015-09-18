import re

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from DictionaryList import DictionaryListModel, DictionaryListView

from Ui_JobEditorWidget import Ui_JobEditorWidget

from ElectoralAddress.Address import Address
from ElectoralAddress.ResolutionData import ResolutionData
from ElectoralAddress.CodeLookup import CodeLookup

import ElectoralAddress.AimsApi


import Config

class AddressList(QObject):
    '''
    Class for managing a list of Address objects and signalling changes 
    to addresses, for use by derived models/views
    '''

    itemChanged = pyqtSignal(int, name="itemChanged")
    listChanged = pyqtSignal(name="listChanged")

    shortNoteLen = 20

    def __init__(self, job=None):
        QObject.__init__(self)
        self._list = []
        self._lookup = None
        self.setJob(job)

    # Management functions - don't emit signals
    def _createItem(self, adr):
        notes = adr.notes() or ''
        shortnotes = notes if len(notes) <= self.shortNoteLen else notes[:self.shortNoteLen - 3] + '...'
        return dict(
            address=adr,
            display=adr.display(),
            id=adr.id(),
            roadname=adr.roadname(),
            rna_id=adr.rna_id(),
            par_id=adr.par_id(),
            rna_par_id=str(adr.rna_id()) + '/' + str(adr.par_id()),
            src_roadname=adr.src_roadname(),
            rna_roadname=adr.rna_roadname(),
            housenumber=adr.housenumber(),
            sad_id=adr.sad_id(),
            sad_address=adr.sad_address(),
            sad_offset=adr.sad_offset(),
            warnings='Yes' if adr.warning_codes() else 'No',
            status=CodeLookup.lookup('address_status', adr.status()),
            src_id=adr.src_id(),
            notes=notes,
            shortnotes=shortnotes,
            cluster_id=adr.cluster_id(),
            notmerged=adr.merge_adr_id() == None
            )

    def _lookupId(self, id):
        if not self._lookup:
            self._lookup = dict((i[1]['id'], i[0]) for i in enumerate(self._list))
        return self._lookup.get(id)

    def _addAddress(self, adr):
        self._lookup = None
        self._list.append(self._createItem(adr))

    def clear(self):
        self._list[:] = []
        self._lookup = None
        self._job = None
        self.listChanged.emit()

    def setJob(self, job):
        self.clear()
        if not job:
            return
        self._job = job
        for adr in job.addresses():
            self._addAddress(adr)
        self.listChanged.emit()

    def job(self): return self._job

    def list(self):
        return self._list 

    def addresses(self, filter=None):
        return [i['address'] for i in self._list if filter == None or filter(i['address'])]

    def addressItem(self, adr):
        index = self.addressIndex(adr)
        if index != None:
            return self._list[index]
        return None

    def addressIndex(self, adr):
        if adr:
            return self._lookupId(adr.id())
        return None

    def addressFromId(self, id):
        i = self._lookupId(id)
        return self._list[i]['address'] if i != None else None

    def addressesFromIds(self, idlist):
        result = []
        for id in idlist:
            adr = self.addressFromId(id)
            if adr:
                result.append(adr)
        return result

    # addNewAddress and removeAddress both create a copy of the list
    # This is because otherwise the list is changed before the resettingModel
    # event of the model is sent.

    def addNewAddress(self, adr):
        self._list = [x for x in self._list]
        self._addAddress(adr)
        self.listChanged.emit()

    def removeAddress(self, adr):
        self._lookup = None
        id = adr.id()
        self._list = [x for x in self._list if x['id'] != id]
        self.listChanged.emit()

    def updateAddress(self, adr):
        if adr == None:
            return
        index = self._lookupId(adr.id())
        if index != None:
            if adr.deleted():
                self.removeAddress(adr)
            else:
                self._list[index] = self._createItem(adr)
                self.itemChanged.emit(index)
        elif not adr.deleted():
            self.addNewAddress(adr)

class ReviewList( QObject ):

    #below obviously a duplicate of should look to merge with above, maybe? 
    '''
    Class for managing a list of Review objects and signalling changes 
    to addresses, for use by derived models/views
    '''

    itemChanged = pyqtSignal(int,name="itemChanged")
    listChanged = pyqtSignal(name="listChanged")
    shortNoteLen = 20

    def __init__( self ):
        QObject.__init__(self)
        self._list = []
        self._lookup = None

    # Management functions - don't emit signals
    def _rCreateItem( self, reviewItem ):

        return dict(
            
            address = reviewItem,
            version = reviewItem.version,
            id = reviewItem.id,
            changeTypeName = reviewItem.changeTypeName,
            submitterUserName = reviewItem.submitterUserName,
            submittedDate = reviewItem.submittedDate,
            queueStatusName = reviewItem.queueStatusName,
           
            addressId = reviewItem.addressId,
            addressType = reviewItem.addressType,
            lifecycle = reviewItem.lifecycle,
            unitType = reviewItem.unitType,
            unitValue = reviewItem.unitValue,
            levelType = reviewItem.levelType,  
            levelValue = reviewItem.levelValue,      
            addressNumberPrefix = reviewItem.addressNumberPrefix,  
            addressNumber = reviewItem.addressNumber,
            addressNumberSuffix = reviewItem.addressNumberSuffix,
            addressNumberHigh = reviewItem.addressNumberHigh,
            roadPrefix = reviewItem.roadPrefix, 
            roadName = reviewItem.roadName,
            roadTypeName = reviewItem.roadTypeName, 
            roadSuffix = reviewItem.roadSuffix,
            roadCentrelineId = reviewItem.roadCentrelineId,
            suburbLocality = reviewItem.suburbLocality,
            townCity = reviewItem.townCity,            
            objectType = reviewItem.objectType,
            addressPositionType = reviewItem.addressPositionType,
            addressPositionCoords =reviewItem.addressPositionCoords,            
            displayNum = reviewItem.displayNum(),
            displayRoad = reviewItem.displayRoad()                   
            )

    def _lookupId(self, id):
        if not self._lookup:
            self._lookup = dict((i[1]['id'], i[0]) for i in enumerate(self._list))
        return self._lookup.get(id)

    def _addAddress(self, adr):
        self._lookup = None
        self._list.append(self._createItem(adr))

    def clear(self):
        self._list[:] = []
        self._lookup = None
        self._job = None
        self.listChanged.emit()

    def setJob(self, job):
        self.clear()
        if not job:
            return
        self._job = job
        for adr in job.addresses():
            self._addAddress(adr)
        self.listChanged.emit()

    def job(self): return self._job

    def list(self):
        return self._list 

    def addresses(self, filter=None):
        return [i['address'] for i in self._list if filter == None or filter(i['address'])]

    def addressItem(self, adr):
        index = self.addressIndex(adr)
        if index != None:
            return self._list[index]
        return None

    def addressIndex(self, adr):
        if adr:
            return self._lookupId(adr.id())
        return None

    def addressFromId(self, id):
        i = self._lookupId(id)
        return self._list[i]['address'] if i != None else None

    def addressesFromIds(self, idlist):
        result = []
        for id in idlist:
            adr = self.addressFromId(id)
            if adr:
                result.append(adr)
        return result 

    def _addReviewItem( self, reviewItem ):
        self._lookup = None
        self._list.append( self._rCreateItem( reviewItem ) )
        
    def _lookupId( self, id ):
        if not self._lookup:
            self._lookup = dict((i[1]['id'],i[0]) for i in enumerate(self._list))
        return self._lookup.get(id)

    def clear( self ):
        self._list[:] = []
        self._lookup = None
        self._job = None
        self.listChanged.emit()

    def setReviewItems ( self, page = 1 ): #now end point COUNT add this needs to be revised
        #need to test the page
        self._page = str(page)
        hrefs = ElectoralAddress.AimsApi.getResolutionPageHrefs(self._page)     
        for href in hrefs:
            reviewItem = ResolutionData( href )
            self._addReviewItem( reviewItem )
        self.listChanged.emit()

    def updateReview(self, adr):
        if adr == None:
            return
        try: #HACK ! REVISIT
            index = self._lookupId(adr.id())
        except:
            index = self._lookupId(adr.id) 
        if index != None:
         
            #if adr.deleted():
            #self.removeAddress(adr)
            self._list[index] = self._rCreateItem(adr)
            self.itemChanged.emit(index)
        elif not adr.deleted():
            self.addNewAddress(adr) 

    #def job( self ): return self._job

    def list(self):
        return self._list

    def addresses( self, filter = None ):
        return [i['address'] for i in self._list if filter==None or filter(i['address'])]

    def addressItem( self, adr ):
        index = self.addressIndex( adr )
        if index != None:
            return self._list[index]
        return None

    def addressIndex( self, adr ):
        if adr:
            return self._lookupId(adr.id)
        return None

    def addressFromId( self, id ):
        i = self._lookupId(id)
        return self._list[i]['address'] if i != None else None

    def addressesFromIds( self, idlist ):
        result = []
        for id in idlist:
            adr = self.addressFromId(id)
            if adr:
                result.append(adr)
        return result

##################################################################

class AddressListModel(DictionaryListModel):
    ''' Model of addresses in an address list '''

    def __init__(self, alist=None, showMerged=False):
        DictionaryListModel.__init__(self)
        self._showMerged = showMerged
        self.setFilter()
        self.setIdColumn('id')
        self.setupColumns()
        self._alist = None
        self.setAddressList(alist)

    def setupColumns(self):
        self.setColumns(
            ['id', 'display'],
            ['Id', 'Address']
            )

    def setShowMerged(self, showMerged=True):
        self._showMerged = showMerged
        self._resetFilter()

    def setFilter(self, filter=None):
        self._adrsfilter = filter
        self._resetFilter()

    def _resetFilter(self):
        pass
        '''
        f = self._adrsfilter
        if not self._showMerged:
            if self._adrsfilter:
                f = lambda x: x['notmerged'] and self._adrsfilter(x)
            else:
                f = lambda x: x['notmerged']
        DictionaryListModel.setFilter(self, f)
        '''

    @pyqtSlot()
    def resetAddressList(self):
        if self._alist: 
            list = self._alist.list()
            self.setList(list)
        else:
            self.setList(None)

    def setAddressList(self, alist):
        if self._alist:
            self._alist.itemChanged.disconnect(self.updateItem)
            self._alist.listChanged.disconnect(self.resetAddressList)
        if alist:
            self.setList(alist.list())
            alist.itemChanged.connect(self.updateItem)
            alist.listChanged.connect(self.resetAddressList)
        else:
            self.setList(None)
        self._alist = alist

    def addressList(self):
        return self._alist

    def address(self, viewRow):
        item = self.getItem(viewRow)
        return item['address'] if item else None

    def addresses(self, viewRows):
        return [self.address[r] for r in viewRows]

    def addressRow(self, address):
        if not self._alist:
            return None
        index = self._alist.addressIndex(address)
        return self.getDisplayRow(index)

    def addressItem(self, address):
        if not self._alist:
            return None
        return self._alist.addressItem(address)


##################################################################

class AddressListView(DictionaryListView):

    addressSelected = pyqtSignal(Address, name="addressSelected")
    reviewSelected = pyqtSignal(ResolutionData, name="reviewSelected") 

    def __init__(self, parent=None):
        DictionaryListView.__init__(self, parent)
        self.rowSelected.connect(self.onRowSelected)

    def onRowSelected(self, int):
        address = self.selectedAddress()
        if isinstance(address, Address):
            self.addressSelected.emit(address)
        elif isinstance(ResolutionData, Address):
            self.reviewSelected.emit(address)

    def selectedAddress(self):
        if isinstance(self.model(), AddressListModel):
            item = self.selectedItem()
            if item:
                try:
                    return item['address']
                except:
                    return None
        return None
    '''
    def selectedAddress(self):
        if isinstance(self.model(), AddressListModel):
            item = self.selectedItem()
            if item:
                return item['address']
        return None
    '''

    def selectAddress(self, address):
        model = self.model()
        if isinstance(model, AddressListModel):
            if not address:
                self.clearSelection()
            else:
                row = model.addressRow(address)
                if row != None:
                    self.selectRow(row)

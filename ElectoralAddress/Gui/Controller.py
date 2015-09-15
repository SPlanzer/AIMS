
from PyQt4.QtCore import *
from AddressList import AddressList
from AddressList import ReviewList
from ElectoralAddress.Job import Job
from ElectoralAddress.Address import Address
from ElectoralAddress.ResolutionData import ResolutionData
from ElectoralAddress.Upload import Upload
import ElectoralAddress.AimsApi


class Controller( QObject ):

    _instance = None
    jobLoading = pyqtSignal( str ,name="jobLoading" )  
    jobLoaded = pyqtSignal( Job, name="jobLoaded" )
    jobUpdated = pyqtSignal( Job, name="jobUpdated" )
    addressSelected = pyqtSignal( Address, name="addressSelected" )
    reviewSelected = pyqtSignal( ResolutionData, name="reviewSelected" )
    addressUpdated = pyqtSignal( Address, name="addressUpdated" )
    reviewUpdated = pyqtSignal( ResolutionData, name="reviewUpdated" )
    uploadUpdated = pyqtSignal( Upload, name="uploadUpdated" )
    suppliersUpdated = pyqtSignal( name="suppliersUpdated" )
    sourceTypesUpdated = pyqtSignal( name="sourceTypesUpdated" )
    
    def __init__( self ):
        QObject.__init__(self)
        self._job = None
        self._alist = AddressList()
        self._rlist = ReviewList() #reviewList
        self._currentAddress = None
        if Controller._instance == None:
            Controller._instance = self

    def job( self ):
        return self._job

    def addressList( self ):
        return self._alist

    def loadJob( self, jobid ):
        self.selectAddress(None)
        if type(jobid)== Job:
            jobid = jobid.id()
        self.jobLoading.emit("Loading job "+str(jobid)) 
        job = Job(jobid)
        self._job = job
        self.jobLoading.emit("Relinking to Landonline")
        job.refreshLandonlineLinks()
        self.jobLoading.emit("Loading addresses")
        self._alist.setJob( job )
        self.jobLoading.emit("")
        self.jobLoaded.emit( job )
        
    
    def updateJob( self, job=None ):
        if job == None:
            job = self._job
        elif type(job) == int:
            try:
                job = Job(job)
            except:
                pass
        if not job:
            return
        job.save()
        if not self._job or self._job.id() != job.id():
            return
        self._job.load()
        self.jobUpdated.emit( self._job )

    def updateUpload( self, upload ):
        # Actually there are currently no upload update functions...
        # so just emit the signal
        self.uploadUpdated.emit( upload )


    def _listAddress( self, address ):
        if type(address) == Address: 
            address = address.id()
        if type(address) == ResolutionData:
            address = address.id
        address = self._rlist.addressFromId(address)
        return address

    def address( self, id ):
        return self._listAddress( id )

    def selectAddress( self, address ):
        address = self._listAddress( address )
        if address != self._currentAddress:
            self.currentAddress = address
            self.addressSelected.emit( address )
    
    def updateAddress( self, address ):
        # If the actual address object was supplied then save it.
        # Otherwise treat as notification of change, and reload
        if type(address) == Address:
            address.save()
            # If the address is already in the list, then 
            # reset to that instance of Address
            listadd = self._listAddress( address )
            if listadd:
                address = listadd
        else:
            address = self._listAddress( address )
            if not address:
                return
        # Reload the address
        address.load()
        if address == self._currentAddress and address.deleted():
            self.selectAddress(None)
        self._alist.updateAddress(address)
        self.addressUpdated.emit( address )

    def updateSuppliers( self ):
        self.suppliersUpdated.emit()

    def updateSourceTypes( self ):
        self.sourceTypesUpdated.emit()
 
 # Review Queue related

    
    def loadReviewQueue( self ):
        self._rlist.setReviewItems( )

    def reviewList( self ):
        return self._rlist
    """
    def selectReview( self, address ):
        address = self._listAddress( address )
        if address != self._currentAddress:
            self.currentAddress = address
            self.addressSelected.emit( address )       
    """
    def selectReview( self, address ):
        self.reviewSelected.emit( address )
        
    
    def updateReview( self, address ):
        # If the actual address object was supplied then save it.
        # Otherwise treat as notification of change, and reload
        if type(address) == ResolutionData:
          
            # If the address is already in the list, then 
            # reset to that instance of Address
            listadd = self._listAddress( address )
            if listadd:
                address = listadd
        else:
            address = self._listAddress( address )
            if not address:
                return
        # Reload the address
        address.load()
        if address == self._currentAddress and address.deleted():
            self.selectAddress(None)
        self._rlist.updateReview(address)
        self.reviewUpdated.emit( address )  
        

       
# Use of singleton instance ...


def instance():
    if Controller._instance == None:
        Controller._instance = Controller()
    return Controller._instance

def loadJob( job ):
    instance().loadJob(job)

def onJobLoaded( slot ):
    instance().jobLoaded.connect( slot )

def updateJob( job ):
    instance().updateJob(job)

def onJobUpdated( slot ):
    instance().jobUpdated.connect( slot )

def selectAddress( address ):
    instance().selectAddress( address )

def onAddressSelected( slot ):
    instance().addressSelected.connect( slot )

def updateAddress( id ):
    instance().updateAddress(address)

def onAddressUpdated( slot ):
    instance().addressUpdated.connect( slot )


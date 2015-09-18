import getpass
import datetime

import Database
from Error import Error
from Address import Address
from Supplier import Supplier
from ReaderType import ReaderType


class JobStatus:
    New = 'N'
    Working = 'P'
    Complete = 'C'
    Uploaded = 'U'


class Job( object ):

    @classmethod
    def list( cls, where='' ):
        jobs = []
        sql = 'select job_id, created_by, creation_time, description, source_name, status, n_address, status_string, upl_id, completed_time, n_insert, n_delete from elc_GetJobDetails(NULL)'
        if where:
            sql = sql + ' where ' + where
        sql = sql + ' order by job_id'
        for r in Database.execute(sql):
            createdate = ''
            completedate = ''
            if r[2]: createdate=r[2].strftime('%d-%m-%Y')
            if r[9]: completedate=r[9].strftime('%d-%m-%Y')
            jobs.append(dict(
                job_id=r[0], 
                created_by=r[1], 
                creation_time=r[2], 
                creation_date=createdate,
                description=r[3], 
                source_name=r[4], 
                status=r[5], 
                n_address=r[6], 
                status_string=r[7], 
                upl_id=r[8],
                completed_time=r[9],
                completed_date=completedate,
                n_insert=r[10],
                n_delete=r[11]
                ))
        return jobs

    @classmethod
    def completedJobs(cls):
        return cls.list("status='" + JobStatus.Complete + "'")

    @classmethod
    def CreateJob( cls, sup_id, description, sourcename ):
        user = getpass.getuser()
        jobid = Database.executeScalar( 
            'elc_CreateJob',sup_id,description,sourcename,user
            )
        return Job(jobid)

    def __init__( self, id ):
        self._id = id
        self.load()

    # Returns a list of affected address ids
    def refreshLandonlineLinks( self ):
        return Database.executeScalar('elc_refreshJobLinks',self._id)

    def id( self ): return self._id
    def created_by( self ): return self._created_by
    def description( self ): return self._description
    def notes( self ): return self._notes
    def sourcename( self ): return self._sourcename
    def creation_time( self ): return self._creation_time
    def completed_time( self ): return self._completed_time
    def uploaded_time( self ): return self._uploaded_time
    def status( self ): return self._status
    def setStatus(self,status) : self._status = status
    def supplier(self) : return Supplier(self._sup_id) if self._sup_id else None
    def upl_id( self ): return self._upl_id
    def addToUpload( self, upload ): self._upl_id = upload.id()

    def setCompleted( self ):
        self.setStatus(JobStatus.Complete)

    def __str__(self): return 'Job ' + str(self._id) + ': status ' + str(self._status) + ': ' + str(self._description)

    def load( self ):
        r = Database.executeRow('''
                select 
                    created_by, 
                    description, 
                    notes,
                    source_name, 
                    sup_id, 
                    stp_id, 
                    creation_time, 
                    completed_time, 
                    uploaded_time,
                    status,
                    upl_id
                from 
                    elc_GetJobDetails(%s)
                ''', self._id )
        if not r:
            raise Error("Invalid job id " + str(self._id) + " requested")

        self._created_by = r[0]
        self._description = r[1] or ''
        self._notes = r[2] or ''
        self._source_name = r[3] or ''
        self._sup_id = r[4]
        self._stp_id = r[5]
        self._creation_time = r[6]
        self._completed_time = r[7]
        self._uploaded_time = r[8]
        self._status = r[9] or 'UNKN'
        self._upl_id = r[10]

    def save( self, force=False ):
        try:
            Database.execute('elc_UpdateJob',
               self._id,
               self._description,
               self._notes,
               self._source_name,
               self._upl_id,
               self._status,
               force
               )
            Database.commit()
        finally:
            self.load()

    def _getReader( self ):
        return ReaderType.getReader( self._stp_id )

    def fileext( self ):
        return self._getReader.fileext()

    def loadAddresses( self, filename, overwrite = False ):
        # Is job in a valid state to upload addresses
        if not (self._status == JobStatus.New or
                (self._status != JobStatus.Uploaded and overwrite )):
            raise Error('Addresses already uploaded for job '+str(self._id))

        try:
            # If already uploaded then reset status, which clears out old addresses
            Database.beginTransaction()
            if self._status != JobStatus.New:
                self.setStatus( JobStatus.New )
                self.save(True)

            reader = self._getReader()
            reader.load( filename )
            for ad in reader.addresses():
                Address.createAddress( self, ad, ad.transform() )

            # Identify clusters of co-located addresses
            Database.execute('elc_createAddressClusters', self._id )
            # Link to roads, address points, TAs
            Database.execute('elc_ensureLocationsValid',self._id)
            Database.execute('elc_refreshJobLinks',self._id)

            self.setStatus( JobStatus.Working )
            self.save()
    
            Database.commit()
        except:
            Database.rollback()
            raise

    def createAddressFromLandonlineAddress( self, sad_id, status ):
        adr_id = Address.createFromLandonlineAddress( self, sad_id, status )
        return Address( self, adr_id )

    def createNewAddress (self, job_id, wkt):
        adr_id = Database.executeScalar('elc_CreateAddress', job_id, '', '', '', '', '', wkt, 0)
        return Address( self, adr_id )

    def addresses(self):
        for r in Database.execute('select adr_id from elc_GetJobAddressIds(%s)',self._id ):
            yield Address(self,r[0])

    def addNote( self, note ):
        if self._notes:
            self._notes += "\n\n"
        self._notes += (
            getpass.getuser() + ' ' + 
            datetime.datetime.now().strftime('%d-%b-%Y') + ': ' +
            note
            )

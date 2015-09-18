import re

import Database
from Error import Error

import Reader

class AddressStatus:
    Undefined='UNKN'
    BadRoad='BADR'
    BadGeometry = 'BADG'
    BadNumber='BADN'
    New = 'NEWA'
    Replace='REPL'
    Delete='DELE'
    Ignore='IGNR'
    Merged='MERG'

class SortableAddress(object):

    def __init__( self, number, roadname ):
        self._address = number + ' ' + roadname
        number = number.upper()
        lastnumber = 0
        rest=''
        prefix = number
        match = re.search(r"^(.*?)(\d+)([^\d]*)$",number)
        if match:
            prefix=match.group(1)
            lastnumber = int(match.group(2))
            rest = match.group(3)
        compare = roadname.upper()+' '+'%06d'%(lastnumber,)+rest+' '+prefix
        self._compare = re.sub(r"(\s+)"," ",compare).strip()

    def __str__(self):
        return self._address

    def __cmp__( self, other ):
        return cmp(self._compare,other._compare)

class Address(object):

    @staticmethod
    def createAddress( job, data, transform = True ):
        from Job import Job
        assert isinstance(job,Job)
        assert isinstance(data,Reader.AddressData)
        itransform = 1 if transform else 0
        return Database.executeScalar(
            'elc_CreateAddress',
            job.id(),
            data.id(),
            data.status(),
            data.roadname(),
            data.number(),
            data.comment(),
            data.location(),
            itransform
            )

    @staticmethod
    def createFromLandonlineAddress( job, sad_id, status ):
        from Job import Job
        assert isinstance(job,Job)
        return Database.executeScalar(
            'elc_CreateAddressFromLandonline',
            job.id(),
            sad_id,
            status
            )

    def __init__(self,job,id):
        """Initiallize the adddress, standardising roadname and number"""
        self._job = job
        self._id = id
        self._deleted = False
        self._acceptWarnings = False
        self.load()

    def job( self ): return self._job
    def job_id( self ): return self._job.id()
    def id( self ): return self._id
    def address( self ): return self.housenumber() + ' ' + self.roadname()
    def display( self ): return SortableAddress( self.housenumber(), self.roadname())
    def roadname( self ): return self._roadname if self._roadname else self._src_roadname
    def housenumber( self ): return str(self._housenumber) if self._housenumber else ''
    def range_low( self ): return self._range_low
    def range_high( self ): return self._range_high
    def rna_roadname( self ): return self._roadname
    def src_id( self ): return self._src_id
    def src_address( self ): return self.src_housenumber() + ' ' + self.src_roadname()
    def src_roadname( self ): return self._src_roadname
    def src_housenumber( self ): return self._src_housenumber
    def src_status( self ): return self._src_status
    def src_comment( self ): return self._src_comment
    def sad_address( self ): return self._sad_address
    def sad_offset( self ): return self._sad_offset
    def status( self ): return self._status
    def warning_codes( self ): return self._warning_codes
    def notes( self ): return self._notes or ''
    def rna_id( self ): return self._rna_id
    def rcl_id( self ): return self._rcl_id
    def sad_id( self ): return self._sad_id
    def sad_par_id( self ): return self._sad_par_id
    def par_id( self ): return self._par_id
    def par_sad_count( self ): return self._par_address_count
    def roadIsValid( self ): return bool(self._rna_id)
    def geometryIsValid( self ):
        if self._location == [] or self._location is None or len(self._location) < 2:
            return False 
        else: 
            return True
    def merge_adr_id( self ): return self._merge_adr_id
    def cluster_id( self ): return self._cluster_id
    def ismerged( self ): return self._ismerged
    def deleted( self): return self._deleted

    def setStatus( self, status ): self._status = status
    def setHousenumber( self, housenumber ): self._housenumber = str(housenumber)
    def setNotes( self, notes ): self._notes = str(notes) if notes else ''
    def setSad_id( self, sad_id ): self._sad_id = sad_id
    def setRna_id( self, rna_id ): self._rna_id = rna_id

    def location( self ): return self._location

    def setAcceptWarnings( self, accept=True ): self._acceptWarnings = accept

    def load( self ):
        r = Database.executeRow('''
            select
                job_id,
                roadname,
                housenumber,
                src_id,
                src_roadname,
                src_housenumber,
                sad_roadname,
                sad_housenumber,
                status,
                notes,
                rna_id,
                rcl_id,
                sad_id,
                sad_par_id,
                sad_offset,
                par_id,
                par_sad_count,
                merge_adr_id,
                ismerged,
                warning_codes,
                cluster_id,
                src_status,
                src_comment,
                range_low,
                range_high,
                location
            from
                elc_GetAddressDetails(%s)
            ''',
            self._id)
        if not r:
            self._deleted = True
            return
        if r[0] != self._job.id():
            raise Error("Invalid address id "+str(self._id)+" - does not belong to job " + str(self._job.id()))

        self._roadname = r[1]
        self._housenumber = r[2]
        self._src_id = r[3]
        self._src_roadname = r[4]
        self._src_housenumber = r[5]
        sad_roadname = r[6]
        sad_housenumber = r[7]
        self._status = r[8]
        self._notes = r[9]
        self._rna_id = r[10]
        self._rcl_id = r[11]
        self._sad_id = r[12]
        self._sad_par_id = r[13]
        sad_offset = r[14]
        self._par_id = r[15]
        self._par_sad_count = r[16]
        self._merge_adr_id = r[17]
        self._ismerged = r[18]
        self._warning_codes = r[19]
        self._cluster_id = r[20]
        self._src_status = r[21]
        self._src_comment = r[22]
        self._range_low = r[23]
        self._range_high = r[24]

        # Sort out linked address
        self._sad_address = ''
        self._sad_offset = 0.0
        if self._sad_id:
            self._sad_address = sad_housenumber + ' ' + sad_roadname
            self._sad_offset = round(sad_offset,1)

        # Pull out a number for sorting...
        self._number = 0
        match = re.match(r"\d+",self._housenumber)
        if match:
            self._number = int(match.group(0))

        # Pull out coordinates
        location = []
        if r[25] is not None:
            match = re.match(r"POINT\((\-?\d+\.?\d*)\s+(\-?\d+\.?\d*)\)",r[25])
            if match:
                location = [float(match.group(1)),float(match.group(2))]
        self._location = location

    def save( self ):
        try:
            Database.execute( 'elc_updateAddress',
                         self._id,
                         self._status,
                         self._housenumber,
                         self._sad_id,
                         self._rna_id,
                         self._notes,
                         self._acceptWarnings )
        finally:
            self.load()

    def delete( self ):
        Database.execute( 'elc_deleteAddress', self._id )
        self._deleted = True

    def linkToRoad( self, rna_id ):
        self.setRna_id( rna_id )
        self.save()

    def getNearbyRoads( self, radius ):
        roads = []
        for r in Database.execute( 
            'select rna_id, roadname, distance from elc_getRoadList(%s,%s)',
            self._id, radius
            ):
            roads.append( dict(
                rna_id = r[0],
                roadname = r[1],
                offset = round(r[2],0)
                ))
        return roads

    def getNearbyAddressPoints( self, radius ):
        apts = []
        for r in Database.execute(
            '''
            select 
                sad_id, housenumber, roadname, sameparcel, distance 
            from 
                elc_GetAddressList(%s,%s)
            order by
                distance''',
            self._id, radius 
            ):
            apts.append( dict(
                sad_id = r[0],
                display = SortableAddress( r[1], r[2] ),
                sameparcel = 'Yes' if r[3] else 'No',
                distance = "%.2f" % (r[4],),
                linked = 'Yes' if r[0] == self._sad_id else ''
            ))
        return apts

    def mergedIds( self ):
        idlist = [r[0] for r in 
                Database.execute('select adr_id from elc_MergedAddresses(%s)',self.id())
               ]
        return idlist

    def unmerge( self ):
        if not self.ismerged():
            raise Error("Cannot call Address.unmerge on unmerged address")
        affected = self.mergedIds()
        self.delete()
        return affected

    @classmethod
    def mergeAddresses( cls, addresses, number ):
        if len(addresses) < 2:
            raise Error("Address.mergeAddresses called with less than two addresses")
        adr0 = addresses[0]
        linking = []
        deleting = []
        haslocations = False
        for adr in addresses:
            if (adr.job_id() != adr0.job_id() or
                adr.rna_id() != adr0.rna_id() or
                adr.par_id() != adr0.par_id() ):
                raise Error("Address.mergeAddresses called with inconsistent job, road, or parcel ids")
            if adr.ismerged():
                linking.extend( adr.mergedIds())
                deleting.append(adr)
            else:
                linking.append(adr.id())
            if len(adr._location) > 1:
                haslocations = True

        job = adr0.job()
        if haslocations:
            x = (min(adr._location[0] for adr in addresses) 
                 + max(adr._location[0] for adr in addresses))/2
            y = (min(adr._location[1] for adr in addresses) 
                 + max(adr._location[1] for adr in addresses))/2
            location = "POINT(%.8f %.8f)" % (x,y)
        else:
            location = 'POINT EMPTY'
        
        adata = Reader.AddressData( "merge",adr0.rna_roadname(),number,location)
        try:
            Database.beginTransaction()
            mrgid = Address.createAddress( job, adata, False )
            Database.execute('elc_refreshAddressLinks',mrgid)
            Database.execute('elc_LinkMergedAddress',mrgid,linking)
            for adr in deleting:
                linking.append(adr.id())
                adr.delete()
            Database.commit()
        except:
            Database.rollback()
            raise
        return Address(job,mrgid),linking

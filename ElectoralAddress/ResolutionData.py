from ElectoralAddress.AimsApi import *


class ResolutionData( object ):
    ''' 
    '''
    def __init__(self, href):
        """ ... """
        self.href = href
        self.load(  )
    
    #possibly no longer require the majority of the below functions
    def version(self): return str(self.version)
    def id(self): return  str(self.id) 
    def changeTypeName(self): return  self.changeTypeName
    def submitterUserName (self): return self.submitterUserName 
    def submittedDate (self): return self.submittedDate 
    def getQueueStatusName (self): return self.queueStatusName 
    def sourceReason (self): return self.sourceReason
    def getReviewMessage (self): return self.reviewMessage
    def addressId (self): return self.addressId
    def addressType (self): return  self.addressType 
    def lifecycle (self): return  self.lifecycle   
    def unitType (self): return self.unitType                           
    def unitValue (self): return self.unitValue
    def levelType (self): return self.levelType                                               
    def levelValue (self): return self.levelValue
    def addressNumberPrefix (self): return self.addressNumberPrefix
    def addressNumber (self): return  self.addressNumber 
    def addressNumberSuffix (self): return  self.addressNumberSuffix   
    def addressNumberHigh (self): return self.addressNumberHigh
    def roadCentrelineId (self): return self.roadCentrelineId
    def roadPrefix (self): return self.roadPrefix
    def roadName (self): return  self.roadName
    def roadTypeName (self): return  self.roadTypeName
    def roadSuffix (self): return self.roadSuffix 
    def suburbLocality (self): return  self.suburbLocality
    def townCity (self): return self.townCity
    def objectType (self): return self.objectType 
    def addressPositionType (self): return self.addressPositionType
    def addressPositionCoords(self): return self.addressPositionCoords
    def warning(self): return self.warnings if self.warnings else None
    def info(self): return self.info if self.info else None  
    def displayNum (self):
        if self.addressNumberPrefix:  
            num = [self.addressNumberPrefix+'/', str(self.addressNumber),  +  self.addressNumberSuffix]
        else: 
            num = [str(self.addressNumber), self.addressNumberSuffix]
        return ''.join(filter(None, num)) 
   
    def displayRoad (self):
        road = [self.roadPrefix, self.roadName, self.roadTypeName, self.roadSuffix ]  
        return ' '.join(filter(None, road)) 
    
    def setStatus( self, status ): 
        self.queueStatusName = status 
    
    def setMessage( self, status ): 
        self.reviewMessage = status 
        
        
      
    def load( self ):
        r = loadResolutionItem( self.href )
           
        #Properties
        self.version = str(r.get('properties').get('version'))
        self.id = r.get('properties').get('changeId')
        self.changeTypeName = r.get('properties').get('changeTypeName')
        self.submitterUserName = r.get('properties').get('workflow').get('submitterUserName')
        self.submittedDate = r.get('properties').get('workflow').get('submittedDate')
        self.queueStatusName = r.get('properties').get('workflow').get('queueStatusName')
        self.sourceReason = r.get('properties').get('workflow').get('sourceReason')
        
        #Address Attributes
        self.addressId = r.get('properties').get('components').get('addressId')
        self.addressType = r.get('properties').get('components').get('addressType')     
        self.lifecycle = r.get('properties').get('components').get('lifecycle')   
        self.unitType = r.get('properties').get('components').get('unitType')                                          
        self.unitValue = r.get('properties').get('components').get('unitValue')
        self.levelType = r.get('properties').get('components').get('levelType')                                                 
        self.levelValue = r.get('properties').get('components').get('levelValue')
        self.addressNumberPrefix = r.get('properties').get('components').get('addressNumberPrefix')  
        self.addressNumber = r.get('properties').get('components').get('addressNumber')     
        self.addressNumberSuffix = r.get('properties').get('components').get('addressNumberSuffix')   
        self.addressNumberHigh = r.get('properties').get('components').get('addressNumberHigh')
        self.roadCentrelineId = r.get('properties').get('components').get('roadCentrelineId')
        self.roadPrefix = r.get('properties').get('components').get('roadPrefix')       
        self.roadName = r.get('properties').get('components').get('roadName')
        self.roadTypeName = r.get('properties').get('components').get('roadTypeName')
        self.roadSuffix = r.get('properties').get('components').get('roadSuffix')
        
        self.suburbLocality = r.get('properties').get('components').get('suburbLocality')    
        self.townCity = r.get('properties').get('components').get('townCity')
  
        #AddressableObject Attributes
        self.objectType = r.get('properties').get('addressedObject').get('objectType') #chainning used as this will return None if Key does not exists
        try:
            self.addressPositionType = r.get('properties').get('addressedObject').get('addressPosition').get('type')
        except:  self.addressPositionType = 'NONE'
        try:
            self.addressPositionCoords = r.get('properties').get('addressedObject').get('addressPosition').get('coordinates')
        except: self.addressPositionCoords ='NONE'
        
        #Warnings / Info
        info = []
        warnings = []     
 
        for i in r.get('entities'):   
            if i.get('properties').get('severity') == 'Info':
                info.append(i.get('properties').get('description'))
            elif i.get('properties').get('severity') == 'Warning':
                warnings.append(i.get('properties').get('description')) 
        self.info = '\n'.join( info )+'\n'
        self.warnings = '\n'.join( warnings ) 
                
   
        

      

    
    """

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
                sameparcel = 'Yes' if r[3] else  'No',
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
        """
import sys
import os.path
import re

import osgeo.ogr as ogr
from CodeLookup import CodeLookup
from FieldEvaluator import FieldEvaluator
from Error import Error

import Database


class AddressData( object ):
    """AddressData class - address data retrieved from data source """

    def __init__(self,id,roadname,number,location,status='UNKN',comment='',transform=True):
        """Initiallize the adddress, standardising roadname and number"""
        self._id = id
        self._roadname = self.standardiseName(roadname)
        self._number = self.standardiseNumber(number)
        self._location = self.standardiseLocation(location)
        self._status = status
        self._comment = comment
        self._transform = transform

    def id( self ): return self._id
    def roadname( self ): return self._roadname
    def number( self ): return self._number
    def status( self ): return self._status
    def location( self ): return self._location
    def comment(self): return self._comment
    def transform(self): return self._transform

    def standardiseName( self, name ):
        name = name or ''
        name = name.strip().upper()
        name = re.sub(r"\s+"," ",name)
        return name

    def standardiseNumber( self, number ):
        number = number or ''
        number = number.strip().upper()
        number = re.sub(r"\s+"," ",number)
        return number

    def standardiseLocation( self, location ):
        location = location.upper()
        point = re.match(r"^\s*(?:MULTI)?POINT\s*\(\s*(\-?\d+\.?\d*)\s+(\-?\d+\.?\d*)\s*\)\s*$",location)
        if location == 'POINT EMPTY':
            return location
        elif not point:
            raise Error("Invalid geometry "+location)
        else:
            return "POINT("+point.group(1)+" "+point.group(2)+")"

    def __str__( self ):
        return self._number + ' ' + self._roadname

# Base class for address reader

class Reader( object ):

    @classmethod
    def new( cls, classname, **params ):
        for c in cls.__subclasses__():
            if c.__name__ == classname:
                r = c()
                r.setParameters( **params )
                return r
        raise Error("AddressData reader type " + classname + " is not defined")

    @classmethod
    def params( cls ):
        return []

    def __init__(self):
        self._mapping = CodeLookup()
        self._params = dict()

    # Abstract functions - must be overridden

    def load(self,filename):
        raise Error("Reader.load not defined for " + self.__class__.__name__)

    def reset( self ):
        raise Error("Reader.reset not implemented for ".self.__class__.__name__)

    # nextAddress returns srcid, roadname, roadnumber, location
    def nextAddress( self ):
        raise Error("Reader.nextAddress not implemented for ".self.__class__.__name__)

    # Define parameters to be used by a subclass

    def setParameters( self, **params ):
        assert isinstance(params,dict)
        self._params = params

    def param( self, name, dflt=None ):
        return self._params.get(name,dflt)

    # Define a mapping function to be used by a subclass

    def setMappingSource( self, mapping ):
        """ Define an object used for looking up values

            Object must implement
            def lookup( self, type, key, dflt=None )
        """
        assert isinstance(mapping,CodeLookup)
        self._mapping = mapping

    def lookup( self, type, key, default=None ):
        return self._mapping.lookup(type,key,default)

    # Generator to return addresses

    def addresses( self ):
        while True:
            a = self.nextAddress()
            if a == None:
                break
            assert isinstance(a,AddressData)
            yield a

    # Creation and evaluation of definitions

    def loadDefinition( self, paramname ):
        definition = self.param(paramname,'')
        defn = None
        try:
            defn = FieldEvaluator(definition,self.lookup).evaluator()
        except:
            raise Error('Invalid '+paramname+' field definition "' + definition + '"')
        return defn

    def evaluateDefinition( self, func, definition, dflt='' ):
        " Requires a function(x) returning the value of field x"
        if not definition:
            return dflt
        return definition(func)

class OgrReader ( Reader ):

    @classmethod
    def params( cls ):
        return [
            dict(name='id', description='Field(s) defining the suppliers reference for the address'),
            dict(name='roadname', required=True, description='Field(s) defining the roadname of the address'),
            dict(name='number', required=True, description='Field(s) defining the number of the address'),
            dict(name='status', description='Field(s) holding the supplier status (ie DELE if to be deleted)'),
            dict(name='comment', description='Field(s) holding supplier comments')
        ]

    def __init__( self ):
        Reader.__init__( self )
        self._dataset = None
        self._source = None
        self._roadnamedefn = None
        self._numberdefn = None
        self._iddefn = None
        self._commentdefn = None
        self._nextid = 0

    def load( self, filename ):
        ds = ogr.Open( filename )
        if not ds:
            raise Error("Cannot open OGR source: " + filename)
        self._dataset = ds
        layername = self.param('layername','')
        if layername:
            self._source = self._dataset.GetLayerByName( layername )
            if self._source == None:
                raise Error("Cannot load layer " + layername + " in " + filename)
        else:
            if ds.GetLayerCount() != 1:
                raise Error("Ambiguous layer definition in " + filename)
            self._source = ds.GetLayer(0)
        self.reset()

    def reset(self):
        if self._source:
            self._source.ResetReading()
        self._nextid = 0
        self._roaddefn = self.loadDefinition( "roadname")
        self._numberdefn = self.loadDefinition( "number")
        iddefn = self.param("id","")
        if iddefn:
            self._iddefn = self.loadDefinition( "id")
        else:
            self._iddefn = lambda x: str(self._nextid)

        statusdefn = self.param("status","")
        if statusdefn:
            self._statusdefn = self.loadDefinition( "status")
        else:
            self._statusdefn = lambda x: ''

        commentdefn = self.param("comment","")
        if commentdefn:
            self._commentdefn = self.loadDefinition( "comment")
        else:
            self._commentdefn = lambda x: ''

    def nextAddress( self ):
        if self._source == None:
            return None
        f = self._source.GetNextFeature()
        if not f:
            return

        func = lambda x: f.GetFieldAsString(x) or ''#HACK x[0] if isinstance(x,tuple) else x
        self._nextid += 1
        id = self.evaluateDefinition( func, self._iddefn )  
        roadname = self.evaluateDefinition( func, self._roaddefn )
        number = self.evaluateDefinition( func, self._numberdefn )
        point = f.GetGeometryRef().ExportToWkt()
        status = self.evaluateDefinition( func, self._statusdefn, 'UNKN' )
        comment = self.evaluateDefinition( func, self._commentdefn, '' )
        return AddressData( id, roadname, number, point, status, comment )


class CsvReader ( Reader ):

    @classmethod
    def params( cls ):
        return [
            dict(name='id', description='Field(s) defining the suppliers reference for the address'),
            dict(name='roadname', required=True, description='Field(s) defining the roadname of the address'),
            dict(name='number', required=True, description='Field(s) defining the number of the address'),
            dict(name='east', description='Field(s) defining the easting/longitude of the address'),
            dict(name='north', description='Field(s) defining the northing/latitude of the address'),
            dict(name='parcelID', description='Field(s) defining the id of the parcel associated with the address'),
            dict(name='appellation', description='Field(s) defining the appellation of the parcel associated with the address'),
            dict(name='landdistrict', description='Field(s) defining the land district code for the parcel associated with the address'),
            dict(name='status', description='Field(s) holding the supplier status (ie DELE if to be deleted)'),
            dict(name='comment', description='Field(s) holding supplier comments')
        ]

    def __init__( self ):
        Reader.__init__( self )
        self._dataset = None
        self._source = None
        self._roadnamedefn = None
        self._numberdefn = None
        self._iddefn = None
        self._commentdefn = None
        self._parcelIDdefn = None
        self._appellationdefn = None
        self._landdistrictdefn = None
        self._xdefn = None
        self._ydefn = None
        self._nextid = 0

    def load( self, filename ):
        self._filename = filename
        self.reset()

    def reset(self):
        import csv
        self._ds = None
        self._fields = dict()
        try:
            self._ds=csv.reader(open(self._filename,"rb"))
            for i,name in enumerate(self._ds.next()):
                self._fields[name.lower()] = i
        except:
            raise Error("Cannot open CSV source: " + self._filename)
        self._roaddefn = self.loadDefinition( "roadname")
        self._numberdefn = self.loadDefinition( "number")

        xdefn = self.param("east","") 
        if xdefn:
            self._xdefn = self.loadDefinition("east")
        else:
            self._xdefn = lambda x: ''

        ydefn = self.param("north","") 
        if ydefn:
            self._ydefn = self.loadDefinition("north")
        else:
            self._ydefn = lambda x: ''

        iddefn = self.param("id","")
        if iddefn:
            self._iddefn = self.loadDefinition( "id")
        else:
            self._iddefn = lambda x: str(self._nextid)

        statusdefn = self.param("status","")
        if statusdefn:
            self._statusdefn = self.loadDefinition( "status")
        else:
            self._statusdefn = lambda x: ''

        commentdefn = self.param("comment","")
        if commentdefn:
            self._commentdefn = self.loadDefinition( "comment")
        else:
            self._commentdefn = lambda x: ''

        parcelIDdefn = self.param("parcelID","")
        if parcelIDdefn:
            self._parcelIDdefn = self.loadDefinition("parcelID")
        else:
            self._parcelIDdefn = lambda x: ''

        appellationdefn = self.param("appellation","")
        if appellationdefn:
            self._appellationdefn = self.loadDefinition("appellation")
        else:
            self._appellationdefn = lambda x: ''

        landdistrictdefn = self.param("landdistrict","")
        if landdistrictdefn:
            self._landdistrictdefn = self.loadDefinition("landdistrict")
        else:
            self._landdistrictdefn = lambda x: ''

    def getField( self, field ):
        result = ''
        if field.lower() in self._fields:
            index = self._fields[field.lower()]
            if index < len( self._record ):
                result = self._record[index]
        return result

    def nextAddress( self ):
        if self._ds == None:
            return None
        while True:
            self._record = self._ds.next()
            if self._record == None:
                return
            if self._record:
                break
        func = self.getField
        self._nextid += 1
        id = self.evaluateDefinition( func, self._iddefn )
        roadname = self.evaluateDefinition( func, self._roaddefn )
        number = self.evaluateDefinition( func, self._numberdefn )
        status = self.evaluateDefinition( func, self._statusdefn, 'UNKN' )
        comment = self.evaluateDefinition( func, self._commentdefn, '' )
        parcelID = self.evaluateDefinition( func, self._parcelIDdefn, '' )
        appellation = self.evaluateDefinition( func, self._appellationdefn, '' )
        landdistrict = self.evaluateDefinition( func, self._landdistrictdefn, '' )
        x = self.evaluateDefinition( func, self._xdefn )
        y = self.evaluateDefinition( func, self._ydefn )
        transform = True
        
        point = ''
        # Geocode from coordinates
        if x != '' and y != '': 
            x=float(x)
            y=float(y)
            point = 'POINT(%f %f)' % (x,y)
        # Geocode from parcel ID
        if (point.upper() == 'NONE' or point == '') and parcelID is not None and parcelID.strip().isdigit():
            pid = int(parcelID.strip())
            point = str(Database.executeScalar('elc_findparcelpoint', pid))
        # Geocode from appellation
        if (point.upper() == 'NONE' or point == '') and appellation != '' and appellation is not None:
            if landdistrict is not None and landdistrict.strip().isdigit():
                pid = Database.executeScalar('elc_findparcelid', appellation.strip(), int(landdistrict.strip()))
            else:
                pid = Database.executeScalar('elc_findparcelid', appellation.strip(), None)
        if pid is not None:
                point = str(Database.executeScalar('elc_findparcelpoint', pid))
                transform = False
        # Otherwise leave empty 
        if point.upper() == 'NONE' or point == '':
            point = 'POINT EMPTY'

        return AddressData( id, roadname, number, point, status, comment, transform )


if __name__=="__main__":
    if len(sys.argv) < 3:
        print "Need params: (ogr|csv) data_file [params]"
        sys.exit()

    rtype = 'CsvReader' if sys.argv[1]=='csv' else 'OgrReader'
    dfile = sys.argv[2]
    if not os.path.exists(dfile):
        print "File",dfile,"doesn''t exist..."
        sys.exit()
    params={}
    if len(sys.argv) > 3 and sys.argv[3]:
        prmstr = sys.argv[3]
        prms = prmstr[1:].split(prmstr[0])
        for i in range(0,len(prms)-1,2):
            params[prms[i]] = prms[i+1]
    reader = Reader.new(rtype,**params)
    reader.load(dfile)
    for address in reader.addresses():
        print address,' location: ',address.location()

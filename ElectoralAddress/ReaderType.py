import os.path

import Database
from Reader import Reader
from CodeLookup import CodeLookup

class ReaderType( object ):

    _types = dict()
    _loaded = False

    @classmethod
    def loadTypes( cls ):
        if cls._loaded: 
            return
        cls._types.clear()
        c = Database.execute('select stp_id,name,fileext,srsid,reader_type,reader_params from elc_GetSourceTypeDetail(NULL)')
        for r in c:
            rtype = ReaderType( *r )
            id = rtype.id()
            cls._types[id] = rtype
        cls._loaded = True

    @classmethod
    def reload( cls ):
        cls._loaded = False

    @classmethod
    def list( cls ):
        cls.loadTypes()
        list=[]
        for stype in cls._types.itervalues():
            list.append(dict(
                id=stype.id(),
                name=stype.name(),
                srs_id=stype.srsid(),
                file_ext = stype.fileext(),
                readerclass = stype.type(),
                sourcetype = stype,
                params=stype.params()
                ))
        return list

    @classmethod
    def types( cls ):
        cls.loadTypes()
        for k,v in cls._types.iteritems():
            yield v

    @classmethod
    def getType( cls, id):
        cls.loadTypes()
        return cls._types[id]

    @classmethod
    def getReader( cls, id, mapping=None ):
        cls.loadTypes()
        return cls._types[id].reader(mapping)

    @classmethod
    def encodeParams( cls, params ):
        delim = None
        for c in ":;~@#$!%^&*":
            ok = True
            for p in params:
                if c in p['name']: ok=False
                if c in p['value']: ok=False
                if not ok:
                    break
            if ok:
                delim = c
                break
        if not delim:
            raise Error("Cannot find delimiter for parameter name/value pairs")
        prmstr = delim + delim.join((p['name']+delim+p['value'] for p in params))
        return prmstr

    @classmethod
    def decodeParams( cls, prmstr ):
        params = []
        if prmstr:
            prms = prmstr[1:].split(prmstr[0])
            for i in range(0,len(prms)-1,2):
                params.append(dict(name=prms[i],value=prms[i+1]))
        return params

    def __init__(self,id,name,fileext,srsid,type,prmstr):
        self._id = id
        self._name = name
        self._fileext = fileext
        self._srsid = srsid
        self._type = type
        self._params = ReaderType.decodeParams( prmstr )

    def id(self): return self._id
    def name(self): return self._name
    def fileext(self): return self._fileext
    def srsid(self): return self._srsid
    def type(self): return self._type
    def params(self): return self._params

    def reader( self, mapping=None ):

        prm = dict()
        for p in self._params:
            prm[p['name']] = p['value']
        reader = Reader.new( self.type(), **prm ) 
        if reader:
            if not mapping:
                mapping = CodeLookup()
            reader.setMappingSource(mapping)
        return reader

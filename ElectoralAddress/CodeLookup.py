
import Database


class CodeLookup( object ):

    _mapping = dict()
    _fileload = False

    def __init__( self ):
        pass

    @classmethod
    def loadFile( cls, filename ):
        cls._fileload = True
        f = open(filename,"r")
        mapping = cls._mapping
        for line in f:
            line = line.strip()
            parts = line.split('|')
            if len(parts) == 3:
                type = parts[0].upper()
                key = parts[1].upper()
                value = parts[2]
                if not type in mapping:
                    mapping[type] = dict()
                mapping[type][key] = value
        f.close()

    @classmethod
    def loadTypeFromDb( cls, type ):
        mapping = dict()
        c = Database.execute("select code,value from elc_GetCodeList(%s)",type)
        if c:
            for r in c:
                mapping[r[0].upper()] = r[1]
        cls._mapping[type.upper()] = mapping

    @classmethod
    def lookup( cls, type, key, dflt=None ):
        type = type.upper()
        key = key.upper()
        if type not in cls._mapping and not cls._fileload:
            cls.loadTypeFromDb( type )
        if type in cls._mapping and key in cls._mapping[type]:
            return cls._mapping[type][key]
        return dflt

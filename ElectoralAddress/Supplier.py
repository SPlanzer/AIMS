

import Database
from Error import Error
from ReaderType import ReaderType

class Supplier( object ):

    @classmethod
    def list( cls ):
        suppliers = []
        for r in Database.execute('select sup_id, stp_id, stt_id, name from elc_GetSupplier(NULL)'):
            suppliers.append(dict(
                id=r[0],
                stp_id=r[1],
                stt_id=r[2],
                name=r[3]
                ))
        return suppliers

    def __init__( self, id ):
        self._id = id
        stp_id, stt_id, name = Database.executeRow('select stp_id, stt_id, name from elc_GetSupplier(%s)', id )
        self._stp_id = stp_id
        self._stt_id = stt_id
        self._name = name

    def id(self): return self._id
    def name(self): return self._name
    def readerType( self ): return ReaderType.getType( self._stp_id )
    def stp_id( self ): return self._stp_id
    def stt_id( self ): return self._stt_id

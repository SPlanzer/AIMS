
# Configuration settings for electoral address GUI

from PyQt4.QtCore import *
import ElectoralAddress.Database as Database


organisationName='Land Information New Zealand'
applicationName='Electoral Address Loader'
_settings=None

def settings():
    global _settings
    if not _settings:
        _settings = QSettings( organisationName, applicationName )
    return _settings

def set( item, value ):
    settings().setValue(item,value)

def get( item, default='' ):
    value = str(settings().value(item,default)) 
    return value


def configureDatabase(dbmodule=Database):
    dbmodule.setHost( str(get('Database/host',dbmodule.host())))
    dbmodule.setPort( str(get('Database/port',dbmodule.port())))
    dbmodule.setDatabase( str(get('Database/database',dbmodule.database())))
    dbmodule.setUser( str(get('Database/user',dbmodule.user())))
    dbmodule.setPassword( str(get('Database/password',dbmodule.password())))
    dbmodule.setBdeSchema( str(get('Database/bdeSchema',dbmodule.bdeSchema())))
    dbmodule.setAddressSchema( str(get('Database/addressSchema',dbmodule.addressSchema())))

def setDatabaseConfiguration( host=None, port=None, database=None, user=None, password=None, bdeSchema=None, addressSchema=None, dbmodule=Database ):
    if not host: host = dbmodule.host()
    if not port: host = dbmodule.port()
    if not database: database = dbmodule.database()
    if not user: user = dbmodule.user()
    if not password: password = dbmodule.password()
    if not addressSchema: addressSchema = dbmodule.addressSchema()
    if not bdeSchema: bdeSchema = dbmodule.bdeSchema()
    set('Database/host',host)
    set('Database/port',port)
    set('Database/database',database)
    set('Database/user',user)
    set('Database/password',password)
    set('Database/addressSchema',addressSchema)
    set('Database/bdeSchema',bdeSchema)
    configureDatabase(dbmodule)

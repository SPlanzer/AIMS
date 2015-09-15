
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class IntComboBox( QComboBox ):

    def __init__( self, parent=None ):
        QComboBox.__init__(self,parent)

    def addNameValue( self, name, value ):
        assert( type(value) == int )
        self.addItem( name, value )

    def selectValue( self, value ):
        if value == None:
            return
        assert( type(value) == int )
        self.setCurrentIndex(self.findData( value ))
       
    def selectedValue( self ):
        value = self.itemData(int(self.currentIndex()))
        if value == -1:
            return None        
        return value 
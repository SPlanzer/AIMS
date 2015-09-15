import getpass

import __init__
import Config
from ElectoralAddress import Database

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_ConfigureDatabase import Ui_ConfigureDatabase

warnOnClose = True

class ConfigureDatabase( QDialog, Ui_ConfigureDatabase ):

    def __init__( self, parent=None ):
        QDialog.__init__( self, parent )
        self.setupUi( self )
        self.uHost.setText( Database.host() )
        self.uPort.setText( Database.port() )
        self.uDatabase.setText( Database.database() )
        self.uUser.setText( Database.user() )
        self.uPassword.setText( Database.password() )
        self.uBdeSchema.setText( Database.bdeSchema() )
        self.uAddressSchema.setText( Database.addressSchema() )
        self.uDialogButtons.clicked.connect( self.buttonClicked )

    def buttonClicked( self, button ):
        box = self.uDialogButtons
        if button == box.button(box.RestoreDefaults):
            self.setDefault()
        elif button == box.button(box.Save):
            self.save()
            self.close()
        elif button == box.button(box.Close):
            self.close()

    def save( self ):
        if warnOnClose:
            result = QMessageBox.question(self,
                "Close application",
                "The application must be closed to reconfigure the database.  Do you want to proceed?",
                QMessageBox.Yes | QMessageBox.No)
            if result != QMessageBox.Yes:
                return
        Config.setDatabaseConfiguration( 
            str(self.uHost.text()),
            str(self.uPort.text()),
            str(self.uDatabase.text()),
            str(self.uUser.text()),
            str(self.uPassword.text()),
            str(self.uBdeSchema.text()),
            str(self.uAddressSchema.text()))
        QApplication.instance().closeAllWindows()

    def setDefault( self ):
        self.uHost.setText( 'prdgeo01' )
        self.uPort.setText( '5432' )
        self.uDatabase.setText( 'spi_db' )
        self.uUser.setText( getpass.getuser() )
        self.uPassword.setText( '' )
        self.uBdeSchema.setText( 'bde' )
        self.uAddressSchema.setText( 'electoral_address' )

if __name__ == '__main__':
    import sys
    warnOnClose = False
    app = QApplication(sys.argv)
    main = ConfigureDatabase()
    main.show()
    app.exec_()



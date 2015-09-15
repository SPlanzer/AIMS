
import sys
import os.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_MergeAddressDialog import Ui_MergeAddressDialog
import Controller

class MergeAddressDialog( Ui_MergeAddressDialog, QDialog ):
    
    @classmethod
    def mergeAddresses( cls, parent=None, controller=None, address=None ):
        dlg = MergeAddressDialog( parent, controller )
        dlg.setAddress(address)
        dlg.exec_()
        return dlg.currentAddress()

    def __init__( self, parent=None, controller=None ):
        QDialog.__init__( self, parent )
        self.setupUi(self)
        self.setController( controller )

    def setController( self, controller ):
        self.uMergeWidget.setController( controller )
        self.uUnmergeWidget.setController( controller )

    def setAddress( self, address ): 
        self.uMergeWidget.setAddress( address )
        self.uUnmergeWidget.setAddress( address )
        if address and address.ismerged():
            self.uTabManager.setCurrentWidget( self.uUnmergeWidget )
        else:
            self.uTabManager.setCurrentWidget( self.uMergeWidget )

    def currentAddress( self ):
        address = self.uTabManager.currentWidget().currentAddress()
        if not address:
            address=self.uTabManager.widget(0).currentAddress()
        if not address:
            address=self.uTabManager.widget(1).currentAddress()
        return address

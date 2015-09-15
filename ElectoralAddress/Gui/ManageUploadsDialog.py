
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_ManageUploadsDialog import Ui_ManageUploadsDialog

class ManageUploadsDialog( QDialog, Ui_ManageUploadsDialog ):

    @classmethod
    def run( cls, parent=None, controller=None ):
        dlg = ManageUploadsDialog( parent, controller )
        dlg.exec_()

    def __init__( self, parent=None, controller=None ):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        self.setController(controller)

    def setController( self, controller ):
        self.uReviewUploadTab.setController( controller )
        self.uCreateUploadTab.setController( controller )

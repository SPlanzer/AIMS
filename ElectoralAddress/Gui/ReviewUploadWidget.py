
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ElectoralAddress.Upload import Upload
from Ui_ReviewUploadWidget import Ui_ReviewUploadWidget
from DictionaryList import DictionaryListModel
from Utility import attempt

import Controller
import Config

class ReviewUploadWidget( QWidget, Ui_ReviewUploadWidget ):

    def __init__( self, parent=None, controller=None ):
        QWidget.__init__( self, parent )
        self.setupUi(self)
        self._uploadModel = DictionaryListModel(None,
            ['upl_id','created_by','created_date','filename','n_insert','n_delete'],
            ['Id','Created by','Date','Filename','Inserted','Deleted']
            )
        self.uUploadView.setModel( self._uploadModel )
        self.uUploadView.rowSelectionChanged.connect( self.enableButtons )
        self.uCreateSql.clicked.connect( self.createSqlFile )
        self.uDelete.clicked.connect( self.deleteUpload )
        self.uDiscard.clicked.connect( self.discardUpload )
        # Functions not yet enabled...
        self.uDelete.hide()
        self.uDiscard.hide()

        self.setController( controller )
        self.load()

    def setController( self, controller ):
        if controller == None:
            controller = Controller.instance()
        self._controller = controller
        self._controller.uploadUpdated.connect( self.load2 )

    def load2( self, upload ):
        self.load()

    def load( self ):
        self._uploadModel.setList(Upload.list())

    def enableButtons( self ):
        selected = self.uUploadView.selectedRow() != None
        self.uCreateSql.setEnabled( selected )
        self.uDelete.setEnabled( selected )
        self.uDiscard.setEnabled( selected )

    @attempt
    def createSqlFile( self,clicked ):
        item = self.uUploadView.selectedItem()
        if not item:
            return
        upl_id = int(item['upl_id'])
        if not upl_id:
            return
        upload = Upload(upl_id)
        setting = '/Upload/FilePath'
        startDir = Config.get(setting)
        filterstr = "SQL files (*.sql);; All files (*.*)"
        filename = upload.filename()
        if not filename:
            filename = upload.defaultFilename()
        dlg = QFileDialog(self,"Select SQL file",startDir,filterstr)
        dlg.selectFile( filename )
        dlg.setConfirmOverwrite(True)
        if dlg.exec_() == QDialog.Accepted and len(dlg.selectedFiles()) == 1:
            filename = dlg.selectedFiles()[0]
            upload.writeSql(str(filename))

            QMessageBox.information(self,"Address upload created","SQL for the upload has been written to\n"+filename)

    @attempt
    def deleteUpload(self,clicked):
        raise RuntimeError("Delete upload not yet implemented")

    @attempt
    def discardUpload(self,clicked):
        raise RuntimeError("Discard upload not yet implemented")

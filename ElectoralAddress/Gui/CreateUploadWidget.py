
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ElectoralAddress.Upload import Upload
from ElectoralAddress.Job import Job

from Ui_CreateUploadWidget import Ui_CreateUploadWidget
from DictionaryList import DictionaryListModel

import Controller
import Config

class CreateUploadWidget( QWidget, Ui_CreateUploadWidget ):

    def __init__( self, parent=None, controller=None ):
        QWidget.__init__( self, parent )
        self.setupUi(self)
        self._jobsModel = DictionaryListModel(None,
            ['job_id','description','created_by','completed_date','n_insert','n_delete'],
            ['Id','Description','Created by','Completed','No insertions','No deletions']
            )
        self.uJobsView.setModel( self._jobsModel )
        self.uJobsView.setSelectionMode( QAbstractItemView.ExtendedSelection )
        self.uJobsView.rowSelectionChanged.connect( self.enableButtons )
        self.uSqlFile.textChanged.connect( self.enableButtons2 )
        self.uBrowseSqlFile.clicked.connect( self.browseSqlFile )
        self.uCreateUpload.clicked.connect( self.createUpload )
        self.setController( controller )
        self.load()

    def setController( self, controller ):
        if controller == None:
            controller = Controller.instance()
        self._controller = controller
        self._controller.jobLoaded.connect( self.reloadJobs )
        self._controller.jobUpdated.connect( self.reloadJobs )

    def load( self ):
        self.reloadJobs()
        self.uSqlFile.setText('')

    def reloadJobs( self, job=None ):
        self._jobsModel.setList(Job.completedJobs())

    def enableButtons( self ):
        haveRows = len(self.uJobsView.selectedRows()) > 0
        haveFilename = self.uSqlFile.text() != ''
        self.uBrowseSqlFile.setEnabled( haveRows )
        self.uCreateUpload.setEnabled( haveRows and haveFilename )

    def enableButtons2( self,filename ):
        self.enableButtons()

    def browseSqlFile( self ):
        setting = '/Upload/FilePath'
        startDir = Config.get(setting)
        filterstr = "SQL files (*.sql);; All files (*.*)"
        filename = self.uSqlFile.text()
        if filename == '':
            filename = Upload.defaultNewFilename()
        dlg = QFileDialog(self,"Select SQL file",startDir,filterstr)
        dlg.selectFile( filename )
        dlg.setConfirmOverwrite(True)
        if dlg.exec_() == QDialog.Accepted and len(dlg.selectedFiles()) == 1:
            filename = dlg.selectedFiles()[0]
            self.uSqlFile.setText(filename)
            Config.set(setting, QFileInfo(filename).absolutePath())

    def createUpload( self ):
        filename = str(self.uSqlFile.text())
        upload = Upload.CreateUpload(filename)
        for r in self.uJobsView.selectedItems():
            id = r['job_id']
            upload.addJob(id)
            self._controller.updateJob(id)
        filename = str(self.uSqlFile.text())
        upload.writeSql(filename)
        QMessageBox.information(self,"Address upload created","SQL for the upload has been written to\n"+filename)
        self._controller.updateUpload( upload )
        self.load()



import sys
import os.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_JobSelectorDialog import Ui_JobSelectorDialog

from ElectoralAddress.Job import Job
from ElectoralAddress.Error import Error
from NewJobDialog import NewJobDialog
from DictionaryList import DictionaryListModel

class JobTableModel (DictionaryListModel):

    def __init__( self ):
        DictionaryListModel.__init__(self)

        jobs = Job.list()
        for job in jobs:
            job['creation_date'] = job['creation_time'].strftime('%d-%b-%Y')

        columns = [
            'job_id',
            'created_by',
            'creation_date',
            'status_string',
            'n_address',
            'description'
            ]
        headers = [
            'Id',
            'Created by',
            'Created date',
            'Status',
            'Count',
            'Description'
            ]
        self.setList( jobs, columns, headers )

    def getJob( self, index ):
        jobdef = self.listItem(index)
        if jobdef:
            return Job(jobdef['job_id'])
        return None

class JobSelectorDialog( Ui_JobSelectorDialog, QDialog ):
    
    @classmethod
    def getJob( cls, parent=None ):
        dlg = JobSelectorDialog( parent )
        result = dlg.exec_()
        job = None
        if result == QDialog.Accepted:
            job = dlg.job()
        return job

    def __init__( self, parent=None ):
        QDialog.__init__( self, parent )
        self._job = None
        self._model = JobTableModel()
        self.setupUi(self)
        self._initDialog()
        QObject.connect( self.uNewJobButton,SIGNAL("clicked()"),self._createNewJob)
        self.uJobTable.rowDoubleClicked.connect( self._rowDoubleClicked )

    def job( self ): return self._job

    def _initDialog( self ):
        self.uJobTable.setModel( self._model )
        self.uJobTable.resizeColumnsToContents()

    def _createNewJob( self ):
        self._job = NewJobDialog.getJob()
        if self._job:
            QDialog.accept(self)

    def _rowDoubleClicked( self, row ):
        self.accept()

    def accept( self ):
        row = self.uJobTable.selectedItem()
        if row == None:
            QMessageBox.warning(self,"No job selected","You have not selected a job to work on")
            return
        try:
            try:
                self.setCursor( Qt.WaitCursor )
                self._job = Job( row['job_id'] )
            finally:
                self.setCursor( Qt.ArrowCursor )
            if( self._job ):
                QDialog.accept(self)
            else:
                raise Error("Unable to load job")
        except:
            msg = str(sys.exc_info()[1])
            QMessageBox.warning(self,"Error loading job",msg)



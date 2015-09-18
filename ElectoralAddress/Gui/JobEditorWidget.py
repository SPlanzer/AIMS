from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_JobEditorWidget import Ui_JobEditorWidget

from Utility import attempt

from ElectoralAddress.CodeLookup import CodeLookup
from ElectoralAddress.Job import JobStatus

import Controller
import Config

class JobEditorWidget( Ui_JobEditorWidget, QWidget ):

    lastJobSetting = '/History/LastJobId'
    
    def __init__( self, parent=None, controller=None ):
        QWidget.__init__( self, parent )
        self._controller = None
        self.setupUi(self)
        self.uSetCompleted.clicked.connect( self.completeJob )
        self.uAddNoteButton.clicked.connect( self.addNote )
        self.setController( controller )

    def setController( self, controller ):
        if not controller:
            controller = Controller.instance()
        if controller == self._controller:
            return
        if self._controller:
            self._controller.jobLoaded.disconnect( self.loadJob )
            self._controller.jobUpdated.disconnect( self.loadJob )
        self._controller = controller
        self._controller.jobLoaded.connect( self.loadJob )
        self._controller.jobUpdated.connect( self.loadJob )

    def job( self ): return self._controller.job()

    # Job details tab:

    def loadJob( self, job ):
        # If this is not the controllers main job then don't do anything
        if job != self.job():
            return
        if job:
            createdate = job.creation_time().strftime('%d-%b-%Y')
            createdate += ' by ' + job.created_by()
            self.uCreationLabel.setText(createdate)
            self.uSupplierLabel.setText(job.supplier().name())
            self.uStatusLabel.setText( CodeLookup.lookup('job_status',job.status()))
            self.uDescription.setText(job.description())
            self.uNotes.setPlainText(job.notes())
            self.uNotes.setPlainText(job.notes())
            self.uSetCompleted.setEnabled(job.status() == JobStatus.Working)
        else:
            self.uCreationLabel.setText('')
            self.uSupplierLabel.setText('')
            self.uStatusLabel.setText('')
            self.uDescription.setText('')
            self.uNotes.setPlainText('')
            self.uSetCompleted.setEnabled(False)

    @attempt
    def addNote( self, click ):
        job = self.job()
        if not job:
            return
        note = str(self.uNewNote.document().toPlainText()).strip()
        if not note:
            return
        job.addNote(note)
        self.uNotes.setPlainText(job.notes())
        self.uNewNote.setPlainText('')
        self._controller.updateJob(job)

    @attempt
    def completeJob( self, click ):
        job = self.job()
        job.setCompleted()
        job.addNote('Job completed')
        self._controller.updateJob(job)

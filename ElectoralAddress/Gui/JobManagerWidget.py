import os.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_JobManagerWidget import Ui_JobManagerWidget

from JobSelectorDialog import JobSelectorDialog
from NewJobDialog import NewJobDialog

from AdminDialog import AdminDialog

from ElectoralAddress.CodeLookup import CodeLookup
from ElectoralAddress.Job import Job
from ElectoralAddress.Job import JobStatus

import Controller
import Config

class JobManagerWidget( Ui_JobManagerWidget, QWidget ):

    lastJobSetting = '/History/LastJobId'
    
    def __init__( self, parent=None, controller=None, jobid=None ):
        QWidget.__init__( self, parent )
        self.setupUi(self)
        self._controller = None
        self._helpfile = None
        self.setHelpFile(self.defaultHelpFile())

        self.uNewJob.clicked.connect( self.newJob )
        self.uSelectJob.clicked.connect( self.selectJob )
        self.uSysAdmin.clicked.connect( self.runAdminDialog )
        self.uHelp.clicked.connect( self.showHelp )
        self.uTabManager.setCurrentWidget(self.uJobSummaryTab)
        self.setController( controller )

        if jobid:
            try:
                self._controller.loadJob(jobid)
            except:
                pass

    def job( self ): return self._controller.job()

    def setController( self, controller ):
        if not controller:
            controller = Controller.instance()
        if controller == self._controller:
            return
        if self._controller:
            self._controller.jobLoading.disconnect( self.showMessage )
        self._controller = controller
        self._controller.jobLoading.connect( self.showMessage )
        self.uJobSummaryTab.setController(self._controller)
        self.uAddressesTab.setController(self._controller)
        
    def defaultHelpFile( self ):
        from os.path import dirname, abspath, join
        return join(dirname(abspath(__file__)),'help','index.html')

    def setHelpFile( self, file ):
        if file and os.path.exists(file):
            self._helpfile = file
            self.uHelp.show()
        else:
            self._helpfile = None
            self.uhelp.hide()

    def showHelp( self ):
        url = QUrl.fromLocalFile( self._helpfile )
        QDesktopServices.openUrl( url )

    def loadJob( self, job ):
        cursor = self.cursor()
        try:
            self._controller.loadJob( job )
            if self.job():
                Config.set(self.lastJobSetting,self.job().id())
        finally:
            self.setCursor(cursor)

    def showMessage( self, message ):
        self.uMessageLabel.setText(message)
        self.uMessageLabel.repaint()

    def addAddressAction( self, name, action, whatsthis='' ):
        self.uAddressesTab.addAddressAction( name, action, whatsthis )
    # Job details tab:

    def newJob( self ):
        job = NewJobDialog.getJob(self)
        if job:
            self.loadJob( job )

    def selectJob( self ):
        job = JobSelectorDialog.getJob()
        if job:
            self.loadJob( job )

    def runAdminDialog( self ):
        AdminDialog.run(self, self._controller )

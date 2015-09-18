import sys
import os.path

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from Ui_NewJobDialog import Ui_NewJobDialog

from ElectoralAddress.Supplier import Supplier
from ElectoralAddress.Job import Job
from Utility import attempt

import Config

class NewJobDialog( Ui_NewJobDialog, QDialog ):

    @classmethod
    def getJob( cls, parent=None ):
        dlg = NewJobDialog( parent )
        result = dlg.exec_()
        job = None
        if result == QDialog.Accepted:
            job = dlg.job()
        return job

    def __init__( self, parent=None ):
        QDialog.__init__( self, parent )
        self.setupUi(self)
        self._initDialog()
        self._job = None
        QObject.connect( self.uBrowseSource,SIGNAL("clicked()"),self._selectSource)

    def job( self ): return self._job

    def _initDialog( self ):
        for s in Supplier.list():
            self.uSupplierSelector.addNameValue( s['name'], s['id'])

    def _selectSource( self ):
        sup_id = self.uSupplierSelector.selectedValue()
        if sup_id == None:
            QMessageBox.warning(self,"Missing supplier","You must select a supplier")
            return
        supplier = Supplier(sup_id)
        setting = '/Suppliers/Supplier_' + str(supplier.id()) + "/SourcePath"
        startDir = Config.get(setting)
        ext = supplier.readerType().fileext()
        name = supplier.readerType().name()
        filterstr = name + " (*." + ext + ");; All files (*.*)"

        s = QSettings()
        filename = QFileDialog.getOpenFileName(self,"Address data file",
                    startDir,filterstr)
        if filename:
            Config.set(setting,QFileInfo(filename).absolutePath())
            self.uSourceFile.setText(filename)

    @attempt(title="Error loading job!")
    def accept( self ):
        sup_id = self.uSupplierSelector.selectedValue()
        if sup_id == None:
            QMessageBox.warning(self,"Missing supplier","You must select a supplier")

        filename = str(self.uSourceFile.text())
        if not filename or not os.path.exists(filename):
            QMessageBox.warning(self,"Invalid file","File " + filename + " does not exist")
            return
        description = str(self.uDescription.toPlainText()).strip()
        if not description:
            QMessageBox.warning(self,"Missing description","You must supply a brief description of the job")
            return

        try:
            self.uStatusLabel.setText("Loading job ...")
            self.uStatusLabel.repaint()
            self.setCursor(Qt.WaitCursor)
            job = Job.CreateJob( sup_id, description, filename )
            job.loadAddresses( filename )
            self.uStatusLabel.setText("")
            self.setCursor(Qt.ArrowCursor)
            self._job = job
            QDialog.accept(self)
        finally:
            self.uStatusLabel.setText("")
            self.setCursor(Qt.ArrowCursor)

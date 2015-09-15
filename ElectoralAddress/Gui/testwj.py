import __init__
import sys
import Config
Config.configureDatabase()

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ElectoralAddress.Gui.AddressLinkingWidget import AddressLinkingWidget
from ElectoralAddress.Gui.AddressLinkingWidget import AddressLinkingWidget
from ElectoralAddress.Gui.JobEditorWidget import JobEditorWidget
from ElectoralAddress.Gui.JobManagerWidget import JobManagerWidget
from ElectoralAddress.Gui.MergeAddressDialog import MergeAddressDialog
from ElectoralAddress.Job import Job
from ElectoralAddress.Gui.AddressList import AddressList
from Controller import Controller

job = Job(4)
alist = AddressList()
controller = Controller()

app = QApplication(sys.argv)
#main = QMainWindow()
editor = MergeAddressDialog()
print "Created.."
editor.setController( controller )
print "Setting controller.."
controller.loadJob(job)
print "Job loaded"
#main.setCentralWidget(editor)
#main.show()
editor.show()
print "Running.."
app.exec_()



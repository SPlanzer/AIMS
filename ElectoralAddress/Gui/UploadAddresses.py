import sys
import __init__

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from JobManagerWidget import JobManagerWidget
from Controller import Controller


app = QApplication(sys.argv)
main = QMainWindow()
controller = Controller()
editor = JobManagerWidget(controller=controller)
main.setCentralWidget(editor)
main.show()
app.exec_()

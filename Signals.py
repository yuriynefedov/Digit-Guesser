#QtSignal Class to simplify using Signals anywhere

from PyQt5 import QtCore

class Signals(QtCore.QObject):
    
    ticked = QtCore.pyqtSignal()
    unticked = QtCore.pyqtSignal()

    close_app = QtCore.pyqtSignal()
    
    clicked = QtCore.pyqtSignal()
    pressed = QtCore.pyqtSignal()

    update = QtCore.pyqtSignal()

    touched = QtCore.pyqtSignal()

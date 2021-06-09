""" Returns resolution of the screen """

from PyQt5 import QtWidgets

class ScreenGetter(QtWidgets.QWidget):
        def __init__(self):
                QtWidgets.QWidget.__init__(self)
        def screenres(self):
                app = QtWidgets.QApplication.desktop()
                screen_resolution = app.screenGeometry()
                width, height = screen_resolution.width(), screen_resolution.height()
                return tuple((width,height))

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ex = ScreenGetter()
    print(ex.screenres())

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
from ScreenRes import ScreenGetter
from net import MachineLearning

import datetime, random, numpy

class Pixel(QLabel):
    def __init__(self, parent = None):
        QLabel.__init__(self)
        self.setParent(parent)
        self.parent = parent
        self.resize(14,14)
        self.setStyleSheet('background-color:rgb(255,255,255)')
        self.state = 0
        self.tcounter = 0

class PaintingZone(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self)
        self.setParent(parent)
        self.resize(392,392)
        self.testlbl = QLabel('', self)
        self.testlbl.resize(self.size())
        self.setStyleSheet('background-color:rgb(255,255,255);')
        
        self.initPixels()

        parent.clearbtn.clicked.connect(self.clear)

    def clear(self):
        for row in self.pixlist:
            for pixel in row:
                pixel.setStyleSheet('background-color:rgb(255,255,255)')
                pixel.state = 0

    def initPixels(self):
        self.pixlist = []
        for row in range(28):
            self.pixlist.insert(row, [])
            for column in range(28):
                pixel = Pixel(self)
                pixel.move(14 * column, 14 * row)
                self.pixlist[row].insert(column, pixel)

    def mouseMoveEvent(self, e):
            row = int(e.pos().x() / 14)
            column = int(e.pos().y() / 14)
            if row < 28 and row > -1 and column < 28 and column > -1:
                self.pixlist[column][row].state = 1
                self.pixlist[column][row].setStyleSheet('background-color:rgb(0,0,0)')



                
            
class NetWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.screen = ScreenGetter().screenres()
        self.setWindowTitle('Digital Recognition')
        self.setWindowIcon(QtGui.QIcon('atom.png'))
        self.setFixedSize(788, 572)

        self.clearbtn = QPushButton('Clear', self)
        self.clearbtn.setGeometry(0, 432, self.size().width(), 70)
        self.clearbtn.clicked.connect(self.clear)

        self.processbtn = QPushButton('Process', self)
        self.processbtn.setGeometry(0, 502, self.size().width(), 70)
        self.processbtn.clicked.connect(self.process)

        
        self.pzone = PaintingZone(self)
        self.pzone.move(0,37)

        self.yd = QLabel('Your Drawing:', self)
        self.yd.resize(392, 37)
        self.yd.move(0,0)
        self.yd.setFont(QtGui.QFont('Arial', 15))
        self.yd.setAlignment(QtCore.Qt.AlignCenter)
        self.yd.setStyleSheet('background-color:rgb(255,255,255)')

        self.anw = QLabel('Draw this digit:', self)
        self.anw.resize(392, 37)
        self.anw.move(396,0)
        self.anw.setFont(QtGui.QFont('Arial', 15))
        self.anw.setAlignment(QtCore.Qt.AlignCenter)
        self.anw.setStyleSheet('background-color:rgb(255,255,255)')

        self.guesslbl = QLabel('0' , self)
        self.guesslbl.move(396, 37)
        self.guesslbl.resize(392,392)
        self.guesslbl.setFont(QtGui.QFont('Arial', 250))
        self.guesslbl.setAlignment(QtCore.Qt.AlignCenter)
        self.guesslbl.setStyleSheet('background-color:rgb(255,255,255)')

        #self.initNeural()

        self.counter = 0

        self.t1 = datetime.datetime.now()


    def clear(self):
        pass
    
    def initNeural(self):
        
        ins = 784
        hiddens = 100
        outs = 10
        lrate = 0.3
        
        nn = MachineLearning(ins, hiddens, outs, lrate)
        self.nn = nn
        

    def process(self):
        self.datafile = open('knowledgex.csv', 'a')
        string = ''
        
        for row in self.pzone.pixlist:
            for pixel in row:
                if pixel.state:
                    string += ',255'
                else:
                    string += ',0'

        self.datafile.write('\n' + self.guesslbl.text() + string)
        self.datafile.close()
        
        self.clearbtn.click()
        
        if self.guesslbl.text() == '9':
           self.guesslbl.setText('0')
        else:
            self.guesslbl.setText(str(int(self.guesslbl.text()) + 1))

        self.counter += 1
        print(self.counter)

    def keyPressEvent(self, e):
        self.process()

    def closeEvent(self, e):
        t2 = datetime.datetime.now()
        print('\nYou\'ve done ' + str(self.counter) + ' digits in', str(t2 - self.t1) + '!')
                
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    wind = NetWindow()
    wind.show()
    sys.exit(app.exec_())

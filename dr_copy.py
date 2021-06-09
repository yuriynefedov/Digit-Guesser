import random, os, time
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
from ScreenRes import ScreenGetter
from net import MachineLearning
from Signals import Signals
from gtts import gTTS
import pyglet

pyglet.lib.load_library('avbin')
pyglet.have_avbin = True

import datetime, numpy

class Pixel(QLabel):
    def __init__(self, parent = None):
        QLabel.__init__(self)
        self.setParent(parent)
        self.parent = parent
        self.resize(8,8)
        self.setStyleSheet('background-color:rgb(255,255,255)')
        self.state = 0
        self.tcounter = 0
        self.signals = Signals()

class PaintingZone(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self)
        self.setParent(parent)
        self.resize(392 + 56,392 + 56) #448 (+56)
        self.testlbl = QLabel('', self)
        self.testlbl.resize(self.size())
        self.setStyleSheet('background-color:rgb(55,255,255);')
        
        self.initPixels()

        parent.clearbtn.clicked.connect(self.clear)

        self.signals = Signals()


    def clear(self):
        for row in self.pixlist:
            for pixel in row:
                pixel.setStyleSheet('background-color:rgb(255,255,255)')
                pixel.state = 0

    def initPixels(self):
        self.pixlist = []
        for row in range(56):
            self.pixlist.insert(row, [])
            for column in range(56):
                pixel = Pixel(self)
                pixel.signals.touched.connect(self.touchSignal)
                pixel.move(8 * column, 8 * row)
                self.pixlist[row].insert(column, pixel)

    def mouseMoveEvent(self, e):
            row = int(e.pos().x() / 8)
            column = int(e.pos().y() / 8)
            if row < 56 and row > -1 and column < 56 and column > -1:
                self.pixlist[column][row].state = 1
                self.pixlist[column][row].setStyleSheet('background-color:rgb(0,0,0)')
                self.pixlist[column][row].signals.touched.emit()


    def touchSignal(self):
        self.signals.touched.emit()

                
            
class NetWindow(QWidget):
    def __init__(self):

        self.repeats = 5

        #self.diversity = ['I think it\'s ', 'My guess is ', 'I see ', 'I think you draw ',
        #                  'It looks like ', 'Seems like you draw ']

        self.diversity = ['I think it\'s ', 'I see ']
        self.mpname = 'speech.mp3'
        
        QWidget.__init__(self)
        self.screen = ScreenGetter().screenres()
        self.setWindowTitle('Digital Recognition')
        self.setWindowIcon(QtGui.QIcon('logo.png'))
        self.setFixedSize(844 + 56, 728)

        self.addition_left = QLabel('draw a digit from 0 to 9', self)
        self.addition_left.setGeometry(0, 37, 392 + 56, 30)
        self.addition_left.setFont(QtGui.QFont('Arial', 8))
        self.addition_left.setAlignment(QtCore.Qt.AlignHCenter)
        self.addition_left.setStyleSheet('background-color:rgb(255,255,255)')

        self.addition_right = QLabel('neural network\'s guess', self)
        self.addition_right.setGeometry(396 + 56, 37, 392 + 56, 30)
        self.addition_right.setFont(QtGui.QFont('Arial', 8))
        self.addition_right.setAlignment(QtCore.Qt.AlignHCenter)
        self.addition_right.setStyleSheet('background-color:rgb(255,255,255)')

        self.clearbtn = QPushButton('Clear', self)
        self.clearbtn.setGeometry(0, 532 + 56, self.size().width(), 70)
        self.clearbtn.clicked.connect(self.clear)

        self.processbtn = QPushButton('Process', self)
        self.processbtn.setGeometry(0, 658, self.size().width(), 70)
        self.processbtn.clicked.connect(self.process)

        self.clearbtn.setEnabled(False)
        self.processbtn.setEnabled(False)

        self.correctbtn = QPushButton('  Correct', self)
        self.correctbtn.setGeometry(0, 462 + 56, round(self.size().width() / 2), 70)
        self.correctbtn.setIcon(QtGui.QIcon('greentick.png'))
        self.correctbtn.setDisabled(True)
        self.correctbtn.clicked.connect(self.guessed)
        
        self.falsebtn = QPushButton('  Incorrect', self)
        self.falsebtn.setGeometry(395 + 56, 462 + 56, round(self.size().width() / 2), 70)
        self.falsebtn.setIcon(QtGui.QIcon('redcross.png'))
        self.falsebtn.setDisabled(True)
        self.falsebtn.clicked.connect(self.notguessed)

        self.pzone = PaintingZone(self)
        self.pzone.move(0,67)
        self.pzone.signals.touched.connect(self.activateButtons)

        self.yd = QLabel('Your Drawing:', self)
        self.yd.resize(392 + 56, 37)
        self.yd.move(0,0)
        self.yd.setFont(QtGui.QFont('Arial', 15))
        self.yd.setAlignment(QtCore.Qt.AlignCenter)
        self.yd.setStyleSheet('background-color:rgb(255,255,255)')

        self.anw = QLabel('Answer:', self)
        self.anw.resize(392 + 56, 37)
        self.anw.move(396 + 56,0)
        self.anw.setFont(QtGui.QFont('Arial', 15))
        self.anw.setAlignment(QtCore.Qt.AlignCenter)
        self.anw.setStyleSheet('background-color:rgb(255,255,255)')

        self.guesslbl = QLabel('', self)
        self.guesslbl.move(396 + 56, 67)
        self.guesslbl.resize(392 + 56,392 + 56)
        self.guesslbl.setFont(QtGui.QFont('Arial', 250))
        self.guesslbl.setAlignment(QtCore.Qt.AlignCenter)
        self.guesslbl.setStyleSheet('background-color:rgb(255,255,255)')

        print('training neural network...')
        #self.initNeural()

    def initNeural(self):

        datafile = open('knowledgex.csv', 'r')
        lines = datafile.readlines()
        datafile.close()
        
        self.ins = 784
        self.hiddens = 100
        self.outs = 10
        self.lrate = 0.4
        
        nn = MachineLearning(self.ins, self.hiddens, self.outs, self.lrate)
        t1 = datetime.datetime.now()
        #x = 0
        answers_list = [0,0,0,0,0,0,0,0,0,0]

        for x in range(self.repeats):
            for numline in lines:
                try:
                    all_values = numline.split(',')
                    answer = int(all_values[0])
                    answers_list[answer] += 1
                    inputs = numpy.asfarray(all_values[1:]) / 255.0 * 0.99 + 0.01
                    targets = numpy.zeros(self.outs) + 0.01         #OUTS = 10
                    targets[answer] = 0.99
                    nn.train(inputs, targets)
                except ValueError:
                    pass
                
        print(datetime.datetime.now() - t1)
        print(answers_list)

        self.nn = nn

    def activateButtons(self):
        self.clearbtn.setEnabled(True)
        self.processbtn.setEnabled(True)


    def clear(self):
        self.guesslbl.setText('')
        if self.correctbtn.isEnabled:
            self.correctbtn.setEnabled(False)
            self.falsebtn.setEnabled(False)

    def guessed(self):
        self.clearbtn.setEnabled(True)
        self.clearbtn.click()
        self.clearbtn.setEnabled(False)
        self.correctbtn.setEnabled(False)
        self.falsebtn.setEnabled(False)
        
        self.trainOne()

    def notguessed(self):
        self.clearbtn.setEnabled(True)
        self.clearbtn.click()
        self.clearbtn.setEnabled(False)
        self.correctbtn.setEnabled(False)
        self.falsebtn.setEnabled(False)


    def trainOne(self):

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

        string = string[1:]
        
        for x in range(self.repeats):
            try:
                all_values = string.split(',')
                answer = int(self.guesslbl.text())
                inputs = numpy.asfarray(all_values) / 255.0 * 0.99 + 0.01
                targets = numpy.zeros(self.outs) + 0.01
                targets[answer] = 0.99
                self.nn.train(inputs, targets)
                
            except ValueError:
                pass
        
        self.clearbtn.click()

        print('learned')
        

    def process(self):
            string = ''
            for row in self.pzone.pixlist:
                for pixel in row:
                    if pixel.state:
                        string += ',255'
                    else:
                        string += ',0'
                        
            string = string[1:]

            go = self.nn.query(numpy.asfarray(string.split(',')) / 255.0 * 0.99 + 0.01)

            go = list(go)

            for l in go:
                l = list(l)
                
            answer = go.index(max(go))

            print(round(*max(go) / 1 * 100, 2), '% sure')
            
            self.guesslbl.setText(str(answer))
            self.correctbtn.setEnabled(True)
            self.falsebtn.setEnabled(True)
            self.clearbtn.setEnabled(False)
            self.processbtn.setEnabled(False)

            speech = gTTS(text = random.choice(self.diversity) + str(answer), lang = 'en')
            speech.save(self.mpname)

            played = pyglet.resource.media(self.mpname)
            played.play()
            pyglet.app.run()


    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Enter:
            self.process()

        

                
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    wind = NetWindow()
    wind.show()
    sys.exit(app.exec_())

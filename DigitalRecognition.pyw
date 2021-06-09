import random, os, time
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
from ScreenRes import ScreenGetter
from net import MachineLearning
from Signals import Signals
from gtts import gTTS
import pyttsx3 #, pyglet

#pyglet.lib.load_library('avbin')
#pyglet.have_avbin = True

import datetime, numpy


class Pixel(QLabel):
    def __init__(self, parent = None):
        QLabel.__init__(self)
        self.setParent(parent)
        self.parent = parent
        self.resize(14,14)
        self.setStyleSheet('background-color:rgb(255,255,255)')
        self.state = 0
        self.tcounter = 0
        self.signals = Signals()


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

        self.signals = Signals()

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
                pixel.signals.touched.connect(self.touchSignal)
                pixel.move(14 * column, 14 * row)
                self.pixlist[row].insert(column, pixel)

    def mouseMoveEvent(self, e):
            row = int(e.pos().x() / 14)
            column = int(e.pos().y() / 14)
            if row < 28 and row > -1 and column < 28 and column > -1:
                self.pixlist[column][row].state = 1
                self.pixlist[column][row].setStyleSheet('background-color:rgb(0,0,0)')
                self.pixlist[column][row].signals.touched.emit()

    def touchSignal(self):
        self.signals.touched.emit()


class numLabel(QPushButton):
    def __init__(self, number, parent = None):
        QPushButton.__init__(self)
        self.setParent(parent)
        self.resize(60,60)
        #self.setAlignment(QtCore.Qt.AlignCenter)
        self.setFont(QtGui.QFont('Calibri', 15))
        self.setText(str(number))

                
            
class NetWindow(QWidget):
    def __init__(self):

        self.repeats = 5

        self.initAudioSoft()

        #self.diversity = ['I think it\'s ', 'My guess is ', 'I see ', 'I think you draw ',
        #                  'It looks like ', 'Seems like you draw ']

        self.diversity = ['I think it\'s ', 'I see ', 'My guess is ']
        self.mpname = 'speech.mp3'
        
        QWidget.__init__(self)
        self.screen = ScreenGetter().screenres()
        self.setWindowTitle('Digital Recognition')
        self.setWindowIcon(QtGui.QIcon('logo.png'))
        self.setFixedSize(788, 672)

        self.addition_left = QLabel('draw a digit from 0 to 9', self)
        self.addition_left.setGeometry(0, 37, 392, 30)
        self.addition_left.setFont(QtGui.QFont('Arial', 8))
        self.addition_left.setAlignment(QtCore.Qt.AlignHCenter)
        self.addition_left.setStyleSheet('background-color:rgb(255,255,255)')

        self.addition_right = QLabel('neural network\'s guess', self)
        self.addition_right.setGeometry(396, 37, 392, 30)
        self.addition_right.setFont(QtGui.QFont('Arial', 8))
        self.addition_right.setAlignment(QtCore.Qt.AlignHCenter)
        self.addition_right.setStyleSheet('background-color:rgb(255,255,255)')

        self.clearbtn = QPushButton('Clear', self)
        self.clearbtn.setGeometry(0, 532, self.size().width(), 70)
        self.clearbtn.clicked.connect(self.clear)

        self.processbtn = QPushButton('Process', self)
        self.processbtn.setGeometry(0, 602, self.size().width(), 70)
        self.processbtn.clicked.connect(self.process)

        self.clearbtn.setEnabled(False)
        self.processbtn.setEnabled(False)

        self.correctbtn = QPushButton('  Correct', self)
        self.correctbtn.setGeometry(0, 462, round(self.size().width() / 2) - 1, 70)
        self.correctbtn.setIcon(QtGui.QIcon('greentick.png'))
        self.correctbtn.setDisabled(True)
        self.correctbtn.clicked.connect(self.guessed)
        
        self.falsebtn = QPushButton('  Incorrect', self)
        self.falsebtn.setGeometry(395, 462, round(self.size().width() / 2), 70)
        self.falsebtn.setIcon(QtGui.QIcon('redcross.png'))
        self.falsebtn.setDisabled(True)
        self.falsebtn.clicked.connect(self.notguessed)

        self.pzone = PaintingZone(self)
        self.pzone.move(0,67)
        self.pzone.signals.touched.connect(self.activateButtons)

        self.yd = QLabel('Your Drawing:', self)
        self.yd.resize(392, 37)
        self.yd.move(0,0)
        self.yd.setFont(QtGui.QFont('Arial', 15))
        self.yd.setAlignment(QtCore.Qt.AlignCenter)
        self.yd.setStyleSheet('background-color:rgb(255,255,255)')

        self.anw = QLabel('Answer:', self)
        self.anw.resize(392, 37)
        self.anw.move(396,0)
        self.anw.setFont(QtGui.QFont('Arial', 15))
        self.anw.setAlignment(QtCore.Qt.AlignCenter)
        self.anw.setStyleSheet('background-color:rgb(255,255,255)')

        self.guesslbl = QLabel('', self)
        self.guesslbl.move(396, 67)
        self.guesslbl.resize(392,392)
        self.guesslbl.setFont(QtGui.QFont('Arial', 250))
        self.guesslbl.setAlignment(QtCore.Qt.AlignCenter)
        self.guesslbl.setStyleSheet('background-color:rgb(255,255,255)')

        # 'WHAT WAS THAT' SUPPLIES

        self.helpBg = QLabel(' ', self)
        self.helpBg.setGeometry(0,459, self.size().width(), 6)
        self.helpBg.setStyleSheet('background-color:rgb(255,255,255);')
        self.helpBg.hide()

        self.whatLbl = QLabel('What was that?', self)
        self.whatLbl.move(0,465)
        self.whatLbl.resize(self.size().width(), 100)
        self.whatLbl.setAlignment(QtCore.Qt.AlignHCenter)
        self.whatLbl.setStyleSheet('background-color:rgb(255,255,255);')
        self.whatLbl.setFont(QtGui.QFont('Calibri', 16))
        self.whatLbl.hide()

        self.numlist = []
        for a in range(10):
            num = numLabel(a, self)
            num.move(2 + 61 * a, 499)
            self.numlist.append(num)
            num.hide()
            num.clicked.connect(self.hideWhatWasThat)

        self.numlist[0].clicked.connect(self.chose0)
        self.numlist[1].clicked.connect(self.chose1)
        self.numlist[2].clicked.connect(self.chose2)
        self.numlist[3].clicked.connect(self.chose3)
        self.numlist[4].clicked.connect(self.chose4)
        self.numlist[5].clicked.connect(self.chose5)
        self.numlist[6].clicked.connect(self.chose6)
        self.numlist[7].clicked.connect(self.chose7)
        self.numlist[8].clicked.connect(self.chose8)
        self.numlist[9].clicked.connect(self.chose9)

        self.orlbl = QLabel('or', self)
        self.orlbl.move(63 + 61*a, 499)
        self.orlbl.resize(50,60)
        self.orlbl.setStyleSheet('background-color:rgb(255,255,255);')
        self.orlbl.setFont(QtGui.QFont('Calibri', 10))
        self.orlbl.setAlignment(QtCore.Qt.AlignCenter)
        self.orlbl.hide()
        
        self.forgetbtn = numLabel('Forget', self)
        self.forgetbtn.setGeometry(56 + 61 * (a + 1), 499, 120, 60)
        self.forgetbtn.setFont(QtGui.QFont('Calibri', 12))
        self.forgetbtn.hide()
        self.forgetbtn.clicked.connect(self.hideWhatWasThat)

        self.whatout = False
        print('training neural network...')
        self.initNeural()

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
        answers_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

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
        self.trainOne()
        
        self.clearbtn.setEnabled(True)
        self.clearbtn.click()
        self.clearbtn.setEnabled(False)
        self.correctbtn.setEnabled(False)
        self.falsebtn.setEnabled(False)

    def notguessed(self):
        #self.clearbtn.setEnabled(True)
        #self.clearbtn.click()
        #self.clearbtn.setEnabled(False)
        #self.correctbtn.setEnabled(False)
        #self.falsebtn.setEnabled(False)
        self.whatWasThat()
        pass

    def whatWasThat(self):
        self.setFixedSize(788, 772)
        for btn in (self.clearbtn, self.processbtn, self.correctbtn, self.falsebtn):
            btn.move(btn.pos().x(), btn.pos().y() + 100)

        for num in self.numlist:
            num.show()
        print('a')
        self.orlbl.show()
        self.helpBg.show()
        print('b')
        self.whatLbl.show()
        self.forgetbtn.show()
        print('c')
        self.whatout = True
        print('d')
        self.correctbtn.setEnabled(False)
        self.falsebtn.setEnabled(False)

        print('e')
        #speech = 'What was the answer?'
        #self.engine.say(speech)
        #self.engine.runAndWait()
        print('f')

    def hideWhatWasThat(self):
        
        self.setFixedSize(788, 672)
        for btn in (self.clearbtn, self.processbtn, self.correctbtn, self.falsebtn):
            btn.move(btn.pos().x(), btn.pos().y() - 100)
            
        for num in self.numlist:
            num.hide()
        self.orlbl.hide()
        self.helpBg.hide()
        self.whatLbl.hide()
        self.forgetbtn.hide()

        self.clearbtn.setEnabled(True)
        self.clearbtn.click()
        self.clearbtn.setEnabled(False)
        self.correctbtn.setEnabled(False)
        self.falsebtn.setEnabled(False)

        self.whatout = False

    def chose0(self):
        self.guesslbl.setText('0')
        self.guessed()
        #self.say('Got it')

    def chose1(self):
        self.guesslbl.setText('1')
        self.guessed()
        #self.say('Got it')

    def chose2(self):
        self.guesslbl.setText('2')
        self.guessed()
        #self.say('Got it')
        
    def chose3(self):
        self.guesslbl.setText('3')
        self.guessed()
        #self.say('Got it')
        
    def chose4(self):
        self.guesslbl.setText('4')
        self.guessed()
        #self.say('Got it')

    def chose5(self):
        self.guesslbl.setText('5')
        self.guessed()
        #self.say('Got it')
        
    def chose6(self):
        self.guesslbl.setText('6')
        self.guessed()
        #self.say('Got it')
        
    def chose7(self):
        self.guesslbl.setText('7')
        self.guessed()
        #self.say('Got it')
        
    def chose8(self):
        self.guesslbl.setText('8')
        self.guessed()
        #self.say('Got it')
        
    def chose9(self):
        self.guesslbl.setText('9')
        self.guessed()
        #self.say('Got it')
    

        
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
        #print('\n', self.guesslbl.text(), '\n')
        self.datafile.close()

        string = string[1:]
        
        for x in range(self.repeats):
            try:
                all_values = string.split(',')
                answer = int(self.guesslbl.text())
                #print('\n', answer, '\n')
                inputs = numpy.asfarray(all_values) / 255.0 * 0.99 + 0.01
                targets = numpy.zeros(self.outs) + 0.01
                targets[answer] = 0.99
                self.nn.train(inputs, targets)
                print(all_values)
                
            except ValueError:
                pass
        
        self.clearbtn.click()

        print('learned')

    def process(self):
        self.correctbtn.setEnabled(True)
        self.falsebtn.setEnabled(True)
        self.clearbtn.setEnabled(False)
        self.processbtn.setEnabled(False)

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
        print(go)
        for l in go:
            l = list(l)

        answer = go.index(max(go))

        print(round(*max(go) / 1 * 100, 2), '% sure')

        self.guesslbl.setText(str(answer))
        # speech = random.choice(self.diversity) + str(answer)
        # print(speech)
        # self.say(speech)
        print("said")

    def say(self, speech):
        self.engine.say(speech)
        self.engine.runAndWait()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Enter:
            self.process()
            print("event done")

    def mouseReleaseEvent(self, e):
        if self.whatout:
            print('s')

    def initAudioSoft(self):
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
        

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    wind = NetWindow()
    wind.show()
    sys.exit(app.exec_())

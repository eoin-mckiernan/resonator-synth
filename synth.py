SAMPLE_RATE = 32000
AUDIO_CHANS = 1
SAMPLE_SIZE = 16
CTRL_INTERVAL = 100

import matplotlib.pyplot as plt
import numpy as np
import sys
import random
from PyQt5.QtCore import QByteArray, QIODevice,QThread, QObject, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtMultimedia import QAudioFormat, QAudioOutput
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QSlider, QPushButton, QLabel, QComboBox, QMessageBox
from res import RES
import mido



class MidiPortReader(QObject):
    addVoice = pyqtSignal(int)
    removeVoice = pyqtSignal(int)
    def __init__(self):
        QObject.__init__(self)
        mido.set_backend(
                'mido.backends.rtmidi/LINUX_ALSA'
                )

    def listener(self):
        with mido.open_input(
                'pipes',
                virtual = True
                )as mip:
            for  msg in mip:
                print(msg.bytes())
                if(msg.velocity == 0):
                    self.removeVoice.emit(msg.note)
                else:
                    self.addVoice.emit(msg.note)

class Generator(QIODevice):
    SAMPLES_PER_READ = 1024
    def __init__(self,format, parent = None):
        QIODevice.__init__(self,parent)
        self.data = QByteArray()
        self.format = format
        self.voiceList = []
        self.pulseP = 0.3
        self.q = 100
        self.transpose = 36

    def start(self):
        self.open(QIODevice.ReadOnly)

    def readData(self, bytes):
        if bytes > 2 * Generator.SAMPLES_PER_READ:
            bytes = 2 * Generator.SAMPLES_PER_READ
        return self.generateData(self.format, bytes//2)

    def generateData(self, format, samples):

        pulses = np.zeros(samples)
        for n in range(samples):
            pulses[n] = np.random.binomial(1,self.pulseP)
        tone = np.zeros(samples)
        for i in range(len(self.voiceList)):
            tone = tone + self.reslist[i].filter(pulses)
        tone = (50*tone).astype(np.int16)
        return tone.tostring()


    @pyqtSlot(int)
    def addVoice(self, voice):
        self.voiceList.append(voice)
        print(self.voiceList)
        self.resCalc()
        #print(freq)
        

    @pyqtSlot(int)
    def removeVoice(self, voice):
        self.voiceList.remove(voice)
        self.resCalc()
        print(self.voiceList)

    @pyqtSlot(int)
    def changeP(self, slid):
        self.pulseP = slid/200.0

    def resCalc(self):
        self.reslist = []
        for i in range(len(self.voiceList)):
            self.reslist.append(Resonator(440*2**((self.voiceList[i]-69+self.transpose)/12),self.q))

    @pyqtSlot(int)
    def qCalc(self, q):
        self.q = q
        self.resCalc()

class Resonator(QObject):
    def __init__(self,freq = 11000, q=10):
        QObject.__init__(self)
        self.z = np.zeros(2)
        self.a1, self.a2 = RES.acalc(freq,q,SAMPLE_RATE)
        print(self.a1)
        print(self.a2)

    def filter(self,inarr):
        outarr = np.zeros(len(inarr))
        RES.filterArray(outarr, inarr, self.z, self.a1, self.a2)
        return outarr



class MainWindow(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self,parent)

        format = QAudioFormat()
        format.setChannelCount(AUDIO_CHANS)
        format.setSampleRate(SAMPLE_RATE)
        format.setSampleSize(SAMPLE_SIZE)
        format.setCodec("audio/pcm")
        format.setByteOrder(
                QAudioFormat.LittleEndian
        )
        format.setSampleType(
                QAudioFormat.SignedInt
        )


        self.output = QAudioOutput(format,self)
        output_buffer_size = \
                int(2*CTRL_INTERVAL/1000)
        self.output.setBufferSize(
                output_buffer_size
        )
        

        self.generator = Generator(format,self)
        self.midiListener = MidiPortReader()
        self.listenerThread = QThread()
        self.midiListener.moveToThread(self.listenerThread)
        self.listenerThread.started.connect(
                self.midiListener.listener
                )
        self.midiListener.addVoice.connect(self.generator.addVoice)
        self.midiListener.removeVoice.connect(self.generator.removeVoice)

        self.createUI()
        
        self.pslider.valueChanged.connect(self.generator.changeP)
        self.fslider.valueChanged.connect(self.generator.qCalc)
        self.semiDown.clicked.connect(self.smDown)
        self.semiUp.clicked.connect(self.smUp)
        self.octaveDown.clicked.connect(self.ovDown)
        self.octaveUp.clicked.connect(self.ovUp)

        self.listenerThread.start()
        self.generator.start()
        self.output.start(self.generator)
    
    def createUI(self):
        label = QLabel()
        label.setText("Pulse ammount")
        self.pslider = QSlider(Qt.Horizontal)
        self.pslider.setMinimum(0)
        self.pslider.setMaximum(100)
        self.pslider.setValue(60)
        flabel = QLabel()
        flabel.setText("Q")
        self.fslider = QSlider(Qt.Horizontal)
        self.fslider.setMinimum(10)
        self.fslider.setMaximum(10000)
        self.fslider.setValue(1000)
        self.octaveUp = QPushButton("+12")
        self.octaveDown = QPushButton("-12")
        self.semiUp = QPushButton("+1")
        self.semiDown = QPushButton("-1")
        self.transLabel = QLabel(str(self.generator.transpose))
        vl = QVBoxLayout(self)




        hl = QHBoxLayout()
        hl.addWidget(label)
        hl.addStretch(1)
        hl.addWidget(self.pslider)
        vl.addLayout(hl)


        fhl = QHBoxLayout()
        fhl.addWidget(flabel)
        fhl.addStretch(1)
        fhl.addWidget(self.fslider)
        vl.addLayout(fhl)

        bhl = QHBoxLayout()
        bhl.addWidget(self.octaveDown)
        bhl.addWidget(self.semiDown)
        bhl.addWidget(self.transLabel)
        bhl.addWidget(self.semiUp)
        bhl.addWidget(self.octaveUp)
        vl.addLayout(bhl)

    def transposeChange(self, amt):
        self.generator.transpose = self.generator.transpose +amt
        self.transLabel.setText(str(self.generator.transpose))

    @pyqtSlot()
    def ovUp(self):
        self.transposeChange(12)

    @pyqtSlot()
    def ovDown(self):
        self.transposeChange(-12)

    @pyqtSlot()
    def smUp(self):
        self.transposeChange(1)

    @pyqtSlot()
    def smDown(self):
        self.transposeChange(-1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

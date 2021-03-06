import numpy as np
import scipy.signal

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Elliptic(QWidget):

    filterTypes = {'Low-pass': 'lowpass', 'High-pass':'highpass',
                   'Band-pass': 'bandpass', 'Band-stop': 'bandstop'}
    valuesChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()

        typeLabel = QLabel("Type")
        orderLabel = QLabel("Order")
        rippleLabel = QLabel("Max Ripple")
        attenuationLabel = QLabel("Min Attenuation")
        lowCutoffLabel = QLabel("Low Cutoff")
        highCutoffLabel = QLabel("High Cutoff")

        self.typeComboBox = QComboBox()
        self.typeComboBox.addItems(self.filterTypes.keys())
        self.orderBox = QSpinBox()
        self.orderBox.setRange(1, 10)
        self.orderBox.setValue(4)
        self.rippleBox = QDoubleSpinBox()
        self.rippleBox.setRange(0.01, 1000000000.0)
        self.rippleBox.setValue(3.0)
        self.rippleBox.setSuffix(" dB")
        self.attenuationBox = QDoubleSpinBox()
        self.attenuationBox.setRange(0.01, 1000000000.0)
        self.attenuationBox.setValue(3.0)
        self.attenuationBox.setSuffix(" dB")
        self.lowCutoffBox = QDoubleSpinBox()
        self.lowCutoffBox.setRange(0.0, 1000000000.0)
        self.lowCutoffBox.setValue(50)
        self.lowCutoffBox.setSuffix(" Hz")
        self.highCutoffBox = QDoubleSpinBox()
        self.highCutoffBox.setRange(0.0, 1000000000.0)
        self.highCutoffBox.setValue(100)
        self.highCutoffBox.setSuffix(" Hz")

        self.typeComboBox.currentIndexChanged.connect(self.updateUi)
        self.orderBox.valueChanged.connect(self.updateUi)
        self.rippleBox.valueChanged.connect(self.updateUi)
        self.attenuationBox.valueChanged.connect(self.updateUi)
        self.lowCutoffBox.valueChanged.connect(self.updateUi)
        self.highCutoffBox.valueChanged.connect(self.updateUi)

        grid = QGridLayout()
        grid.addWidget(typeLabel, 1, 0)
        grid.addWidget(orderLabel, 2, 0)
        grid.addWidget(rippleLabel, 3, 0)
        grid.addWidget(attenuationLabel, 4, 0)
        grid.addWidget(lowCutoffLabel, 5, 0)
        grid.addWidget(highCutoffLabel, 6, 0)
        grid.addWidget(self.typeComboBox, 1, 1)
        grid.addWidget(self.orderBox, 2, 1)
        grid.addWidget(self.rippleBox, 3, 1)
        grid.addWidget(self.attenuationBox, 4, 1)
        grid.addWidget(self.lowCutoffBox, 5, 1)
        grid.addWidget(self.highCutoffBox, 6, 1)
        self.setLayout(grid)

        self.updateUi()

    def updateUi(self):
        _type = self.filterTypes[self.typeComboBox.currentText()]
        if _type in ('bandstop', 'bandpass'):
            self.lowCutoffBox.setEnabled(True)
            self.highCutoffBox.setEnabled(True)
        elif _type == 'lowpass':
            self.lowCutoffBox.setEnabled(True)
            self.highCutoffBox.setEnabled(False)
        elif _type == 'highpass':
            self.lowCutoffBox.setEnabled(False)
            self.highCutoffBox.setEnabled(True)
        self.valuesChanged.emit()

    def filter(self, data):
        if not data:
            return None
        x, y = data
        order = self.orderBox.value()
        maxRipple = self.rippleBox.value()
        minAttenuation = self.attenuationBox.value()
        lowCutoff = self.lowCutoffBox.value()
        highCutoff = self.highCutoffBox.value()
        dataLengthSeconds = max(x) - min(x)
        dataLengthSamples = len(x)
        sampleRate = dataLengthSamples / dataLengthSeconds
        _type = self.filterTypes[self.typeComboBox.currentText()]
        if _type in ('bandstop', 'bandpass'):
            wn = (lowCutoff / (sampleRate/2), highCutoff / (sampleRate/2))
            if wn[0] > 1:
                wn = (1, wn[1])
            if wn[1] > 1:
                wn = (wn[0], 1)
        elif _type == 'highpass':
            wn = highCutoff / (sampleRate/2)
            if wn > 1:
                wn = 1
        elif _type == 'lowpass':
            wn = lowCutoff / (sampleRate/2)
            if wn > 1:
                wn = 1
        try:
            coefficients = scipy.signal.ellip(
                order, maxRipple, minAttenuation, wn, _type, output='sos')
            signal = scipy.signal.sosfiltfilt(coefficients, y)
            data = (x, signal)
        except ValueError as e:
            print("Error in elliptic filter: {}".format(e))
        except np.linalg.linalg.LinAlgError:
            return (0, 0)
        return data

import json
import os
import random
import string
import time

import requests
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QThread,pyqtSignal
from PyQt6 import uic
_count = 0
_countAudio = 0
_countAudioSucess = 0
import glob
class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi("DATA/untitled.ui", self)
        self.pushButton = self.findChild(QPushButton,'pushButton')
        self.pushButton.clicked.connect(self.dialogFiles)
        self.pushButton_2 = self.findChild(QPushButton,'pushButton_2')
        self.pushButton_2.clicked.connect(self.start)
        self.comboBox = self.findChild(QComboBox,'comboBox')
        self.label = self.findChild(QLabel,'label')

        self.show()
        self.childThread = {}

    def start(self):
        with open(self.fileName, 'r', encoding='utf8') as rTxt:
            rTxt = rTxt.read()
        firstcount = 0
        secondcount = 400
        splitText = rTxt.split()
        lenText = len(splitText)
        self.lenText = lenText
        global _countAudio
        while True:
            if secondcount < lenText:
                self.text = ' '.join(splitText[firstcount:secondcount])
                self.useThread(firstcount)
                _countAudio += 1
            else:
                self.text = ' '.join(splitText[firstcount:secondcount])
                self.useThread(firstcount)
                _countAudio += 1
                break


            firstcount += 400
            secondcount += 400
            time.sleep(0.3)

    def useThread(self,index):
        self.label.setText('Đang khởi tạo audio download !')
        self.childThread[index] = StartThread(index=index)
        self.childThread[index].text = self.text
        self.childThread[index].comboBox = self.comboBox.currentIndex()
        self.childThread[index].nameFolder = self.name.split('.')[0]
        self.childThread[index].lbstatus.connect(self.labelSTT)
        self.childThread[index].start()

    def dialogFiles(self):
        global _count
        global _countAudioSucess
        global _countAudio
        _count = 0
        _countAudioSucess = 0
        _countAudio = 0
        try:
            self.fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()")
            path, self.name = os.path.split(self.fileName)

        except:pass


    def labelSTT(self,text):
        global _countAudio
        self.label.setText(f"Tải thành công {text}/{_countAudio} Audio !")



class StartThread(QThread):
    lbstatus = pyqtSignal(int)
    def __init__(self,index = 0):
        super(StartThread, self).__init__()
        self.index = index
        self.is_running = True

    def run(self):
        global _count
        _count += 1
        self.count = _count
        self.textToAudio(self.text)

    def downloadAudio(self,id):
        global _countAudioSucess
        listVoice = ["en-US_AllisonV3Voice","en-US_EmilyV3Voice","en-US_HenryV3Voice","en-US_KevinV3Voice","en-US_LisaV3Voice","en-US_MichaelV3Voice","en-US_OliviaV3Voice"]
        url = "https://www.ibm.com/demos/live/tts-demo/api/tts/newSynthesize"
        cookies = open('DATA/cookies.json')

        cookies = json.load(cookies)
        cookie = cookies[0]['cookies']
        voice = listVoice[self.comboBox]
        querystring = {"voice": f"{voice}",
                       "id": f"{id}"}  # en-US_AllisonV3Voice

        payload = ""
        headers = {
            'cookie': f'{cookie}'}

        response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
        if not os.path.exists(self.nameFolder):
            os.mkdir(self.nameFolder)
        with open(f'{self.nameFolder}/{self.count}.mp3', 'wb') as f:
            f.write(response.content)
        _countAudioSucess += 1
        self.lbstatus.emit(_countAudioSucess)

    def textToAudio(self,text):
        cookies = open('DATA/cookies.json')

        cookies = json.load(cookies)
        cookie = cookies[0]['cookies']
        numberRD = random.randint(100, 999)
        url = "https://www.ibm.com/demos/live/tts-demo/api/tts/store"
        payload = {
            "ssmlText": f"<prosody pitch=\"default\" rate=\"-0%\">{text}</prosody>",
            "sessionID": f"9aa3c990-1f2e-48b3-900d-adfc1f4ab{numberRD}"
        }
        headers = {
            'cookie': f"{cookie}",
            'content-type': "application/json;charset=UTF-8"
        }

        response = requests.request("POST", url, json=payload, headers=headers)

        data = json.loads(response.text)
        message = data['message']
        id = message.split(':')[1][1:]
        self.downloadAudio(id)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    UiWindow = UI()
    app.exec()
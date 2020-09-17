import random
import time

import requests
from SibADI import *
from TSUAD import *
from USPU import *
from VGYES import *
from agu import *
from mgppu import *


class Main:
    def sendMessOnError(self, e):
        url = "https://api.vk.com/method/messages.send?peer_id=2000000001&message=message&v=5.101&random_id=124&access_token=2d552811d20aecb776cacad7245ce05bda56ceb56c8495683e4a171ccb0227287126e7afae532d00b8665"
        id_slava = 33262047
        id_kolya = 197547980

        headers = {
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'peer_id': id_slava,
            'message': str(e),
            'v': 5.101,
            'random_id': random.randint(1, 100000),
            'access_token': 'a73613fa18243570b115d56169cc32bdb6d15bc63c8ad211514846c7fb60b5859621e9ca02e03ecd3e1a6'
        }
        requests.post(url, headers)
        time.sleep(10)

        headers = {
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'peer_id': id_kolya,
            'message': str(e),
            'v': 5.101,
            'random_id': random.randint(1, 100000),
            'access_token': 'a73613fa18243570b115d56169cc32bdb6d15bc63c8ad211514846c7fb60b5859621e9ca02e03ecd3e1a6'
        }
        requests.post(url, headers)
        time.sleep(10)

    def runVVSU(self):
        try:
            RUNVVSU()
        except Exception as e:
            self.onError("VVSU " + str(e))

    def runMGPPU(self):
        try:
            Mgppu().run()
        except Exception as e:
            self.onError("MGPPU" + str(e))

    def runUSPU(self):
        try:
            RunUspuGroup()
        except Exception as e:
            self.onError("USPU group " + str(e))

        try:
            RunUspuTeacher()
        except Exception as e:
            self.onError("USPU teacher " + str(e))

    def runSIBADI(self):
        try:
            RUNSibADI()
        except Exception as e:
            self.onError("SIBADI " + str(e))

    def runTSUAD(self):
        try:
            RUNTsuad()
        except Exception as e:
            self.onError("TSUAD " + str(e))


    def runAGU(self):
        try:
            runAGU()
        except Exception as e:
            self.onError("AGU " + str(e))


    def onError(self, e):
        print(e)
        self.sendMessOnError(e)




    def run(self):
        #self.runMGPPU()
        #self.runVVSU()
        #self.runUSPU()
        #self.runTSUAD()
        #self.runSIBADI()
        self.runAGU()

Main().run()

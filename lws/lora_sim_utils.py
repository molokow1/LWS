import math
import numpy as np
import random
import matplotlib.pyplot as plt
import subprocess
from matplotlib.backends.backend_pdf import PdfPages
import json
import os 
import datetime 

TIME_ON_AIR = 1712.13
PACKET_RATE = 1e-6
Ptx = 14
GL = 0
freq = 915
sens = -133.25

def calc_ALOHA_DER(num_transmitters, air_time, trans_rate):
    # most basic DER calculation with ALOHA
    der = np.exp(-2 * num_transmitters * air_time * trans_rate)
    return der

def calcMaxRange(Ptx, GL, sens, freq):
    beforeLog = (Ptx + GL - sens - 32.4) / 20 -  math.log10(freq)
    maxRange = math.pow(10, (beforeLog))
    return maxRange

class FileUtils(object):
    simResultFolderPath = os.path.join(os.getcwd(), "sim_result")

    def __createResultFolder(self):
        if not os.path.exists(self.simResultFolderPath):
            os.mkdir(self.simResultFolderPath)

    def createNewSession(self, sessionName = ""):
        self.currentSession = sessionName + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        self.__createResultFolder()
        self.__currentSessionPath = os.path.join(self.simResultFolderPath, self.currentSession)
        os.mkdir(os.path.join(self.simResultFolderPath, self.currentSession))

    @property
    def currentSessionPath(self):
        return self.__currentSessionPath

    def __initSimResultFile(self, fileName):
        self.currentFileName = fileName + ".dat"
        f = os.path.join(self.__currentSessionPath, self.currentFileName)
        names = "nrNodes nrCollisions nrLost pktsSent OverallEnergy DER Retransmissions RetransmissionRate\r\n"
        if not os.path.isfile(f):
            with open(f, "a") as openFile:
                openFile.write(names)
            openFile.close()
        
        return f

    
    def writeSimResult(self, writeStr, fileName):
        if not hasattr(self, "currentSession"):
            raise ValueError("Need to create a new Session First.")
        filePath = self.__initSimResultFile(fileName)
        with open(filePath, "a") as openFile:
            openFile.write(writeStr)
        openFile.close()
        print("Simulation result successfully stored in {}.dat".format(self.currentSession + "/" + fileName))



def main():
    fileUtils = FileUtils()
    fileUtils.createNewSession()
    fileUtils.writeSimResult("hello", fileName = "test")
    # maxRange = calcMaxRange(Ptx, GL, sens, freq)
    # print("max range is: {}km".format(maxRange))
    


if __name__ == '__main__':
    main()

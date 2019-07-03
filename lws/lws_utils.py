import math
import numpy as np
import random
import subprocess
import json
import os 
import datetime 
from lws.region_params import RegionalParams


def calc_ALOHA_DER(num_transmitters, air_time, trans_rate):
    # most basic DER calculation with ALOHA
    der = np.exp(-2 * num_transmitters * air_time * trans_rate)
    return der

def calc_max_range(Ptx, GL, sens, freq):
    beforeLog = (Ptx + GL - sens - 32.4) / 20 -  math.log10(freq)
    maxRange = math.pow(10, (beforeLog))
    return maxRange

# this function computes the airtime of a packet
# according to LoraDesignGuide_STD.pdf
def airtime(sf, cr, pl, bw):
    H = 0        # implicit header disabled (H=0) or not (H=1)
    DE = 0       # low data rate optimization enabled (=1) or not (=0)
    Npream = 8   # number of preamble symbol (12.25  from Utz paper)

    if bw == 125 and sf in [11, 12]:
        # low data rate optimization mandated for BW125 with SF11 and SF12
        DE = 1
    if sf == 6:
        # can only have implicit header with SF6
        H = 1

    Tsym = (2.0**sf)/bw
    Tpream = (Npream + 4.25)*Tsym
    print("sf", sf, " cr", cr, "pl", pl, "bw", bw)
    payloadSymbNB = 8 + \
        max(math.ceil((8.0*pl-4.0*sf+28+16-20*H)/(4.0*(sf-2*DE)))*(cr+4), 0)
    Tpayload = payloadSymbNB * Tsym
    return Tpream + Tpayload
    

def generate_random_end_device_positions(num_end_devices, max_dist, bs_x, bs_y):
    device_pos_arr = []

    for _ in range(num_end_devices):
        found = False
        rounds = 0
        pos_x = 0.0
        pos_y = 0.0 
        while found == False and rounds < 100:
            a = random.random()
            b = random.uniform(a,1.0)

            pos_x = b * max_dist * math.cos(2 * math.pi * a/b) + bs_x
            pos_y = b * max_dist * math.sin(2 * math.pi * a/b) + bs_x

            if device_pos_arr:
                for device_pos in device_pos_arr:
                    x, y, _ = device_pos
                    dist = np.sqrt(abs(x - pos_x) ** 2 + abs(y - pos_y) ** 2)
                    if dist >= 1:
                        found = True
                        save_x = pos_x
                        save_y = pos_y
                    else:
                        rounds += 1
                        if rounds == 100:
                            print("Could not place a new node randomly due to tight spaces")
                            exit(-1)
            else:
                save_x = pos_x
                save_y = pos_y
                found = True

        dist_to_bs = np.sqrt(abs(save_x - bs_x) ** 2 + abs(save_y - bs_y) ** 2) 
        device_pos_arr.append((save_x, save_y, dist_to_bs))
    
    return device_pos_arr


class FileUtils(object):
#creates a subfolder in the sim_result folder for different simulation session
#can be inherited to change the dateformat which is the prefix for the subfolders. can also change the headline for the result file to indicate the columns (TODO: modify this class to output a csv file instead of a .dat file)

    simResultFolderPath = os.path.join(os.getcwd(), "sim_result")
    dateFormat = '%Y-%m-%d-%H-%M-%S'
    resultHeadLine = "nrNodes nrCollisions nrLost pktsSent OverallEnergy DER Retransmissions RetransmissionRate\r\n"

    def _createResultFolder(self):
        if not os.path.exists(self.simResultFolderPath):
            os.mkdir(self.simResultFolderPath)

    def createNewSession(self, sessionName = ""):
        self.currentSession = sessionName + datetime.datetime.now().strftime(self.dateFormat)
        self._createResultFolder()
        self._currentSessionPath = os.path.join(self.simResultFolderPath, self.currentSession)
        os.mkdir(os.path.join(self.simResultFolderPath, self.currentSession))

    @property
    def currentSessionPath(self):
        return self._currentSessionPath

    def _initSimResultFile(self, fileName):
        self.currentFileName = fileName + ".dat"
        f = os.path.join(self._currentSessionPath, self.currentFileName)
        if not os.path.isfile(f):
            with open(f, "a") as openFile:
                openFile.write(self.resultHeadLine)
            openFile.close()
        return f

    def writeSimResult(self, writeStr, fileName):
        if not hasattr(self, "currentSession"):
            raise ValueError("Need to create a new Session First.")
        filePath = self._initSimResultFile(fileName)
        with open(filePath, "a") as openFile:
            openFile.write(writeStr)
        openFile.close()
        print("Simulation result successfully stored in {}.dat".format(self.currentSession + "/" + fileName))

class ConfigReader(object):
    #Read a json config file lora_sim_config.json

    # this is an array with measured values for sensitivity
    # see paper, Table 3
    sf7 = np.array([7, -126.5, -124.25, -120.75])
    sf8 = np.array([8, -127.25, -126.75, -124.0])
    sf9 = np.array([9, -131.25, -128.25, -127.5])
    sf10 = np.array([10, -132.75, -130.25, -128.75])
    sf11 = np.array([11, -134.5, -132.75, -128.75])
    sf12 = np.array([12, -133.25, -132.25, -132.25])

    def __init__(self, configPath):
        with open(configPath) as f:
            self.__configData = json.load(f)

        self.__setRegionFrequencies()
        self.__calcAdditionalParams()

    def __setRegionFrequencies(self):
        #TODO: these frequencies need to be more detailed
        #can use https://www.thethingsnetwork.org/docs/lorawan/frequency-plans.html as reference
        #also add auto sf and bw selection
        if self.region == "AU":
            self.__configData["centreFreqList"] = RegionalParams.AU_FREQ
            # [915e+6, 916e+6, 917e+6, 918e+6]
        elif self.region == "EU":
            self.__configData["centreFreqList"] = [
                860e+6, 864e+6, 867e+6, 868e+6]
        else:
            raise NotImplementedError

    def __calcAdditionalParams(self):
        self.__configData["sensitivityList"] = np.array(
            [self.sf7, self.sf8, self.sf9, self.sf10, self.sf11, self.sf12])
        if self.experiment in [0, 1, 4]:
            # 5th row is SF12, 2nd column is BW125
            self.__configData["minSens"] = self.__configData["sensitivityList"][5, 2]
        elif self.experiment == 2:
            # no experiments, so value from datasheet (change to SX1276's value)
            self.__configData["minSens"] = -112.0
        elif self.experiment in [3, 5]:
            # Experiment 3 can use any setting, so take minimum
            self.__configData["minSens"] = np.amin(
                self.__configData["sensitivityList"])

        self.__configData["Lpl"] = self.pTx - self.__configData["minSens"]

        
        if self.useAutoMaxDist is True:
            #calculate the maximum distance of lorawan using the urban pathloss model
            self.__configData["maxDist"] = self.d0 * \
                (math.e**((self.Lpl-self.Lpld0)/(10.0*self.gamma)))

        self.__configData["bsX"] = self.maxDist + 10
        self.__configData["bsY"] = self.maxDist + 10
        self.__configData["xMax"] = self.bsX + self.maxDist + 20
        self.__configData["yMax"] = self.bsY + self.maxDist + 20

    @property
    def region(self):
        return self.__configData["region"]

    @property
    def experiment(self):
        return self.__configData["experiment"]

    @experiment.setter 
    def experiment(self,value):
        self.__configData["experiment"] = value
        
    @property
    def configData(self):
        return self.__configData

    @property
    def sensitivityList(self):
        return self.__configData["sensitivityList"]

    @property
    def fullCollision(self):
        return self.__configData["fullCollision"]

    @property
    def pktLen(self):
        return self.__configData["pktLen"]

    @property
    def maxBSReceives(self):
        return self.__configData["maxBSReceives"]

    @property
    def graphics(self):
        return self.__configData["graphics"]

    @property
    def gamma(self):
        return self.__configData["gamma"]

    @property
    def d0(self):
        return self.__configData["d0"]

    @property
    def var(self):
        return self.__configData["var"]

    @property
    def Lpld0(self):
        return self.__configData["Lpld0"]

    @property
    def GL(self):
        return self.__configData["GL"]

    @property
    def Lpl(self):
        return self.__configData["Lpl"]

    @property
    def maxDist(self):
        return self.__configData["maxDist"]

    @maxDist.setter
    def maxDist(self, value):
        self.__configData["maxDist"] = value

    @property
    def bsX(self):
        return self.__configData["bsX"]

    @property
    def bsY(self):
        return self.__configData["bsY"]

    @property
    def xMax(self):
        return self.__configData["xMax"]

    @property
    def yMax(self):
        return self.__configData["yMax"]

    @property
    def undergroundEnv(self):
        return self.__configData["undergroundEnv"]

    @property
    def burialDepth(self):
        return self.__configData["burialDepth"]

    @burialDepth.setter
    def burialDepth(self, value):
        self.__configData["burialDepth"] = value

    @property
    def baseStationHeight(self):
        return self.__configData["baseStationHeight"]

    @property
    def vwc(self):
        return self.__configData["vwc"]

    @vwc.setter
    def vwc(self, value):
        self.__configData["vwc"] = value

    @property
    def bulkDensity(self):
        return self.__configData["bulkDensity"]

    @property
    def particleDensity(self):
        return self.__configData["particleDensity"]

    @property
    def sandFrac(self):
        return self.__configData["sandFrac"]

    @sandFrac.setter
    def sandFrac(self, value):
        self.__configData["sandFrac"] = value

    @property
    def clayFrac(self):
        return self.__configData["clayFrac"]

    @clayFrac.setter
    def clayFrac(self, value):
        self.__configData["clayFrac"] = value

    @property
    def useAutoMaxDist(self):
        return self.__configData["useAutoMaxDist"]

    @property
    def nodeSF(self):
        return self.__configData["nodeSettings"]["SF"]
    
    @property
    def nodeCR(self):
        return self.__configData["nodeSettings"]["CR"]
    
    @property
    def nodeBW(self):
        return self.__configData["nodeSettings"]["BW"]

    @property
    def pTx(self):
        return self.__configData["nodeSettings"]["pTx"]

    @property
    def numNodeRetransmissions(self):
        return self.__configData["nodeSettings"]["numRetransmissions"]

    @property
    def centreFreqList(self):
        return self.__configData["centreFreqList"]

    @property
    def numNodes(self):
        return self.__configData["simulationParams"]["numNodes"]

    @numNodes.setter
    def numNodes(self, value):
        self.__configData["simulationParams"]["numNodes"] = value

    @property
    def numBasestations(self):
        return self.__configData["simulationParams"]["numBasestations"]
    
    @property
    def avgSendTime(self):
        #in minutes
        return self.__configData["simulationParams"]["avgSendTime"]
    
    @property
    def simTime(self):
        #in hours
        return self.__configData["simulationParams"]["simTime"]
    
    @property
    def pathLossModelType(self):
        return self.__configData["simulationParams"]["pathLossModelType"]

    @pathLossModelType.setter
    def pathLossModelType(self, value):
        self.__configData["simulationParams"]["pathLossModelType"] = value

    @property
    def experimentDataMultiplier(self):
        return self.__configData["simulationParams"]["experimentDataMultiplier"]

    @property
    def RX1_DELAY(self):
        return self.__configData["nodeSettings"]["RX1_DELAY"]
    
    @property
    def RX2_DELAY(self):
        return self.__configData["nodeSettings"]["RX2_DELAY"]

    @property
    def ACKPercentage(self):
        return self.__configData["ACKSettings"]["ACKPercentage"]

    @ACKPercentage.setter
    def ACKPercentage(self, value):
        self.__configData["ACKSettings"]["ACKPercentage"] = value

    @property
    def enableACKTest(self):
        return self.__configData["ACKSettings"]["enableACKTest"]
    
    @property
    def nodeSens(self):
        return self.__configData["nodeSettings"]["sensitivity"]
    
    @property
    def enableDutyCycle(self):
        return self.__configData["dutyCycleSettings"]["enableDutyCycle"]

    @property
    def dutyCycleAmount(self):
        return self.__configData["dutyCycleSettings"]["dutyCycleAmount"]

    def __str__(self):
        return str(self.__configData)




if __name__ == '__main__':
    fileUtils = FileUtils()
    fileUtils.createNewSession()
    fileUtils.writeSimResult("hello", fileName = "test")

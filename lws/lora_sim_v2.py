"""
Trying to improve the code quality of LoRaSim in "Do LoRa Low-Power Wide-Area Networks Scale?" Martin Bor, Utz Roedig, Thiemo Voigt
 and Juan Alonso, MSWiM '16, http://dx.doi.org/10.1145/2988287.2989163
Also, this will incoporate underground path loss model for a underground LoRa sensor network simulation.
AUTHOR: SEAN WU
"""

import simpy
import random
import numpy as np
import math
import sys
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_pdf import PdfPages
import os
import subprocess
from enum import Enum

from path_loss_model import soil_path_loss_model, free_space_path_loss_model
from pprint import pprint
from lora_sim_utils import *
from region_params import RegionalParams



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


def checkPacketLoss(rssi, sens):
    if rssi < sens:
        return True
    return False


def generateRandomNodePos(numNodes, maxDist, bsX, bsY):
    nodePosArr = []
    for i in range(numNodes):
        found = 0
        rounds = 0
        nodeX = 0.0
        nodeY = 0.0
        while(found == 0 and rounds < 100):
            a = random.random()
            b = random.random()
            if b < a:
                a, b = b, a
            posx = b*maxDist * math.cos(2*math.pi*a/b)+bsX
            posy = b*maxDist * math.sin(2*math.pi*a/b)+bsX
            if len(nodePosArr) > 0:
                for nodePos in nodePosArr:
                    dist = np.sqrt(
                        ((abs(nodePos[0]-posx))**2) + ((abs(nodePos[1]-posy))**2))
                    if dist >= 1:
                        found = 1
                        nodeX = posx
                        nodeY = posy
                    else:
                        rounds = rounds + 1
                        if rounds == 100:
                            print("could not place new node, giving up")
                            exit(-1)
            else:
                nodeX = posx
                nodeY = posy
                found = 1

        nodeDist = np.sqrt((nodeX-bsX)*(nodeX - bsX) + (nodeY-bsY)*(nodeY - bsY))
        nodePosArr.append([nodeX, nodeY, nodeDist])
    return nodePosArr

# check for collisions at base station
# Note: called before a packet (or rather node) is inserted into the list
def checkCollision(packet, packetsAtBS, maxBSReceives, fullCollision, currentTime):
    col = False  # flag needed since there might be several collisions for packet
    processing = 0
    for i in range(0, len(packetsAtBS)):
        if packetsAtBS[i].packet.processed == True:
            processing = processing + 1
    if (processing > maxBSReceives):
        print("too long:" + len(packetsAtBS))
        packet.processed = False
    else:
        packet.processed = True

    if packetsAtBS:
        print("CHECK node {} (sf:{} bw:{} freq:{:.6e}) others: {}".format(
            packet.nodeId, packet.sf, packet.bw, packet.freq,
            len(packetsAtBS)))
        for other in packetsAtBS:
            if other.nodeId != packet.nodeId:
                pass
                # print ">> node {} (sf:{} bw:{} freq:{:.6e})".format(other.nodeId, other.packet.sf, other.packet.bw, other.packet.freq)
            # simple collision
            if frequencyCollision(packet, other.packet) and sfCollision(packet, other.packet):
                if fullCollision:
                    if timingCollision(packet, other.packet, currentTime):
                        # check who collides in the power domain
                        c = powerCollision(packet, other.packet)
                        # mark all the collided packets
                        # either this one, the other one, or both
                        for p in c:
                            p.collided = True
                            if p == packet:
                                col = True
                    else:
                        # no timing collision, all fine
                        pass
                else:
                    packet.collided = True
                    other.packet.collided = True  # other also got lost, if it wasn't lost already
                    col = True
        return col
    return False


def frequencyCollision(p1, p2):
        if (abs(p1.freq-p2.freq) <= 120 and (p1.bw == 500 or p2.freq == 500)):
            print("frequency coll 500")
            return True
        elif (abs(p1.freq-p2.freq) <= 60 and (p1.bw == 250 or p2.freq == 250)):
            print("frequency coll 250")
            return True
        else:
            if (abs(p1.freq-p2.freq) <= 30):
                print("frequency coll 125")
                return True
            #else:
        print("no frequency coll")
        return False

def sfCollision(p1, p2):
    if p1.sf == p2.sf:
        print("collision sf node {} and node {}".format(p1.nodeId, p2.nodeId))
        # p2 may have been lost too, will be marked by other checks
        return True
    print("no sf collision")
    return False

def powerCollision(p1, p2):
    powerThreshold = 6  # dB
    print("pwr: node {0.nodeId} {0.rssi:3.2f} dBm node {1.nodeId} {1.rssi:3.2f} dBm; diff {2:3.2f} dBm".format(
        p1, p2, round(p1.rssi - p2.rssi, 2)))
    if abs(p1.rssi - p2.rssi) < powerThreshold:
        print("collision pwr both node {} and node {}".format(
            p1.nodeId, p2.nodeId))
        # packets are too close to each other, both collide
        # return both packets as casualties
        return (p1, p2)
    elif p1.rssi - p2.rssi < powerThreshold:
        # p2 overpowered p1, return p1 as casualty
        print("collision pwr node {} overpowered node {}".format(
            p2.nodeId, p1.nodeId))
        return (p1,)
    print("p1 wins, p2 lost")
    # p2 was the weaker packet, return it as a casualty
    return (p2,)

def timingCollision(p1, p2, currentTime):
        # assuming p1 is the freshly arrived packet and this is the last check
        # we've already determined that p1 is a weak packet, so the only
        # way we can win is by being late enough (only the first n - 5 preamble symbols overlap)

        # assuming 8 preamble symbols
    Npream = 8

    # we can lose at most (Npream - 5) * Tsym of our preamble
    Tpreamb = 2**p1.sf/(1.0*p1.bw) * (Npream - 5)

    # check whether p2 ends in p1's critical section
    p2_end = p2.addTime + p2.rectime
    p1_cs = currentTime + Tpreamb
    print("collision timing node {} ({},{},{}) node {} ({},{})".format(
        p1.nodeId, currentTime - currentTime, p1_cs - currentTime, p1.rectime,
        p2.nodeId, p2.addTime - currentTime, p2_end - currentTime))
    if p1_cs < p2_end:
        # p1 collided with p2 and lost
        print("not late enough")
        return True
    print("saved by the preamble")
    return False


class PacketType(Enum):
    Data = 1
    DataAck = 2
    ACK = 3
    LinkCheckReq = 4
    LinkCheckAns = 5
    LinkADRReq = 6
    LinkADRAns = 7
    DutyCycleReq = 8
    DutyCycleAns = 9
    RXParamsSetupReq = 10
    RXParamSetupAns = 11
    DevStatusReq = 12
    DevStatusAns = 13
    NewChaneelReq = 14
    NewChannelAns = 15
    RXTimingSetupReq = 16
    RXTimingSetupAns = 17

#provides frequency slot calculation for dutycycle regulation
class FrequencySlot(object):
    def __init__(self, freq, dutyCycle):
        self.freq = freq 
        self.dutyCycle = dutyCycle
        self.lastTransmissionTime = -1
        self.lastOffTime = -1
        self.lastPeriod = -1
        
    def isChannelFree(self, node, currentTime):
        period = node.airTime/self.dutyCycle
        offTime = period - node.airTime

        #first transmission
        if currentTime == -1:
            self.lastTransmissionTime = currentTime
            self.lastPeriod = period
            self.lastOffTime = offTime
            return True
        
        timeGap = currentTime - self.lastTransmissionTime
        #still in the off period or still transmission
        if timeGap < self.lastPeriod:
            print("currentGap: {}, lastPeriod: {}, currentTime: {}".format(timeGap, self.lastPeriod, currentTime))
            return False
        else:
            self.lastTransmissionTime = currentTime
            self.lastPeriod = period
            self.lastOffTime = offTime
            return True



#Basestation class
#Responsible for receiving uplink to node and send downlink to node.
#does collision and packetloss check as well 
class Basestation():
    def __init__(self, config, baseID):
        
        self.config = config
        self.baseID = baseID 
        self.packetsAtBS = []
        self.__processedPacketCount = 0 
        self.__receivedPacketCount = 0
        self.setRegionalFreqChannels()

    def setRegionalFreqChannels(self):
        self.channelSlots = {}
        for c in self.config.centreFreqList:
            self.channelSlots[c] = FrequencySlot(c, self.config.dutyCycleAmount)
        

    def scheduleDownlink(self, node, currentTime):
        currentFreqSlot = self.channelSlots[node.freq]
        if currentFreqSlot.isChannelFree(node, currentTime):
            # self.sendDownlink(node)
            return True
        else:
            print("CURRENTLY BUSY")
            return False



    def receiveUplink(self, node, currentTime):
        self.sensitivity = self.config.sensitivityList[node.packet.sf - 7, [125, 250, 500].index(node.packet.bw) + 1]
        node.sent = node.sent + 1
        if (node in self.packetsAtBS):
            print("ERROR: packet already in")
        else:
            if checkPacketLoss(node.packet.rssi, self.sensitivity):
                print("node {}: packet will be lost".format(node.nodeId))
                node.packet.lost = True
            else:
                node.packet.lost = False
                # adding packet if no collision
                if (checkCollision(node.packet, self.packetsAtBS, self.config.maxBSReceives, self.config.fullCollision, currentTime)):
                    node.packet.collided = True
                else:
                    node.packet.collided = False
                # packet arrives -> add to base station
                self.packetsAtBS.append(node)
                node.packet.addTime = currentTime
    
    def needDownlink(self, node):
        if node.packet.packetType != PacketType.Data:
            return True
        else:
            return False
    
    def saveTransmissionResult(self, node):
        if node.packet.processed:
            self.__processedPacketCount += 1

        if node.packet.lost:
            node.packetLossCount += 1
        elif node.packet.collided:
            node.packetCollisionCount += 1
        else:
            self.__receivedPacketCount += 1

    def correctReceivedPacketCount(self):
        if self.__receivedPacketCount > 0:
            self.__receivedPacketCount -= 1
                
    def removeCompletedNode(self, node):
        if (node in self.packetsAtBS):
            self.packetsAtBS.remove(node)       

    def sendDownlink(self, node, rxInterval):
        packet = Packet(self.baseID, self.config.pktLen, node.dist, self.config, packetType = PacketType.ACK)
        node.receiveDownlink(packet, rxInterval)

    @property
    def receivedPacketCount(self):
        return self.__receivedPacketCount
    
    @property
    def processedPacketCount(self):
        return self.__processedPacketCount
    

class Node():
    def __init__(self, nodeId, period, x, y, dist, config, packetType = PacketType.Data):
        self.nodeId = nodeId
        self.period = period
        self._x = x
        self._y = y
        self.packetLen = config.pktLen
        self.dist = dist
        self.sent = 0
        self.config = config
        self.packetLossCount = 0 
        self.packetCollisionCount = 0
        self.retransmissionCount = 0
        self.packet = Packet(nodeId = self.nodeId, plen = self.packetLen, distance = self.dist, config = config, packetType=packetType)
        self.rx1Failed = False
        self.downlinkFailed = False
        #number of retransmissions (reset when larger than numNodeRetransmissions)
        self.currentNumOfRetransmissions = 0
        #number of lost downlink packets, this is different from basestation being busy
        self.downlinkPacketLostCount = 0

    #return True to indicate packet is not lost
    def receiveDownlink(self, packet, rxInterval):
        if not checkPacketLoss(packet.rssi, self.config.nodeSens):
            print("Downlink received, no need for retransmission")
            if rxInterval == 1:
                self.rx1Failed = False
                self.downlinkFailed = False
            elif rxInterval == 2:
                self.rx1Failed = False
                self.downlinkFailed = False
                pass
            else:
                raise NotImplementedError
        else:
            print("rx lost ")
            self.downlinkPacketLostCount += 1
    
    def scheduleRetransmission(self, rxInterval):
        if rxInterval == 1:
            self.rx1Failed = True
            
            #wait for next interval
        elif rxInterval == 2:
            if self.rx1Failed == True and self.currentNumOfRetransmissions <= self.config.numNodeRetransmissions:
                self.rx1Failed = False
                self.retransmissionCount += 1
                self.currentNumOfRetransmissions += 1
                self.downlinkFailed = True
            elif self.currentNumOfRetransmissions > self.config.numNodeRetransmissions:
                self.currentNumOfRetransmissions = 0
                self.rx1Failed = False
                self.downlinkFailed = False
            #now need retransmission
            
        

    @property
    def x(self):
        return self._x 
    
    @property
    def y(self):
        return self._y

    @property
    def freq(self):
        return self.packet.freq

    @property
    def airTime(self):
        return self.packet.rectime

    @property
    def isPacketLost(self):
        return self.packet.lost

    @property
    def isDownlinkFailed(self):
        return self.downlinkFailed

    def resetPacket(self):
        self.packet.collided = False
        self.packet.processed = False 
        self.packet.lost = False
        
    def __eq__(self, other):
        return self.nodeId == other.nodeId

    def __str__(self):
        return ("Node [{}] x:{}, y:{}".format(self.nodeId, self._x, self._y))




class Packet():
    def __init__(self, nodeId, plen, distance, config, packetType = PacketType.Data):
        self.nodeId = nodeId
        # GLOBAL: self.txpow = Ptx
        self.config = config
        self.distance = distance
        self.pl = plen
        self.collided = False
        self.processed = False
        self.lost = False
        self.pathLossModel = soil_path_loss_model(config.vwc, config.bulkDensity, config.particleDensity, config.sandFrac, config.clayFrac)
        self.packetType = packetType
        self.__setLoRaParams()
        self.__setFreq()
        self.__calcPathLoss()

    def __calcPathLoss(self):
        if not self.config.undergroundEnv:
            Lpl = self.config.Lpld0 + 10 * self.config.gamma * math.log10( self.distance / self.config.d0)
            self.rssi = self.txPow - self.config.GL - Lpl
        else:
            #path loss = path loss from soil + path loss from air
            if self.config.pathLossModelType == "simple":
                pathloss = self.pathLossModel.calc_simple_underground_pathloss(self.freq, self.config.burialDepth, self.distance, self.config.baseStationHeight)
            elif self.config.pathLossModelType == "approximated":
                pathloss = self.pathLossModel.calc_approximated_path_loss(self.freq, self.config.burialDepth, self.distance, self.config.baseStationHeight)
            elif self.config.pathLossModelType == "experimentData":
                pathloss = self.pathLossModel.calc_approximated_path_loss(self.freq, self.config.burialDepth, self.distance, self.config.baseStationHeight) * self.config.experimentDataMultiplier
            else:
                raise NotImplementedError
            self.rssi = self.txPow - self.config.GL - pathloss
            print("pathloss = {}, rssi = {}, distance = {}\r\n".format(pathloss, self.rssi, self.distance ))
            
    
    def __setFreq(self):
        if self.config.experiment == 1:
            self.freq = random.choice(self.config.centreFreqList)
            # self.freq = random.choice([860000000, 864000000, 868000000])
        else:
            self.freq = self.config.centreFreqList[0]
            # self.freq = 860000000

    def __setLoRaParams(self):
        self.sf = self.config.nodeSF
        self.cr = self.config.nodeCR 
        self.bw = self.config.nodeBW
        self.txPow = self.config.pTx
        # if self.config.experiment == 1 or self.config.experiment == 0:
        #     self.sf = 12
        #     self.cr = 4
        #     self.bw = 125
        # elif self.config.experiment == 2:
        #     self.sf = 6
        #     self.cr = 1
        #     self.bw = 500
        # # lorawan
        # elif self.config.experiment == 4:
        #     self.sf = 12
        #     self.cr = 1
        #     self.bw = 125
        # else:
        #     # randomize configuration values
        #     self.sf = random.randint(6, 12)
        #     self.cr = random.randint(1, 4)
        #     self.bw = random.choice([125, 250, 500]) 
        # self.txPow = self.config.pTx
        # transmission range, needs update XXX
        self.transRange = 150
        self.symTime = (2.0**self.sf)/self.bw
        self.arriveTime = 0
        self.rectime = airtime(self.sf, self.cr, self.pl, self.bw)

    def __str__(self):
        return ("Sent from node[{}], rssi: {}, sf: {}, cr: {}, bw: {}, symbol time: {}, airtime: {}".format(self.nodeId, self.rssi, self.sf, self.cr, self.bw, self.symTime, self.rectime))


class States(Enum):
    NodeTransmitting = 1
    ParseNodePacket = 2
    NodeSleep = 3
    BasestationReply = 4


class LoRaSim():
    def __init__(self, config, readParamsFromConfig = False, numNodes = None, numBasestations = None, avgSendTime = None, simtime = None, nodePosArr = None):
        self.env = simpy.Environment()
        
        self.nrLost = 0
        self.nrCollisions = 0
        self.nrReceived = 0
        self.nrProcessed = 0
        self.packetsAtBS = []
        if readParamsFromConfig:
            self.numNodes = config.numNodes
            self.numBasestations = config.numBasestations
            self.avgSendTime = int(config.avgSendTime * 1000 * 60) #min to ms
            self.simtime = int(config.simTime * 60 * 60 * 1000) #hour to ms
        else:
            if numNodes == None or numBasestations == None or avgSendTime == None or simtime == None:
                raise ValueError
            else:
                self.numNodes = numNodes
                self.numBasestations = numBasestations
                self.avgSendTime = avgSendTime
                self.simtime = simtime
        self.config = config
        
        
        self.baseStation = Basestation(config, "B0")
        self.__initNodes(nodePosArr)

    def __initNodes(self, nodePosArr = None):
        self.nodes = []
        limit = 0
        if nodePosArr == None:
            #generate node positions if nodePosArr is not provided in the constructor
            nodePosArr = generateRandomNodePos(self.numNodes, self.config.maxDist, self.config.bsX, self.config.bsY)
        
        if self.config.enableACKTest:
            limit = int(self.numNodes * self.config.ACKPercentage)
        #generate from nodePosArr which has the structure of [[nodeX0, nodeY0, nodeDist0], [nodeX1, nodeY1, nodeDist1] ... ]
        for i, nPos in enumerate(nodePosArr):
            if i < limit:
                pktType = PacketType.DataAck
            else:
                pktType = PacketType.Data
            self.nodes.append(Node(i, self.avgSendTime, nPos[0], nPos[1], nPos[2], self.config, packetType=pktType))
        pprint([str(n) for n in self.nodes])


    def transmit(self, env, node):
        while True:
            #random sending time
            yield env.timeout(random.expovariate(1.0/float(node.period)))

            self.baseStation.receiveUplink(node, env.now)
            self.baseStation.saveTransmissionResult(node)

            #airtime
            yield env.timeout(node.packet.rectime)

            if not node.isPacketLost:
                if self.baseStation.needDownlink(node):

                    #RX INTERVAL 1
                    yield env.timeout(self.config.RX1_DELAY)
                    
                    if self.baseStation.scheduleDownlink(node, env.now):
                        self.baseStation.sendDownlink(node, 1)
                        print("RX1 SUCCESSFULLY TRANSMITTED")
                    else:
                        node.scheduleRetransmission(1)
                        print("RX1 FAILED")

                    #RX INTERVAL 2
                    yield env.timeout(self.config.RX2_DELAY)

                    if self.baseStation.scheduleDownlink(node, env.now):
                        self.baseStation.sendDownlink(node, 2)
                        print("RX2 SUCCESSFULLY TRANSMITTED")
                    else:
                        node.scheduleRetransmission(2)
                        print("RX2 FAILED")
                    
                    if node.isDownlinkFailed:
                        self.baseStation.correctReceivedPacketCount()



            node.resetPacket()

            self.baseStation.removeCompletedNode(node)

            

    
    def startSimluation(self):
        for n in self.nodes:
            self.env.process(self.transmit(self.env,n))

        self.env.run(until = self.simtime)
    
    def sumNodeStats(self):
        nrLost = sum(n.packetLossCount for n in self.nodes)
        nrCollisions = sum(n.packetCollisionCount for n in self.nodes)
        nrRetransmissions = sum(n.retransmissionCount for n in self.nodes)
        nrDownlinksLost = sum(n.downlinkPacketLostCount for n in self.nodes)
        return nrLost, nrCollisions, nrRetransmissions, nrDownlinksLost

    def printSimResult(self):
        self.nrLost, self.nrCollisions, self.nrRetransmissions, self.nrDownlinksLost = self.sumNodeStats()
        self.nrReceived = self.baseStation.receivedPacketCount
        self.nrProcessed = self.baseStation.processedPacketCount
        self.resultDict = {}
        self.resultDict["pktsReceived"] = self.nrReceived
        print(" ================= \r\n")

        self.resultDict["pktsSent"] = sum(n.sent for n in self.nodes)
        
        print("Total packets sent: {}\r\n".format(self.resultDict["pktsSent"]))
        print("Packets Lost: {}\r\nPackets Collided: {}\r\nNumber of Packets Sent: {}\r\nNumber of Retransmissions: {}\r\nDownlink packet loss: {}\r\n".format(self.nrLost, self.nrCollisions, self.resultDict["pktsSent"], self.nrRetransmissions, self.nrDownlinksLost))
        # self.resultDict["der"] = (self.resultDict["pktsSent"] - self.nrCollisions)/float(self.resultDict["pktsSent"])
        self.resultDict["der"] = self.nrReceived / float(self.resultDict["pktsSent"])
        print("DER: {}\r\n".format(self.resultDict["der"]))

        self.resultDict["retransmissionRate"] = self.nrRetransmissions / float(self.resultDict["pktsSent"])
        print("Retransmission Rate: {}\r\n".format(self.resultDict["retransmissionRate"]))

        print(" ================= \r\n")

    
    
    def writeSimResult(self, f):
        fileUtils = FileUtils()
        result = self.getSimResultStr()
        fileUtils.writeSimResult(result, f)
        
    def getSimResultStr(self):
        return "{} {} {} {} {} {} {} {}\r\n".format(self.numNodes, self.nrCollisions, self.nrLost, self.resultDict["pktsSent"], "0", self.resultDict["der"], self.nrRetransmissions, self.resultDict["retransmissionRate"])

    def showGraphics(self):
        plt.ion()
        fig = plt.figure()
        ax = plt.gcf().gca()

        # ax.add_artist(plt.((self.config.bsX, self.config.bsY) ,1 , fill=True, color = 'green'))
        plt.plot(self.config.bsX, self.config.bsY, marker='x')
        ax.add_artist(plt.Circle((self.config.bsX, self.config.bsY), self.config.maxDist, fill = False, color='green' ))

        for n in self.nodes:
            ax.add_artist(plt.Circle((n.x, n.y), 0.1, fill=True, color = 'blue'))

        
        plt.axis('equal')
        plt.xlim([0, self.config.xMax])
        plt.ylim([0, self.config.yMax])
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.draw()
        plt.show()
        return fig


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




def main():
    configFile = "lora_sim_config.json"

    config = ConfigReader(configFile)
    # pprint(config.configData)

    avg_send_interval = 10 #10 mins interval
    send_interval_ms = str(int(avg_send_interval * 60 * 1000))
    sim_time = 24 * 60 #one day
    sim_time_ms = str(sim_time * 60 * 1000)

    sim = LoRaSim(config = config, readParamsFromConfig = True)
    sim.startSimluation()
    sim.printSimResult()
    # sim.writeSimResult("lora_sim")
    fileUtils = FileUtils()
    fileUtils.createNewSession()
    fileUtils.writeSimResult(sim.getSimResultStr(), "lorasimTest")
    if config.graphics == 1:
        sim.showGraphics()
        input("press Enter to continue...")

    
        
    

    # pprint(config.configData)
    # sim.writeSimResult("test1")
    # # get arguments
    # if len(sys.argv) >= 5:
    #     nrNodes = int(sys.argv[1])
    #     avgSendTime = int(sys.argv[2])
    #     experiment = int(sys.argv[3])
    #     simtime = int(sys.argv[4])
    #     if len(sys.argv) > 5:
    #         full_collision = bool(int(sys.argv[5]))
    #     print "Nodes:", nrNodes
    #     print "AvgSendTime (exp. distributed):", avgSendTime
    #     print "Experiment: ", experiment
    #     print "Simtime: ", simtime
    #     print "Full Collision: ", full_collision
    # else:
    #     print "usage: ./loraDir <nodes> <avgsend> <experiment> <simtime> [collision]"
    #     print "experiment 0 and 1 use 1 frequency only"
    #     exit(-1)

if __name__ == '__main__':
    main()

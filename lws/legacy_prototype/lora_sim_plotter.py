import math
import numpy as np
import matplotlib.pyplot as plt
import subprocess
from matplotlib.backends.backend_pdf import PdfPages
from plot_utils import *
from lora_sim_v2 import *
from lora_sim_utils import *

TIME_ON_AIR = 1712.13
PACKET_RATE = 1e-6

#variables that will be replaced to proper names with unit during plotting
plottingNames = {   "vwc"           :   "VWC(%)",
                    "burialDepth"   :   "Burial Depth(m)",
                    "maxDist"       :   "Deployment Radius(m)",
                    "numNodes"      :   "Number of Nodes",
                    "ACKPercentage" :   "ACK Rate(%)"}


# def calc_ALOHA_DER(num_transmitters, air_time, trans_rate):
#     # most basic DER calculation with ALOHA
#     der = np.exp(-2 * num_transmitters * air_time * trans_rate)
#     return der


def calc_batch_ALOHA_DER(num_nodes_arr):
    result_arr = [] 
    for n in num_nodes_arr:
        current_result = calc_ALOHA_DER(n, TIME_ON_AIR, PACKET_RATE)
        result_arr.append(current_result)

    return result_arr



def add_plot_data(num_nodes, sim_data, sim_name, exp_type):
    plt.plot(num_nodes, sim_data[sim_name], label="SN" + str(exp_type))
    
def plot_sim_data(num_nodes,sim_name, exp_type):
    fig = plt.figure()
    if sim_name == 'DER':
        aloha_arr = calc_batch_ALOHA_DER(num_nodes)
        # plt.plot(num_nodes, aloha_arr, label = "ALOHA result")
        # plt.plot(num_nodes, sim_data[sim_name], label = "SN" + str(exp_type))
    else:
        pass
        # plt.plot(num_nodes, sim_data[sim_name], label = "SN" + str(exp_type))

    plt.xlabel("Number of nodes")
    plt.ylabel(sim_name)
    plt.grid()

    plt.legend(loc=2, ncol=3, mode="expand", shadow=True, fancybox=True)

    plt.show()

class lora_sim_wrapper():
    #wrapper class for calling lora_sim more conveniently (and for the potential refactoring in the future)
    lora_sim_path = 'lorasim/'
    single_base_sim_name = 'loraDir.py'

    def __init__(self):
        pass
        
    def clean_previous_data(self):
        try:
            subprocess.check_call(["rm", "exp*.dat"])
            print("Previous simiulation data deleted.")
        except subprocess.CalledProcessError as e:
            pass
        


    def single_simulation(self, sim_type, num_nodes, avg_send_interval, exp_type, sim_time, collision):
        if sim_type == "single_base":
            complete_path = self.lora_sim_path + self.single_base_sim_name
            print(complete_path)
            send_interval_ms = str(int(avg_send_interval * 60 * 1000))
            sim_time_ms = str(sim_time * 60 * 1000)
            subprocess.check_call(["python", complete_path, str(num_nodes), send_interval_ms, str(exp_type), sim_time_ms, str(collision)])
        else:
            print("Wrong simulation type.")
    
    def batch_simulation(self, sim_type, num_nodes_arr, avg_send_interval, exp_type, sim_time, collision):
        self.exp_type = exp_type

        for n in num_nodes_arr:
            if int(n) == 0:
                n = 1
            self.single_simulation(sim_type, int(n), avg_send_interval, exp_type, sim_time, collision)

    def get_sim_result(self, fname = None):
        if fname is None:
            fname = "exp" + str(self.exp_type) + ".dat"

        with open(fname) as f:
            content = f.readlines()
        content = [x.strip() for x in content]

        der_result = []
        collision_result = []
        retransmit_result = []

        for line in content:
            line = [x.strip() for x in line.split()]
            der_result.append(line[4])
            collision_result.append(line[1])
            retransmit_result.append(line[2])

        print (der_result)
        print (collision_result)
        print (retransmit_result)
        retDict = {}
        retDict.update({'DER': der_result,
                        'collision': collision_result,
                        'retransmit': retransmit_result})
        return retDict
        
    def get_exp_type(self):
    	return 0
        # return self.exp_type

def plot_original_sim():
    num_nodes_arr = np.linspace(10, 1600, 17)
    # plot_DER(num_nodes)
    sim_wrapper = lora_sim_wrapper()
    # sim_wrapper.clean_previous_data()
    # sim_wrapper.batch_simulation(sim_type = "single_base" , num_nodes_arr = num_nodes_arr, avg_send_interval = 16.7, exp_type = 0, sim_time = 10, collision = 1)
    sn0_sim_result = sim_wrapper.get_sim_result(fname="exp0.dat")
    fig = plt.figure()
    print(len(sn0_sim_result["DER"]))
    # plt.plot(num_nodes_arr, sn0_sim_result["DER"],label="SN" + str(sim_wrapper.get_exp_type()))
    # sim_wrapper.batch_simulation(sim_type="single_base", num_nodes_arr=num_nodes_arr,
    #                              avg_send_interval=16.7, exp_type=1, sim_time=10, collision=1)
    # sn1_sim_result = sim_wrapper.get_sim_result()
    # plt.plot(num_nodes_arr, sn1_sim_result["DER"],
    #          label="SN" + str(sim_wrapper.get_exp_type()))
    # aloha_arr = calc_batch_ALOHA_DER(num_nodes_arr)
    # plt.plot(num_nodes_arr, aloha_arr, label="ALOHA")
    # plt.xlabel("Number of nodes")
    # plt.ylabel("DER")
    # plt.grid()

    # plt.legend(loc=2, ncol=3, mode="expand", shadow=True, fancybox=True)

    # plt.show()

    # pp = PdfPages("lora_sim_result.pdf")
    # pp.savefig(fig)
    # pp.close()

def genMultiVarDictEntry(name, arr1, arr2, configDict, configFile):
    param1, param2 = name.split("&")
    configDict[name] = []
    for a1 in arr1:
        configList = []
        for a2 in arr2:
            c = ConfigReader(configFile)
            setattr(c, param1, a1)
            setattr(c, param2, a2)
            configList.append(c)
        configDict[name].append(configList)
    


def generateSimScenario(configFile, option):
    #generate a dict containing lists of configs for different simulation scenarios
    retDict = {}

    if option == "single_var":
        ##single variable for only changing one parametre at a time

        ##vwc
        vwcRange = np.linspace(0.001, 1, num=40)
        retDict["vwc"] = []
        for v in vwcRange:
            tempConfig = ConfigReader(configFile)
            tempConfig.vwc = v
            retDict["vwc"].append(tempConfig)

        ##burial depth
        depthRange = np.linspace(0.05, 5, num=40)
        retDict["burialDepth"] = []
        for d in depthRange:
            tempConfig = ConfigReader(configFile)
            tempConfig.burialDepth = d
            retDict["burialDepth"].append(tempConfig)

        ##max dist
        maxDistRange = np.linspace(3, 60, num=40)
        retDict["maxDist"] = []
        for dist in maxDistRange:
            tempConfig = ConfigReader(configFile)
            tempConfig.maxDist = dist
            retDict["maxDist"].append(tempConfig)
        
        

    elif option == "multi_var":
        ##multi variable for changing vwc and burial depth at the same time
        vwcRange = np.concatenate((np.linspace(0, 0.25, num = 6), np.linspace(0.30, 1.0, num = 8)), axis = 0)
        depthRange = np.linspace(0.01 , 3.0, num = 10)
        genMultiVarDictEntry("vwc&burialDepth", vwcRange, depthRange, retDict, configFile)
        

        # ##exp & vwc 
        # expList = [0,1]
        # vwcRange = np.linspace(0.001, 1, num=40)
        # genMultiVarDictEntry("experiment&vwc", expList, vwcRange, retDict, configFile)
       

        # depthRange = np.linspace(0.05, 5, num=40)
        # retDict["experiment&burialDepth"] = []
        # genMultiVarDictEntry("experiment&burialDepth", expList, depthRange, retDict, configFile)
        
        # ##pathlossModelType & vwc
        # pathlossModelTypeList = ["simple", "approximated"]
        # vwcRange = np.linspace(0.001, 1, num = 40)
        # genMultiVarDictEntry("pathLossModelType&vwc", pathlossModelTypeList, vwcRange, retDict, configFile)

        ## pathLossModelType & burialDepth
        # depthRange = np.linspace(0.05, 5, num = 40)
        # genMultiVarDictEntry("pathLossModelType&burialDepth", pathlossModelTypeList, vwcRange, retDict, configFile)

        # #number of nodes and ack percentage
        # ACKRateArr = np.linspace(0, 1, num=11)
        # numNodesArr = np.linspace(30, 1000, num=10, dtype=int)
        # genMultiVarDictEntry("ACKPercentage&numNodes",ACKRateArr, numNodesArr, retDict, configFile)

        ## burialdepth and maxdist
        # maxDistRange = np.linspace(3, 20000, num=10)
        # depthRange = np.concatenate(([0.05], np.linspace(0.1, 1.5, num=8)), axis=0)
        # genMultiVarDictEntry("burialDepth&maxDist", depthRange, maxDistRange, retDict, configFile)
    
    elif option == "retransmission":
        #network size with 5% ACK
        numNodesArr = np.linspace(1, 1000, num=10, dtype=int)
        ACKRateConst = 0.05
        retDict["numNodes"] = [] 
        for n in numNodesArr:
            c = ConfigReader(configFile)
            c.numNodes = n
            c.ACKPercentage = ACKRateConst
            retDict["numNodes"].append(c)
        #ACK with fixed network size
        ACKRateArr = np.linspace(0,1,num=10)
        numNodesConst = 100
        retDict["ACKPercentage"] = []
        for a in ACKRateArr:
            c = ConfigReader(configFile)
            c.ACKPercentage = a
            c.numNodes = numNodesConst
            retDict["ACKPercentage"].append(c)

        #vwc
        ACKRateConst = 0.05
        numNodesConst = 30
        vwcRange = np.linspace(0.001, 1, num=40)

        retDict["vwc"] = []
        for v in vwcRange:
            c = ConfigReader(configFile)
            c.vwc = v
            c.ACKPercentage = ACKRateConst
            c.numNodes = numNodesConst
            retDict["vwc"].append(c)
        depthRange = np.linspace(0.05, 5, num=40)
        retDict["burialDepth"] = []
        for d in depthRange:
            c = ConfigReader(configFile)
            c.burialDepth = d
            c.ACKPercentage = ACKRateConst
            c.numNodes = numNodesConst
            retDict["burialDepth"].append(c)

        ##max dist
        maxDistRange = np.linspace(3, 60, num=40)
        retDict["maxDist"] = []
        for m in maxDistRange:
            c = ConfigReader(configFile)
            c.maxDist = m
            c.ACKPercentage = ACKRateConst
            c.numNodes = numNodesConst
            retDict["maxDist"].append(c)
            

    else:
        raise NotImplementedError

    return retDict

#deprecated method due to new session folders.
def cleanPrevResult(fileName, extension):
    if os.path.isfile(fileName + extension):
        os.remove(fileName + extension)



def runSimScenario(configDict, option):
    avg_send_interval = 10  # 10 mins interval
    send_interval_ms = str(int(avg_send_interval * 60 * 1000))
    sim_time = 24 * 60  # one day
    sim_time_ms = str(sim_time * 60 * 1000)
    numNodes = 30
    numBasestations = 1
    fileUtils = FileUtils()
    fileUtils.createNewSession(option)

    if option == "single_var":
        #get first config
        firstConfig = configDict[next(iter(configDict))][0]
        nodePosArr = generateRandomNodePos(numNodes, firstConfig.maxDist, firstConfig.bsX, firstConfig.bsY)

        for scenario in configDict:
            
            for c in configDict[scenario]:
                if scenario is not "maxDist":
                    tempSim = LoRaSim(numNodes=numNodes, numBasestations=numBasestations, avgSendTime=send_interval_ms, simtime=sim_time_ms, config=c, nodePosArr=nodePosArr)
                else:
                    tempSim = LoRaSim(numNodes=numNodes, numBasestations=numBasestations, avgSendTime=send_interval_ms, simtime=sim_time_ms, config=c, nodePosArr=None)
                tempSim.startSimluation()
                tempSim.printSimResult()
                fileUtils.writeSimResult(tempSim.getSimResultStr(), fileName = scenario)
            simResult = readSimResult(fileUtils.currentSessionPath, scenario)
            paramArr = getParametreArr(configDict, scenario)
            plotSimPktsResult(fileUtils.currentSessionPath, scenario, simResult, paramArr)
            plotSimDERResult(fileUtils.currentSessionPath, scenario, simResult, paramArr)

    elif option == "multi_var":
        firstConfig = configDict[next(iter(configDict))][0][0]
        nodePosArr = generateRandomNodePos(numNodes, firstConfig.maxDist, firstConfig.bsX, firstConfig.bsY)
        for scenario in configDict:
            for cList in configDict[scenario]:
                for c in cList:
                    if "maxDist" in scenario or "numNodes" in scenario:
                        tempSim = LoRaSim(c, readParamsFromConfig=True)
                    else:
                        tempSim = LoRaSim(config=c, readParamsFromConfig=True, nodePosArr=nodePosArr)
                    tempSim.startSimluation()
                    tempSim.printSimResult()
                    fileUtils.writeSimResult(tempSim.getSimResultStr(), fileName = scenario)
                    
            labelList, paramList = getMultiVarParamArr(configDict, scenario)
            resultDict = readSimResult(fileUtils.currentSessionPath, scenario)
            plotMultiVarDERResult(fileUtils.currentSessionPath, scenario, resultDict, paramList, labelList)
    
    elif option == "retransmission":
        firstConfig = configDict[next(iter(configDict))][0]
        nodePosArr = generateRandomNodePos(numNodes, firstConfig.maxDist, firstConfig.bsX, firstConfig.bsY)
        for scenario in configDict:
            for c in configDict[scenario]:
                if scenario is "numNodes" or scenario is "maxDist":
                    tempSim = LoRaSim(c, readParamsFromConfig=True)
                else:
                    tempSim = LoRaSim(config = c, readParamsFromConfig=True, nodePosArr=nodePosArr)
                tempSim.startSimluation()
                tempSim.printSimResult()
                fileUtils.writeSimResult(tempSim.getSimResultStr(), fileName=scenario)
            simResult = readSimResult(fileUtils.currentSessionPath, scenario)
            paramArr = getParametreArr(configDict, scenario)
            plotSimRetransmittedPktsResult(fileUtils.currentSessionPath, scenario, simResult, paramArr)
            plotSimRetransmissionRateResult(fileUtils.currentSessionPath, scenario, simResult, paramArr)
            plotSimPktsResult(fileUtils.currentSessionPath,
                              scenario, simResult, paramArr)
            plotSimDERResult(fileUtils.currentSessionPath,
                             scenario, simResult, paramArr)
            
        
    
    else:
        raise NotImplementedError

def getParametreArr(configDict, paramName):
    return [getattr(p, paramName) for p in configDict[paramName]]

def getMultiVarParamArr(configDict, scenario):
    ##multi var will have 2d array
    ##sceneario:  "param1&param2" e.g. "vwc&burialDepth"
    configList = configDict[scenario]
    param0, param1 = scenario.split("&")
    labelList = []
    for clist in configList:
        labelList.append(getattr(clist[0], param0))
    paramList = [getattr(c, param1) for c in configList[0]]
    return labelList, paramList
    
            

def readSimResult(path, resultFile):
    #returns a dict of results
    with open(os.path.join(path, resultFile) + ".dat") as f:
        content = f.readlines()
    content = [x.strip() for x in content][1:]

    retDict = {}
    retDict["pktsLost"] = []
    retDict["pktsCollided"] = []
    retDict["pktsSent"] = []
    retDict["DER"] = []
    retDict["retransmittedPkt"] = []
    retDict["retransmissionRate"] = []
    for c in content:
        arr = c.split(" ")
        retDict["pktsCollided"].append(arr[1])
        retDict["pktsLost"].append(arr[2])
        retDict["pktsSent"].append(arr[3])
        retDict["DER"].append(arr[5])
        retDict["retransmittedPkt"].append(arr[6])
        retDict["retransmissionRate"].append(arr[7])

    return retDict



def plotSimPktsResult(path, name, resultDict, parametreArr):
    fig = plt.figure()
    
    plt.plot(parametreArr, resultDict["pktsLost"], label="Packets Lost")
    plt.plot(parametreArr, resultDict["pktsCollided"], label="Packets Collided")
    ymin, ymax = plt.ylim()
    plt.ylim(ymax = ymax + 500)
    plt.ylabel("Packets")
    plt.xlabel(plottingNames[name])
    plt.grid()
    plt.legend(loc=2, ncol=3, mode="expand", shadow=True, fancybox=True)
    # plt.show()
    savePlotAsPdf(path, name + "Pkts.pdf", fig)
    


def plotSimDERResult(path, name, resultDict, parametreArr):
    fig = plt.figure()
    
    plt.plot(parametreArr, resultDict["DER"])
    plt.ylim((-0.05, 1))
    plt.ylabel("DER")
    plt.xlabel(plottingNames[name])
    plt.grid()
    plt.legend(loc=2, ncol=3, mode="expand", shadow=True, fancybox=True)
    # plt.show()
    savePlotAsPdf(path, name + "DER.pdf", fig)

def plotSimRetransmittedPktsResult(path, name, resultDict, parametreArr):
    fig = plt.figure()
    plt.plot(parametreArr, resultDict["retransmittedPkt"])
    plt.ylabel("No. of Retransmitted Packets")
    plt.xlabel(plottingNames[name])
    plt.grid()
    plt.legend(loc=2, ncol=3, mode="expand", shadow=True, fancybox=True)
    # plt.show()
    savePlotAsPdf(path, name + "RetransmittedPkt.pdf", fig)

def plotSimRetransmissionRateResult(path, name, resultDict, parametreArr):
    fig = plt.figure()
    plt.plot(parametreArr, resultDict["retransmissionRate"])
    plt.ylabel("Retransmission Rate")
    plt.xlabel(plottingNames[name])
    plt.grid()
    plt.legend(loc=2, ncol=3, mode="expand", shadow=True, fancybox=True)
    # plt.show()
    savePlotAsPdf(path, name + "RetransmissionRate.pdf", fig)

def plotMultiVarDERResult(path, name, resultDict, paramArr, labelList):
    fig = plt.figure()
    stepSize = len(resultDict["DER"])/len(labelList)
    prevPos = 0
    

    plt.ylim((-0.05, 1))
    for i in range(0, len(resultDict["DER"]) + 1, stepSize):
        # print(i)
        if i != 0:
            currentLabelIndex = int(i / stepSize) - 1
            if isinstance(labelList[currentLabelIndex], str):
                labelStr = labelList[currentLabelIndex]
            else:
                labelStr = "{:.2f}".format(labelList[currentLabelIndex])

            plt.plot(paramArr, resultDict["DER"][prevPos : i], label = labelStr)
        prevPos = i
        
    plt.ylabel("DER")
    plt.xlabel(plottingNames[name.split("&")[1]])
    plt.grid()
    # plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    # plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
    #            ncol=2, mode="expand", borderaxespad=0.)
    plt.legend(loc=1, shadow=True, fancybox=True)
    savePlotAsPdf(path, name + "DER.pdf", fig)
    

def plot_new_sim(option):
    configFile = "lora_sim_config.json"
    # runSimScenario(generateSimScenario(configFile))
    scenarioDict = generateSimScenario(configFile, option)
    runSimScenario(scenarioDict, option)
  
    # pprint(getParametreArr(generateSimScenario(configFile), "burialDepth"))
    


    
    

if __name__ == '__main__':
    # option_arr = ["multi_var", "single_var", "retransmission"]
    option_arr = ["multi_var"]
    # plot_original_sim()
    for o in option_arr:
        plot_new_sim(o)

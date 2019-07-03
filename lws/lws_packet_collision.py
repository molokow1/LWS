# check for collisions at base station
# Note: called before a packet (or rather node) is inserted into the list
def check_collision(packet, packetsAtBS, maxBSReceives, fullCollision, currentTime):
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
            if frequency_collision(packet, other.packet) and sf_collision(packet, other.packet):
                if fullCollision:
                    if timing_collision(packet, other.packet, currentTime):
                        # check who collides in the power domain
                        c = power_collision(packet, other.packet)
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


def frequency_collision(p1, p2):
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

def sf_collision(p1, p2):
    if p1.sf == p2.sf:
        print("collision sf node {} and node {}".format(p1.nodeId, p2.nodeId))
        # p2 may have been lost too, will be marked by other checks
        return True
    print("no sf collision")
    return False

def power_collision(p1, p2):
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

def timing_collision(p1, p2, currentTime):
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


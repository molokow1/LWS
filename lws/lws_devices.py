from abc import ABC, abstractmethod, abstractproperty
from enum import Enum
from lora_sim_utils import ConfigReader


class DeviceType(Enum):
    END_DEVICE = 1
    BASE_STATION = 2



class LWSDevice(ABC):

    def __init__(self, device_id, x, y, dist, global_config):
        super().__init__()

        self.device_id = device_id
        self._x = x 
        self._y = y
        self.global_config = global_config
        self.dist = dist

        self.init_params()

        self._num_pkt_sent = 0 
        self._num_pkt_received = 0

        self._pkt_loss_count = 0
        self._pkt_collision_count = 0
        
        self.event_list = []
        
    def add_event(self, timestamp, event):
        self.event_list.append({
            "timestamp" : timestamp,
            "event"     : event
        })

    def init_params(self):
        #TODO: change the global_config attributes to better names e.g. device_sf
        self.sf = self.global_config.nodeSF
        self.cr = self.global_config.nodeCR 
        self.bw = self.global_config.nodeBW
        self.txPow = self.global_config.pTx

    @abstractmethod
    def send_packet(self, packet, target_device):
        pass 
    
    @abstractmethod
    def receive_packet(self, packet, from_device):
        pass

    @property
    def num_pkt_sent(self):
        return self.num_pkt_sent

    @property
    def pkt_collision_count(self):
        return self.pkt_collision_count
    
    @property
    def pkt_loss_count(self):
        return self.pkt_loss_count
        
    @abstractproperty
    def device_type(self):
        raise NotImplementedError


class EndDevice(LWSDevice):

    device_type = DeviceType.END_DEVICE

    def __init__(self, device_id, x, y, dist, global_config):
        super().__init__(device_id, x, y, dist, global_config)
        self.retransmission_cnt = 0
        

    def send_packet(self, packet, target_device):
        print("Sent packet {} to target_device {}".format(packet, target_device))
        self._num_pkt_sent += 1 
        
    def receive_packet(self, packet, from_device):
        pass

    def schedule_retransmission(self):
        pass



class BaseStation(LWSDevice):

    device_type = DeviceType.BASE_STATION

    def send_packet(self, packet, target_device):
        pass

    def receive_packet(self, packet, from_device):
        pass
    


if __name__ == "__main__":
    config = ConfigReader("./lora_sim_config.json")
    end_device = EndDevice(0,1,2,3, config)
    print(end_device.sf, end_device.device_type)

from lws.lws_devices import EndDevice, BaseStation

def mins_to_ms(val):
    return int(val * 60 * 1000)

def hours_to_ms(val):
    return int(val * 60 * 60 * 1000)

class LWSCore():
    def __init__(self, global_config, override_global_config = False, new_config = None):
        
        self.total_lost_packets = 0 
        self.total_collided_packets = 0
        self.total_received_packets = 0
        self.total_processed_pacekts = 0

        if not override_global_config: 
            self.num_end_devices = global_config.numNodes
            self.num_basestations = global_config.numBasestations
            self.avg_send_time = mins_to_ms(global_config.avgSendTime)            
            self.sim_time = hours_to_ms(global_config.simTime)
        else:
            if new_config == None:
                print("Need to provide a new config if the override_global_confgi is True")
                raise ValueError
            #TODO: check if the config val is the valid int type
            self.num_end_devices = new_config["num_end_devices"]
            self.num_basestations = new_config["num_basestations"]
            self.avg_send_time = mins_to_ms(new_config["avg_send_time"]) 
            self.sim_time = hours_to_ms(new_config["sim_time"])

        self.global_config = global_config

        self.base_station = BaseStation('B0', global_config.bsX, global_config.bsY, 0, global_config)
    
    def init_end_devices(self, node_pos_arr = None):
        self.end_devices = []
        limit = 0
        if node_pos_arr == None:
            pass
    
        

    def transmit(self, env, end_device):
        pass

    def start_simulation(self):
        pass

    def sum_end_device_stats(self):
        pass

    def print_sim_result(self):
        pass

    def write_sim_result(self):
        pass

    def get_sim_result_str(self):
        pass

    def show_all_devices_positions(self):
        pass

    

import simpy

from lws.lws_devices import EndDevice, BaseStation, PacketType
from lws_utils import generate_random_end_device_positions


class LWSCore():
    def __init__(self, global_config, override_global_config=False, new_config=None):

        self.env = simpy.Environment()

        self.total_lost_packets = 0
        self.total_sent_packets = 0
        self.total_collided_packets = 0
        self.total_received_packets = 0
        self.total_retransmissions = 0
        self.total_lost_downlinks = 0

        self.total_processed_pacekts = 0

        self.total_energy_consumed = 0.0

        self.final_der = 0.0
        self.final_retransmission_rate = 0.0

        if not override_global_config:
            self.num_end_devices = global_config.numNodes
            self.num_basestations = global_config.numBasestations
            self.avg_send_time = mins_to_ms(global_config.avgSendTime)
            self.sim_time = hours_to_ms(global_config.simTime)
        else:
            if new_config == None:
                print(
                    "Need to provide a new config if the override_global_confgi is True")
                raise ValueError
            # TODO: check if the config val is the valid int type
            self.num_end_devices = new_config["num_end_devices"]
            self.num_basestations = new_config["num_basestations"]
            self.avg_send_time = mins_to_ms(new_config["avg_send_time"])
            self.sim_time = hours_to_ms(new_config["sim_time"])

        self.global_config = global_config

        self.base_station = BaseStation(
            'B0', global_config.bsX, global_config.bsY, 0, global_config, env=self.env)
        self.init_end_devices(node_pos_arr=new_config["node_pos_arr"])

    def init_end_devices(self, node_pos_arr=None):
        self.end_devices = []

        if node_pos_arr == None:
            node_pos_arr = generate_random_end_device_positions(
                self.num_end_devices, self.global_config.maxDist, self.global_config.bsX, self.global_config.bs_y)

        if self.global_config.enableACKTest:
            limit = int(self.num_end_devices *
                        self.global_config.ACKPercentage)
        else:
            limit = 0

        for i, pos in enumerate(node_pos_arr):
            if i < limit:
                pkt_type = PacketType.DataAck
            else:
                pkt_type = PacketType.Data

            self.end_devices.append(EndDevice(
                device_id=i, x=pos[0], y=pos[1], dist=pos[2], global_config=self.global_config, pkt_type=pkt_type, env=self.env))

    def transmit(self, env, end_device):
        while True:

            # random initial send timeout
            env.process(end_device.send_uplink(self.base_station.device_id))
            # end_device.send
            env.process(self.base_station.receive_uplink(end_device.device_id))

            # downlink stuff here

    def start_simulation(self):
        for d in self.end_devices:
            self.env.process(self.transmit(self.env, d))

        self.env.run(until=self.sim_time)

    def sum_end_device_stats(self):
        # reset the counts first
        self.total_lost_packets = 0
        self.total_collided_packets = 0
        self.total_sent_packets = 0
        self.total_retransmissions = 0
        self.total_lost_downlinks = 0

        for d in self.end_devices:
            self.total_lost_packets += d.pkt_loss_count
            self.total_collided_packets += d.pkt_collision_count
            self.total_sent_packets += d.num_pkt_sent
            self.total_retransmissions += d.num_pkt_retransmitted
            self.total_lost_downlinks += d.downlink_loss_count

    def sum_all_stats(self):
        self.sum_end_device_stats()
        self.final_der = self.calc_final_DER()
        self.final_retransmission_rate = self.calc_retransmission_rate()
        self.total_energy_consumed = self.calc_total_energy_comsumed()

    def calc_final_DER(self):
        return self.base_station.num_pkt_received / float(self.total_sent_packets)

    def calc_retransmission_rate(self):
        return self.base_station.num_pkt_received / float(self.total_retransmissions)

    def calc_total_energy_comsumed(self):
        return 0

    def print_sim_result(self):
        pass

    def write_sim_result(self):
        pass

    @property
    def sim_result_dict(self):
        return {
            'num_nodes':   self.num_end_devices,
            'num_collisions':   self.total_collided_packets,
            'num_lost':   self.total_lost_packets,
            'pkts_sent':   self.total_sent_packets,
            'energy_consumption':   self.total_energy_consumed,
            'DER':   self.final_der,
            'retransmissions':   self.total_retransmissions,
            'retransmission_rate':   self.final_retransmission_rate,
        }

    def get_sim_result_str(self):
        pass

    def show_all_devices_positions(self):
        pass

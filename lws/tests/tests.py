import os
import subprocess
import unittest
import numpy as np
import csv
import simpy 

from lws import lws_utils
from lws import lws_devices

test_folder_path = 'test_folder'

class TestLWSUtils(unittest.TestCase):
    num_devices = 100
    max_dist = 20
    bs_x = 50
    bs_y = 50
    def test_generate_random_device_pos_within_max_dist(self):
        
        device_pos_arr = lws_utils.generate_random_end_device_positions(self.num_devices, self.max_dist, self.bs_x, self.bs_y)

        for pos in device_pos_arr:
            self.assertLess(pos[2], self.max_dist)
            calculated_dist = np.sqrt(
                abs(pos[0] - self.bs_x) ** 2 + abs(pos[1] - self.bs_y) ** 2
            )
            self.assertLess(calculated_dist, self.max_dist)

    

    test_dict = {
        'num_nodes'             :   '0',
        'num_collisions'        :   '1',
        'num_lost'              :   '2',
        'pkts_sent'             :   '3',
        'energy_consumption'    :   '4',
        'DER'                   :   '5',
        'retransmissions'       :   '6',
        'retransmission_rate'   :   '7',
    }

    def test_file_utils_able_to_create_sim_result_folder(self):
        file_utils = lws_utils.FileUtils(sim_result_folder_path=test_folder_path)
        file_utils.create_new_session(session_name='test1')
        file_utils.write_sim_result_to_csv(result_dict={}, file_name='test_file')

        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), 'test_folder')))

    def test_file_utils_able_to_generate_sim_result_csv_file(self):
        file_utils = lws_utils.FileUtils(sim_result_folder_path=test_folder_path)
        file_utils.create_new_session(session_name='test2')
        file_utils.write_sim_result_to_csv(result_dict={}, file_name='test_file')

        file_path = '/'.join(['test_folder', file_utils.current_session, 'test_file.csv'])
        
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), file_path)))

    def test_file_utils_generate_csv_file(self):
        file_utils = lws_utils.FileUtils(sim_result_folder_path=test_folder_path)
        file_utils.create_new_session(session_name='test3')
        
        file_utils.write_sim_result_to_csv(result_dict=self.test_dict, file_name='test_csv_file')

        #write it twice
        file_utils.write_sim_result_to_csv(result_dict=self.test_dict, file_name='test_csv_file')

        file_path = '/'.join([test_folder_path, file_utils.current_session, 'test_csv_file.csv'])

        with open(os.path.join(os.getcwd(), file_path), newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                for k in row:
                    self.assertEqual(row[k], self.test_dict[k])
        
        csvfile.close()

    def test_file_utils_read_csv_file(self):
        file_utils = lws_utils.FileUtils(sim_result_folder_path=test_folder_path)
        file_utils.create_new_session(session_name=self.test_file_utils_read_csv_file.__name__)
        #write dict
        file_utils.write_sim_result_to_csv(result_dict=self.test_dict, file_name='test_csv_file')
        file_utils.write_sim_result_to_csv(result_dict=self.test_dict, file_name='test_csv_file')
        # file_path = os.path.join(file_utils.current_session_path, 'test_csv_file.csv')
        print(file_utils.read_csv_file()) #should be able to read the most recent saved file
        
        

def LWSDevices_test_loop(end_device, basestation, env):
    while True:
        yield env.timeout(5)
        env.process(end_device.send_packet("Packet 1 from end_device", basestation.device_id, env.now))
        # print("Packet sent at " + str(env.now))
        env.process(basestation.receive_packet(end_device.device_id, env.now))
        yield env.timeout(5)
        env.process(basestation.send_packet("Packet 2 from basestation", end_device.device_id))

        env.process(end_device.receive_packet(basestation.device_id))
        # print(basestation.received_packet)
    
class TestLWSDevices(unittest.TestCase):

    config = lws_utils.ConfigReader('../lora_sim_config.json')


    SIM_TIME = 100

    def test_message_passing(self):
        env = simpy.Environment()
        
        end_device = lws_devices.EndDevice(device_id=0, x=3, y=4, dist=5, global_config=self.config, pkt_type=lws_devices.PacketType.Data, env=env)

        basestation = lws_devices.BaseStation(device_id='B0', x=0, y=1, dist=0, global_config=self.config, env=env)

        lws_devices.create_full_duplex_connection(end_device, basestation)

        env.process(LWSDevices_test_loop(end_device, basestation, env))
        env.run(until=self.SIM_TIME)
        # while env.peek() < self.SIM_TIME:
        #     env.step()






if __name__ == "__main__":
    unittest.main(exit=False)
    #delete the test folder
    if(os.path.exists(os.path.join(os.getcwd(), test_folder_path))):
        subprocess.call(["rm","-R",test_folder_path])
        print("Test folder cleaned up.")
    
        
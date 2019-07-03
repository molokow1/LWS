import unittest
import numpy as np
from lws import lws_utils
from lws import lws_devices



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
    

class TestLWSDevices(unittest.TestCase):

    def test_end_device(self):
        pass
    




if __name__ == "__main__":
    unittest.main()

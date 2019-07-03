# Lp = 6.4 + 20 log(d) + 20 log(beta) + 8.69 * alpha * d
# d is distance, beta is phase shifting constant, alpha is attenuation constant
import math 


class soil_path_loss_model(object):

    def __init__(self, vwc, bulk_density, particle_density, sand_frac, clay_frac):
        self.vwc = vwc
        self.bulk_density = bulk_density
        self.particle_density = particle_density
        self.sand_frac = sand_frac
        self.clay_frac = clay_frac
        
        self.mu = (4*math.pi) * 1e-7 #relative magnetic permeability
        self.epsilon_0 = 8.854e-12 #magnetic permeability

        #constants for calculating dielectric properties of soil
        self.beta_1 = 1.2748 - (0.519 * sand_frac) - (0.152 * clay_frac)
        self.beta_2 = 1.33797 - (0.603 * sand_frac) - (0.166 * clay_frac)
        self.alpha_1 = 0.65
        self.epsilon_s = math.pow(1.01 + 0.44 * particle_density,2) - 0.062 #Relative permittivities of the hose (soil solids)
        

        #constants for calculating relative water constant
        self.relaxation_time = 0.58e-10
        self.epsilon_high_freq_limit = 4.9
        self.static_water_constant = 80.1


    def calc_relative_water_const(self, freq):
        effective_conduct = 0.0467 + 0.2204 * self.bulk_density - 0.4111 * self.sand_frac + 0.6614 * self.clay_frac
        # effective_conduct = -1.645 + 1.939 * self.bulk_density - 2.25622 * self.sand_frac + 1.594 * self.clay_frac
        
        epsilon_water_real = self.epsilon_high_freq_limit + (self.static_water_constant - self.epsilon_high_freq_limit) / (1 + math.pow((self.relaxation_time * freq), 2)) 

        epsilon_water_imag = self.relaxation_time * freq * (self.static_water_constant - self.epsilon_high_freq_limit) / (1 + math.pow((self.relaxation_time * freq), 2)) 

        epsilon_water_imag += (effective_conduct / (2 * math.pi * self.epsilon_0 * freq)) * ((self.particle_density - self.bulk_density) / (self.particle_density * self.vwc))

        return epsilon_water_real, epsilon_water_imag


    def calc_soil_dielectric_const(self, epsilon_water_real, epsilon_water_imag):
        epsilon_soil_real = 1 + (self.bulk_density / self.particle_density) * (math.pow(self.epsilon_s, self.alpha_1) - 1) 

        epsilon_soil_real += math.pow(self.vwc, self.beta_1) * math.pow(epsilon_water_real, self.alpha_1) - self.vwc 

        epsilon_soil_real = 1.15 * math.pow(epsilon_soil_real, (1 / self.alpha_1))  - 0.68

        epsilon_soil_imag = math.pow(self.vwc, self.beta_2) * math.pow(epsilon_water_imag, self.alpha_1)

        epsilon_soil_imag = math.pow(epsilon_soil_imag, (1 / self.alpha_1))

        return epsilon_soil_real, epsilon_soil_imag

    def calc_propogation_const(self, freq, epsilon_soil_real, epsilon_soil_imag):
        omega = 2 * math.pi * freq/1e+6

        a = math.sqrt(1 + math.pow(epsilon_soil_imag / epsilon_soil_real, 2)) 

        b = self.mu * epsilon_soil_real / 2 

        alpha = omega * math.sqrt(b * (a - 1))

        beta = omega * math.sqrt(b * (a + 1))

        return alpha, beta

    def calc_one_way_path_loss(self, dist, freq, vwc = None, sand_frac=None, clay_frac=None):
        if vwc is not None:
            self.vwc = vwc

        if sand_frac is not None:
            self.sand_frac = sand_frac
        
        if clay_frac is not None:
            self.clay_frac = clay_frac

        epsilon_water_real, epsilon_water_imag = self.calc_relative_water_const(freq)

        # print("water_real: {}\nwater_imag: {}\n".format(epsilon_water_real, epsilon_water_imag))

        epsilon_soil_real, epsilon_soil_imag = self.calc_soil_dielectric_const(epsilon_water_real, epsilon_water_imag)

        # print("soil_real: {}\nsoil_imag: {}\n".format(epsilon_soil_real, epsilon_soil_imag))

        alpha, beta = self.calc_propogation_const(freq, epsilon_soil_real, epsilon_soil_imag)

        # print("alpha: {}\nbeta: {}\n".format(alpha, beta))
        # if only_alpha:
        #     one_way_path_loss = math.pow(math.e, 2*alpha*dist)
        # else:
        #     one_way_path_loss = 6.4 + 20 * math.log10(dist) + 20 * math.log10(beta) + 8.69 * alpha * dist 
        l_alpha = 8.69 * alpha * dist
        l_beta = 154 - 20 * math.log10(freq) + 20 * math.log10(beta)
        # return l_alpha + l_beta
        return 6.4 + 20 * math.log10(dist) + 20 * math.log10(beta) + 8.69 * alpha * dist

    def calc_reflection_params(self, burial_depth, dist, gateway_height):
        #calc reflection angle in radians
        theta = math.atan((burial_depth + gateway_height) / dist)
        d_underground = burial_depth / math.sin(theta)
        d_overground = gateway_height / math.sin(theta)
        return theta, d_underground, d_overground
        

    def calc_simple_underground_pathloss(self, freq, burial_depth, dist, gateway_height):
        theta, d_underground, d_overground = self.calc_reflection_params(burial_depth, dist, gateway_height)
        underground_path_loss = self.calc_one_way_path_loss(d_underground, freq)
        free_space = free_space_path_loss_model(d_overground)

        #currently uses the free space model as this is expected to be deployed in a rural area
        #can be changed to a urban area if needed 
        overground_path_loss = free_space.calc_path_loss(freq/1e6)
        return underground_path_loss + overground_path_loss
    
    def calc_approximated_path_loss(self, freq, burial_depth, dist, gateway_height):
        underground_path_loss = self.calc_one_way_path_loss(burial_depth, freq)
        overground_dist = math.sqrt(math.pow(dist, 2) + math.pow(gateway_height, 2))
        free_space = free_space_path_loss_model(overground_dist/1e3)

        overground_path_loss = free_space.calc_path_loss(freq/1e6)

        return underground_path_loss + overground_path_loss

class free_space_path_loss_model(object):
    #in km and mhz
    def __init__(self, dist=None):
        self.dist = dist 

    def calc_path_loss(self,freq, dist=None):
        if dist is None:
            return (20 * math.log10(self.dist) + 20 * math.log10(freq) + 32.4)
        else:
            return (20 * math.log10(dist) + 20 * math.log10(freq) + 32.4)

def main():
    vwc = 0.10
    bulk_density = 1.5
    particle_density = 2.66 
    sand_frac = 0.50
    clay_frac = 0.15
    model = soil_path_loss_model(vwc,bulk_density,particle_density,sand_frac,clay_frac)
    free_space = free_space_path_loss_model(3) 
    

    # model2 = soil_path_loss(vwc,bulk_density,particle_density,sand_frac,clay_frac)

    # path_loss_only_alpha = model.calc_one_way_path_loss(3,600e+6)
    
    print("Free space path loss: {}dB".format(free_space.calc_path_loss(9.15)))
    # path_loss2 = model2.calc_pathloss(3, 900e+6)
    # print("Current loss is: {}dB.".format(path_loss))
    # print("Current loss is: {}dB.".format(path_loss2))


if __name__ == '__main__':
    main()
         

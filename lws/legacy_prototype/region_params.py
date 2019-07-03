#this defines regional params of LoRaWAN


#AU915-928

# Uplink:

# 916.8 - SF7BW125 to SF10BW125
# 917.0 - SF7BW125 to SF10BW125
# 917.2 - SF7BW125 to SF10BW125
# 917.4 - SF7BW125 to SF10BW125
# 917.6 - SF7BW125 to SF10BW125
# 917.8 - SF7BW125 to SF10BW125
# 918.0 - SF7BW125 to SF10BW125
# 918.2 - SF7BW125 to SF10BW125
# 917.5 SF8BW500

# Downlink:

# 923.3 - SF7BW500 to SF12BW500
# 923.9 - SF7BW500 to SF12BW500
# 924.5 - SF7BW500 to SF12BW500
# 925.1 - SF7BW500 to SF12BW500
# 925.7 - SF7BW500 to SF12BW500
# 926.3 - SF7BW500 to SF12BW500
# 926.9 - SF7BW500 to SF12BW500
# 927.5 - SF7BW500 to SF12BW500


class RegionalParams():
    
    AU_FREQ = [916.8e+6, 917.0e+6, 917.2e+6, 917.4e+6,
               917.6e+6, 917.8e+6, 918.0e+6, 918.2e+6]
    AU_BW = 125
    AU_SF = [7,8,9,10]



def main():
    print(RegionalParams.AU_FREQ)

if __name__ == '__main__':
    main()

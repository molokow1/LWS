const faker = require("faker");

const sim_result = {
    overall_result: {
        der: "0.5",
        energy_comsumption: "100",
        total_packets_sent: "1000",
        total_packets_received: "2000",
        total_packets_lost: "0",
        total_packets_collided: "0"
    },
    basestation: {
        basestation1_id: {
            x: "30",
            y: "40"
        }
    },
    end_device: {
        end_device1_id: {
            x: "10",
            y: "20"
        },
        end_device2_id: {
            x: "5",
            y: "10"
        },
        end_deviceN_id: {
            x: "2",
            y: "40"
        }
    }
};

const sim_form = {
    regional_settings: {
        header: "Regional Transmission Settings",
        settings: {
            region: {
                label: "Region",
                selections: {
                    AU: "AU",
                    EU: "EU",
                    AS: "AS"
                }
            },
            freq: {
                label: "Frequency",
                selections: {
                    915: "915MHz",
                    916: "916MHz",
                    917: "917MHz"
                }
            },
            bw: {
                label: "Bandwidth",
                selections: {
                    125: "125kHz",
                    250: "250kHz"
                }
            },
            sf: {
                label: "Spreading Factor",
                selections: {
                    7: 7,
                    8: 8,
                    9: 9,
                    10: 10,
                    11: 11,
                    12: 12
                }
            }
        }
    },
    environment_settings: {
        header: "Environment Settings",
        settings: {
            burial_depth: {
                label: "Burial Depth (m)",
                default_value: "0.5"
            },
            vwc: {
                label: "Volumetric Water Content (%)",
                default_value: 0.2
            },
            sand_frac: {
                label: "Sand (%)",
                default_value: 0.3,
            },
            clay: {
                label: "Clay (%)",
                default_value: 0.2
            }
        }
    },
    simulation_settings: {
        header: "Simulation Settings",
        settings: {
            sim_duration: {
                label: "Simulation Duration (Hrs)",
                default_value: 2
            },
            sim_avg_send_time: {
                label: "Average Send Time (mins)",
                default_value: 10
            }
        }
    }
};
module.exports = {
    sim_result,
    sim_form
};

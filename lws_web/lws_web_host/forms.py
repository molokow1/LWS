from django import forms

REGION_CHOICES = [
    ('AU', 'AU'),
    ('EU', 'EU'),
    ('AS', 'AS'),
]

FREQ_CHOICES = [
    (915, '915MHz'),
    (916, '916MHz'),
    (917, '917MHz'),
]

BW_CHOICES = [
    (125, '125kHz'),
    (250, '250kHz'),
]

SF_CHOICES = [
    (7, 7),
    (8, 8),
    (9, 9),
    (10, 10),
    (11, 11),
    (12, 12),
]


class SimulationSettingsForm(forms.Form):
    regional_settings_header = "Regional Transmission Settings"
    select_region = forms.ChoiceField(label="Region", choices=REGION_CHOICES)
    select_freq = forms.ChoiceField(
        label="Center Frequency", choices=FREQ_CHOICES)
    select_bw = forms.ChoiceField(label="Bandwidth", choices=BW_CHOICES)
    select_sf = forms.ChoiceField(label="Spreading Factor", choices=SF_CHOICES)

    environment_settings_header = "Environment Settings"
    env_burial_depth = forms.DecimalField(
        label="Burial Depth (m)", required=True, min_value=0, localize=True)
    env_vwc = forms.DecimalField(
        label="VWC (%)", required=True, min_value=0, localize=True)
    env_sand = forms.DecimalField(
        label="Sand (%)", required=True, min_value=0, localize=True)
    env_clay = forms.DecimalField(
        label="Clay (%)", required=True, min_value=0, localize=True)

    simulation_settings_header = "Simulation Parameters"

    sim_duration = forms.DecimalField(
        label="Simulation Duration (Hr)", required=True, min_value=0, localize=True)

    sim_avg_send_time = forms.DecimalField(
        label="Average Send Time (Mins)", required=True, min_value=0, localize=True)

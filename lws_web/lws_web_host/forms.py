from django import forms

REGION_CHOICES = [
    ('AU' , 'AU'),
    ('EU' , 'EU'),
    ('AS' , 'AS'),
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
    
    region = forms.ChoiceField(label="Region", choices=REGION_CHOICES)
    freq = forms.ChoiceField(label="Center Frequency", choices=FREQ_CHOICES)
    bw = forms.ChoiceField(label="Bandwidth", choices=BW_CHOICES)
    sf = forms.ChoiceField(label="Spreading Factor", choices=SF_CHOICES)

class EnvironmentSettingsForm(forms.Form):

    pass
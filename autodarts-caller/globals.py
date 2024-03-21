AUTODART_URL = 'https://autodarts.io'
AUTODART_AUTH_URL = 'https://login.autodarts.io/'
AUTODART_CLIENT_ID = 'wusaaa-caller-for-autodarts'
AUTODART_REALM_NAME = 'autodarts'
AUTODART_CLIENT_SECRET = "4hg5d4fddW7rqgoY8gZ42aMpi2vjLkzf"
AUTODART_LOBBIES_URL = 'https://api.autodarts.io/gs/v0/lobbies/'
AUTODART_MATCHES_URL = 'https://api.autodarts.io/gs/v0/matches/'
AUTODART_BOARDS_URL = 'https://api.autodarts.io/bs/v0/boards/'
AUTODART_USERS_URL = 'https://api.autodarts.io/as/v0/users/'
AUTODART_WEBSOCKET_URL = 'wss://api.autodarts.io/ms/v0/subscribe'

SUPPORTED_SOUND_FORMATS = ['.mp3', '.wav']
SUPPORTED_GAME_VARIANTS = ['X01', 'Cricket', 'Random Checkout', 'ATC']
SUPPORTED_CRICKET_FIELDS = [15, 16, 17, 18, 19, 20, 25]
BOGEY_NUMBERS = [169, 168, 166, 165, 163, 162, 159]
TEMPLATE_FILE_ENCODING = 'utf-8-sig'

CALLER_LANGUAGES = {
    1: ['english', 'en', ],
    2: ['french', 'fr', ],
    3: ['russian', 'ru', ],
    4: ['german', 'de', ],
    5: ['spanish', 'es', ],
    6: ['dutch', 'nl', ],
}
CALLER_GENDERS = {
    1: ['female', 'f'],
    2: ['male', 'm'],
}
CALLER_PROFILES = {
    #------------------------------------------------------------------------------------------------
    # GOOGLE / Cloud TTS
    #------------------------------------------------------------------------------------------------
    # -- fr-FR --
    'fr-FR-Wavenet-E-FEMALE': ('https://add.arnes-design.de/ADC/fr-FR-Wavenet-E-FEMALE-v3.zip', 3),
    'fr-FR-Wavenet-B-MALE': ('https://add.arnes-design.de/ADC/fr-FR-Wavenet-B-MALE-v3.zip', 3),
    # -- ru-RU --
    'ru-RU-Wavenet-E-FEMALE': ('https://add.arnes-design.de/ADC/ru-RU-Wavenet-E-FEMALE-v3.zip', 3),
    'ru-RU-Wavenet-B-MALE': ('https://add.arnes-design.de/ADC/ru-RU-Wavenet-B-MALE-v3.zip', 3),
    # -- de-DE --
    'de-DE-Wavenet-F-FEMALE': ('https://add.arnes-design.de/ADC/de-DE-Wavenet-F-FEMALE-v3.zip', 3),  
    'de-DE-Wavenet-B-MALE': ('https://add.arnes-design.de/ADC/de-DE-Wavenet-B-MALE-v3.zip', 3),
    # -- es-ES --
    'es-ES-Wavenet-C-FEMALE': ('https://add.arnes-design.de/ADC/es-ES-Wavenet-C-FEMALE-v3.zip', 3),  
    'es-ES-Wavenet-B-MALE': ('https://add.arnes-design.de/ADC/es-ES-Wavenet-B-MALE-v3.zip', 3),
    # -- nl-NL --
    'nl-NL-Wavenet-B-MALE': ('https://add.arnes-design.de/ADC/nl-NL-Wavenet-B-MALE-v3.zip', 3),  
    'nl-NL-Wavenet-D-FEMALE': ('https://add.arnes-design.de/ADC/nl-NL-Wavenet-D-FEMALE-v3.zip', 3),
    # -- en-US --
    'en-US-Wavenet-E-FEMALE': ('https://add.arnes-design.de/ADC/en-US-Wavenet-E-FEMALE-v4.zip', 4),
    'en-US-Wavenet-G-FEMALE': ('https://add.arnes-design.de/ADC/en-US-Wavenet-G-FEMALE-v4.zip', 4),
    'en-US-Wavenet-A-MALE': ('https://add.arnes-design.de/ADC/en-US-Wavenet-A-MALE-v4.zip', 4),
    'en-US-Wavenet-H-FEMALE': ('https://add.arnes-design.de/ADC/en-US-Wavenet-H-FEMALE-v4.zip', 4),
    'en-US-Wavenet-I-MALE': ('https://add.arnes-design.de/ADC/en-US-Wavenet-I-MALE-v4.zip', 4),
    'en-US-Wavenet-J-MALE': ('https://add.arnes-design.de/ADC/en-US-Wavenet-J-MALE-v4.zip', 4),
    'en-US-Wavenet-F-FEMALE': ('https://add.arnes-design.de/ADC/en-US-Wavenet-F-FEMALE-v4.zip', 4),

    #------------------------------------------------------------------------------------------------
    # AMAZON / AWS Polly
    #------------------------------------------------------------------------------------------------
    # -- nl-NL --
    'nl-NL-Laura-Female': ('https://add.arnes-design.de/ADC/nl-NL-Laura-Female-v2.zip', 2),
    # -- de-AT --
    'de-AT-Hannah-Female': ('https://add.arnes-design.de/ADC/de-AT-Hannah-Female-v2.zip', 2),
    # -- de-DE --
    'de-DE-Vicki-Female': ('https://add.arnes-design.de/ADC/de-DE-Vicki-Female-v5.zip', 5),  
    'de-DE-Daniel-Male': ('https://add.arnes-design.de/ADC/de-DE-Daniel-Male-v5.zip', 5),
    # -- en-US --
    'en-US-Ivy-Female': ('https://add.arnes-design.de/ADC/en-US-Ivy-Female-v5.zip', 5),
    'en-US-Joey-Male': ('https://add.arnes-design.de/ADC/en-US-Joey-Male-v6.zip', 6),
    'en-US-Joanna-Female': ('https://add.arnes-design.de/ADC/en-US-Joanna-Female-v6.zip', 6),
    'en-US-Matthew-Male': ('https://add.arnes-design.de/ADC/en-US-Matthew-Male-v3.zip', 3),
    'en-US-Danielle-Female': ('https://add.arnes-design.de/ADC/en-US-Danielle-Female-v3.zip', 3),
    'en-US-Kimberly-Female': ('https://add.arnes-design.de/ADC/en-US-Kimberly-Female-v2.zip', 2),
    'en-US-Ruth-Female': ('https://add.arnes-design.de/ADC/en-US-Ruth-Female-v2.zip', 2),
    'en-US-Salli-Female': ('https://add.arnes-design.de/ADC/en-US-Salli-Female-v2.zip', 2),
    'en-US-Kevin-Male': ('https://add.arnes-design.de/ADC/en-US-Kevin-Male-v2.zip', 2),
    'en-US-Justin-Male': ('https://add.arnes-design.de/ADC/en-US-Justin-Male-v2.zip', 2),
    'en-US-Stephen-Male': ('https://add.arnes-design.de/ADC/en-US-Stephen-Male-v5.zip', 5),  
    'en-US-Kendra-Female': ('https://add.arnes-design.de/ADC/en-US-Kendra-Female-v6.zip', 6),
    'en-US-Gregory-Male': ('https://add.arnes-design.de/ADC/en-US-Gregory-Male-v3.zip', 3),
    
    # 'TODONAME': ('TODOLINK', TODOVERSION),  
}
FIELD_COORDS = {
    "0": {"x": 0.016160134143785285,"y": 1.1049884720184449},
    "S1": {"x": 0.2415216935652902,"y": 0.7347516243974009}, 
    "D1": {"x": 0.29786208342066656,"y": 0.9359673024523162}, 
    "T1": {"x": 0.17713267658771747,"y": 0.5818277090756655},
    "S2": {"x": 0.4668832529867955,"y": -0.6415636134982183}, 
    "D2": {"x": 0.5876126598197445,"y": -0.7783902745755609}, 
    "T2": {"x": 0.35420247327604254,"y": -0.4725424439320897},
    "S3": {"x": 0.008111507021588693,"y": -0.7864389016977573}, 
    "D3": {"x": -0.007985747222804492,"y": -0.9715573255082791}, 
    "T3": {"x": -0.007985747222804492,"y": -0.5932718507650387},
    "S4": {"x": 0.6439530496751206,"y": 0.4530496751205198}, 
    "D4": {"x": 0.7888283378746596,"y": 0.5657304548312723}, 
    "T4": {"x": 0.48298050723118835,"y": 0.36451477677635713},
    "S5": {"x": -0.23334730664430925,"y": 0.7508488786417943}, 
    "D5": {"x": -0.31383357786627536,"y": 0.9279186753301195}, 
    "T5": {"x": -0.1850555439111297,"y": 0.5737790819534688},
    "S6": {"x": 0.7888283378746596,"y": -0.013770697966883233}, 
    "D6": {"x": 0.9739467616851814,"y": 0.010375183399706544}, 
    "T6": {"x": 0.5956612869419406,"y": -0.005722070844686641},
    "S7": {"x": -0.4506602389436176,"y": -0.6335149863760215}, 
    "D7": {"x": -0.5713896457765667,"y": -0.7703416474533641}, 
    "T7": {"x": -0.3540767134772585,"y": -0.4725424439320897},
    "S8": {"x": -0.7323621882204988,"y": -0.239132257388388}, 
    "D8": {"x": -0.9255292391532174,"y": -0.2954726472437643}, 
    "T8": {"x": -0.5713896457765667,"y": -0.18279186753301202},
    "S9": {"x": -0.627730035631943,"y": 0.4691469293649132}, 
    "D9": {"x": -0.7726053238314818,"y": 0.5657304548312723}, 
    "T9": {"x": -0.48285474743240414,"y": 0.34841752253196395},
    "S10": {"x": 0.7244393208970865,"y": -0.23108363026619158}, 
    "D10": {"x": 0.9256549989520018,"y": -0.28742402012156787}, 
    "T10": {"x": 0.5715154055753511,"y": -0.19084049465520878},
    "S11": {"x": -0.7726053238314818,"y": -0.005722070844686641}, 
    "D11": {"x": -0.9657723747642004,"y": -0.005722070844686641}, 
    "T11": {"x": -0.5955355271431566,"y": 0.0023265562775099512},
    "S12": {"x": -0.4506602389436176,"y": 0.6140222175644519}, 
    "D12": {"x": -0.5633410186543703,"y": 0.7910920142527772}, 
    "T12": {"x": -0.3540767134772585,"y": 0.4932928107315028},
    "S13": {"x": 0.7244393208970865,"y": 0.24378536994340808}, 
    "D13": {"x": 0.917606371829805,"y": 0.308174386920981}, 
    "T13": {"x": 0.5634667784531546,"y": 0.18744498008803193},
    "S14": {"x": -0.7223277562650692,"y": 0.2440637100898663}, 
    "D14": {"x": -0.9255292391532174,"y": 0.308174386920981}, 
    "T14": {"x": -0.5713896457765667,"y": 0.19549360721022835},
    "S15": {"x": 0.6278557954307273,"y": -0.46449381680989327}, 
    "D15": {"x": 0.7888283378746596,"y": -0.5771745965206456}, 
    "T15": {"x": 0.4910291343533851,"y": -0.34376440997694424},
    "S16": {"x": -0.6196814085097464,"y": -0.4725424439320897}, 
    "D16": {"x": -0.7967512051980717,"y": -0.5610773422762524}, 
    "T16": {"x": -0.49090337455460076,"y": -0.33571578285474746},
    "S17": {"x": 0.2415216935652902,"y": -0.730098511842381}, 
    "D17": {"x": 0.29786208342066656,"y": -0.9152169356529029}, 
    "T17": {"x": 0.18518130370991423,"y": -0.5691259693984492},
    "S18": {"x": 0.48298050723118835,"y": 0.6462167260532384}, 
    "D18": {"x": 0.5554181513309578,"y": 0.799140641374974}, 
    "T18": {"x": 0.3292712798530314,"y": 0.49608083282302506},
    "S19": {"x": -0.2586037966932027,"y": -0.7658909981628906}, 
    "D19": {"x": -0.3134721371708513,"y": -0.9148193508879362}, 
    "T19": {"x": -0.19589712186160443,"y": -0.562094304960196},
    "S20": {"x": 0.00006123698714003468,"y": 0.7939375382731171}, 
    "D20": {"x": 0.01119619445411297, "y": 0.9726766446223462}, 
    "T20": {"x": 0.00006123698714003468, "y": 0.6058175137783223},
    "25": {"x": 0.06276791181873864, "y": 0.01794243723208814}, 
    "50": {"x": -0.007777097366809472, "y": 0.0022657685241886157},
}

WEB_DB_NAME = "ADC1"
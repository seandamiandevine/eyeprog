from psychopy import visual, core, event, monitors, sound, gui, data, hardware
import psychopy.iohub as io
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)

import pandas as pd
import numpy as np
import datetime
import os

import pyfiglet
import termcolor

### ------------------------- ADMIN ------------------------- ###

TEST_MODE = 0
GUI_ENABLED = 1
IF_SEE_COMPUTR_PLAY = 0

### ------------------------- TERMINAL ------------------------- ###

def start_terminal():

    os.system('clear')
    message = pyfiglet.Figlet(font = 'univers').renderText('IPROG')
    print(termcolor.colored(message, 'blue'))

### ------------------------- GUI ------------------------- ###

def GUI(GUI_ENABLED):
    
    TIME = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    
    if GUI_ENABLED:
        
        import PyQt5
        
        ### Experimenters ###
        EXPERIMENTERS = ['Aashiha Babu', 'Clara Nadeau', 'Doug Dong', 'Sean Devine']

        myDlg = gui.Dlg(title='IPROG')
        myDlg.addText(f'Time: {TIME}')
        myDlg.addField('PID')
        myDlg.addField('SONA ID')
        myDlg.addField('Age')
        myDlg.addField('Gender', choices=['F', 'M', 'O'])
        myDlg.addField('Experimenter', choices=EXPERIMENTERS)

        try:
            PID, SONA, AGE, GENDER, EXPERIMENTER = myDlg.show()
            EXPTR_INITIAL = EXPERIMENTER.split()[0][0] + EXPERIMENTER.split()[1][0]
        except:
            message = 'Session Cancelled \n Please restart the program.'
            raise Exception(termcolor.colored(message, 'red'))
        
        try:
            PID = int(PID)
        except:
            message = 'The entered PID is NOT a number \n Please restart the program.'
            raise Exception(termcolor.colored(message, 'red'))        
        try:
            SONA = int(SONA)
        except:
            message = 'The entered SONA ID is NOT a number \n Please restart the program.'
            raise Exception(termcolor.colored(message, 'red'))
        try:
            AGE = int(AGE)
        except:
            message = 'The entered AGE is NOT a number \n Please restart the program.'
            raise Exception(termcolor.colored(message, 'red'))

    else:
        PID, SONA, AGE, GENDER, EXPTR_INITIAL = [np.random.randint(1, 1000), np.random.randint(1, 1000), 999, 'O', 'AI']

    demographics = {'PID':PID, 'SONA':SONA, 'Age': AGE, 'Gender':GENDER, 'TIME':TIME, 'EXPERIMENTER': EXPTR_INITIAL}

    return demographics

### ------------------------- RUN SET UP  ------------------------- ###

start_terminal()
DEMOGRAPHICS = GUI(GUI_ENABLED)
SONA = DEMOGRAPHICS.get('SONA')
try:
    os.mkdir(f'.{os.sep}data{os.sep}{SONA}') # mkdir for each participant
except:
    print('It seems like you are running the same participant more than once. Be careful about the data!')
FILENAME = f'.{os.sep}data{os.sep}{SONA}{os.sep}{SONA}'
EXPDATA = data.ExperimentHandler(dataFileName=FILENAME,
                                 extraInfo=DEMOGRAPHICS, 
                                 saveWideText=True) # save .csv

### ------------------------- PSYCHOPY ------------------------- ###

### Window Setup ###
WIN = visual.Window(
    size=[1280, 1024],
    fullscr=True,  
    color='black',
    screen=0,
    allowGUI=True,
    allowStencil=True,
    monitor='testMonitor',
    units='height', # relative to the percentage of the screen # NOTE: visual angle available, see psychopy page
    colorSpace='rgb255')  # ??? LATER SOMETHING IS OFF WITH THE COLOR SCALE
WIN.mouseVisible = False

## Eyetracker Setup ###

### MOUSE ###

# ioDevice = 'eyetracker.hw.mouse.EyeTracker'
# ioConfig = {
#     ioDevice: {
#         'name': 'tracker',
#         'controls': {
#             'move': [],
#             'blink':('MIDDLE_BUTTON',),
#             'saccade_threshold': 0.5,
#         }
#     }
# }

### EYELINK 1000 ###

ioDevice = 'eyetracker.hw.sr_research.eyelink.EyeTracker'
ioConfig = {
    ioDevice: {
        'name': 'tracker',
        'model_name': 'EYELINK 1000 DESKTOP',
        'simulation_mode': False,
        'network_settings': '100.1.1.1',
        'default_native_data_file_name': 'EXPFILE',
        'runtime_settings': {
            'sampling_rate': 1000.0,
            'track_eyes': 'LEFT_EYE',
            'sample_filtering': {
                'sample_filtering': 'FILTER_LEVEL_2',
                'elLiveFiltering': 'FILTER_LEVEL_OFF',
            },
            'vog_settings': {
                'pupil_measure_types': 'PUPIL_AREA',
                'tracking_mode': 'PUPIL_CR_TRACKING',
                'pupil_center_algorithm': 'ELLIPSE_FIT',
            }
        }
    }
}

ioServer = io.launchHubServer(window=WIN, datastore_name=FILENAME, **ioConfig)
eyetracker = ioServer.getDevice('tracker')
eyetracker_record = hardware.eyetracker.EyetrackerControl(
            server=ioServer,
            tracker=eyetracker)

eyetracker.setConnectionState(True)
# eyetracker.setRecordingState(True)

### ------------------------- --------- ------------------------- ###
### ------------------------- Constants ------------------------- ###
### ------------------------- --------- ------------------------- ###

### TASK PARAMTERS ###
FIXATION    = visual.TextStim(win=WIN, text='+', height=.2, pos=[0, 0], color='white')
BLOCK_TXT   = visual.TextStim(win=WIN, text='NEW ROUND', height=.05, pos=[0, 0], color='white')
FINISH_TXT  = visual.TextStim(win=WIN, text='F I N', height=.05, pos=[0, 0], color='red')
CHOICE_KEYS = ['q', 'w', 'e']

### TRIALS ###
GLOBALTRIAL = 0
BLOCKS    = [0] * 8 + [1] * 8
np.random.shuffle(BLOCKS)
NUM_BLOCK = len(BLOCKS)
TRIALS  = np.random.randint(low=45, high=55+1, size=16)
NUM_PRACTICE_CORRECT_BAR   = 20
NUM_PRACTICE_CORRECT_FINAL = 15

### Timing ###
CLOCK         = core.Clock()
TIMEOUT       = .750          # response window
TIMEOUT_FAST  = .600          # 10% trial (random)
FEEDBACK_DUR  = .500          # duration feedback is on screen
BLOCK_TXT_DUR = 1.000         # duration block info is on screen
ITI1          = .750          # a chance to see the progress bar
ITI2          = .250          # duration blank screen after feedback

### INSTURCTION PATH ###
INST_PATH = f'.{os.sep}stimuli{os.sep}instructions{os.sep}'
INST_1 = f'{INST_PATH}inst_1{os.sep}'
INST_2 = f'{INST_PATH}inst_2{os.sep}'
INST_3 = f'{INST_PATH}inst_3{os.sep}'
INST_4 = f'{INST_PATH}inst_4{os.sep}'
INST_5 = f'{INST_PATH}inst_5{os.sep}'
INST_6 = f'{INST_PATH}inst_6{os.sep}'

### STIMULI - ODD BALL ###
SIZE   = (.15, .15)
BALL_1 = visual.ImageStim(WIN, pos=[-.25, 0], size=SIZE)
BALL_2 = visual.ImageStim(WIN, pos=[0, 0], size=SIZE)
BALL_3 = visual.ImageStim(WIN, pos=[+.25, 0], size=SIZE)
balls  = [BALL_1, BALL_2, BALL_3]

### STIMULI - PROGRESS BAR ###
OUTLINE_POS      = (0.0, .40)  # x-center, y-up
OUTLINE_SIZE     = (.80, .05)  # length, width
PROG_BAR_OUTLINE = visual.Rect(win=WIN, pos=OUTLINE_POS, size=(OUTLINE_SIZE[0]+0.01, OUTLINE_SIZE[1]), 
                               lineWidth=4, lineColor='white', fillColor='white')

PROG_BAR         = visual.Rect(win=WIN, pos=(0,0), size=(0,0), lineColor='white', fillColor='green')
PROG_BAR_CONTROL = visual.Rect(win=WIN, pos=OUTLINE_POS, size=OUTLINE_SIZE, lineColor='white', fillColor='gray')

# AOI
gazeCursor  = visual.ShapeStim(win=WIN, size=(.025, .025), vertices='circle', fillColor='yellow')

PROG_TARGET   = visual.Rect(win=WIN, pos=(0,+.40), size=(.90, .30), lineColor='blue', lineWidth=10)
PROG_AOI      = visual.ROI(win=WIN, tracker=eyetracker, shape='rectangle', pos=(0,+.40), size=(.90, .30))

FIXATION_TAR = visual.Rect(win=WIN, pos=(0,0), size=(.15, .15), lineColor='blue', lineWidth=10)
FIXATION_AOI = visual.ROI(win=WIN, tracker=eyetracker, shape='rectangle', pos=(0,0), size=(.15, .15))

### STIMULI - IMAGE PATH ###
STIM_BALL_DIR           = f'.{os.sep}stimuli{os.sep}ball{os.sep}'
BALL_UP_DIR             = f'{STIM_BALL_DIR}up_b.png'
BALL_DOWN_DIR           = f'{STIM_BALL_DIR}down_b.png'
BALL_UP_DIR_CORRECT     = f'{STIM_BALL_DIR}up_g.png'
BALL_DOWN_DIR_CORRECT   = f'{STIM_BALL_DIR}down_g.png'
BALL_UP_DIR_WRONG       = f'{STIM_BALL_DIR}up_r.png'
BALL_DOWN_DIR_WRONG     = f'{STIM_BALL_DIR}down_r.png'
BALL_UP_DIR_SLOW        = f'{STIM_BALL_DIR}up_gray.png'
BALL_DOWN_DIR_SLOW      = f'{STIM_BALL_DIR}down_gray.png'

### ------------------------- ADMIN ------------------------- ###

if TEST_MODE:
    NUM_PRACTICE_CORRECT_BAR   = 10
    NUM_PRACTICE_CORRECT_FINAL = 10

if IF_SEE_COMPUTR_PLAY:
    ITI1 = 2e-16
    ITI2 = 2e-16
    AI_INSTRUCTION_TIME = 2e-16 # 1.000
    AI_RT_LOW  = 2e-16 #.300 # .001
    AI_RT_HIGH = 2e-16 #.700 # .001
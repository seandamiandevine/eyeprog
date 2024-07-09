import numpy as np
from .constant import *

### ------------------------- TASK BLOCK ------------------------- ###

def show_insturction(inst_dir):

    slides     = os.listdir(inst_dir)
    slides     = [slide for slide in slides if slide[0] == 'S'] # exclude hidden files
    slide_nums = [int(slide[5:-4]) for slide in slides] # extract num from 'Slide1.png'
    total_num  = len(slides)
    pic        = visual.ImageStim(WIN, image=None,)
    
    counter = 0
    while counter < total_num:

        if slide_nums[counter] < 10:
            pic.image = f'{inst_dir}Slide0{slide_nums[counter]}.png'
        else:
            pic.image = f'{inst_dir}Slide{slide_nums[counter]}.png'
        pic.draw()
        WIN.flip()
        
        if IF_SEE_COMPUTR_PLAY:
            core.wait(AI_INSTRUCTION_TIME)
            response = 'right'
        else:
            key_press = event.waitKeys(keyList=['escape']+['left', 'right'])
            response  = key_press[0]

        if response == 'escape': 
            core.quit()
        elif (response =='left') & (counter>0):
            counter -= 1
        elif response =='right':
            counter += 1

def calibrate_eyetracker():

    calibrationTarget = visual.TargetStim(WIN, 
        name='calibrationTarget',
        radius=0.01, borderColor='black', lineWidth=2.0,
        innerRadius=0.0035, innerFillColor='black', innerLineWidth=2.0,
        fillColor='blue', 
        innerBorderColor='blue',
        colorSpace='rgb255', units=None
    )
    # define parameters for calibration
    calibration = hardware.eyetracker.EyetrackerCalibration(
        WIN, eyetracker, calibrationTarget,
        units=None, colorSpace='rgb255',
        progressMode='time', targetDur=1.5, expandScale=1.5,
        targetLayout='NINE_POINTS', randomisePos=True,
        movementAnimation=True, targetDelay=1.0
    )
    # run calibration
    calibration.run()

def practice_progressbar(TARGET_NUM, EXPDATA, Phase='PraticeBar', ITI1=ITI1):

    t = 0
    correct_count = 0 # show one grid at first
    prog_percent  = 0
    
    progLookStart = np.nan
    progLookEnd   = np.nan
    progLookDur   = 0
    ifFacilitate  = True
    TXT = visual.TextStim(win=WIN, text='', height=.05, pos=[0, .2], color='white')
     
    ### ----------  Tutorial Starts ---------- ###
    while prog_percent <= 1.00:

        t += 1
        # GLOBALTRIAL += 1 # global trial
        # start with facilitation #
        if prog_percent == 0:
            TXT.text = 'Follow the blue rectangle!'
            TXT.draw()
            WIN.flip()
            core.wait(3.000)

        # turn off facilitation #
        if prog_percent == 0.5:
            ifFacilitate = False 
            TXT.text = 'Keep going without facilitation!'
            TXT.draw()
            WIN.flip()
            core.wait(3.000)

        ### Notice ###
        TXT.text = 'Get ready!'
        TXT.draw()
        WIN.flip()
        core.wait(1.000)
        key_press = event.waitKeys(keyList=['escape'], maxWait=(1.000))
        if not key_press == None:
            if key_press[0] == 'escape':
                core.quit()

        ### ----------  Fixation Trial ---------- ###

        ### Present ITI 1 - Progress ###
        ITI1_time = CLOCK.getTime()
        ifLookedFix  = False
        ifLookedProg = False # only allow look once
        gazeCursor.status = STARTED
        eyetracker_record.status = STARTED
        PROG_AOI.stauts = STARTED
        
        while CLOCK.getTime() - ITI1_time < ITI1:

            # # gaze cursor #
            # gazeCursor.setPos([eyetracker.getPos()], log=False)
            # gazeCursor.setAutoDraw(True)

            # fixation #
            if not ifLookedFix:
                FIXATION.color = 'white'
                FIXATION.draw()
            else:
                FIXATION.color = 'green'
                FIXATION.draw()

            ### faciliatation ###
            if ifFacilitate:
                if not ifLookedFix:
                    FIXATION_TAR.draw() # facilitation no.1 - cross
                if ifLookedFix & (not ifLookedProg):
                    PROG_TARGET.draw() # facilitation no.1 - progress bar
 
            # show #
            WIN.flip()

            if FIXATION_AOI.isLookedIn:
                ifLookedFix = True

            # Looking at the progress bar #
            progStartLoc = np.nan
            progEndLoc = np.nan
            progLookStart = np.nan
            progLookEnd = np.nan
            progLookDur = 0
            progStartDiff = np.nan
            progEndDiff = np.nan
            
            if ifLookedFix & (not ifLookedProg): # only one chance

                ifFreeze = False
                while PROG_AOI.isLookedIn & (CLOCK.getTime() - ITI1_time < ITI1):
                    
                    # draw #
                    FIXATION.draw() # keep fixation
                    PROG_BAR_OUTLINE.draw()

                    PROG_BAR.draw()

                    # freeze bar #
                    if not ifFreeze:
                        WIN.flip()
                        progStartLoc  = eyetracker.getPos()
                        progLookStart = CLOCK.getTime()
                        ifFreeze = True
                        ifLookedProg = True
                    else:
                        pass # no flip update = Freeze
                
                if ifLookedProg:
                    progEndLoc  = eyetracker.getPos()
                    progLookEnd = CLOCK.getTime()
                    progLookDur = progLookEnd - progLookStart
                    # progStartDiff = np.sqrt((progStartLoc[0]-PROG_BAR.pos[0])**2 + (progStartLoc[1]-PROG_BAR.pos[1])**2)
                    # progEndDiff = np.sqrt((progEndLoc[0]-PROG_BAR.pos[0])**2 + (progEndLoc[1]-PROG_BAR.pos[1])**2)

        ### END OF ITI 1 ###
        if ifLookedProg: correct_count += 1
        prog_percent  = correct_count/TARGET_NUM
        PROG_BAR.size = (OUTLINE_SIZE[0] * prog_percent, OUTLINE_SIZE[1] * .80)
        PROG_BAR.pos  = (-OUTLINE_SIZE[0] / 2 + PROG_BAR.size[0] / 2, OUTLINE_POS[1]) # update progress bar
        gazeCursor.status = FINISHED
        eyetracker_record.status = FINISHED
        gazeCursor.setAutoDraw(False)

        ### Present ITI 2 - Fixation ###
        WIN.flip() # blank
        FIXATION.color = 'white'
        ITI2_time = CLOCK.getTime()
        FIXATION.draw()
        WIN.flip()
        core.wait(ITI2)

        ### ---------- Save Data ---------- ###
        # EXPDATA.addData('GLOBALTRIAL',    GLOBALTRIAL)
        EXPDATA.addData('Phase',          Phase)
        EXPDATA.addData('TrialType',      'Fixation')
        EXPDATA.addData('Trial',          t)
        EXPDATA.addData('ifProgress',     1)
        ### Progress Bar ###
        EXPDATA.addData('ifLookedFix',    int(ifLookedFix))
        EXPDATA.addData('ifLookProg',     int(ifLookedProg))
        EXPDATA.addData('progLookDur',    progLookDur)
        EXPDATA.addData('progStartLoc',   progStartLoc)
        EXPDATA.addData('progEndLoc',     progEndLoc)
        EXPDATA.addData('progPosition',   list(PROG_BAR.pos))
        # EXPDATA.addData('progStartDiff',  progStartDiff)
        # EXPDATA.addData('progEndDiff',    progEndDiff)
        ### TIME STAMP ###
        EXPDATA.addData('ITI1',           ITI1_time)
        EXPDATA.addData('progLookStart',  progLookStart)
        EXPDATA.addData('progLookEnd',    progLookEnd)
        EXPDATA.addData('ITI2',           ITI2_time)
        EXPDATA.addData('END',            datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
        EXPDATA.nextEntry()

def run_block(EXPDATA, correct_target, isProgress, block_idx, Phase):

    t = 0
    correct_count = 0
    prog_percent = 0

    ### show block number ###
    BLOCK_TXT.draw()
    WIN.flip()
    core.wait(BLOCK_TXT_DUR)

    # run trial
    while True:

        ### ---------- Prepare Trial Stimuli ---------- ###
        t += 1 # Actual trial = odd
        # GLOBALTRIAL += 1 # global trial
        ball_indices = [None, None, None]
        patterns = ['up', 'down']
        correct_feedback_paths = []
        wrong_feedback_paths = []
        slow_feedback_paths = []

        # randomize odd location (i.e., left, middle, right)
        outlier = np.random.randint(0, 2 + 1)
        # randomize odd pattern (i.e., up, down)
        outlier_pattern = np.random.choice(patterns)
        non_outlier_pattern = list(set(patterns) - set([outlier_pattern]))[0]

        # fill ball_indices with corresonding image
        for i in range(len(balls)):

            if i == outlier:
                ball_indices[i] = outlier_pattern
            else:
                ball_indices[i] = non_outlier_pattern

        # assign image to each ball stimulus
        for i in range(len(balls)):

            if ball_indices[i] == 'up':
                balls[i].image = BALL_UP_DIR
                correct_feedback_paths.append(BALL_UP_DIR_CORRECT)
                wrong_feedback_paths.append(BALL_UP_DIR_WRONG)
                slow_feedback_paths.append(BALL_UP_DIR_SLOW)
            else:
                balls[i].image = BALL_DOWN_DIR
                correct_feedback_paths.append(BALL_DOWN_DIR_CORRECT)
                wrong_feedback_paths.append(BALL_DOWN_DIR_WRONG)
                slow_feedback_paths.append(BALL_DOWN_DIR_SLOW)
        
        # assign color based on ifCorrect
        if np.random.random() <= .10:
            this_timeout = TIMEOUT_FAST   # 10% trials have faster deadline
        else:
            this_timeout = TIMEOUT        # 90% standard deadline

        ### ---------- Actual Trial Begins ---------- ###
        
        gazeCursor.status = STARTED
        eyetracker_record.status = STARTED
        
        ### present trial ###
        for ball in balls:
            ball.draw()

        stimuli_time = CLOCK.getTime()
        WIN.flip()
        ioServer.sendMessageEvent(text='Odd Ball Presented')

        ### record Response & RT ###
        if IF_SEE_COMPUTR_PLAY:
            
            core.wait(np.random.uniform(AI_RT_LOW, AI_RT_HIGH))
            rand = np.random.random()
            if rand <= .10: key_press = None # 10% miss
            elif rand <= .30: key_press = CHOICE_KEYS[np.random.randint(0, len(balls))] # 20% random choice
            else: key_press = CHOICE_KEYS[outlier] # 80% accuracy robot
            
        else:
            key_press = event.waitKeys(keyList=CHOICE_KEYS + ['escape'], maxWait=this_timeout)
            ioServer.sendMessageEvent(text='Response Registered')

        ### Process Key Press ###
        if key_press == None:
            # too slow
            isSlow    = True
            isCorrect = False
            RT        = np.nan
            choice    = np.nan
            key_press_time = np.nan
        else:
            # end game if escape
            response = key_press[0]
            if response == 'escape': 
                eyetracker.setConnectionState(False)
                core.quit()
            
            # valid response
            isSlow    = False
            key_press_time = CLOCK.getTime()
            RT = key_press_time - stimuli_time
            response_idx = CHOICE_KEYS.index(response)
            isCorrect = (response_idx == outlier)
            choice = response_idx + 1 # python starts 0

        ### Prepare feedback ###
        if isSlow:
            feedback_paths = slow_feedback_paths
            feedback = 'SLOW'
        elif isCorrect:
            feedback_paths = correct_feedback_paths
            feedback = 'CORRECT'
        elif ~isCorrect:
            feedback_paths = wrong_feedback_paths
            feedback = 'WRONG'

        ### Present feedback ###
        for i in range(len(balls)):
            balls[i].image = feedback_paths[i]
            balls[i].draw()

        WIN.flip()
        feedback_time = CLOCK.getTime()
        core.wait(FEEDBACK_DUR)

        ### Prepare Progress ###
        if isCorrect: correct_count += 1
        new_prog_percent = correct_count / correct_target
        gazeCursor.status = FINISHED
        eyetracker_record.status = FINISHED

        ### ---------- Save Data ---------- ###
        # EXPDATA.addData('GLOBALTRIAL',    GLOBALTRIAL)
        EXPDATA.addData('Phase',          Phase)
        EXPDATA.addData('Block',          block_idx)
        EXPDATA.addData('TrialType',      'Ball')
        EXPDATA.addData('ifProgress',     isProgress)
        EXPDATA.addData('Trial',          t)
        # save the progress before current trial is completed
        EXPDATA.addData('PFilled',        prog_percent)
        EXPDATA.addData('TimeOut',        this_timeout)
        EXPDATA.addData('RT',             RT)
        EXPDATA.addData('Choice',         choice)
        EXPDATA.addData('CorrectAnswer',  outlier + 1)
        EXPDATA.addData('CorrectLoc',     outlier_pattern)
        EXPDATA.addData('Feedback',       feedback)  # correct, wrong, slow
        EXPDATA.addData('CorrectCount',   correct_count)
        EXPDATA.addData('CorrectRequire', correct_target)
        EXPDATA.addData('PFilledNew',     new_prog_percent)
        ### TIME STAMP ###
        EXPDATA.addData('START',          stimuli_time)
        EXPDATA.addData('KeyPressTime',   key_press_time)
        EXPDATA.addData('FeedbackTime',   feedback_time)
        EXPDATA.addData('END',            datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
        ### SAVE BEHAVIOR DATA ###
        EXPDATA.nextEntry()

        ### ----------  Fixation Trial ---------- ###
        ### Prepare ITI 1 - Progress ###
        WIN.flip() # blank
        t += 1 # Fixation = odd
        # GLOBALTRIAL += 1 # GLOBAL GLOBALTRIAL

        PROG_BAR.size = (OUTLINE_SIZE[0] * new_prog_percent, OUTLINE_SIZE[1] * .80)
        PROG_BAR.pos = (-OUTLINE_SIZE[0] / 2 + PROG_BAR.size[0] / 2, OUTLINE_POS[1]) # update progress bar
        ### Present ITI 1 - Progress ###
        ITI1_time = CLOCK.getTime()

        ifLookedFix  = False
        ifLookedProg = False # only allow look once
        progStartLoc = np.nan
        progEndLoc = np.nan
        progLookStart = np.nan
        progLookEnd = np.nan
        progLookDur = 0
        progStartDiff = np.nan
        progEndDiff = np.nan
        gazeCursor.status = STARTED
        eyetracker_record.status = STARTED
        PROG_AOI.stauts = STARTED
        
        if isProgress == None: # pure behavorial Trial
            WIN.flip() # blank
            FIXATION.color = 'white'
            ITI1_time = CLOCK.getTime()
            FIXATION.draw()
            WIN.flip()
            core.wait(ITI1)
            ITI2_time = CLOCK.getTime()
            core.wait(ITI2)

            gazeCursor.status = FINISHED
            eyetracker_record.status = FINISHED

        if isProgress != None: # eyetracker trial
            while (CLOCK.getTime() - ITI1_time < ITI1):
        
                # gaze cursor #
                # gazeCursor.setPos([eyetracker.getPos()], log=False)
                # gazeCursor.setAutoDraw(True)
    
                # fixation #
                if not ifLookedFix:
                    FIXATION.color = 'white'
                    FIXATION.draw()
                else:
                    if isProgress==0:
                        FIXATION.color = 'gray'
                    if isProgress==1:
                        FIXATION.color = 'green'
                    FIXATION.draw()
                
                # show #
                WIN.flip()
                
                if FIXATION_AOI.isLookedIn:
                    ifLookedFix = True  
                
                # Looking at the progress bar #
                if ifLookedFix & (not ifLookedProg): # only one chance

                    ifFreeze = False
                    while PROG_AOI.isLookedIn & (CLOCK.getTime() - ITI1_time < ITI1):
                        
                        # draw #
                        FIXATION.draw() # keep fixation
                        PROG_BAR_OUTLINE.draw()

                        if isProgress:
                            PROG_BAR.draw()
                        if not isProgress: 
                            PROG_BAR_CONTROL.draw()

                        # freeze bar #
                        if not ifFreeze:
                            WIN.flip()
                            ioServer.sendMessageEvent(text='Start Looking at Progress Bar')
                            progStartLoc  = eyetracker.getPos()
                            progLookStart = CLOCK.getTime()
                            ifFreeze = True
                            ifLookedProg = True
                        else:
                            pass # no flip update = Freeze

                    ### End of Looking at Progress Bar ###
                    if ifLookedProg: # if the switch is flipped
                        ioServer.sendMessageEvent(text='Finish Looking at Progress Bar')
                        progEndLoc  = eyetracker.getPos()
                        progLookEnd = CLOCK.getTime()
                        progLookDur = progLookEnd - progLookStart
                        # progStartDiff = np.sqrt((progStartLoc[0]-PROG_BAR.pos[0])**2 + (progStartLoc[1]-PROG_BAR.pos[1])**2)
                        # progEndDiff = np.sqrt((progEndLoc[0]-PROG_BAR.pos[0])**2 + (progEndLoc[1]-PROG_BAR.pos[1])**2)

            ### END OF ITI 1 ###
            gazeCursor.status = FINISHED
            eyetracker_record.status = FINISHED
            gazeCursor.setAutoDraw(False)

            ### Present ITI 2 - Fixation ###
            WIN.flip() # blank
            FIXATION.color = 'white'
            ITI2_time = CLOCK.getTime()
            FIXATION.draw()
            WIN.flip()
            core.wait(ITI2)
        
        ### ---------- Save Data ---------- ###
        # EXPDATA.addData('GLOBALTRIAL',    GLOBALTRIAL)
        EXPDATA.addData('Phase',          Phase)
        EXPDATA.addData('Block',          block_idx)
        EXPDATA.addData('TrialType',      'Fixation')
        EXPDATA.addData('ifProgress',     isProgress)
        EXPDATA.addData('Trial',          t)
        ### Progress Bar ###
        EXPDATA.addData('ifLookedFix',    int(ifLookedFix))
        EXPDATA.addData('ifLookProg',     int(ifLookedProg))
        EXPDATA.addData('progLookDur',    progLookDur)
        EXPDATA.addData('progStartLoc',   progStartLoc)
        EXPDATA.addData('progEndLoc',     progEndLoc)
        EXPDATA.addData('progPosition',   list(PROG_BAR.pos))
        # EXPDATA.addData('progStartDiff',  progStartDiff)
        # EXPDATA.addData('progEndDiff',    progEndDiff)
        ### TIME STAMP ###
        EXPDATA.addData('START',          ITI1_time)
        EXPDATA.addData('ITI1',           ITI1_time)
        EXPDATA.addData('progLookStart',  progLookStart)
        EXPDATA.addData('progLookEnd',    progLookEnd)
        EXPDATA.addData('ITI2',           ITI2_time)
        EXPDATA.addData('END',            datetime.datetime.now().strftime("%y%m%d_%H%M%S"))
        
        ### SAVE BEHAVIOR DATA ###
        EXPDATA.nextEntry()

        ### CHECK END OF BLOCK ###
        if new_prog_percent != 1.00:  # CHECK the end of the prorgess
            prog_percent = new_prog_percent
            continue
        else: # end block and return accuracy
            # reset progress bar
            PROG_BAR.size = (OUTLINE_SIZE[0] * 0.00, OUTLINE_SIZE[1] * .80)
            PROG_BAR.pos = (-OUTLINE_SIZE[0] / 2 + PROG_BAR.size[0] / 2, OUTLINE_POS[1]) # update progress bar
            return correct_count / t

def terminal_final_msg():
    ### FINAL MESSAGE TERMINAL ###
    SONA = DEMOGRAPHICS.get('SONA')    
    EXPTR_NAME = DEMOGRAPHICS.get('EXPERIMENTER').split(' ')[0]
    message = f'------------------------- FINISHED TESTING PARTICIPANT {SONA} ---------------------'
    print(termcolor.colored(message, 'blue'))
    message = f'------------------------- THANK YOU {EXPTR_NAME.upper()} -------------------------'
    print(termcolor.colored(message, 'green'))

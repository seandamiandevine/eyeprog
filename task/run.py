from src.constant import *   # task-specific global variables
from src import IPROG        # task-specific functions

### ------------------------- PRACTICE PHASE ------------------------- ###

# ### PHASE 1 - WELCOME & CALIRATION ###
IPROG.show_insturction(INST_1)
IPROG.calibrate_eyetracker()

# ### PHASE 2 - PRACTICE PHASE - BEHAVIORAL ###
IPROG.show_insturction(INST_2)
IPROG.run_block(Phase='PraticeBall', correct_target=5, isProgress=None, 
                block_idx=None, EXPDATA=EXPDATA)

### PHASE 3 - PRACTICE PHASE - PROGRESS BAR ###
IPROG.show_insturction(INST_3)
IPROG.practice_progressbar(Phase='PraticeBar', TARGET_NUM=NUM_PRACTICE_CORRECT_BAR, EXPDATA=EXPDATA)

### PHASE 4 - PRACTICE PHASE - BEHAVIORAL + PROGRESS ###
IPROG.show_insturction(INST_4)
isProgresses = [0, 1]
np.random.shuffle(isProgresses)
for i in isProgresses:
	IPROG.run_block(isProgress=i, 
					Phase='PracticeFinal', correct_target=NUM_PRACTICE_CORRECT_FINAL,
               		block_idx=None, EXPDATA=EXPDATA)

### ------------------------- MAIN TASK ------------------------- ###

## PHASE 5 - MAIN PHASE ###
IPROG.show_insturction(INST_5)

accuracies = []
for i in range(NUM_BLOCK):

    acc = IPROG.run_block(Phase='Task', correct_target=TRIALS[i], isProgress=BLOCKS[i], 
                          block_idx=i+1, EXPDATA=EXPDATA)
    accuracies.append(acc)

accuracy = np.mean(accuracies)

### ------------------------- END ------------------------- ###

### calculate compensation here ###
pass

eyetracker.setConnectionState(False)

### FINAL MESSAGE - PSYCHOPY ###
IPROG.show_insturction(INST_6)
WIN.flip()
event.waitKeys(keyList=['escape'])

### FINAL MESSAGE - TERMINAL ###
IPROG.terminal_final_msg()

### QUIT ###
core.quit()
EXPDATA.abort()
WIN.close()
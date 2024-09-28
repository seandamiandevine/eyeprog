
"""
Process pupillometry data for eyeprog study.

To run from terminal: 
	python process.py

Note: If this is the first time you've run this script, make sure `CONV_EDF` is True. 
This converts .EDF files into .ascii files, which is necessary for processing, but slow. 
If you are rerunning this script, set `CONV_EDF` to False for significantly faster runtime. 

For questions: 
seandamiandevine@gmail.com

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import sem 
from scipy.signal import resample, decimate
import pypillometry as pp
import pickle
import os
from glob import glob
import os
os.chdir('/Users/sean/documents/eyeprog/full/eye')
import warnings
from tqdm import tqdm
from fx.fx import *

pd.options.mode.chained_assignment = None  # default='warn'


# Constants
FIGPATH       = 'figs/'
OUTPATH       = 'processed/'
PLOT_SEGS     = False
CONV_EDF      = False # should the .ascii files be extracted from the .edf files? 
PROCESS_PARS  = { "min_duration":2,                # min duration of a blink          
                  "min_offset_len": 5,             # offset/onset-length for blink-detection
                  "min_onset_len":5,               # minimum number of samples that cross threshold to detect as onset                                
                  "vel_onset":-5,                  # velocity thresholds for onset and offset
                  "vel_offset":5,                  # positive velocity that needs to be exceeded                               
                  "strategies":["zero","velocity"],# strategies for blink-detection  
                  "distance":10,                   # minimum distance between two blinks
                  "margin":(50,150),               # margins for interpolation
                  "interp_type":'cubic',           # type of interpolation    
                  "cutoff":5,		               # lowpass-filter cutoff (Hz)        
                  "fix_time_win":  (0, 1000),      # time window for Fixation trials (750 ms fixation + 250 ms ITI)
                  "ball_time_win": (0, 750),       # time window for Ball trials (750 ms trial (without considering RT))
                  "ball_base_win": (-250,0)        # time window for baseline for Ball trials (250 ms ITI)
                  }          

# Loop through subjs
bases = [f.replace('.EDF','') for f in glob('../data/*/Data/*.EDF')]
PIDs  = [b.split('/')[2] for b in bases]

# convert EDF --> asc if needed
if CONV_EDF:
	files = glob('../data/*/Data/*.EDF')
	edf2asc(files)

processed = {}
for i,base in enumerate(bases):
	
	print('*'*25, 'Processed file: ', i, '/', len(bases), '*'*25)

	# load
	behav, df = read_file(base, convert_edf = False, save_out=True)

	# preprocess
	dp = df.blinks_detect(units="ms", 
		min_duration=PROCESS_PARS["min_duration"],
		strategies=PROCESS_PARS["strategies"])\
	        .blinks_merge(distance=PROCESS_PARS["distance"])\
	        .blinks_interpolate(vel_onset=PROCESS_PARS["vel_onset"], 
	        	vel_offset=PROCESS_PARS["vel_offset"], 
	        	margin=PROCESS_PARS["margin"])

	## compute phasic signal with 5Hz filter
	dp_p = dp.copy()
	dp_p = dp_p.lowpass_filter(cutoff=PROCESS_PARS["cutoff"])\
	        .downsample(50)\
	        .scale()

	## compute tonic signal with 0.01Hz filter
	dp_t = dp.copy()
	dp_t = dp_t.lowpass_filter(cutoff=0.01)\
	        .downsample(50)\
	        .scale()

	## example visualization
	# fig,ax=plt.subplots(1)
	# idx = 70_000
    # ax.plot(dp_p.tx[:idx]/1000/60, dp_p.sy[:idx], label="Phasic")
    # ax.plot(dp_t.tx[:idx]/1000/60, dp_t.sy[:idx], label="Tonic", lw=2)
    # ax.set(xlabel="Minutes", title=f"Subject #{behav.PID.iloc[0]}")
    # ax.legend()
    # plt.show()

    ## save preprocess for group analysis
	processed[PIDs[i]] = dp_p 

	if PLOT_SEGS:
    	df.plot_segments(overlay=dp_p, pdffile=f'{FIGPATH}subj_seg/{PIDs[i]}.pdf')

    # Compute summary statistics
    ## This requires different baseline correction periods based on the task phase: 
    	# For Fixation trials, there is no ITI before the fixation, so we do not baseline correct (would overlap with feedback)
    	# For Trials, there is a 250 ms ITI that we can take as a baseline
    ## Furthermore, different trials have different RTs and rare  trials have shorter deadlines (10% of the time).
    ## This means that the time window around events is not the same trial to trial. 
    	## We can either ignore this and use a fixed window for all trials (implemented when USE_RTS is False)
    	## or cycle through all behavioural data and adjust windows dynamically (when USE_RTS is True)

    ## before anything, check if number of event labels match number of recorded behavioural trials. 
    ## If not, default to fixed windows. 
    if behav.shape[0]!=len(dp_p.event_labels):
    	warnings.warn("Number of eyetracking events and number of behavioural events do NOT match!")     	

    ## Prepare containers 
	behav["phasic_pupil_base"]       = np.nan
	behav["phasic_pupil_terp_mean"]  = np.nan
	behav["phasic_pupil_terp_max"]   = np.nan
	behav["tonic_pupil_base"]        = np.nan
	behav["tonic_pupil_terp_mean"]   = np.nan
	behav["tonic_pupil_terp_max"]    = np.nan

	## Compute all non-dynamic summary statistics + merge with behaviour <-- Saves a significant amount of time
	### phasic 
	p_fix_terp_mean  = dp_p.stat_per_event(PROCESS_PARS["fix_time_win"], event_select="Fixation_", statfct=np.mean)
    p_fix_terp_max   = dp_p.stat_per_event(PROCESS_PARS["fix_time_win"], event_select="Fixation_", statfct=np.max)
	p_ball_baseline  = dp_p.stat_per_event(PROCESS_PARS["ball_base_win"], event_select="Ball_",    statfct=np.mean)

	### tonic
	t_fix_terp_mean  = dp_t.stat_per_event(PROCESS_PARS["fix_time_win"], event_select="Fixation_", statfct=np.mean)
    t_fix_terp_max   = dp_t.stat_per_event(PROCESS_PARS["fix_time_win"], event_select="Fixation_", statfct=np.max)
	t_ball_baseline  = dp_t.stat_per_event(PROCESS_PARS["ball_base_win"], event_select="Ball_",    statfct=np.mean)

	## store
	behav["phasic_pupil_base"][behav.TrialType=="Fixation"]      = np.nan
	behav["phasic_pupil_terp_mean"][behav.TrialType=="Fixation"] = p_fix_terp_mean
	behav["phasic_pupil_terp_max"][behav.TrialType=="Fixation"]  = p_fix_terp_max
	behav["phasic_pupil_base"][behav.TrialType=="Ball"]          = p_ball_baseline

	behav["tonic_pupil_base"][behav.TrialType=="Fixation"]      = np.nan
	behav["tonic_pupil_terp_mean"][behav.TrialType=="Fixation"] = t_fix_terp_mean
	behav["tonic_pupil_terp_max"][behav.TrialType=="Fixation"]  = t_fix_terp_max
	behav["tonic_pupil_base"][behav.TrialType=="Ball"]          = t_ball_baseline

	## Loop through events
	for j in tqdm(range(behav.shape[0])):

		if behav.iloc[j]["TrialType"]=="Ball":

			## Get timeout and RT info to make dynamic stimulus window
			timeout  = behav.iloc[j]["TimeOut"]*1000
			rt       = np.nanmin([behav.iloc[j]["RT"]*1000,timeout]) ## if no RT, just use max timeout
			stim_win = (dp_p.event_onsets[j],dp_p.event_onsets[j]+rt)

			## Compute phasic signal
			phasic_signal_mu  = dp_p.sub_slice(*stim_win, units="ms").sy.mean()
			phasic_signal_max = dp_p.sub_slice(*stim_win, units="ms").sy.max()

			## Compute tonic signal
			tonic_signal_mu  = dp_t.sub_slice(*stim_win, units="ms").sy.mean()
			tonic_signal_max = dp_t.sub_slice(*stim_win, units="ms").sy.max()

			## Store results
			behav["phasic_pupil_terp_mean"].iloc[j]  = phasic_signal_mu
			behav["phasic_pupil_terp_max"].iloc[j]   = phasic_signal_max
			behav["tonic_pupil_terp_mean"].iloc[j]   = tonic_signal_mu
			behav["tonic_pupil_terp_max"].iloc[j]    = tonic_signal_max

	# save to csv
	behav.to_csv(f'{OUTPATH}{PIDs[i]}.csv')




import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pypillometry as pp
import os

def edf2asc(files: list, progress:bool=False) -> None :
	"""Converts a list of files to asc in their respective directory.
	Requires SR's edf2asc mac binary: https://ihrke.github.io/pypillometry/html/docs/importdata.html
	
	Args:
	    files (list):    The file list to convert.
	    progress (bool): Show progress?

	Returns: 
		None
	"""

	for i, file in enumerate(files):
		if(progress):
			print('*'*5, f'Parsing file: {i}/{len(files)}', '*'*5)

		os.system(f'edf2asc -s {file} {file.replace(".EDF","_samples.asc")}')
		os.system(f'edf2asc -e {file} {file.replace(".EDF","_events.asc")}')

	return None


def read_file(base_url: str, convert_edf:bool = False, save_out:bool = True) -> pp.PupilData:
	"""Read Eyelink file (EDF or asc) to pp.PupilData.
	
	Args:
	    base_url (str):               Location of eyelink and behavioural files.
	    convert_edf (bool, optional): Is the input file EDF? If so, convert it to asc in, and store in base_url.
	    save_out (bool, optional):    Should the output be saved to base_url?
	
	Returns:
	    pp.PupilData: pypillometry data frame
	"""
	if convert_edf:
		edf2asc(base_url+'.EDF')

	fname_behav   = base_url + '.csv'
	fname_samples = base_url + '_samples.asc'
	fname_events  = base_url + '_events.asc'

	# load behav
	behav = pd.read_csv(fname_behav)

	# load samples
	samples = pd.read_table(fname_samples, index_col=False, names=["time", "left_x", "left_y", "left_p","right_x", "right_y", "right_p"])

	# load events
	with open(fname_events) as f:
		events=f.readlines()

	events = [ev for ev in events if ev.startswith("START")]
	events = pd.DataFrame([ev.split() for ev in events]).iloc[:,0:2]
	events.columns = ['start','time']

	# Combine behavioural and event data
	be = behav.copy()
	be['PFilled'] = be.PFilled.fillna(method='ffill')
	be['time_ev'] = events.time
	be['event']   = be['TrialType'] + '_' + be['ifProgress'] + '_' + be['PFilled'].astype(str)
	
	# Remove practice
	# be = be[be.Phase=='Task']
	be = be[['time_ev','event']]

	# store as pp.PupilData
	df = pp.PupilData(samples.left_p, time=samples.time, event_onsets=be.time_ev, event_labels=be.event, name=base_url.split('/')[-1])
	df = df.reset_time()

	if save_out: 
		df.write_file(base_url + '_pp.pd')

	return behav, df 




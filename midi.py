from midiutil.MidiFile import MIDIFile
import random
import numpy as np
import pandas as pd
import os
import sys

def getPercentOffBeat(i):
	percentOffBeatMin = -0.5 + (i * 0.1)
	percentOffBeatMax = percentOffBeatMin + 0.1
	percentOffBeat = np.linspace(percentOffBeatMin, percentOffBeatMax, num=10)
	return percentOffBeat

# Define CSV arrays
snareMicrotiming = np.array([])
bassDrumMicrotiming = np.array([])
hihatMicrotiming = np.array([])
snareVelocity = np.array([])
bassDrumVelocity = np.array([])
hihatVelocity = np.array([])

# Get drummer number
# Method 1: command line argument (ex. "python midi.py 3" for drummer 3)
# Method 2: input (ex. "python midi.py", then type 3 when prompted to select drummer 3)
drummerNum = ""
if len(sys.argv) > 1:
	drummerNum = sys.argv[1]
else:
	drummerNum = input("Enter drummer number: ")

# Get info from csv files
csv = 'drummer' + drummerNum + 'Microtiming.csv'
if(os.path.exists(csv)):
	df = pd.read_csv(csv)
	snareMicrotiming = df.loc[:,"snareMicrotiming"].values
	bassDrumMicrotiming = df.loc[:,"bassDrumMicrotiming"].values
	hihatMicrotiming = df.loc[:,"hihatMicrotiming"].values
else:
	print("Error! Could not find file " + csv)
	quit()

csv = 'drummer' + drummerNum + 'Velocity.csv'
if(os.path.exists(csv)):
	df = pd.read_csv(csv)
	snareVelocity = df.loc[:,"snareVelocity"].values
	bassDrumVelocity = df.loc[:,"bassDrumVelocity"].values
	hihatVelocity = df.loc[:,"hihatVelocity"].values
else:
	print("Error! Could not find file " + csv)
	quit()

# Change all negative values to 0s
snareMicrotiming[snareMicrotiming < 0] = 0
bassDrumMicrotiming[bassDrumMicrotiming < 0] = 0
hihatMicrotiming[hihatMicrotiming < 0] = 0
snareVelocity[snareVelocity < 0] = 0
bassDrumVelocity[bassDrumVelocity < 0] = 0
hihatVelocity[hihatVelocity < 0] = 0

# Normalize all arrays so the sum equals 1
snareMicrotiming = snareMicrotiming / sum(snareMicrotiming)
bassDrumMicrotiming = bassDrumMicrotiming / sum(bassDrumMicrotiming)
hihatMicrotiming = hihatMicrotiming / sum(hihatMicrotiming)
snareVelocity = snareVelocity / sum(snareVelocity)
bassDrumVelocity = bassDrumVelocity / sum(bassDrumVelocity)
hihatVelocity = hihatVelocity / sum(hihatVelocity)

snarePercentOffBeatValues = np.array([])
snarePercentOffBeatProbabilites = np.array([])
bassDrumPercentOffBeatValues = np.array([])
bassDrumPercentOffBeatProbabilites = np.array([])
hihatPercentOffBeatValues = np.array([])
hihatPercentOffBeatProbabilites = np.array([])

snareVelocityValues = np.arange(128)
snareVelocityProbabilites = np.array([])
bassDrumVelocityValues = np.arange(128)
bassDrumVelocityProbabilites = np.array([])
hihatVelocityValues = np.arange(128)
hihatVelocityProbabilites = np.array([])

# Interpolate the values in the histogram bins (10 for microtiming, 8 for velocity)
for i in range(0, snareMicrotiming.size):
	# Microtiming
	percentOffBeat = getPercentOffBeat(i)

	snarePercentOffBeatValues = np.concatenate((snarePercentOffBeatValues, percentOffBeat))
	bassDrumPercentOffBeatValues = np.concatenate((bassDrumPercentOffBeatValues, percentOffBeat))
	hihatPercentOffBeatValues = np.concatenate((hihatPercentOffBeatValues, percentOffBeat))

	snareProbabilites = np.repeat((snareMicrotiming[i] / 10), 10)
	bassDrumProbabilites = np.repeat((bassDrumMicrotiming[i] / 10), 10)
	hihatProbabilites = np.repeat((hihatMicrotiming[i] / 10), 10)

	snarePercentOffBeatProbabilites = np.concatenate((snarePercentOffBeatProbabilites, snareProbabilites))
	bassDrumPercentOffBeatProbabilites = np.concatenate((bassDrumPercentOffBeatProbabilites, bassDrumProbabilites))
	hihatPercentOffBeatProbabilites = np.concatenate((hihatPercentOffBeatProbabilites, hihatProbabilites))

for i in range(0, snareVelocity.size):
	# Velocity
	snareProbabilites = np.repeat((snareVelocity[i] / 8), 8)
	bassDrumProbabilites = np.repeat((bassDrumVelocity[i] / 8), 8)
	hihatProbabilites = np.repeat((hihatVelocity[i] / 8), 8)

	snareVelocityProbabilites = np.concatenate((snareVelocityProbabilites, snareProbabilites))
	bassDrumVelocityProbabilites = np.concatenate((bassDrumVelocityProbabilites, bassDrumProbabilites))
	hihatVelocityProbabilites = np.concatenate((hihatVelocityProbabilites, hihatProbabilites))
        
# Create 100 simple MIDI files with a 4/4 drum beat, featuring hi-hat, snare, and bass drum,
# using the interpolated microtiming and velocity values defined above

# Note on the "time" variable: since it is measured in beats (ex. "1" is beat 1, "2" is beat 2, and so on), 
# 0.125 is a 32nd note. Therefore, I divide the percentOffBeatArray value (between -0.5 and 0.5) by 4, 
# which gives us the correct off beat amount 

for fileNum in range(0, 100):
	mf = MIDIFile(1)
	tempo = 120
	mf.addTrackName(0, 0, "Drums")
	mf.addTempo(0, 0, tempo)
	channel = 0
	track = 0

	percentOffBeatArray = np.random.choice(snarePercentOffBeatValues, 800, p=snarePercentOffBeatProbabilites)
	velocityArray = np.random.choice(snareVelocityValues, 800, p=snareVelocityProbabilites)
	for i in np.linspace(0, 200, num=801):
		#hi-hat
		pitch = 42
		index = int(i*4) - 1
		time = max(0, i + (percentOffBeatArray[index] / 4))
		duration = 1
		volume = max(1, int(velocityArray[index]))
		mf.addNote(track, channel, pitch, time, duration, volume)

	percentOffBeatArray = np.random.choice(bassDrumPercentOffBeatValues, 800, p=bassDrumPercentOffBeatProbabilites)    
	velocityArray = np.random.choice(bassDrumVelocityValues, 800, p=bassDrumVelocityProbabilites)
	for i in np.linspace(0, 200, num=801):
		#bass drum
		pitch = 35
		index = int(i*4) - 1
		time = max(0, i + (percentOffBeatArray[index] / 4))
		duration = 1
		volume = max(1, int(velocityArray[index]))
		mf.addNote(track, channel, pitch, time, duration, volume)

	percentOffBeatArray = np.random.choice(hihatPercentOffBeatValues, 800, p=hihatPercentOffBeatProbabilites)
	velocityArray = np.random.choice(hihatVelocityValues, 800, p=hihatVelocityProbabilites)  
	for i in np.linspace(0, 200, num=801):
		#snare
		pitch = 38
		index = int((i*4)) - 1
		time = max(0, i + (percentOffBeatArray[index] / 4))
		duration = 1
		volume = max(1, int(velocityArray[index]))
		mf.addNote(track, channel, pitch, time, duration, volume)

	# write to disk
	directory = "./generatedGroove"
	if not os.path.exists(directory):
		os.mkdir(directory)

	directory += "/drummer" + drummerNum
	if not os.path.exists(directory):
		os.mkdir(directory)

	with open(directory + "/" + drummerNum + "_rock_120_beat_4-4_" + str(fileNum) + ".mid", 'wb') as outf:
		mf.writeFile(outf)
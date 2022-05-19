# Contains information for each individual note
class Note:
    def __init__(self, velocity, beginTick, endTick):
        self.velocity = velocity
        self.beginTick = beginTick
        self.endTick = endTick
    
    def addEndTick(self, endTick):
        self.endTick = endTick

# Contians information for each MIDI file
class File:
    def __init__(self, name, ticksPerSixteenthNote, style, tempo, isBeat, timeSignature, instruments):
        self.name = name
        self.ticksPerSixteenthNote = ticksPerSixteenthNote
        self.style = style
        self.tempo = tempo
        self.isBeat = isBeat
        self.timeSignature = timeSignature
        self.instruments = instruments
    
    def extractFeatures(self):
        import numpy as np

        bassDrumVelocity = []
        bassDrumMicrotiming = []

        snareVelocity = []
        snareMicrotiming = []

        hihatVelocity = []
        hihatMicrotiming = []

        ticksPerSixteenthNote = self.ticksPerSixteenthNote * 2

        # Put velocities and microtiminging percentages into seperate arrays
        for instrumentNum in self.instruments:
            if instrumentNum == 35 or instrumentNum == 36:
                for note in self.instruments[instrumentNum]:
                    bassDrumVelocity.append(note.velocity)
                    bassDrumMicrotiming.append(self.getPercentOffBeat(note.beginTick, ticksPerSixteenthNote))
            elif instrumentNum == 38 or instrumentNum == 40:
                for note in self.instruments[instrumentNum]:
                    snareVelocity.append(note.velocity)
                    snareMicrotiming.append(self.getPercentOffBeat(note.beginTick, ticksPerSixteenthNote))
            elif instrumentNum == 42 or instrumentNum == 44 or instrumentNum == 46 or instrumentNum == 49 or instrumentNum == 57:
                for note in self.instruments[instrumentNum]:
                    hihatVelocity.append(note.velocity)
                    hihatMicrotiming.append(self.getPercentOffBeat(note.beginTick, ticksPerSixteenthNote))

        # 16 velocity bins
        velocityBins = np.linspace(0, 128, num=17)
        # 10 histogram bins
        microtimingBins = np.linspace(-0.5, 0.5, num=11)
        
        # Unused, just for getting images for the paper
        #self.graphHistogram("Hi-Hat Velocity Histogram Example", "Velocity", "Hits", hihatVelocity, velocityBins)
        #self.graphHistogram("Hi-Hat Microtiming Histogram Example", "Percentage Off Beat (-50% through +50%)", "Hits", hihatMicrotiming, microtimingBins)

        bassDrumVelocityHist, bins = np.histogram(bassDrumVelocity, bins=velocityBins)
        bassDrumMicrotimingHist, bins = np.histogram(bassDrumMicrotiming, bins=microtimingBins)

        snareVelocityHist, bins = np.histogram(snareVelocity, bins=velocityBins)
        snareMicrotimingHist, bins = np.histogram(snareMicrotiming, bins=microtimingBins)

        hihatVelocityHist, bins = np.histogram(hihatVelocity, bins=velocityBins)
        hihatMicrotimingHist, bins = np.histogram(hihatMicrotiming, bins=microtimingBins)

        if ((sum(bassDrumVelocityHist) == 0 or sum(bassDrumMicrotimingHist) == 0)
        or (sum(snareVelocityHist) == 0 or sum(snareMicrotimingHist) == 0)
        or (sum(hihatVelocityHist) == 0 or sum(hihatMicrotimingHist) == 0)):
            return 0,0
        else:
            bassDrumVelocityHist = bassDrumVelocityHist / sum(bassDrumVelocityHist)
            bassDrumMicrotimingHist = bassDrumMicrotimingHist / sum(bassDrumMicrotimingHist)
            snareVelocityHist = snareVelocityHist / sum(snareVelocityHist)
            snareMicrotimingHist = snareMicrotimingHist / sum(snareMicrotimingHist)
            hihatVelocityHist = hihatVelocityHist / sum(hihatVelocityHist)
            hihatMicrotimingHist = hihatMicrotimingHist / sum(hihatMicrotimingHist)

        velocities = np.concatenate((snareVelocityHist, bassDrumVelocityHist, hihatVelocityHist))
        microtimings = np.concatenate((snareMicrotimingHist, bassDrumMicrotimingHist, hihatMicrotimingHist))

        return velocities, microtimings
    
    def getPercentOffBeat(self, beginTick, ticksPerSixteenthNote):
        # Using percentage instead of ticks off beat to normalize in case files have differing ticks per beat
        ticksOffBeat = int(beginTick % ticksPerSixteenthNote)
        if(ticksOffBeat > (ticksPerSixteenthNote / 2)):
            ticksOffBeat = ticksOffBeat - ticksPerSixteenthNote
        percentageOffBeat = ticksOffBeat / ticksPerSixteenthNote
        return percentageOffBeat

    # Unused, this was just to get graphs for the paper
    def graphHistogram(self, name, xlabel, ylabel, data, bins):
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize =(10, 7))
        plt.hist(data, bins = bins)
        plt.title(name)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        # show plot
        plt.show()
    
    # This function is unused, but kept here for posterity
    def getInstrumentDensity(self):
        # Create an array for every MIDI note
        instrumentCounts = np.zeros((128))
        totalNotes = 0
        for key in self.instruments:
            # The key represents an instrument number, so we are counting every instance of an instrument hit
            instrumentCounts[key] += 1
            totalNotes += 1

        # Divide each instrument count by the total number of notes to get a percentage
        return (instrumentCounts / totalNotes)

# Contains information for each drummer
class Drummer:
    def __init__(self, name, num, files):
        self.name = name
        self.files = files
        self.num = num
        self.regressorPipe = 0

        
    def setRegressorPipe(self, regressorPipe):
        self.regressorPipe = regressorPipe
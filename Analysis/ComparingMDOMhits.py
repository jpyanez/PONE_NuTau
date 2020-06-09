from icecube import dataclasses, dataio, simclasses
from icecube.icetray import I3Units, OMKey, I3Frame
from icecube.dataclasses import ModuleKey
import matplotlib.pyplot as plt
import numpy as np

#loading files
step3infile = []
custominfile = []
for m in range(1000, 1005):
    step3infile.append(dataio.I3File('/data/p-one/akatil/step_3_medium_water/Custom/step_3_'+str(m)+'_medium_water_custom_mDOM_katil.i3.gz'))
    custominfile.append(dataio.I3File('/data/p-one/akatil/step_3_medium_water/Custom/step_3_'+str(m)+'_medium_water_custom.i3.gz'))
#step3infile = dataio.I3File('/home/users/akatil/P-ONE/sim/clsim/genHitsTrial_IceCube.i3.gz')
#custominfile = dataio.I3File('/home/users/akatil/P-ONE/sim/clsim/genHitsTrial.i3.gz')
gcdFile = dataio.I3File('/home/users/akatil/P-ONE/GCD_files/PONE_Phase1.i3.gz')
geometry = gcdFile.pop_frame(I3Frame.Geometry)["I3Geometry"]

# get all Q frames
step3qframes = []
customqframes = []

for m in range(0, len(step3infile)):
    while(step3infile[m].more()):
        step3qframes.append(step3infile[m].pop_daq())

    while(custominfile[m].more()):
        customqframes.append(custominfile[m].pop_daq())

def getNumHitsInFrame(frame):
    mcpeSeriesMap = frame["MCPESeriesMap"]
    numHits = 0

    for omkey in mcpeSeriesMap.keys():
        hits = mcpeSeriesMap[omkey]
        numHits += len(hits)
        #print(len(hits), numHits)
    return numHits

def getDOMDataFromFrames(frameList):
    numDOMs = []

    for frame in frameList:
        mcpeMap = frame["MCPESeriesMap"]
        numDOMs.append(len(mcpeMap.keys()))

    return numDOMs

def getrelativeAngle(photon, omkey):
    geoMap = geometry.omgeo
    domGeo = geoMap[omkey]
    domDirection = domGeo.direction
    photonDirection = photon.dir
    dotProduct = photonDirection.x*domDirection.x + photonDirection.y*domDirection.y + photonDirection.z*domDirection.z

    return -dotProduct

def getPhotonDataFromFrames(frameList):
    photonAngle = []
    photonWavelength = []
    photonMap = []

    for frame in frameList:
        pMap = frame["I3Photons"]
        photonMap.append(pMap)
        for modkey, photons in pMap:
            for photon in photons:
                photonAngle.append( getrelativeAngle( photon, OMKey(modkey.string, modkey.om, 0) ) )
                photonWavelength.append(photon.wavelength)

    return photonAngle, photonWavelength, photonMap

step3Hits = []
customHits = []

for frame in step3qframes:
    step3Hits.append(getNumHitsInFrame(frame))

for customFrame in customqframes:
    customHits.append(getNumHitsInFrame(customFrame))
    #print(getNumHitsInFrame(customFrame))
    if getNumHitsInFrame(customFrame) == 0:
        print("error")

#print(customHits, step3Hits)
#print(len(customHits), len(step3Hits))

numDOMsstep3 = getDOMDataFromFrames(step3qframes)
numDOMscust = getDOMDataFromFrames(customqframes)

photonAnglestep3, photonWavelengthstep3, photonMapstep3 = getPhotonDataFromFrames(step3qframes)
photonAnglecust, photonWavelengthcust, photonMapcust = getPhotonDataFromFrames(customqframes)

commonFramesStep3 = []
commonFramesCust = []
for i in range(0, len(photonMapstep3)):
    for j in range(0, len(photonMapcust)):
        if photonMapstep3[i] == photonMapcust[j]:
            commonFramesStep3.append(step3qframes[i])
            commonFramesCust.append(customqframes[j])

res1 = [a for a in commonFramesStep3 + step3qframes if a not in commonFramesStep3 or a not in step3qframes]
res2 = [b for b in commonFramesCust + customqframes if b not in commonFramesCust or b not in customqframes]

#Collecting Hits from Frames that are not Common
commonHitsStep3NC = []
commonHitsCustNC = []

for frame in res1:
    commonHitsStep3NC.append(getNumHitsInFrame(frame))

for customFrame in res2:
    commonHitsCustNC.append(getNumHitsInFrame(customFrame))

#Collecting hits from frames that are common to both icecube and custom code
commonHitsStep3 = []
commonHitsCust = []

for frame in commonFramesStep3:
    commonHitsStep3.append(getNumHitsInFrame(frame))

for customFrame in commonFramesCust:
    commonHitsCust.append(getNumHitsInFrame(customFrame))

commonFramesNumDOMsstep3 = np.array(getDOMDataFromFrames(commonFramesStep3))
commonFramesNumDOMscust = np.array(getDOMDataFromFrames(commonFramesCust))

xBar = np.arange(len(commonFramesStep3))
xBarStepNC = np.arange(len(commonHitsStep3NC))
xBarCustNC = np.arange(len(commonHitsCustNC))
xBarDOM = np.arange(len(commonFramesNumDOMsstep3))
width = 1

ratio = np.array(commonHitsStep3)/np.array(commonHitsCust)
ratioDOM = commonFramesNumDOMscust/commonFramesNumDOMsstep3

nHCust = np.array(commonHitsCust)
nHStep = np.array(commonHitsStep3)
diff = abs(nHCust - nHStep)

#nHStep = nHStep[nHCust > 80]
xBar1 = np.arange(len(nHStep[nHCust>80]))
#ratio1 = ratio[nHCust > 80]
#nHCust = nHCust[nHCust > 80]

#plot number of hits
fig, axs = plt.subplots(2, 1, sharex=True, gridspec_kw={'height_ratios': [2, 1]})
fig.set_figheight(30)
fig.set_figwidth(90)
fig.suptitle('Comparing Hits (DOM vs mDOM)', fontsize=92)
fig.subplots_adjust(hspace=0)

axs[0].bar(xBar[ratio < 10], nHCust[ratio < 10], width, label='DOM Hits', fill=False, edgecolor='Red', linewidth=5)
axs[0].bar(xBar[ratio < 10], nHStep[ratio < 10], width, label='mDOM Hits', log=True, fill=False, edgecolor='Black', linewidth=5)
axs[0].set_ylabel('Number of Hits per Frame', fontsize=48)
axs[0].legend(fontsize=50)
axs[0].tick_params(axis="x", labelsize=50)
axs[0].tick_params(axis="y", labelsize=50)

#axs[1].bar(xBar, ratio, width, fill=False, edgecolor='Blue', linewidth=5)
axs[1].plot(xBar[ratio < 10], ratio[ratio < 10], '.', color='Blue', markersize=30)
axs[1].set_ylabel('(mDOM Hits) / (DOM Hits)', fontsize=38)
axs[1].set_xlabel('Frames', fontsize=68)
axs[1].tick_params(axis="x", labelsize=40)
axs[1].tick_params(axis="y", labelsize=40)

plt.axhline(y=ratio[ratio<10].mean(), linewidth=6, color='r')
print(ratio[ratio<10].mean())

plt.savefig("CompareHitsPerCommonFrameAndRatio_mDOM.pdf", dpi = 200)
plt.clf()

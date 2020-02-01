import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
import config
import grid
import seaborn as sns

gridDimensions = config.gridDimensions
xDimension = gridDimensions[0]
#chromosome = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]

def createFullChromosome(chromosome,boxList):
    '''
    To convert the chromosome into a heat map, we need the whole box array
    '''
    chromosomeDictionary = {}

    for box in chromosome.genes:
        if box not in chromosomeDictionary:
            chromosomeDictionary[box] = 1
        else:
            chromosomeDictionary[box] +=1

    fullBoxListArray = []
    for boxIdx in range(0,len(boxList)-1):
        if boxList[boxIdx] in chromosomeDictionary:
            fullBoxListArray.insert(boxIdx,chromosomeDictionary[boxList[boxIdx]])
        else:
             fullBoxListArray.insert(boxIdx,0)
    maxContainedPods = max(fullBoxListArray)

    return fullBoxListArray,maxContainedPods


def convertToNested(array,xDimension):

    nested = []
    iSlice = 0
    for i in range(int(len(array)/xDimension)):
        jSlice = iSlice + xDimension
        nested.append(array[iSlice:jSlice])
        iSlice = jSlice

    return nested

def showGAVisuals(generation,boxlist,currentGeneration,fitnessData,averageFitnessData):

    generationHeatmapArray = []
    fitnessArray = []
    maxPods = 6
    for chromosome in generation:
        fullArray,maxPodNumber = createFullChromosome(chromosome,boxlist)
        fitnessArray.append(chromosome.fitness)
        heatmapArray = convertToNested(fullArray,config.gridDimensions[0])
        generationHeatmapArray.append(heatmapArray)
        if maxPodNumber > maxPods:
            maxPods = maxPodNumber

    generationSize = len(generation)

    plt.rcParams['figure.facecolor'] = 'white'#'lavender'
    plt.rcParams['toolbar'] = 'None'
    plt.rcParams['figure.figsize'] = 19, 7.8

    if fitnessData:
        y2Data = averageFitnessData
        yData= fitnessData
        xData = [i for i in range(1,len(fitnessData)+1)]
    else:
        y2Data = [0]
        yData = [0]
        xData = [0]


    gs = GridSpec(3,int(generationSize/2))
    plt.subplots_adjust(left=0.042, bottom=0.08, right=0.98, top=0.93, wspace=0.04, hspace=0.05)

    for j in [0,1]:
        for i in range(0,int(generationSize/2)):
            if j ==0:
                k=int(i)
            else:
                k = int(i+generationSize/2)

            plt.subplot(gs[j,i])
            sns.heatmap(generationHeatmapArray[k], annot=False,  linewidths=0.05,cbar=False,xticklabels=False, yticklabels=False,linecolor = 'black',vmin= 0 , vmax= maxPods)
            if fitnessArray[k]:
                plt.text(0.95, 0.01, '{:.0f}'.format(fitnessArray[k]),fontsize=8,color = '.9',transform=plt.gca().transAxes)

    with sns.axes_style("darkgrid"):
        sns.set_style("darkgrid", {"axes.facecolor": ".8",'axes.edgecolor': '.9', 'grid.color': '.9','xtick.color': '.3','ytick.color': '.3','axes.labelcolor': '.3'})#xkcd:violet'

        plt.subplot(gs[2,:])
        ax = sns.lineplot(xData,yData,color="xkcd:dark purple",label = 'Fittest Chromosome')
        ax2 = sns.lineplot(xData,y2Data,color="xkcd:blue",label = 'Average Fitness')
        leg = ax.legend(loc='upper right', bbox_to_anchor=(1,1.02))
        leg.get_frame().set_linewidth(0.0)
        ax.set(xlabel='Generation', ylabel='Fitness',xlim=(0, config.maxGenerationNum),ylim = (0, 100))


    fig = plt.gcf()
    fig.suptitle('Generation {0}'.format(currentGeneration),color = '.2',fontsize=25,x = 0.12)

    return fig







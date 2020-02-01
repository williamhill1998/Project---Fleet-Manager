import config
import grid

import VisGA
import threading
import random
import queue
import sys

from fleetvisualiser import App

class GA:

    def __init__(self,N=config.generationSize,mutationProb = config.mutationProb, crossoverProb = config.crossoverProb,maxGenerationNum =config.maxGenerationNum):

        self.mutationNumerator , self.mutationDenominator = mutationProb.as_integer_ratio()
        self.crossoverNumerator , self.crossoverDenominator = crossoverProb.as_integer_ratio()
        self.grid = grid.Grid(config.gridDimensions)
        self.maxGenerationNum = maxGenerationNum
        self.generationNumber = 0
        self.generationSize = N
        self.generation = []
        self.newGeneration = []
        self.roulette = []
        self.fitnessHistory = []
        self.averageFitnessHistory = []
        self.fittest = None
        self.createFirstGeneration()
        self.top8Chromosomes = self.generation[:8]
        # print(self.generation[0].genes,len(self.generation[0].genes))

    def run(self,queueHandler=None,signalHandler=None):

        generationInfoDict = {
            'Generation Size' : len(self.generation)
        }


        for i in range(0,self.maxGenerationNum):
            generationFitnessDict = {}
            generationInfoDict['Generation Number'] = i+1
            generationInfoDict['New Generation bool'] = False
            self.totalGenerationFitness = 0
            for chromosomeIdx in range(0,len(self.generation)):
                self.grid.clearGridData()
                if signalHandler:
                    if self.checkIfReady(signalHandler):
                        if self.generation[chromosomeIdx].fitness:
                            #if tournament, then the fitnesses would have already been evaluated
                            fitness = self.generation[chromosomeIdx].fitness
                        else:
                            fitness = self.testChromosome(chromIdx = chromosomeIdx, default = 'average')
                            self.generation[chromosomeIdx].fitness = fitness
                        # print(fitness)
                        self.totalGenerationFitness += fitness

                        # print('{:.1f}'.format(fitness))
                        generationFitnessDict[self.generation[chromosomeIdx]] = fitness
                        generationInfoDict['Completed Simulations']= chromosomeIdx +1

                        if chromosomeIdx < len(self.generation)-1:
                            generationInfoDict['New Generation bool'] = False
                            if queueHandler:
                                queueHandler.put(generationInfoDict)
                        else:
                            generationInfoDict['New Generation bool'] = True
                    else:
                        print('Simulation Thread ending')
                        return True #Ends the Thread

                else:
                    fitness = self.testChromsome(chromIdx = chromosomeIdx)
                    generationFitnessDict[self.generation[chromosomeIdx]] = fitness
                    generationInfoDict['Completed Simulations']= chromosomeIdx +1
                    if chromosomeIdx < len(self.generation)-1:
                        generationInfoDict['New Generation bool'] = False
                    else:
                        generationInfoDict['New Generation bool'] = True

            generationInfoDict['ChromosomeFitness'] = generationFitnessDict
            self.generationNumber += 1
            self.fittestChromosome = max(generationFitnessDict,key=generationFitnessDict.get)
            self.fittestValue = self.fittestChromosome.fitness
            self.averageFitness = self.totalGenerationFitness / len(self.generation)
            print("MEAN FITNESS = {0}".format(self.averageFitness))
            print(self.fittestValue)
            self.fitnessHistory.append(self.fittestValue)
            self.averageFitnessHistory.append(self.averageFitness)

            for chromosome in self.generation:
                try:
                    chromosome.scaledFitness = chromosome.fitness/self.totalGenerationFitness
                except ZeroDivisionError:
                    chromosome.scaledFitness = 1/len(self.generation)

            self.top8Chromosomes = sorted(self.generation,key = lambda chromosome: chromosome.fitness,reverse=True)[:8]

            print([chrom.fitness for chrom in self.top8Chromosomes])
            if queueHandler:
                queueHandler.put(generationInfoDict)

            if signalHandler:
                if self.checkIfReady(signalHandler):
                    self.createNextGeneration()
            else:
                self.createNextGeneration()

    def checkIfReady(self,signalHandler):
        try:
            msg = signalHandler.get()
            if msg == 'Ready':
                return True
            elif msg == 'Stop':
                print('Received Stop Signal')
                for item in range(signalHandler.qsize()):
                    signalHandler.get()
                signalHandler.put('Stop')
                return False

        except queue.Empty:
            threading.Timer(0.1, self.checkIfReady)

    def testChromosome(self, chromIdx = None, chromosomeObj = None , default = None):

        if chromIdx:
            theApp = App(geneticGrid = self.grid ,chromosome = self.generation[chromIdx])
        else:
            theApp = App(geneticGrid = self.grid ,chromosome = chromosomeObj)

        try:
            fitness = theApp.onExecute()
            print(fitness)
            return fitness
        except Exception as e:
            print(e)
            raise Exception("error occured").with_traceback(e.__traceback__)
            if default == 'zero':
                fitness = 0
            elif default == 'average':
                fitness = self.totalGenerationFitness/config.generationSize
            return fitness


    def crossover(self,chromosome1,chromosome2):
        idx = random.randint(0,len(chromosome1.genes)-1)
        chrome1Slice1 = chromosome1.genes[:idx]
        chrome1Slice2 = chromosome1.genes[idx:]
        chrome2Slice1 = chromosome2.genes[:idx]
        chrome2Slice2 = chromosome2.genes[idx:]

        offspringGenes1 = chrome1Slice1 + chrome2Slice2
        offspringGenes2 = chrome2Slice1 + chrome1Slice2

        #Need to assert offspring and parent genes are the same length

        return offspringGenes1,offspringGenes2

    def mutate(self,chromosomeGenes):
        idx = random.randint(0,len(chromosomeGenes)-1)
        chromosomeGenes[idx] = random.choice(self.grid.boxesContainingNodes)

        return chromosomeGenes

    def createRoutletteArray(self):
        '''
        Error: Roulette isnt clearing
        '''
        self.roulette = []
        for chrom in self.generation:
            numSlots = int(chrom.scaledFitness*100)
            print('chromosome with scaled Fitness {0:.4f} gets {1} slots'.format(chrom.scaledFitness,numSlots))
            if numSlots:
                if numSlots == 1:
                    self.roulette.append(chrom)

            #else:
            for i in range(1,numSlots):
                self.roulette.append(chrom)

        print(len(self.roulette),len(self.generation ))


    def selectParents(self):
        chromosome = random.choice(self.roulette)
        print('Selected Chomosome: {0} with fitness {1:.0f}'.format(chromosome,chromosome.fitness))
        return chromosome


    def createOffspringPair(self):
        #Roulette Wheel spin
        chrome1 = self.selectParents()
        chrome2 = self.selectParents()

        if self.crossoverNumerator <= random.randint(1,self.crossoverDenominator):
            newChromosomeGenes1,newChromosomeGenes2 = self.crossover(chrome1,chrome2)
            print("Crossover occurred")
            offspring1 = Chromosome(self.grid,newChromosomeGenes1)
            offspring2 = Chromosome(self.grid,newChromosomeGenes2)
        else:
            offspring1 = Chromosome(self.grid,chrome1.genes)
            offspring2 = Chromosome(self.grid,chrome2.genes)

        if self.mutationNumerator <= random.randint(1,self.mutationDenominator):
            print("Mutation occurred")
            self.mutate(offspring1.genes)
        if self.mutationNumerator <= random.randint(1,self.mutationDenominator):
            print("Mutation occurred")
            self.mutate(offspring2.genes)

        if config.tournament:
            winners = self.runTournament([chrome1,chrome2],[offspring1,offspring2])
            offspring1 = winners[0]
            offspring2 = winners[1]

        return offspring1, offspring2

    def createFirstGeneration(self):
        for chrom in range(self.generationSize):
            newChromosome = Chromosome(self.grid)
            newChromosome.createRandom()
            self.generation.append(newChromosome)
        #print(self.generation)
        return self.generation


    def createRandomGeneration(self):
        self.generation = []
        for chrom in range(self.generationSize):
            newChromosome = Chromosome(self.grid)
            newChromosome.createRandom()
            self.generation.append(newChromosome)
        return self.generation


    def createNextGeneration(self):
        # print('Creating Next Generation...')

        self.newGeneration = []
        self.createRoutletteArray()
        while len(self.newGeneration) < self.generationSize:
            offspring1, offspring2 = self.createOffspringPair()
            self.newGeneration.append(offspring1)
            self.newGeneration.append(offspring2)
        # self.newGeneration = self.createRandomGeneration()
        self.generation = self.newGeneration


    def showGAVisuals(self,currentGen):
        fig = VisGA.showGAVisuals(self.top8Chromosomes,self.grid.sortedBoxList,currentGen,self.fitnessHistory,self.averageFitnessHistory)
        return fig

    def runTournament(self,parents,offspring):
        parentFitness = [parent.fitness for parent in parents]
        childFitness = []
        for child in offspring:
            child.fitness = self.testChromosome(chromosomeObj = child , default = 'zero')
            childFitness.append(child.fitness)
        print(parentFitness, childFitness)
        chromosomes = parents + offspring
        chromosomes.sort(key=lambda chrome: chrome.fitness, reverse=True)
        winners = chromosomes[:2]
        return winners




class Chromosome():
    '''
    Chromomes will be structured so that:
        The total number of genes is the number of pods
        The genotype is the box in which the pods belong
        The Chromosomes will be ranked by the percentage of pods that complete their journeys in half the time it would take to walk the same route.
    '''
    def __init__(self,grid,genes=None):
        self.grid = grid
        self.fitness = None # value from 1 to 100
        self.size = config.maxNumberOfPods
        if genes:
            self.genes = genes
        else:
            self.genes = []



    def createRandom(self):
        for pod in range(self.size):
            self.genes.append(random.choice(self.grid.boxesContainingNodes))

if __name__ == "__main__":
    ga = GA(N = config.generationSize)
    ga.run()


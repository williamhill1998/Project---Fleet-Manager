from GeneticAlgorithm import GA
import time
def runSimulation():
    ga = GA(N = 1)
    ga.run()

if __name__=='__main__':
    repeats = 100
    startTime = time.time()
    for i in range(1,repeats+1):
        print("Simulation Number {0} out of {1}".format(i,repeats))
        runSimulation()
    endTime = time.time()
    averageTime = (endTime - startTime)/repeats
    print("Done. Average Completion time: {0:.2f}s. Total Time: {1:.2f}mins".format(averageTime,(endTime-startTime)/60))

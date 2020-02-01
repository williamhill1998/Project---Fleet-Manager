import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from GeneticAlgorithm import GA
import threading
import queue
import config
import sys
import matplotlib.pyplot as plt

class GUI:

    def __init__(self):
        self.ga = GA(N = config.generationSize)
        self.root = tk.Tk()
        self.closingFlag = False

    def run(self):
        self.createWindow()

    def createWindow(self):
        self.fig = self.ga.showGAVisuals(0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.dataLabel = tk.Label(self.root, text="Data", bg="black",fg="#585858",font=("Helvetica", 10),anchor=tk.W)

        tk.Grid.columnconfigure(self.root, 0, weight=1)
        tk.Grid.rowconfigure(self.root, 0, weight=1)
        tk.Grid.rowconfigure(self.root, 1, weight=0)

        self.plt_canvas = self.canvas.get_tk_widget().grid(row=0, sticky=tk.N+tk.S+tk.E+tk.W)
        self.plot_data = self.dataLabel.grid(row=1, sticky=tk.N+tk.S+tk.E+tk.W)

        self.root.overrideredirect(True)
        self.root.overrideredirect(False)
        self.root.attributes("-fullscreen", True)
        self.root.after(100, self.runSimulation)
        self.root.bind('<Escape>', self.quit)
        self.root.mainloop()


    def runSimulation(self):
        self.currentGenerationNumber = 0
        self.simulationQueue = queue.Queue()
        self.signalQueue = queue.Queue()
        self.simulationThread = ThreadedTask(self.simulationQueue,self.ga,self.signalQueue)
        self.simulationThread.start()
        self.root.after(100, self.process_queue)

    def process_queue(self):
        try:
            msg = self.simulationQueue.get()
            # Show result of the task if needed
            newGen = False
            if type(msg) == dict:
                self.completedSimulations = msg["Completed Simulations"]
                self.generationSize = msg["Generation Size"]
                self.newGenerationNumber = msg["Generation Number"]
                self.newGenBool = msg['New Generation bool']

                if self.newGenBool:
                    print('New Generation started')
                    newGen = True
                    self.currentGenerationNumber +=1
                    self.updateFigure()
                self.signalQueue.put('Ready')
                self.root.after(100, self.process_queue)
                self.updateLabel()

            else:
                print(msg)
        except queue.Empty:
            self.root.after(100, self.process_queue)

    def updateLabel(self):
        info = "Generation Progress: {0}/{1}".format(self.completedSimulations,self.generationSize)
        if self.closingFlag:
            info = info + '\t\t\t' + 'CLOSING...'
        self.dataLabel.config(text=info)

    def updateFigure(self):
        self.fig = self.ga.showGAVisuals(self.currentGenerationNumber)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.plt_canvas = self.canvas.get_tk_widget().grid(row=0, sticky=tk.N+tk.S+tk.E+tk.W)
        self.signalQueue.put('Ready')

    def quit(self,event):
        self.closingFlag = True
        print('key press detected')
        self.signalQueue.put('Stop')
        print('Put stop signal in queue')
        self.simulationThread.join()
        print("Simulation Thread joined main")
        sys.exit()

    def refreshWindow(self):
        self.root.destroy()
        self.root = tk.Tk()
        self.createWindow()




class ThreadedTask(threading.Thread):
    def __init__(self, queue,ga,signalQueue):
        threading.Thread.__init__(self)
        self.simulationQueue = queue
        self.ga = ga
        self.signalQueue = signalQueue
        self.signalQueue.put('Ready')
    def run(self):
        self.ga.run(queueHandler=self.simulationQueue,signalHandler= self.signalQueue)
        self.simulationQueue.put("Task finished")



if __name__=="__main__":
    # if sys.argv[1:]:
    #     if sys.argv[1] == 'vis':
    #         config.GA = False
    #     elif sys.argv[1] == 'hide':
    #         config.GA = True
    gui = GUI()
    gui.createWindow()

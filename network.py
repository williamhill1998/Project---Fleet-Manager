
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy.misc import imread
import os
import math
import config
import imageio


class PathNetwork:
    """
    Helper class for accessing values in the graph route network
    """
    def __init__(self, drawGraph=True):
        self.graphMain = GraphMain()

        if(drawGraph):
            self.graphMain.drawGraph()

    def getCoordinatesForNodeList(self, nodeRoute):
        return self.graphMain.getCoordinatesForNodeList(nodeRoute)

    def getShortestPath(self, source, target):
        return self.graphMain.getShortestPath(source=source,target=target)

    def getNumberOfNodes(self):
        return len(self.graphMain.graph.nodes())

    def getNodeList(self):
        return list(self.graphMain.nodeList)


class GraphMain:
    """
    Draws the route ontop of the map image.  Also allows for the generation of new
    routes.
    Note: Uses the networkx python packagae to create and traverse the undirect graph (the route network)
    """
    def __init__(self):

        self.graph = nx.Graph()
        self.firstNodeClick = None

        # Load nodes and edges from file
        self.nodeList = self.loadNodesFromFile(r'resources/MapData/nodes.dat', asInt = False)
        self.edgeList = self.loadListFromFile(r'resources/MapData/edges.dat')
        self.loadNodeList()
        self.loadEdgeList()

        if(self.graph.nodes()):
            self.nodeCount = max(list(self.graph.nodes()))+1
        else:
            self.nodeCount = 1

    def drawGraph(self):

        plt.clf()
        positions = nx.get_node_attributes(self.graph,'posxy')
        nx.draw_networkx(self.graph, positions, node_size=50, with_labels=True, node_color='b', font_size=6, font_color='w')
        nx.draw_networkx_edges(self.graph, positions, width=1.0, alpha=0.5, edge_color='r')

        # Highlight the first node selected for adding an edge to
        if(self.firstNodeClick is not None):
            nx.draw_networkx_nodes(self.graph, positions,
                           nodelist=[self.firstNodeClick],
                           node_color='r',
                           node_size=50,
                       alpha=0.8)

        plt.axis('off')
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=1, hspace=1)

        # Get the background route image to be added to the chart
        image = imageio.imread(config.cityImage)

        # Display the graph and background image on the chart
        plt.imshow(image, alpha=0.8, interpolation='quadric')
        plt.show()
        plt.savefig('output.png')

    def loadNodeList(self):
        count = 1
        for node in self.nodeList:
            self.graph.add_node(node.name, posxy=(node.x, node.y))
            count+=1

    def loadEdgeList(self):
        for nodepair in self.edgeList:
            if (nodepair[0] not in list(self.graph.nodes())) :
                print("Node {0} no longer exists in Graph.nodes()".format(nodepair[0]))
                self.edgeList.remove((nodepair[0],nodepair[1]))
            elif(nodepair[1] not in list(self.graph.nodes())):
                print("Node {0} no longer exists in Graph.nodes()".format(nodepair[1]))
                self.edgeList.remove(nodepair)
            else:
                self.graph.add_edge(nodepair[0],nodepair[1])

    def onClick(self, event):
        """kkk
        This allows for routes to be drawn on the graph
        """
        print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' % (event.button, event.x, event.y, event.xdata, event.ydata))

        if(event.button == 1):
            x, y   = (event.xdata, event.ydata)
            self.nodeList.append(Node(x,y,self.nodeCount))
            self.graph.add_node(self.nodeCount, posxy=(x, y))
            self.nodeCount +=1
        if(event.button == 3):
            x,y   = (event.xdata, event.ydata)
            distance = 5
            for node in self.nodeList:

                if (abs(x-node.x) < distance) and (abs(y-node.y) < distance): #checks if distance between click and node is close enough
                    if (self.firstNodeClick):
                        second_click = node_name
                        self.graph.add_edge(self.firstNodeClick,second_click)
                        self.edgeList.append((self.firstNodeClick,second_click))
                        print("Add Edge: {0} , {1} ".format(self.firstNodeClick,second_click))
                        self.firstNodeClick = None
                    else:
                        self.firstNodeClick = node.name
                        print("First node clicked: {0}".format(self.firstNodeClick) )
        # Draw graphs
        self.drawGraph()

        # Each time there is a click, write the changes to the nodes and edges data files
        self.saveListToFile(r'./resources/MapData/nodes.dat', self.nodeList)
        self.saveListToFile(r'./resources/MapData/edges.dat', self.edgeList)

    def keyPress(self,event):

        print('key=%s, xdata=%f, ydata=%f' % (event.key, event.xdata, event.ydata))
        #Remove node from both graph and file when k is pressed while hovering over the node - error labelling nodes after deletion
        if (event.key == 'k'):
            x,y = (event.xdata,event.ydata)
            distance = 15
            for node in self.nodeList:
                if (abs(x-node.x) < distance) and (abs(y-node.y) < distance):
                    self.nodeList.remove(node)
                    del_edge_list = [tuple1 for tuple1 in self.edgeList if (tuple1[0] == node.name) or (tuple1[1] == node.name) ]
                    print('Edges to delete: ' + str(del_edge_list))
                    for item in del_edge_list:
                        #print(item)
                        self.edgeList.remove(item)
                    print('Deleted node : {0} And Edges: {1} ' .format(node.name, del_edge_list))
                    self.graph.remove_node(node.name)

        elif(event.key == ' '):
            x,y   = (event.xdata, event.ydata)
            distance = 5
            for node in self.nodeList:

                if (abs(x-node.x) < distance) and (abs(y-node.y) < distance): #checks if distance between click and node is close enough
                    if (self.firstNodeClick):
                        second_click = node.name
                        self.graph.add_edge(self.firstNodeClick,second_click)
                        self.edgeList.append((self.firstNodeClick,second_click))
                        print("Add Edge: {0} , {1} ".format(self.firstNodeClick,second_click))
                        self.firstNodeClick = None
                    else:
                        self.firstNodeClick = node.name
                        print("First node clicked: {0}".format(self.firstNodeClick) )

        #print(self.nodeList)
        # Draw graphs
        self.drawGraph()

        # Each tim5e there is a click, write the changes to the nodes and edges data files
        self.saveListToFile(r'./resources/MapData/nodes.dat', self.nodeList)
        self.saveListToFile(r'./resources/MapData/edges.dat', self.edgeList)



    def saveListToFile(self, filepath, listToSave):
        """
        Save a CSV file
        """
        with open(filepath, 'w') as fileHandler:
            for item in listToSave:
                fileHandler.write(str(item).strip("()") + "\n")

    def loadListFromFile(self, filepath, asInt=True):
        """
        Load a CSV file
        """
        tempList = []


        if(os.path.exists(filepath)):
            with open(filepath, 'r') as fileHandler:
                for line in fileHandler:
                    tupleList = []
                    lineList = line.strip().split(',')
                    if(asInt):
                        tupleList.append(int(lineList[0]))
                        tupleList.append(int(lineList[1]))
                    else:
                        tupleList.append(float(lineList[0]))
                        tupleList.append(float(lineList[1]))
                    if(len(lineList) > 2):
                        tupleList.append(int(lineList[2]))
                    tempList.append(tuple(tupleList))

        return tempList

    def loadNodesFromFile(self, filepath, asInt=True):
        tempList = []


        if(os.path.exists(filepath)):
            with open(filepath, 'r') as fileHandler:
                for line in fileHandler:
                    tupleList = []
                    lineList = line.strip().split(',')
                    if(asInt):
                        tupleList.append(int(lineList[0]))
                        tupleList.append(int(lineList[1]))
                    else:
                        tupleList.append(float(lineList[0]))
                        tupleList.append(float(lineList[1]))
                    if(len(lineList) > 2):
                        tupleList.append(int(lineList[2]))
                        node = Node(tupleList[0],tupleList[1],tupleList[2])
                        tempList.append(node)
        return tempList


    def calculateDistanceBetweenNodes(self, node1Index, node2Index):
        # Calculate distance betwqeen two points

        point1 = ()
        point2 = self.nodeList[node2Index-1]

        return math.hypot(point2[0] - point1[0], point2[1] - point1[1])

    def calculateTotalDistanceOfNodeList(self, nodeList):
        totalDistance = 0

        for nodeIndex in range(1, len(nodeList)):
            node1 = self.getNodeByName(nodeList[nodeIndex-1])
            node2 = self.getNodeByName(nodeList[nodeIndex])
            totalDistance += math.hypot(node2.x - node1.x, node2.y - node1.y)

        return totalDistance

    def getNodeByName(self,name):
        for node in self.nodeList:
            if int(node.name) == int(name):
                return node

    def getShortestPath(self, source, target):
        """
        Get a list of nodes that are the shortest distance between the sourec and target nodes
        """
        return nx.shortest_path(self.graph,source=source,target=target)

    def getCoordinatesForNodeList(self, routeNodeList):
        """
        Get the x, y coordinates for each node in the node list
        """
        if type(routeNodeList) is int:
            coordinates = [(node.x,node.y)  for node in self.nodeList if node.name == routeNodeList][0]
        elif type(routeNodeList) is list :

            coordinates = [(node.x,node.y) for routeNode in routeNodeList for node in self.nodeList if node.name == routeNode]
        else:
            raise Exception ("routeNodeList is not a list or int but {} ".format(type(routeNodeList)))

        assert(type(coordinates) is tuple,'coordinate is not a tuple')
        return coordinates


class Node:
    def __init__(self,x,y,name):
        self.x = x
        self.y = y
        self.name = name



if __name__ == "__main__" :
    """
    This runs the route setup.  If you already have a nodes.dat and edges.dat then it will allow you to generate a route.
    If there is no existing route then you can create a new one.

    Left click on the map to place nodes.  To places edges, right click on the node (which will highlight it in green)
    then right click on another node to draw and edge between.
    """
    graphMain = GraphMain()
    fig, ax = plt.subplots()
    fig.canvas.mpl_connect('button_press_event', graphMain.onClick)
    fig.canvas.mpl_connect('key_press_event', graphMain.keyPress)
    graphMain.drawGraph()


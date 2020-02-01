import matplotlib.pyplot as plt
from ast import literal_eval
import imageio
import config
import podhandler
import network

pathNetwork = network.PathNetwork(config.drawGraph)
podFleet = podhandler.PodFleet(pathNetwork)

for pod in podFleet.podArray:
    filename = r'resources/PodData/Pod_{}/Route.dat'.format(pod.podId)
    tupleList = []

    with open(filename, 'r') as fileHandler:
        for line in fileHandler:
            for item in line.strip().split('\t'):
                tup = literal_eval(item)
                tupleList.append(tup)


    xCoords = [tup[0] for tup in tupleList]
    yCoords = [tup[1] for tup in tupleList]

#    print("X: " + str(xCoords))
#    print("Y: " + str(yCoords))
    plt.ioff()
    plt.rcParams.update({'figure.max_open_warning': 0})
    fig, ax = plt.subplots()
    plt.axis('off')
    ax.plot(xCoords, yCoords, 'ob-', markersize = 0.1)

    # Get the background route image to be added to the chart
    image = imageio.imread(config.cityImage)

    # Display the graph and background image on the chart
    plt.imshow(image, alpha=0.8, interpolation='quadric')
    #plt.show()
    plt.savefig(r'resources/PodData/Pod_{}/route_img.png'.format(pod.podId),dpi = 300)
    print("Finished saving Pod {} route image".format(pod.podId))

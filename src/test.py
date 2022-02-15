import cv2
import numpy as np
import sampler.BN_Sample as BN_Sample
from PIL import Image
import numpy as np
# load the image
import matplotlib.pyplot as plt
from sampling.importance_map import ImportanceMap
from sampling.triangulate import Triangulate
from util.settings import Settings
import open3d
# Used to test the code for memory leaks: requires an OpenCV-compatible webcam to be connected to the system
# If there is a memory leak in the conversion, memory used by the program should grow to eventually overwhelm
# the system; memory usage monitors may be used to check the behavior
if __name__ == "__main__":

    image = cv2.imread('../img/test7.jpg')



    im = ImportanceMap()
    dt = Triangulate()

    importance_map = im.run(None, image, 0.5)

    # Sampled = BN_Sample.GetPoints(data, 100.0)
    Sampler = BN_Sample.ImageQuasisampler()
    Sampler.loadImg(importance_map,1000.0)
    debug = Sampler.debugTool()
    plt.imshow(debug, cmap='hot', interpolation='nearest')
    # Sampler.loadPGM('image.pgm', 100.0)
    Sampled = Sampler.getSampledPoints()
    x = Sampled[:,0]
    y = Sampled[:,1]
    plt.scatter(x,y, marker='.', s = 10,c='green')
    plt.show()


    triangulated = dt.run(None, image, Sampled)
    print("old tri:")
    print(len(triangulated))
    pointlist = [np.array(triangle[:6]) for triangle in triangulated]
    pointlist = np.array(pointlist)
    pointlist = pointlist.reshape(pointlist.shape[0], pointlist.shape[1]//2, -1)
    # shape = pointlist.shape
    pr = np.pad(pointlist,((0,0),(0,0),(0,1)),'constant', constant_values=(0))
    pg = np.copy(pr)
    pb = np.copy(pr)

    for pcount,points in enumerate(pointlist):
        # print(image[int(point[0])][int(point[1])])
        for vcount, point in enumerate(points):
            # print(p[0])
            r,g,b = image[tuple(point.astype(int))[::-1]]
            pr[pcount][vcount][-1] = r
            pg[pcount][vcount][-1] = g
            pb[pcount][vcount][-1] = b

    pr = pr.reshape(-1, pr.shape[-1])
    len = pr.shape[0]
    tri_ind = np.arange(0,len).reshape(-1,3)
    mesh = open3d.geometry.TriangleMesh()
    mesh.vertices = open3d.utility.Vector3dVector(pr)
    mesh.triangles = open3d.utility.Vector3iVector(tri_ind)
    # mesh.Image = image
    # mesh.textures = [open3d.geometry.Image(image)]
    # open3d.visualization.draw_geometries([mesh])

    newmesh = mesh.simplify_quadric_decimation(len//10)
    vets = np.asarray(newmesh.vertices)
    vets = vets[:,:2]
    tri = np.asarray(newmesh.triangles)

    print("new tri:")
    print(tri.shape[0])
    print("old vertex:")
    print(pr.shape[0])
    print("new vertex:")
    print(vets.shape[0])
    plt.show()


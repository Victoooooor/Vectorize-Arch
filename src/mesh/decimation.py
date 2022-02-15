import open3d as o3d
import numpy as np
from util.geometry_types import PointList
import cv2

class Decimate:
    def __init__(self):
        None

    def run(self, image:np.ndarray, vertices:PointList, shrink = 20) -> PointList:
        rect = (0, 0, image.shape[1], image.shape[0])
        subdiv = cv2.Subdiv2D(rect)

        for x in vertices:
            subdiv.insert(x)

        pointlist = subdiv.getTriangleList()

        pointlist = np.array(pointlist)
        pointlist = pointlist.reshape(pointlist.shape[0], pointlist.shape[1] // 2, -1)

        pr = np.pad(pointlist, ((0, 0), (0, 0), (0, 1)), 'constant', constant_values=(0))
        pg = np.copy(pr)
        pb = np.copy(pr)

        for pcount, points in enumerate(pointlist):

            for vcount, point in enumerate(points):
                # print(p[0])
                r, g, b = image[tuple(point.astype(int))[::-1]]
                pr[pcount][vcount][-1] = r
                pg[pcount][vcount][-1] = g
                pb[pcount][vcount][-1] = b

        pr = pr.reshape(-1, pr.shape[-1])
        len = pr.shape[0]
        tri_ind = np.arange(0, len).reshape(-1, 3)
        mesh = o3d.geometry.TriangleMesh()
        mesh.vertices = o3d.utility.Vector3dVector(pr)
        mesh.triangles = o3d.utility.Vector3iVector(tri_ind)

        newmesh = mesh.simplify_quadric_decimation(len // shrink)
        vets = np.asarray(newmesh.vertices)
        vets = vets[:, :2].astype(int)
        tri = np.asarray(newmesh.triangles)

        pixmap = np.full_like(image[:, :, 0], 0)
        for t in tri.flatten():
            x = vets[t][0]
            y = vets[t][1]
            pixmap[y - 1][x - 1] = 1

        newpts = np.array(np.where(pixmap == 1)).T
        newpts[:, [0, 1]] = newpts[:, [1, 0]]
        return newpts
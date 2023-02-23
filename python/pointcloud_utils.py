import numpy as np
from scipy.spatial import ConvexHull
from Constants import Const
import joblib
from scipy.spatial.distance import cdist, pdist, squareform
from collections import defaultdict
from scipy.spatial import Delaunay

def filter_pcloud_outliers(points, maxq = .95, min_k = 3):
    #removes all points that have less than min_k neighbors at within the bottom maxq % in terms of distance
    #since we get a few outliers
    if points.shape[0] < 10:
        return points
    dists = pdist(points)
    square_dists = squareform(dists)
    (maxval) = np.quantile(dists,[maxq])
    good = (square_dists < maxval).sum(axis=1)
    good = (good >= min_k)
    return points[good]

def np_converter(obj):
    #converts stuff to vanilla python  for json since it gives an error with np.int64 and arrays
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.float):
        return round(float(obj),3)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, datetime.datetime) or isinstance(obj, datetime.time):
        return obj.__str__()
    print('np_converter cant encode obj of type', obj,type(obj))
    return obj

#this code if for formatting and extracitng the patient info with custom scripts
def cloud_centroid(points):
    #centroid of pointclouds
    return (points.max(axis=0) + points.min(axis=0))/2
  

def concave_hull_3d(pos, alpha=None, ratio = None,alpha_scales=[1], return_vertices = False):
    #basically this tries to get all the points on the outsie surface of the pointcloud
    #edited from other code I cant find anymore using an alpha-shape algorithm
    #defaults to mean radius as alpha value because this works best based on trial and error
    """
    Compute the alpha shape (concave hull) of a set of 3D points.
    Parameters:
        pos - np.array of shape (n,3) points.
        alpha - alpha value.
    return
        outer surface vertex indices, edge indices, and triangle indices
    """

    tetra = Delaunay(pos)
    # Find radius of the circumsphere.
    # By definition, radius of the sphere fitting inside the tetrahedral needs 
    # to be smaller than alpha value
    # http://mathworld.wolfram.com/Circumsphere.html
    #added stuff so if you pass mulitple alpha scale it will adjust alpha an return a list of results
    #to save time checkig if the valeu sucks
    tetrapos = np.take(pos,tetra.vertices,axis=0)
    normsq = np.sum(tetrapos**2,axis=2)[:,:,None]
    ones = np.ones((tetrapos.shape[0],tetrapos.shape[1],1))
    a = np.linalg.det(np.concatenate((tetrapos,ones),axis=2))
    Dx = np.linalg.det(np.concatenate((normsq,tetrapos[:,:,[1,2]],ones),axis=2))
    Dy = -np.linalg.det(np.concatenate((normsq,tetrapos[:,:,[0,2]],ones),axis=2))
    Dz = np.linalg.det(np.concatenate((normsq,tetrapos[:,:,[0,1]],ones),axis=2))
    c = np.linalg.det(np.concatenate((normsq,tetrapos),axis=2))
    r = np.sqrt(Dx**2+Dy**2+Dz**2-4*a*c)/(2*np.abs(a) + .001)
    r = np.nan_to_num(r)
    # Find tetrahedrals
    if alpha is None:
        if ratio is not None:
            alpha = np.quantile(r,[ratio]) 
        else:
            alpha = np.mean(r)
            
    def get_verts(threshold):
        tetras = tetra.vertices[r<threshold,:]
        # triangles
        TriComb = np.array([(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)])
        Triangles = tetras[:,TriComb].reshape(-1,3)
        Triangles = np.sort(Triangles,axis=1)
        # Remove triangles that occurs twice, because they are within shapes
        TrianglesDict = defaultdict(int)
        for tri in Triangles:
            TrianglesDict[tuple(tri)] += 1
        Triangles=np.array([tri for tri in TrianglesDict if TrianglesDict[tri] ==1])
        #edges
        EdgeComb=np.array([(0, 1), (0, 2), (1, 2)])
        Edges=Triangles[:,EdgeComb].reshape(-1,2)
        Edges=np.sort(Edges,axis=1)
        Edges=np.unique(Edges,axis=0)

        Vertices = np.unique(Edges)
        return Vertices
    
    verts = [get_verts(alpha*ascale) for ascale in alpha_scales]
    points = [pos[v] for v in verts]
    if len(verts) == [0]:
        verts = verts[0]
        points = points[0]
    if return_vertices:
        return verts
    return points#,Edges,Triangles

def pcloud_to_concave_hull(roi_clouds,**kwargs):
    #wrapper for taking a dict of {roi: pointcloud} and returning {roi: pointcloud_concave_hull}
    temp = {}
    for k,v in roi_clouds.items():
        #skip if too few points 
        if v.shape[0] > 5:
            hull_points = concave_hull_3d(v,**kwargs)
            temp[k] = hull_points
        else:
            temp[k] = v
    return temp

def pointcloud_distance(pc1,pc2,metric='euclidean'):
    #get two pointcloud arrays, checks distance between each pair of points
    #returns the smallest distance (inter-organ distance)
    
    #skip empty items
    if pc1.shape[0] < 1 or pc2.shape[0] < 1:
        return False
    
    #scipy function to get pointwise distances
    cdists = cdist(pc1,pc2,metric)
    if cdists.shape[0] < 1:
        return False
    min_dist = cdists.min()
    
    #this should check for overlap
    #somewhat simple, but looks at closests points and checks if source roi is closer
    #to target's centroid than the point on the target roi
    min_locs = np.argwhere(cdists==min_dist)
    target_center = cloud_centroid(pc2)
    
    #check if the distance should be negative if closest point in pc1 is closer than closest point in pc2 to pc2's centroid
    for min_args in min_locs:
        min_pc1 = pc1[min_args[0]]
        min_pc2 = pc2[min_args[1]]
        if np.linalg.norm(min_pc1 - target_center) < np.linalg.norm(min_pc1 - target_center):
            return -min_dist
    return min_dist
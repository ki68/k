# -*- coding: utf-8 -*-
'''
# by kim sung rock
py2.7/3.7
'''

import maya.cmds as mc
import maya.mel as mel
import maya.api.OpenMaya as om2
import operator
import re

import k.ba.fn 

print ('read mesh module')

'''
////////////// glTools ////////////////
https://github.com/bungnoid/glTools

MIT License

Copyright (c) 2016 Grant Laker

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

    
#=======================================================#
#                 get_closest_edge
#=======================================================#
# If there are multiple edges, the lowest id is obtained first. ( If "pos" is on the vtx )
'''
pos = mc.xform('joint1', q=1, ws=1, a=1, t=1)
val=closest_edge('pCube2', pos) 
mc.select('pCube2.e[%s]'%val[0])
'''

def closest_edge( mesh, pos=(0,0,0) ):

    pos = om2.MPoint(pos)

    sel = om2.MSelectionList()
    sel.add(mesh)
    fn_mesh = om2.MFnMesh(sel.getDagPath(0))
    
    mesh_edge_it = om2.MItMeshEdge(sel.getDagPath(0))
    mesh_edge_it.reset()
    edge_ids_distances = []
    
    while not mesh_edge_it.isDone():
    
        edgeVtx1_pos = mesh_edge_it.point(0, om2.MSpace.kWorld) 
        edgeVtx2_pos = mesh_edge_it.point(1, om2.MSpace.kWorld) 
        closest_pos = k.ba.fn.closest_point(pos, edgeVtx1_pos, edgeVtx2_pos)
        closest_pos = om2.MPoint(closest_pos)
        edge_ids_distances.append((mesh_edge_it.index(), closest_pos.distanceTo(pos)))        
        mesh_edge_it.next()    
    
    return min(edge_ids_distances, key=operator.itemgetter(1))
    

#=======================================================#
#              get_closest_edge_inaccurate
#=======================================================#
# If there are multiple edges, the lowest id is obtained first. ( If "pos" is on the vtx )
''' 
pos = mc.xform('joint1', q=1, ws=1, a=1, t=1)
val=closest_edge_inaccurate('pCube2', pos) 
mc.select('pCube2.e[%s]'%val[0])
'''

def closest_edge_inaccurate( mesh, pos=(0,0,0) ):

    pos = om2.MPoint(pos)

    sel = om2.MSelectionList()
    sel.add(mesh)
    fn_mesh = om2.MFnMesh(sel.getDagPath(0))
    
    faceIndex = fn_mesh.getClosestPoint(pos, space=om2.MSpace.kWorld)[1]    
    edges=cmds.polyListComponentConversion('%s.f[%s]'%(mesh, faceIndex), ff=1, te=1)
    edges = cmds.filterExpand(edges, sm=32) 
    
    edge_ids_distances = []
    for edge in edges:
        edge_pos = mc.xform(edge, q=1, ws=1, a=1, t=1)
        edge_center = (
        (edge_pos[0]+edge_pos[3])*0.5,
        (edge_pos[1]+edge_pos[4])*0.5,
        (edge_pos[2]+edge_pos[5])*0.5
        )
        
        index = int( re.findall('e\[(\d+)',edge)[0] )
        
        edge_center = om2.MPoint(edge_center)
        edge_ids_distances.append((index, edge_center.distanceTo(pos)))

    return min(edge_ids_distances, key=operator.itemgetter(1))
    

#=======================================================#
#                 closest_face_vtx
#=======================================================# 
'''
This is not the nearest face center.
you have to use api 2.0, not api 1.0, in this function
if you use api 1.0, an error will occur.

operating structure
- get the nearest face id to a given point
- get the id of vertices from the face
- return the nearest vertex id and distance of the vertices
'''

def closest_face_vtx( mesh, pos=(0,0,0) ):
    '''Return closest vertex and distance from mesh to world-space position [x, y, z].        
    Uses om2.MfnMesh.getClosestPoint() returned face ID and iterates through face's vertices.
    
    Example:
        >>> closest_face_vtx("pCube1", pos=[0.5, 0.5, 0.5])
        # (1, 3, 0.0)

    Args:
        mesh (str): Mesh node name.
        pos (list): Position vector XYZ
        
    Returns:
        tuple: (face index, vertex index, distance)
    
    '''

    pos = om2.MPoint(pos) # MPoint
    sel = om2.MSelectionList() # MSelectionList
    sel.add(mesh)
    fn_mesh = om2.MFnMesh(sel.getDagPath(0)) # get MFnMesh
    
    # return value - nearest MPoint and a face id with the point
    # ex) (maya.api.OpenMaya.MPoint(22.3566, 101.9476, 7.4321, 1), 3342)
    faceIndex = fn_mesh.getClosestPoint(pos, space=om2.MSpace.kWorld)[1]      
    
    # get polygon vertices ( MIntArray type)
    faceVtxIndexs = fn_mesh.getPolygonVertices(faceIndex)

    
    # tuple of (vertex id, distance) 
    vertex_distances = (  (vertexIndex, fn_mesh.getPoint(vertexIndex, om2.MSpace.kWorld).distanceTo(pos)) for vertexIndex in faceVtxIndexs  )  
    
    # print type(vertex_distances) # <type 'generator'>
    # ----- generator note. ------
    # [] is list, () is generator type
    # http://pythonstudy.xyz/python/article/23-Iterator%EC%99%80-Generator
    # https://tibetsandfox.tistory.com/27 
    # https://wikidocs.net/16069 for, list are generator type
    
    # generator features are printed only once. redefine "a=.." to use it again
    '''
    a = ( (b, 1.2) for b in [1,2,3])
    for e in a: 
        print (e)
        
    (1, 1.2)
    (2, 1.2)
    (3, 1.2)    
    '''    
    
    a = (faceIndex,)  # add (,) to make tuple
    b = min(vertex_distances, key=operator.itemgetter(1))
    
    # key=operator.itemgetter(1) means getting the smallest generator value based on the second value of the generator(vertex_distances). so "b= .." means getting the nearest tuple value ( index, diatance ) 

    # combine tuples. (face id, vtx id, nearest vertex distance)
    return (a + b) 
    
    
    
#=======================================================#
#                 get_closest_two_edges
#=======================================================# 
# given the nearest vertex and a face inclde the vertex
# This is not the two closest edges of all edges.    
def closest_two_edges( mesh, faceIndex, vtxIndex ):

    sel = om2.MSelectionList()
    sel.add(mesh)
    fn_mesh = om2.MFnMesh(sel.getDagPath(0))
    
    MItMeshPolygon = om2.MItMeshPolygon(sel.getDagPath(0))
    
    ''' ---- note -----
    # (Not used here) It's good to use when loop
    while not MItMeshPolygon.isDone():
        # do work here...
        print ('1')
        MItMeshPolygon.next(None)   
        #Maya 2019 requires 1 argument i.e. MItMeshPolygon.next(None)
        #Maya 2020 requires NO argument i.e. MItMeshPolygon.next()        
    '''
    
    MItMeshPolygon.setIndex(faceIndex)
    allEdgesOfFace=MItMeshPolygon.getEdges() # all edges of the face ( 4 edges )
    
    MItMeshVertex = om2.MItMeshVertex(sel.getDagPath(0))
    MItMeshVertex.setIndex(vtxIndex)
    allEdgesOfVtx=MItMeshVertex.getConnectedEdges() # all edges of the nearest vertex ( other 4 edges )
    
    # intersection -> the nearest two edges.
    # convert MIntArray type to list
    intersection = list( set(list(allEdgesOfFace)) & set(list(allEdgesOfVtx)) )

    # get average length of the nearest two edges to scale rivet locator
    MItMeshEdge = om2.MItMeshEdge(sel.getDagPath(0))
    MItMeshEdge.setIndex(intersection[0])
    len1=MItMeshEdge.length()
    MItMeshEdge.setIndex(intersection[1])
    len2=MItMeshEdge.length()
    averLength = (len1+len2)/2.0

    return (intersection, averLength)

    

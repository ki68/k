# -*- coding: utf-8 -*-

import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as om1
import maya.api.OpenMaya as om2

print ('read surface module')


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

# --------- glTools api 1.0 ---------
def is_surface( surface ):
    '''
    Check if the specified object is a nurbs surface or transform parent of a surface
    @param surface: Object to query
    @type surface: str
    '''
    # Check object exists
    if not mc.objExists(surface): return False
    # Check shape
    if mc.objectType(surface) == 'transform': surface = mc.listRelatives(surface,s=True,ni=True,pa=True)[0]
    if mc.objectType(surface) != 'nurbsSurface': return False
    
    # Return result
    return True

# --------- glTools api 1.0 ---------
def get_surfaceFn( surface ):
    '''
    Create an MFnNurbsSurface class object from the specified nurbs surface
    @param surface: Surface to create function class for
    @type surface: str
    '''
    # Checks
    if not is_surface(surface): raise Exception('Object '+surface+' is not a valid surface!')
    if mc.objectType(surface) == 'transform':
        surface = mc.listRelatives(surface,s=True,ni=True,pa=True)[0]
    
    # Get MFnNurbsSurface
    selection = om1.MSelectionList()
    om1.MGlobal.getSelectionListByName(surface,selection)
    surfacePath = om1.MDagPath()
    selection.getDagPath(0,surfacePath)
    surfaceFn = om1.MFnNurbsSurface()
    surfaceFn.setObject(surfacePath)
    
    # Return result
    return surfaceFn


#=======================================================#
#                 closest_uv
#=======================================================# 

def closest_uv( surf, pos=(0,0,0) ):
    
    selList = om2.MSelectionList()
    selList.add(surf)
    #surfFn = om2.MFnNurbsSurface(selList.getDagPath(0))
    
    # https://github.com/bungnoid/glTools/blob/master/utils/surface.py
    #  -------- glTools api 1.0 방식으로 uv 캐치 -----------
    pt = om1.MPoint(pos[0],pos[1],pos[2],1.0)
    
    # Get surface function set
    surfFn = get_surfaceFn(surf)
    
    # Get uCoord and vCoord pointer objects
    uCoord = om1.MScriptUtil()
    uCoord.createFromDouble(0.0)
    uCoordPtr = uCoord.asDoublePtr()
    vCoord = om1.MScriptUtil()
    vCoord.createFromDouble(0.0)
    vCoordPtr = vCoord.asDoublePtr()
    
    # get closest uCoord to edit point position
    surfFn.closestPoint(pt,uCoordPtr,vCoordPtr,True,0.0001,om1.MSpace.kWorld)
    u = om1.MScriptUtil(uCoordPtr).asDouble()
    v = om1.MScriptUtil(vCoordPtr).asDouble()  
    
    '''
    # ------- note ---------
    # api 2.0 cause an error! 
    # In the case, the incorrect uv value is obtained.
    #p, u, v = surfFn.closestPoint(om2.MPoint(pos), 0,0,True,0.0001,om2.MSpace.kWorld) 

    - Error saying it must be int because of 0.0001. 
    - similar situation below. 
    - It seems to have been fixed in the 2022 version. 
    - Not tested in 2020.1
    https://forums.autodesk.com/t5/maya-programming/how-do-you-use-kwargs-within-openmaya-api-v-2-0/td-p/7301677
    https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2022/ENU/Maya-ReleaseNotes/files/2022-release-notes/Maya-ReleaseNotes-2022-release-notes-fixed-issues2022-html-html.html
    
    '''

    return (u, v)




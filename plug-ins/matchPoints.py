# -*- coding: utf-8 -*-
''' 
custom maya cmd :
Vertex matching between two mesh objects


https://github.com/minoue
https://ex3_transfervertexposition.py/

MIT License

Copyright (c) 2019 Michi Inoue

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

import maya.api.OpenMaya as om2
import maya.OpenMayaMPx as OpenMayaMPx
import sys 

commandName = "matchPoints" 

class matchPoints(OpenMayaMPx.MPxCommand):

    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)

        self.sourceFnMesh = None
        self.targetFnMesh = None
        self.sourcePoints = None
        self.targetPoints = None

    def isUndoable (self):
        return True

    def redoIt(self):
        self.sourceFnMesh.setPoints(self.targetPoints) # to target

    def undoIt(self):
        self.sourceFnMesh.setPoints(self.sourcePoints) # to source    

    def doIt(self, argList):
    
        sel = om2.MGlobal.getActiveSelectionList()
        self.targetFnMesh = om2.MFnMesh(sel.getDagPath(0)) # target 
        self.sourceFnMesh = om2.MFnMesh(sel.getDagPath(1)) # source (to be changed)
 
        # get points from target       
        self.targetPoints = self.targetFnMesh.getPoints()       
        self.sourcePoints = self.sourceFnMesh.getPoints() # for undo         

        # set points to source
        self.sourceFnMesh.setPoints(self.targetPoints)
        
        print ('Compelte.')


def creator():
    return OpenMayaMPx.asMPxPtr(matchPoints())

def initializePlugin (mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerCommand("matchPoints", creator)
    except:
        sys.stderr.write( "Failed to register command: %s\n" % commandName )


def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand("matchPoints")
    except:
        sys.stderr.write( "Failed to unregister command: %s\n" % commandName )
        
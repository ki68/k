# -*- coding: utf-8 -*-

import maya.cmds as mc
import maya.api.OpenMaya as om2

print ('read cuv module')

'''

import sys
sys.path.append('c:/')

import k.ba.cuv
importlib.reload(k.ba.cuv)

kCuv = k.ba.cuv.Curve()

kCuv.get_pos_para([50],'curve1')
mc.select(cl=1)
mc.joint(p=kCuv.posList[0])

kCuv.get_equal_pos_para(5,'curve1')
for e in kCuv.posList:
	mc.select(cl=1)
	mc.joint(p=e)

'''


class Curve:

    def __init__( self ):
        self.para = None
        self.paraList = []
        self.pos = None 
        self.posList = []

    #====================================
    #         get equalPosUpara
    #====================================
    # get the position of the curve divided equally
    # by a given number of curves
    # get_equal_pos_para(3,'curve1')
    
    def get_equal_pos_para(self, objNum, cuv):
                  
        if not mc.nodeType(cuv) == 'nurbsCurve':    	              
            child = mc.listRelatives(cuv, c=1, s=1, ni=1) or []

        if not mc.nodeType(child[0]) == 'nurbsCurve':
            mc.error(' You should select a Curve Transform.')
                
        if objNum <= 1:
            mc.error('The number of object should be greater than 1')

        mSel = om2.MSelectionList()
        mSel.add(cuv) #  transform or shape
        fnCuv = om2.MFnNurbsCurve(mSel.getDagPath(0))
        
        length = mc.arclen(cuv)
        length_unit = length/float(objNum-1) 
        
        for i in range(objNum):
            uPara = fnCuv.findParamFromLength(i*length_unit)            
            self.posList.append(mc.pointOnCurve(cuv, pr=uPara, p=1))
            self.paraList.append(uPara)
    
    #====================================
    #     get posPara from length
    #====================================
    # get the position and u parameter of a given percentage
    # get_pos_para([50],'curve1') # 50%
    
    def get_pos_para(self, percents, cuv):
    
        if not isinstance(percents, list):
            mc.error(' You should put the parameter of list type.')

        if not mc.nodeType(cuv) == 'nurbsCurve':    	              
            child = mc.listRelatives(cuv, c=1, s=1, ni=1) or []

        if not mc.nodeType(child[0]) == 'nurbsCurve':
            mc.error(' You should select a Curve Transform.')

        mSel = om2.MSelectionList()
        mSel.add(cuv) #  transform or shape
        fnCuv = om2.MFnNurbsCurve(mSel.getDagPath(0))
        
        length = mc.arclen(cuv)
        
        for percent in percents:
            uPara = fnCuv.findParamFromLength(length * percent * 0.01)
            pos = mc.pointOnCurve(cuv, pr=uPara, p=1)
            
            self.posList.append(pos)
            self.paraList.append(uPara)
        


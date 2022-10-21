# -*- coding: utf-8 -*-
'''
py2.7/3.7
'''
import maya.cmds as mc
import maya.mel as mel
import math
from os.path import isfile, isdir
from sys import stdout
import io
import maya.OpenMaya as OpenMaya
import re

#====================================
#       position-related class
#==================================== 

class Pos:

    #====================================
    #            get position 
    #====================================
    
    def get_t( self, objs ):
        posList=[]
        for obj in objs:
            posList.append(mc.xform(obj,q=1,a=1,ws=1,t=1))
        return posList
        
    #========================================
    #            set mosition
    #========================================
    
    def set_t( self, posList ):
        for n,obj in enumerate(objs):
            mc.xform(obj,a=1,ws=1,t=posList[n])
            
            

#====================================
#       get serialized new name
#==================================== 
def newName(name):  
      
    while mc.objExists(name):   
        m = re.search(r'\d+$', name) # $ is the end of string
        if m is not None:
            number = m.group()
            frontStr = name.split(number)[0]
            name = frontStr + str(int(number) + 1)
        else : 
            name = name + '1'
    
    return name
            

 
#====================================
#     function to add attribute
#====================================  

# ats argument - long(int type) or float
# dvs argument - if string type, have to put string list in dvs
def addAttrs( objs,attrs,ats,mins,maxs,dvs,IsString='no',enumVals=[]): # 'non' in the mins and maxs means undefined.
    objAttrs=[]
    for n, obj in enumerate(objs):
        if IsString == 'no':
            if ats[n] != 'enum':
                if maxs[n]=='non' and mins[n]!='non': mc.addAttr(obj, ln=attrs[n],at=ats[n],min=mins[n],dv=dvs[n])
                elif mins[n]=='non'and maxs[n]!='non': mc.addAttr(obj, ln=attrs[n],at=ats[n],max=maxs[n],dv=dvs[n])
                elif mins[n]=='non'and maxs[n]=='non': 
                    mc.addAttr(obj, ln=attrs[n],at=ats[n],dv=dvs[n])
                else: mc.addAttr(obj, ln=attrs[n], at=ats[n], min=mins[n], max=maxs[n], dv=dvs[n])
                             
            else : mc.addAttr(obj, ln=attrs[n], at=ats[n], en=enumVals[n])               
            
            mc.setAttr(obj+'.'+attrs[n],k=1) 
            
        else:
            mc.addAttr(obj, ln=attrs[n],dt='string')        
            mc.setAttr(obj+'.'+attrs[n],dvs[n],type='string') 
            
        objAttrs.append(obj+'.'+attrs[n])
        
    return objAttrs
    
    
#====================================
#      set driven key function
#====================================  
''' example) two driven objects
sdk('joint1.ty',['pSphere1.ty','pCube1.ty'],[0,0,0],[-10,-1,-2],[10,1,2],1,[['linear','linear'],['linear','linear']],[['spline','spline'],['spline','spline']],[['spline','spline'],['spline','linear']],[['linear','linear'],['constant','linear']])
'''
''' example) one driven objects
sdk('joint1.rz',['blendShape1.pCube2'],[0,0],[],[45,1],0,[['linear','linear'],['linear','linear']],[['spline','spline'],['spline','spline']],[['spline','spline'],['spline','linear']],[['linear','linear'],['constant','linear']])

'''
# put driver object in dvs, mins, maxs in the first order
# dvTans, minTans, maxTans are the pre and post tangent type of each key(curve)
# infinityShps are the front and back shape type of each key(curve) extension

def sdk( driver,drivens,dvs,mins,maxs,infinity,dvTans,minTans,maxTans,infinityShps): 


    mc.setAttr(driver,dvs[0]) # default value set
    for n,e in enumerate(drivens):      
        mc.setAttr(drivens[n],dvs[n+1]) # default value set
    mc.setDrivenKeyframe(drivens,currentDriver=driver) # apply sdk
    
    if not mins == []:
        mc.setAttr(driver,mins[0]) # min value set
        for n,e in enumerate(drivens):    
            mc.setAttr(drivens[n],mins[n+1]) # min value set
        mc.setDrivenKeyframe(drivens,currentDriver=driver)
    
    if not maxs == []:
        mc.setAttr(driver,maxs[0]) # max value set
        for n,e in enumerate(drivens):    
            mc.setAttr(drivens[n],maxs[n+1]) # max value set
        mc.setDrivenKeyframe(drivens,currentDriver=driver)

    Added_AnimCuv_L=[]
    
    for n,e in enumerate(drivens):
    
        # if driver are several, will have 'blendWeighted' node. 
        if mc.nodeType(mc.listConnections(e)[0],scn=1) == 'blendWeighted': # scn 1 - pass conversion node
            Added_AnimCuv = mc.listConnections(mc.listConnections(e)[0]+'.input',scn=1)[-1] # select final animCurve
        else : 
            Added_AnimCuv = mc.listConnections(e,scn=1)[0]


        mc.select(Added_AnimCuv) 
        Added_AnimCuv_L.append(Added_AnimCuv)
        
        mc.selectKey(Added_AnimCuv,k=1,f=(dvs[0],)) # Usually pre and post tangents of selected key are chosen.
        mc.keyTangent(itt=dvTans[n][0],ott=dvTans[n][1])
        
        if not mins == []:        
            mc.selectKey(Added_AnimCuv,k=1,f=(mins[0],)) # in python, f=(value,). have to type a single value like this.
            mc.keyTangent(itt=minTans[n][0],ott=minTans[n][1])
        
        if not maxs == []:        
            mc.selectKey(Added_AnimCuv,k=1,f=(maxs[0],))
            mc.keyTangent(itt=maxTans[n][0],ott=maxTans[n][1])
        
        mc.setInfinity(pri=infinityShps[n][0], poi=infinityShps[n][1]) 
        
    mc.setAttr(driver,dvs[0])    
    mc.animCurveEditor('graphEditor1GraphEd',e=1,displayInfinities=infinity) # seems to apply to all curves. CAUTION!
    

    # keyTangent, setInfinity - can't put animCurve parameter in the first order in command()
    # keyTangent - set pre and post tangents type of selected key. 
    # in the case of linear type, post tangent will be flated if the key is at the end of the curve,
    # setInfinity - constant(value) is flat

    return Added_AnimCuv_L    
    



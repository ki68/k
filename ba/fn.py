# -*- coding: utf-8 -*-
'''
# by kim sung rock
py2.7/3.7
'''
import maya.cmds as mc
import maya.mel as mel
import math
from os.path import isfile, isdir
from sys import stdout
import io
import maya.api.OpenMaya as om2
import re

print ('read fn module')

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
            
         

#=======================================================#
#                 get_closest_point
#=======================================================#
# basic principle : Orthogonal Projection, Gram-Schmidt Orthogonalization
# help : https://ki68.github.io/Get_Closest_Point_On_Line/
# refer to :
# https://forums.cgsociety.org/t/snap-vertices-to-nearest-point-on-curve-or-edge/1833911/2
# https://wizardmania.tistory.com/m/20
# https://m.blog.naver.com/qio910/221778224660
# https://www.geogebra.org/m/b5c9x8ef
# Vector A * Vector B == Vector B * Vector A

# the nearest point on a line (connecting p2_pos and p3_pos) from p1_pos 
def closest_point(p1_pos, p2_pos, p3_pos):

    p1_pos = om2.MPoint(p1_pos)
    p2_pos = om2.MPoint(p2_pos)
    p3_pos = om2.MPoint(p3_pos)   

    # normalized vectorA : p2 --> p3
    VectA = p3_pos - p2_pos 
    n_VectA = VectA.normal() # MVector. Normalize the  magnitude(length) of the vector to 1
    
    # vectorB : p2 --> p1
    VectB = p1_pos - p2_pos # MVector 
        
    dotP_nVectA_VectB = n_VectA * VectB # MVector x MVector = dot product

    # p is the point closest to VectA from p1_pos
    # p is MPoint Type.
    
    # If the p1 is away from the start point of the line(=VectA)
    if dotP_nVectA_VectB <= 0.0: # angle between vectors >= 90                 
        p = p2_pos # start point of VectA
        
    elif dotP_nVectA_VectB > 0.0: #  angle between vectors < 90 
  
        # projected VectB = (normalized VectA * VectB) x normalized VectA
        # proj_VectB is MVector Type -----> Float x MVector => MVector
        
        proj_VectB = dotP_nVectA_VectB * n_VectA         
        p = p2_pos +  proj_VectB # MPoint + MVector => MPoint
   
        # If the p1 is away from the end point of the line(=VectA)
        if (p - p2_pos).length() >= VectA.length():        
            p = p3_pos # end point of VectA

    return (p.x, p.y, p.z)    

         
#====================================
#       get serialized new name
#==================================== 
def new_name(name):  
      
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
def add_attrs( objs,attrs,ats,mins,maxs,dvs,IsString='no',enumVals=[]): # 'non' in the mins and maxs means undefined.
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
    
    
#====================================
#             grouping
#====================================   
def grp( sels, repeat=1, grpStrName='grp' ):  

    for n in range(repeat):
        if not isinstance(sels,list): 
            sels=[sels]
        newGrp=[] 
        i=0
        for ssel in sels:
            parent = mc.listRelatives(ssel,p=1,f=1)      
            space = mc.group(em=1,n= ssel + '_'+grpStrName)
            mc.delete(mc.parentConstraint(ssel, space))

            if parent!=None: 
                mc.parent(space,parent[0])
            mc.parent(ssel, space) 
            newGrp_=mc.listRelatives(p=1,path=1)
            newGrp.append(newGrp_[0])
            i+=1  
        sels=newGrp  
        
    return newGrp  


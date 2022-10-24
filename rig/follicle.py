# -*- coding: utf-8 -*-
''' 
How to use it externally :

    # select target objects and mesh(or surface)
    # Or select target elements of surface like vtx, cv..
    # In case of the rivet type on mesh, vtxs or edges selection doesn't work.
    
    attach = k.rig.follicle.Attach()
    attach.run()
    follicles = attach.follicles
    
'''

import sys
import maya.cmds as mc
import maya.api.OpenMaya as om2
import re

import k.ba.mesh 
import k.ba.surf

# for code feedback
if sys.version_info > (3,7,0): 
    import importlib
    importlib.reload(k.ba.mesh)
    importlib.reload(k.ba.surf)
else :
    import imp
    imp.reload(k.ba.mesh) 
    imp.reload(k.ba.surf) 
    
    
print ('read follicle module')    

#=======================================================#
#                    Attachment Class
#=======================================================#  

class Attach:

    def __init__( self ):    
    
        # whether the targets(selected by the user) are geometries or not
        self.targetsNotGeo = None
        
        self.geoType = None
        self.targets = []
        self.geo = None
        
        self.attrAdd = None
        self.follicles = []
        
    #==============================================#
    #                    run
    #==============================================#  
    
    def run( self, argType='sel',objs=[], type='follicle', attrAdd=1 ):
    
        print ('run')
        
        self.attrAdd = attrAdd # custom u,v attribute for nurbsSurface
        
        # ====================
        # - Define Variables -
        # ====================        
        
        # if you chose object(s)
        if argType == 'sel':
            sels=mc.ls(sl=1,fl=1)
            
            self.targets=sels[:-1] # target objects
            self.geo =sels[-1] # last choice is mesh or nurbSurface        
            
        #  for when you run function as a command
        else : 
            self.targets=objs[:-1]
            self.geo =objs[-1]
            
        # =======================
        # - the number of cases -
        # =======================  
        
        # categorized into next selected objs types
        # case 1. only points
        #         - case 1-1. mesh
        #         - case 1-2. nurbsSuf
        # case 2. points and (mesh or surface) are given
        #         - case 2-1. mesh
        #         - case 2-2. nurbsSuf        
        # case 3. two edges - case 3 was included in the case 1
   
        # case 1.
        if ('.cv[' in self.geo or
            '.uv[' in self.geo or
            '.vtx[' in self.geo or
            '.e[' in self.geo or  
            '.f[' in self.geo ):            
            self.targetsNotGeo=1 
            
            if ('.vtx[' in self.geo or
                '.f[' in self.geo or
                '.e[' in self.geo):
                self.geoType = 'mesh'   # case 1-1
            else : 
                self.geoType = 'nurbsSuf'   # case 1-2
                
            
        # case 2.    
        else :
            self.targetsNotGeo=0
            if mc.listRelatives(self.geo, s=1, type='mesh',ni=1):
                self.geoType = 'mesh'     # case 2-1
            elif mc.listRelatives(self.geo, s=1, type='nurbsSurface',ni=1):
                self.geoType = 'nurbsSuf'    # case 2-2

        
        print (self.targetsNotGeo, self.geoType)
        
        # ====================
        # - Put Cases In Dic -
        # ====================                
            
        options = {    
        (0, 'mesh'): self.attach_selected_targets_on_mesh, # temp objs, mesh    
        (1, 'mesh'): self.attach_on_face, # mesh face 
        (0, 'nurbsSuf'): self.attach_selected_targets_on_nurbsSuf, # temp objs, nurbsSurface        
        (1, 'nurbsSuf'): self.attach_on_nurbsSuf, # cvs or surface points    
        }
        
        # ------ execute ------
        options[(self.targetsNotGeo, self.geoType)]()


    #==============================================#
    #      case - attach_selected_targets_on_mesh
    #==============================================# 
    
    def attach_selected_targets_on_mesh( self ):
    
        
        print ('method - attach_selected_targets_on_mesh')
        
        
        self.follicles=[]
        for target in self.targets:
            target_pos = mc.xform(target, q=1, ws=1, a=1, t=1)[:3] # no piv=1
 
            follicle = create_on_mesh(self.geo, target_pos, 'follicle1')
            
            self.follicles.append(follicle)

        mc.select(self.follicles)            


    #==============================================#
    #           case - attach_on_face
    #==============================================# 
    
    def attach_on_face( self ): 
        print ('method - attach_on_face')   

        self.targets=mc.ls(sl=1,fl=1) # get again. 
        
        if '.f[' in self.geo : 
            self.follicles=[]
            self.geo = self.geo.split('.f[')[0]
            for target in self.targets:     
                
                bbx = mc.xform(target, q=1, bb=1, ws=1) 
                centerX = (bbx[0] + bbx[3]) / 2.0
                centerY = (bbx[1] + bbx[4]) / 2.0
                centerZ = (bbx[2] + bbx[5]) / 2.0  

                follicle = create_on_mesh(self.geo, [centerX, centerY, centerZ], 'follicle1')
                
                self.follicles.append(follicle)

            mc.select(self.follicles)   

        elif '.vtx[' in self.geo : 
            self.follicles=[]
            self.geo = self.geo.split('.vtx[')[0]
            for target in self.targets:     
                
                pos=mc.xform(target, q=1, ws=1, a=1, t=1)
                
                follicle = create_on_mesh(self.geo, pos, 'follicle1')
                
                self.follicles.append(follicle)

            mc.select(self.follicles) 
            
        elif '.e[' in self.geo : 
            self.follicles=[]
            self.geo = self.geo.split('.e[')[0]
            for target in self.targets:     
                
                bbx = mc.xform(target, q=1, bb=1, ws=1) 
                centerX = (bbx[0] + bbx[3]) / 2.0
                centerY = (bbx[1] + bbx[4]) / 2.0
                centerZ = (bbx[2] + bbx[5]) / 2.0  

                follicle = create_on_mesh(self.geo, [centerX, centerY, centerZ], 'follicle1')
                
                self.follicles.append(follicle)

            mc.select(self.follicles)             
            
        else:
            pass        


    #==============================================#
    #   case - attach_selected_targets_on_nurbsSuf
    #==============================================#  
    
    def attach_selected_targets_on_nurbsSuf( self ): 
        print ('method - attach_selected_targets_on_nurbsSuf') 
        
        self.follicles=[]
        for e in self.targets:
            target_pos=mc.xform(e, q=1, ws=1, a=1, piv=1)[:3]
                
            uv_values=k.ba.surf.closest_uv(self.geo, target_pos)
            mc.select(self.geo+'.uv['+ str(uv_values[0]) + '][' + str(uv_values[1]) + ']')

            follicle = create_on_surface(self.geo, uv_values[0], uv_values[1], 'follicle1')

            self.follicles.append(follicle)

        mc.select(self.follicles)
      


    #==============================================#
    #        case - attach_on_nurbsSuf
    #==============================================# 
    
    def attach_on_nurbsSuf( self ): 
        print ('method - attach_on_nurbsSuf')         

        self.targets=mc.ls(sl=1,fl=1) # select again.
        self.follicles=[]
        if '.uv[' in self.geo :    
            surf = self.geo.split('.uv[')[0]
            for e in self.targets:
                mc.select(e)
                
                uv_values = re.findall(r'\[\d+.\d+\]', e) # get u, v
                uv_values = [ float(x[1:-1]) for x in uv_values ] 
                # remove '[' and ']'
                
                self.geo = self.geo.split('.uv')[0]
                
                follicle = create_on_surface(self.geo, uv_values[0], uv_values[1], 'follicle1')
                
                self.follicles.append(follicle)


        if '.cv[' in self.geo :  
            surf = self.geo.split('.cv[')[0]        
            for e in self.targets:
                target_pos=mc.xform(e, q=1, ws=1, a=1, t=1)
                uv_values=k.ba.surf.closest_uv(surf, target_pos)
                
                self.geo = self.geo.split('.cv[')[0]
                
                follicle = create_on_surface(self.geo, uv_values[0], uv_values[1], 'follicle1')
                
                self.follicles.append(follicle)
                

        mc.select(self.follicles)      




#=======================================================#
#             create follicle on nurbSurface
#=======================================================#
def create_on_surface(surf, u, v, name='follicle1'):

    grp = mc.group(em=1) 
    name = k.ba.fn.new_name(name)
    grp = mc.rename(grp, name)
    shp = mc.listRelatives(surf, s=1, ni=1)[0]
    fol = mc.createNode('follicle', n=grp+'Shape', p=grp)
    mc.connectAttr(shp + '.local', fol+'.inputSurface')
    mc.connectAttr(shp + '.worldMatrix[0]', fol+'.inputWorldMatrix')
    mc.connectAttr(fol + '.outTranslate', grp + '.translate')
    mc.connectAttr(fol + '.outRotate', grp + '.rotate')
    uMax = mc.getAttr(surf +'.mxu')
    vMax = mc.getAttr(surf +'.mxv')
    mc.setAttr(fol+ '.parameterU', u/float(uMax) )
    mc.setAttr(fol+ '.parameterV', v/float(vMax) )
    
    mc.select(grp)
    
    return grp
    
#=======================================================#
#             create follicle on mesh
#=======================================================#  
# issue - It will take a load while this function looping because mesh is copyed.
def create_on_mesh(surf, pos, name='follicle1'):

    # duplicate and freeze for getting the right uv value. 
    # remove after using it
    surf_clone=mc.duplicate(surf,st=1)[0]     
    mc.makeIdentity(surf_clone, apply=1, t=1, r=1, s=1, n=0)

    pos = om2.MPoint(pos) # MPoint
    sel = om2.MSelectionList() # MSelectionList
    sel.add(surf_clone)
    fn_mesh = om2.MFnMesh(sel.getDagPath(0)) # get MFnMesh
    values = fn_mesh.getUVAtPoint(pos)	 # get the uv of the nearest point , face id containing the point
    u = values[0]
    v = values[1]

    grp = mc.group(em=1) 
    name = k.ba.fn.new_name(name)
    grp = mc.rename(grp, name)
    shp = mc.listRelatives(surf, s=1, ni=1)[0]
    fol = mc.createNode('follicle', n=grp+'Shape', p=grp)
    
    mc.connectAttr(shp + '.worldMesh[0]', fol+'.inputMesh')
        
    mc.connectAttr(shp + '.worldMatrix[0]', fol+'.inputWorldMatrix')
    mc.connectAttr(fol + '.outTranslate', grp + '.translate')
    mc.connectAttr(fol + '.outRotate', grp + '.rotate')

    mc.setAttr(fol+ '.parameterU', u )
    mc.setAttr(fol+ '.parameterV', v )
    
    mc.delete(surf_clone)
    mc.select(grp)
    
    return grp    



#=======================================================#
#             attach many follicles on nurbsSurface
#=======================================================#
'''
1. Get max u,v of surface
2. Divide max u, v by uNum, vUnm
3. In loop, create a follicle repeatedly    
** if number has 1, follicle is located at the middle of the max  value.
'''

def create_many_follicles(uNum, vNum, u_offset, v_offset):
    
    # ------- Get values from viewport
    surf = mc.ls(sl=1)[0]
    surfShp = mc.listRelatives(surf,s=1,ni=1)[0]
    if not mc.nodeType(surfShp) == 'nurbsSurface':
        mc.error('It is not nurbSurface type.')
        return
    
    uMax = mc.getAttr(surf +'.mxu')
    vMax = mc.getAttr(surf +'.mxv')
    
    # -------- Defining Variables -----
    u = 0
    v = 0
    u_unit = 0
    v_unit = 0
    
    # ------ Defining unit u, v values --------
    if uNum == 0 and vNum ==0:  
        return
    
    else :        
        # ----------- unit u value --------
        # case 1-1.
        if uNum == 1 :        
            u_unit = uMax * 0.5
            uNum = uNum - 1 # to enter the loop and create a follicle
            
        # case 1-2.    
        else : 
            u_unit = uMax / float(uNum-1) # divide into equal parts

        # ----------- unit v value --------
        # case 2-1.
        if vNum == 1 :        
            v_unit = vMax * 0.5
            vNum = vNum - 1  # to enter the loop and create a follicle
            
        # case 2-2.            
        else : 
            v_unit = vMax / float(vNum-1) # divide into equal parts
    
    follicles = []
    
    # ------------ u value loop ----------    
    
    for i in list(range(uNum+1)):
    
        # case 1-1.
        if uNum == 0 : # when actually uNum == 1 in ui
            u = uMax*0.5 + u_offset * u_unit * 0.01        
        # case 1-2.
        else :            
            u = u_unit * i + u_offset * u_unit * 0.01

                
        # If the u is out of the u range, the follicle is not created.
        if u > uMax or u < 0.0 : 
            continue

        # --------------- v value loop ----------
        
        # case 2-1.
        if vNum == 0 : # when actually vNum == 1 in ui            
            v = vMax*0.5 + v_offset * v_unit * 0.01
            
            fol = k.rig.follicle.create_on_surface(surf, u, v, 'follicle1')
            follicles.append(fol)  
            
        # case 2-2.            
        else :                
            for j in list(range(vNum+1)):               
                v = v_unit * j + v_offset * v_unit * 0.01
                
                # If the v is out of the v range, the follicle is not created.
                if v > vMax or v < 0.0 : 
                    continue                
                    
                fol = k.rig.follicle.create_on_surface(surf, u, v, 'follicle1')
                follicles.append(fol)                                
                              
    
    mc.select(follicles)
    
    # ------- print follicles number ------
    
    follicles_num = len(follicles)     
    if follicles_num == 1: word1 = 'was'
    elif follicles_num > 1: word1 = 'were'    
    print ('%d %s created.' % (follicles_num, word1))
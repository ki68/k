# -*- coding: utf-8 -*-
''' 
How to use it externally :

    # select target objects and mesh(or surface)
    # Or select target elements of surface like vtx, cv..
    # In case of the rivet type on mesh, vtxs or edges selection doesn't work.
    
    attach = k.rig.rivetk.Attach()
    attach.run()
    locs = attach.locs
    
'''

import sys
import maya.cmds as mc

import k.ba.fn 
import k.ba.mesh 
import k.ba.surf
import k.rig.rivet

# for code feedback
if sys.version_info > (3,7,0): 
    import importlib
    importlib.reload(k.ba.mesh)
    importlib.reload(k.ba.surf)
    importlib.reload(k.rig.rivet)
else :
    import imp
    imp.reload(k.ba.mesh) 
    imp.reload(k.ba.surf) 
    imp.reload(k.rig.rivet)
    
    
print ('read rivetk module')    

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
        self.locs = []
        
    #==============================================#
    #                    run
    #==============================================#  
    
    def run( self, argType='sel',objs=[], type='rivet', attrAdd=1 ):
    
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
        # case 3. two edges
   
        # case 1.
        if ('.cv[' in self.geo or
            '.uv[' in self.geo or
            '.vtx[' in self.geo or
            '.f[' in self.geo ):            
            self.targetsNotGeo=1 
            
            if '.vtx[' in self.geo or '.f[' in self.geo:
                self.geoType = 'mesh'   # case 1-1
            else : 
                self.geoType = 'nurbsSuf'   # case 1-2
                
        # case 3.        
        elif '.e[' in self.geo : # if it's a mesh
            k.rig.rivet.run() # apply original rivet script.
            return
            
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
        
        self.locs=[]
        for e in self.targets:
            target_pos = mc.xform(e, q=1, ws=1, a=1, t=1)[:3] # no piv=1
            
            # =========================
            # - Get Nearest Two Edges -
            # =========================                     
            
            # (the nearest face id, vertex id, distance of the vertex) to target_pos
            values = k.ba.mesh.closest_face_vtx(self.geo, target_pos) 
            faceId=values[0]
            vtxId=values[1]
            
            mc.select(self.geo + '.vtx[' + str(vtxId) + ']')
             
                        
            values2 = k.ba.mesh.closest_two_edges(self.geo, faceId, vtxId)    
            closestTwoEdgeIds = values2[0]
            averEdgeLength = values2[1]
            
            mc.select(self.geo + '.e['+str(closestTwoEdgeIds[0])+']', self.geo + '.e['+str(closestTwoEdgeIds[1])+']')
            
            # ======================
            # - Apply Rivet Script -
            # ======================            
            
            loc=k.rig.rivet.run() # apply original rivet script.
            
            
            # =====================
            # - Adjust Rivet Etc -
            # =====================             
            
            locS=averEdgeLength*0.5 # in half
            mc.setAttr(loc+'Shape.localScale', locS,locS,locS)
            
            self.locs.append(loc)
                        
            # ----- set rivet pos ---------
            surfInfo=mc.listConnections(loc+'.t',s=1,d=0)[0]
            loft=mc.listConnections(surfInfo+'.inputSurface',s=1,d=0)[0]
              
            tempSuf=mc.createNode('nurbsSurface')

            mc.connectAttr(loft+'.outputSurface', tempSuf+'.create')
            uv_values=k.ba.surf.closest_uv(tempSuf, target_pos)  
            mc.setAttr(surfInfo+'.parameterU', uv_values[0])
            mc.setAttr(surfInfo+'.parameterV', uv_values[1])
            mc.setAttr(surfInfo+'.turnOnPercentage', 0) # because nurbsSurface is not normalized(rebuild)
            
            mc.delete(mc.listRelatives(tempSuf,p=1))

        mc.select(self.locs)


    #==============================================#
    #           case - attach_on_face
    #==============================================# 
    
    def attach_on_face( self ): 
        print ('method - attach_on_face')   

        self.targets=mc.ls(sl=1,fl=1) # get again. 
        
        if '.f[' in self.geo : 
            self.locs=[]
            self.geo = self.geo.split('.f[')[0]
            for e in self.targets:     
                
                bbx = mc.xform(e, q=1, bb=1, ws=1) 
                centerX = (bbx[0] + bbx[3]) / 2.0
                centerY = (bbx[1] + bbx[4]) / 2.0
                centerZ = (bbx[2] + bbx[5]) / 2.0       
                                
                values= k.ba.mesh.closest_face_vtx(self.geo, (centerX,centerY,centerZ)) 
                faceId=values[0] # nearest face
                vtxId=values[1] # nearest vtx
                            
                values2= k.ba.mesh.closest_two_edges(self.geo, faceId, vtxId)    
                closestTwoEdgeIds = values2[0]
                averEdgeLength = values2[1]
                mc.select(self.geo+ '.e['+str(closestTwoEdgeIds[0])+']', self.geo + '.e['+str(closestTwoEdgeIds[1])+']')
                
                loc=k.rig.rivet.run() # apply original rivet script.
                
                locS=averEdgeLength*0.5 # locator scale.
                mc.setAttr(loc+'Shape.localScale', locS,locS,locS)
                
                self.locs.append(loc)
                
                ''' (stop) It can be centered on the surface, but it is impossible to visually determine which side it is attached to with two edges. so just don't.
                # ----- adjust rivet position ---------
                surfInfo=mc.listConnections(loc+'.t',s=1,d=0)[0]
                loft=mc.listConnections(surfInfo+'.inputSurface',s=1,d=0)[0]
                tempSuf=mc.createNode('nurbsSurface')
                mc.connectAttr(loft+'.outputSurface', tempSuf+'.create')
                uv_values=k.ba.surf.closest_uv(tempSuf, (centerX,centerY,centerZ))  
                mc.setAttr(surfInfo+'.parameterU', uv_values[0])
                mc.setAttr(surfInfo+'.parameterV', uv_values[1])
                mc.setAttr(surfInfo+'.turnOnPercentage', 0) # becuase nurbSurface is not normalized(rebuild)
                mc.delete(tempSuf)
                '''
     
            mc.select(self.locs)                
                                    
        else:
            pass        


    #==============================================#
    #   case - attach_selected_targets_on_nurbsSuf
    #==============================================#  
    
    def attach_selected_targets_on_nurbsSuf( self ): 
        print ('method - attach_selected_targets_on_nurbsSuf')         
        self.locs=[]
        for e in self.targets:
            target_pos=mc.xform(e, q=1, ws=1, a=1, piv=1)[:3]
                
            uv_values=k.ba.surf.closest_uv(self.geo, target_pos)
            mc.select(self.geo+'.uv['+ str(uv_values[0]) + '][' + str(uv_values[1]) + ']')
            
            #print stop 
            loc=k.rig.rivet.run()
            self.locs.append(loc)
            
            if self.attrAdd == 0:
                continue                
            # --add uv atrribute  (If u value have both extremes,  orientation is twisted )---                                  
            maxU=mc.getAttr(self.geo+'.mxu')
            maxV=mc.getAttr(self.geo+'.mxv')
            k.ba.fn.add_attrs([loc],['move_u'],['float'],[0],[10],[0]) 
            k.ba.fn.add_attrs([loc],['move_v'],['float'],[0],[10],[0]) 
            geoInfo=mc.listConnections(loc+'.t',s=1,d=0)[0]
            currU=mc.getAttr(geoInfo+'.parameterU')
            currV=mc.getAttr(geoInfo+'.parameterV')
            # 10 : maxU = x : currU >> x = 10 * currU / maxU 
            currMove_u = 10 * currU / maxU
            currMove_v = 10 * currV / maxV
            
            k.ba.fn.sdk(loc+'.move_u',[geoInfo+'.parameterU'],[0,0],[],[10,maxU],0,[['linear','linear'],['linear','linear']],[['spline','spline'],['spline','spline']],[['spline','spline'],['spline','linear']],[['linear','linear'],['constant','linear']])
            k.ba.fn.sdk(loc+'.move_v',[geoInfo+'.parameterV'],[0,0],[],[10,maxV],0,[['linear','linear'],['linear','linear']],[['spline','spline'],['spline','spline']],[['spline','spline'],['spline','linear']],[['linear','linear'],['constant','linear']])  

            mc.setAttr( loc+'.move_u', currMove_u)
            mc.setAttr( loc+'.move_v', currMove_v)
            # ----------------------------------               
        
        mc.select(self.locs)
      


    #==============================================#
    #        case - attach_on_nurbsSuf
    #==============================================# 
    
    def attach_on_nurbsSuf( self ): 
        print ('method - attach_on_nurbsSuf')         

        self.targets=mc.ls(sl=1,fl=1) # select again.
        self.locs=[]
        if '.uv[' in self.geo :    
            surf = self.geo.split('.uv[')[0]
            for e in self.targets:
                mc.select(e)
                loc=k.rig.rivet.run()
                self.locs.append(loc)
                                
                if self.attrAdd == 0:
                    continue
                # --add uv atrribute  (If u value have both extremes,  orientation is twisted )---                                 
                maxU=mc.getAttr(surf+'.mxu')
                maxV=mc.getAttr(surf+'.mxv')
                k.ba.fn.add_attrs([loc],['move_u'],['float'],[0],[10],[0]) 
                k.ba.fn.add_attrs([loc],['move_v'],['float'],[0],[10],[0]) 
                surfInfo=mc.listConnections(loc+'.t',s=1,d=0)[0]
                currU=mc.getAttr(surfInfo+'.parameterU')
                currV=mc.getAttr(surfInfo+'.parameterV')
                # 10 : maxU = x : currU >> x = 10 * currU / maxU 
                currMove_u = 10 * currU / maxU
                currMove_v = 10 * currV / maxV
                
                k.ba.fn.sdk(loc+'.move_u',[surfInfo+'.parameterU'],[0,0],[],[10,maxU],0,[['linear','linear'],['linear','linear']],[['spline','spline'],['spline','spline']],[['spline','spline'],['spline','linear']],[['linear','linear'],['constant','linear']])
                k.ba.fn.sdk(loc+'.move_v',[surfInfo+'.parameterV'],[0,0],[],[10,maxV],0,[['linear','linear'],['linear','linear']],[['spline','spline'],['spline','spline']],[['spline','spline'],['spline','linear']],[['linear','linear'],['constant','linear']])  

                mc.setAttr( loc+'.move_u', currMove_u)
                mc.setAttr( loc+'.move_v', currMove_v)
                # ----------------------------------
   
        if '.cv[' in self.geo :  
            surf = self.geo.split('.cv[')[0]        
            for e in self.targets:
                target_pos=mc.xform(e, q=1, ws=1, a=1, t=1)
                uv_values=k.ba.surf.closest_uv(surf, target_pos)
                mc.select(surf.split('.cv[')[0]+'.uv['+ str(uv_values[0]) + '][' + str(uv_values[1]) + ']')
                loc=k.rig.rivet.run()
                self.locs.append(loc)
                
                if self.attrAdd == 0:
                    continue                
                # --add uv atrribute  (If u value have both extremes,  orientation is twisted )---                                    
                maxU=mc.getAttr(surf+'.mxu')
                maxV=mc.getAttr(surf+'.mxv')
                k.ba.fn.add_attrs([loc],['move_u'],['float'],[0],[10],[0]) 
                k.ba.fn.add_attrs([loc],['move_v'],['float'],[0],[10],[0]) 
                surfInfo=mc.listConnections(loc+'.t',s=1,d=0)[0]
                currU=mc.getAttr(surfInfo+'.parameterU')
                currV=mc.getAttr(surfInfo+'.parameterV')
                # 10 : maxU = x : currU >> x = 10 * currU / maxU 
                currMove_u = 10 * currU / maxU
                currMove_v = 10 * currV / maxV
                
                k.ba.fn.sdk(loc+'.move_u',[surfInfo+'.parameterU'],[0,0],[],[10,maxU],0,[['linear','linear'],['linear','linear']],[['spline','spline'],['spline','spline']],[['spline','spline'],['spline','linear']],[['linear','linear'],['constant','linear']])
                k.ba.fn.sdk(loc+'.move_v',[surfInfo+'.parameterV'],[0,0],[],[10,maxV],0,[['linear','linear'],['linear','linear']],[['spline','spline'],['spline','spline']],[['spline','spline'],['spline','linear']],[['linear','linear'],['constant','linear']])  

                mc.setAttr( loc+'.move_u', currMove_u)
                mc.setAttr( loc+'.move_v', currMove_v)
                # ----------------------------------                
        
        mc.select(self.locs)      



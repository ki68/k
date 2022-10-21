# -*- coding: utf-8 -*-

'''
py2.7 py3.7

** The function can be executed in two types: when an objects are directly selected and when executed by providing parameters.

Rivet Improvements:
The rivet was positioned in the mesh case at the point closest to the face.

Feature Added:
    - cv, face selection enable
    - target objects selection enable
    - to can to add simple nurbsCurve control 

** It is difficult to obtain a standard for adjusting the locator scale on the nurbsSurface side, so no rivet scale adjustment on nurbsSurface is performed 

** rivet on the selected specific mesh don't know where they will be created onto edges. if you want to head rivet to a specific edge, you should use original rivet script.

-------- note --------
- v1.0
22.10.17~10.22 - creation 

'''

import sys
import os 
import maya.cmds as mc
import maya.mel as mel

import k.ba.fn 
import k.ba.mesh 
import k.ba.surf
import k.rig.rivet
import k.rig.rivetk
import k.rig.follicle

# for code feedback
if sys.version_info > (3,7,0): 
    import importlib
    importlib.reload(k.ba.mesh)
    importlib.reload(k.ba.surf)
    importlib.reload(k.rig.rivet)
    importlib.reload(k.rig.rivetk)    
    importlib.reload(k.rig.follicle)    
else :
    import imp
    imp.reload(k.ba.mesh) 
    imp.reload(k.ba.surf) 
    imp.reload(k.rig.rivet) 
    imp.reload(k.rig.rivetk) 
    imp.reload(k.rig.follicle)    


print ('read rivetTool module')

#=======================================================#
#                    attach rivet 
#=======================================================# 
def attach_rivet():
    
    attach = k.rig.rivetk.Attach()
    attach.run()
    
#=======================================================#
#                    attach follicle 
#=======================================================#     
def attach_follicle():
    
    attach = k.rig.follicle.Attach()
    attach.run()
    

#=======================================================#
#             attach rivet(or follicle) with ctrl
#=======================================================# 
'''
- When rivet is on nurbsSurface, move_U, move_V attributes is added at rivet. But they don't connect to control.

- This function combine (Rivet Creation With Ctrl and Follicle Creation With Ctrl). So it was written in rivetTool.main.py, not in follicle.py or rivetk.py.

- Tis function can be used without a UI from the outside.

'''
def attach_with_ctrl(attachType):

    # ====================
    # - Define Variables -
    # ==================== 

    sels=mc.ls(sl=1)
    targets=sels[:-1]
    geo=sels[-1]
    
    # ================
    # - Create Rivet -
    # ================      
    
    attach_class_dic = {'rivet':k.rig.rivetk.Attach, 'follicle':k.rig.follicle.Attach}    

    attach = attach_class_dic[attachType]()
    attach.run()

    attached_objs_dic = {'rivet':'attach.locs', 'follicle':'attach.follicles'}
    
    attachedObjs = eval(attached_objs_dic[attachType])
    geoType = attach.geoType
    targetsNotGeo = attach.targetsNotGeo

    # 1. create a control. and parent it to rivet locator.
    # 2. create parentConsraint : control -> an object 
    # 3. hide locator shape, create all group.
    
    ctrls=[]
  
    for n, e in enumerate(attachedObjs):
    
        # ==================
        # - Create Control -
        # ==================       
    
        ctrl=mc.circle(ch=0,c=(0,0,0),nr=(0,1,0),sw=360,r=1,d=3,ut=0,tol=0.01,s=8)[0]
        ctrlShp = mc.listRelatives(ctrl,s=1,ni=1)[0]
        mc.setAttr(ctrlShp +'.overrideEnabled', 1)
        mc.setAttr(ctrlShp +'.overrideColor', 17)        
                
        mc.parent(ctrl, e) # contorl in locator
        mc.setAttr(ctrl + '.t',0,0,0)
        if attachType == 'follicle':
            rxVal = 90
        else : rxVal = 0
        mc.setAttr(ctrl + '.r',rxVal,0,0)
        
        if targetsNotGeo == False : # if targets are geometries
            mc.parentConstraint(ctrl, targets[n],mo=1)
            mc.scaleConstraint(ctrl, targets[n],mo=1)
        
        # hide shape
        mc.setAttr(mc.listRelatives(e,s=1,ni=1)[0]+'.v', 0)
        
        ctrls.append(ctrl)
              
    # =======================
    # - Control structuring -
    # ======================= 

    if attachedObjs == []:
        return
    
    # create group to contain rivets or follicles
    if not mc.objExists('%sCtrls_grp*' % attachType):            
        rivetFollicleGrp=mc.group(em=1)
        rivetFollicleGrp=mc.rename(rivetFollicleGrp, '%sCtrls_grp' % attachType)
        mc.setAttr(rivetFollicleGrp+'.inheritsTransform', 0)
    else : 
        rivetFollicleGrp = mc.ls('%sCtrls_grp*' % attachType)[0]
    
    # create node to scale rivets or follicles    
    if not mc.objExists('%s_scale_node*' % attachType):            
        scaleGrp=mc.group(em=1)
        scaleGrp=mc.rename(scaleGrp, '%s_scale_node' % attachType)
    else : 
        scaleGrp = mc.ls('%s_scale_node*' % attachType)[0]        
                   
    for e in attachedObjs:
        mc.parent (e, rivetFollicleGrp)
        mc.scaleConstraint(scaleGrp, e, mo=1)
        
        
    mc.select(ctrls)


#=======================================================#
#             attach many follicles on nurbsSurface
#=======================================================#
'''
1. Get max u,v of surface
2. Divide max u, v by uNum, vUnm
3. In loop, create a follicle repeatedly    
** if number has 1, follicle is located at the middle of the max  value.
'''

def attach_many_follicles(uField, vField, uOffsetField, vOffsetField):

    # ------- Get values from ui --------
    uNum = mc.intField(uField, q=1, v=1)
    vNum = mc.intField(vField, q=1, v=1)    
    u_offset = mc.floatField(uOffsetField, q=1, v=1) 
    v_offset = mc.floatField(vOffsetField, q=1, v=1) 
    
    
    k.rig.follicle.create_many_follicles(uNum, vNum, u_offset, v_offset)
    
 
#=======================================================#
#                      toggle CV
#=======================================================#

def toggle_cv():
    mel.eval('toggle -controlVertex;')
    
#=======================================================#
#                      help
#=======================================================#

def help():

    '''
    subToolDirPath = os.path.dirname(__file__)
    subToolDirPath = subToolDirPath.replace('\\','/')
    subToolName = subToolDirPath.split('/')[-1]
    part = subToolDirPath.split('/')[-2]
    kRootPath = '/'.join(subToolDirPath.split('/')[:-2])
    
    path = kRootPath + '/help/' + part + '/' + subToolName + '.'+ ext
    '''
        
    path = 'https://www.youtube.com/watch?v=otN2K1AbbPk'
    os.startfile(path) 
    
    
#=======================================================#
#                      UI
#=======================================================# 

def ui():
    if mc.window('rivetTool_Win', q=1, ex=1):
        mc.deleteUI('rivetTool_Win')
    mc.window('rivetTool_Win',title=u'Rivet Tool')    
    mc.columnLayout( adj=1 )  

    #====================================#
    #            Help Layout
    #====================================#

    mc.rowColumnLayout(nc=2)
    mc.text(l='', w=220)
    mc.symbolButton( image='help.png' ,w=30, bgc=(0.2,0.2,0.2),
    c=lambda x:help(), ann=u'Help')   
    mc.setParent('..')
    
    
    #====================================#
    #             Main Layout
    #====================================#    

    #==========================#
    #    rowColumn Layout 1
    #==========================#  

    mc.rowColumnLayout(nc=2)
    
    # -------------- Rivet -------------   
    
    mc.button( label='Rivet',
    c= lambda x: attach_rivet(),
    bgc=(0,0,0.4),
    w=120, h=60, ann=u'Select cvs or surface points or two edges or faces or temporary objects\n Or select those and (mesh or nurbsSurface)')    
    
    # -------------- Rivet With Control -------------
    
    mc.button( label='Rivet   ( + Control )',
    c= lambda x: attach_with_ctrl('rivet'), 
    w=130, h=60, bgc=(.8,.8,0), ann=u'Select cvs or surface points or two edges or faces or temporary objects\n Or select those and (mesh or nurbsSurface)')

    mc.setParent('..') # rowCol nc=2
    
    #==========================#
    #    rowColumn Layout 2
    #==========================#     
    
    mc.rowColumnLayout(nc=2)
            
    # -------------- Follicle -------------
      
    mc.button( label='Follicle',
    c= lambda x: attach_follicle(), 
    bgc=(0,0,0.4),
    w=120, h=60, ann='Select cvs or surface points or two edges or faces or temporary objects\n Or select those and (mesh or nurbsSurface)')
    
    # -------------- Follicle With Control -------------
    
    mc.button( label='Follicle   ( + Control )',
    c= lambda x: attach_with_ctrl('follicle'), 
    w=130, h=60, bgc=(.8,.8,0), ann=u'Select cvs or surface points or two edges or faces or temporary objects\n Or select those and (mesh or nurbsSurface)')        
    mc.setParent('..') # rowCol nc=2    
    
    
    #==========================#
    #    rowColumn Layout 3
    #==========================#     
    # --------- Many Follicles On NurbSurf --------
    
    mc.rowColumnLayout(nc=12)    

    # ----Front Layout  (U, V, Offset Fields) ---
    
    mc.rowColumnLayout(nc=7)
        
    # -------- Upper Line -------
    
    mc.text(l=' U : ', w=25)
    uField = mc.intField(h=30,w=40, v=0, min=0, ann='This divides maximum u value')
    mc.text(l='EA ', w=20)   
    mc.text(l=' ', w=10)
    mc.text(l='Offset : ', w=40)
    uOffsetField = mc.floatField(h=30,w=50, v=0.0, pre=2,
    ann='- Offset is a percentage of the divided unit u value \n- Offset has a negative number too.')
    mc.text(l='%', w=15)         
    
    # -------- Lower Line -------
    
    mc.text(l=' V : ', w=25)
    vField = mc.intField(h=30,w=40, v=0, min=0, ann='This divides maximum v value')
    mc.text(l='EA ', w=20)        
    mc.text(l=' ', w=10)
    mc.text(l='Offset : ', w=40)
    vOffsetField = mc.floatField(h=30,w=50, v=0.0, pre=2,
    ann='- Offset is a percentage of the divided unit u value \n- Offset has a negative number too.')    
    mc.text(l='%', w=15) 
    
    mc.setParent('..') # rowCol 
    
    # -------- (End) Front Layout --------
        
    mc.text(w=10, l='') # empty space
           
    # ------- CV Button -------
    
    mc.button( label='CV', w=40, c=lambda x:toggle_cv(), bgc=(0,0,0), ann='toggle CV') 
       
    mc.setParent('..') # rowCol 
    
    
    #==========================#
    #    rowColumn Layout 4
    #==========================#       

    mc.columnLayout(adj=1)
    
    mc.button( label='Many Follicles On NurbSurf',
    c= lambda x: attach_many_follicles(uField, vField, uOffsetField, vOffsetField), 
    bgc=(0,0,0.4),
    h=60, ann=u'Put u,v number and offset percentages in fields \nAnd select nurbsSurface')    
    
    mc.setParent('..') # col       

    
    mc.window('rivetTool_Win', e=1, w=240, h=120)
    mc.showWindow('rivetTool_Win')


#=======================================================#
#          run ( executed by rivetTool shelf button )
#=======================================================# 

def run():
    ui()
# -*- coding: utf-8 -*-
# ver 1.0, pyCode_8, 2016.3.7
# py2.7 py3.7

## principle : 
## mesh - edge > convert nurbsCurve > loft > pointOnSuf > locator 
## normal, tangent of face give to aimConstraint node.
## aimConstraint -> locator.rotate 

'''
// Copyright (C) 2000-2001 Michael Bazhutkin - Copyright (C) 2000 studio Klassika
// www.geocites.com/bazhutkin
// bazhutkin@mail.ru
//
//  Rivet (button) 1.0
//  Script File
//  MODIFY THIS AT YOUR OWN RISK
//
//  Creation Date:  April 13, 2001
//
//
//  Description:
//  Use "Rivet" to constrain locator to polygon or NURBS surfaces
//  Select two edges on polygon object
//  or select one point on NURBS surface and call rivet
//  Parent your rivets and buttons to this locator
'''

import maya.cmds as mc

def rivet():

    nameObject=''
    namePOSI='' ## pInfo
    
    parts=[]
    list = mc.filterExpand(sm=32) or []  ## selected edges. ex) pPlane1.e[155]
    # TypeError: object of type 'NoneType' has no len() // so add "or []".
    size = len(list)  
    
    if size > 0:  ## if edges are selected, it is mesh
        
        if size != 2:
            mc.error( "No two edges selected" )
            return ''
        
        parts=list[0].split('.')
        nameObject = parts[0]  ## object name
        
        #  pCube1.e[1]
        e1=list[0].split('[')[1].split(']')[0] ## edge1 index
        e2=list[1].split('[')[1].split(']')[0] ## edge2 index

        
        nameCFME1 = mc.createNode( 'curveFromMeshEdge', n='rivetCurveFromMeshEdge1' ) # quary >> name
         
        ## mc.attributeQuery ('ihi', node='rivetCurveFromMeshEdge1',  ln=1) long name.
        ## mel -> attributeQuery -node rivetCurveFromMeshEdge3  -ln ihi;        
        mc.setAttr ('.ihi' ,1)  ## isHistoricallyInteresting
        mc.setAttr ('.ei[0]' ,int(e1)) ## Available only in integers
        
        nameCFME2 = mc.createNode( 'curveFromMeshEdge', n='rivetCurveFromMeshEdge2' )        
        mc.setAttr ('.ihi' ,1)  
        mc.setAttr ('.ei[0]' ,int(e2)) ## Available only in integers
        
        nameLoft = mc.createNode( 'loft', n='rivetLoft1' )      
        mc.setAttr ('.ic', s=2) ## -size > array  ## inputCuve - array size 2
        mc.setAttr ('.u', 1) ## -uniform
        mc.setAttr ('.rsn', 1) ## -reverseSurfaceNormals 
        ## It doesn't look like the normal attribute of nurbsSurface..        
        ## Anyway .rsn should be turned on by default when lofting manually..

        namePOSI = mc.createNode( 'pointOnSurfaceInfo', n='rivetPointOnSurfaceInfo1' ) 
        mc.setAttr ('.turnOnPercentage', 1) ## maybe regardless of the uv max.
        mc.setAttr ('.parameterU', 0.5) ## center
        mc.setAttr ('.parameterV', 0.5)

        mc.connectAttr( nameLoft+'.os' , namePOSI+'.is' , f=1 ) ## outputSurface -> inputSurface
        mc.connectAttr( nameCFME1+'.oc' , nameLoft+'.ic[0]' , f=1 ) ## outputCurve -> inputCurve[0]
        mc.connectAttr( nameCFME2+'.oc' , nameLoft+'.ic[1]' , f=1 )
        mc.connectAttr( nameObject+'.w' , nameCFME1+'.im' , f=1 ) ## worldmatrix[0] -> inputmesh
        mc.connectAttr( nameObject+'.w' , nameCFME2+'.im' , f=1 )


    
    else: ## if not, it is nurbsSurface.
        list = mc.filterExpand (sm=41) ## selected nurbsSuface uv point
        size = len(list)

        if size > 0:
        
            if size != 1:
                mc.error("No one point selected")
                return ''
                   
            # nurbsPlane1.uv[0.5][0.5]           
            parts=list[0].split('.',1) # Left search, separate once
            nameObject = parts[0]  ## object name
    
            # Left search
            u=list[0].split(']')[0].split('[')[1]  ## edge1 index
            v=list[0].split('][')[1].split(']')[0]  ## edge2 index
            # v = re.findall('\[.*?\]\[(.*?)\]',a)[0] # maybe this is also possible?

            namePOSI = mc.createNode( 'pointOnSurfaceInfo', n='rivetPointOnSurfaceInfo1' ) 

            mc.setAttr ('.turnOnPercentage' ,0)
 
            mc.setAttr ('.parameterU' ,float(u))    
            mc.setAttr ('.parameterV' ,float(v))
            '''
            double type disabled. Must use Decimal module.
            from decimal import Decimal
            x = "0.44444444444444444444445666666666"
            print (Decimal(x))           
            '''  
            mc.connectAttr( nameObject+'.ws' , namePOSI+'.is' , f=1 )     
            ## worldspace[0] -> inputSurface  poly unlike outputSurface
        
        else:
            mc.error("No edges or point selected")
            return ''
        

    pureName = 'rivet'
    rivetName = 'rivet1'
    i=1
    while mc.objExists(rivetName):
        rivetName = pureName+ str(i+1)
        i=i+1
  
   
    nameLocator = mc.createNode( 'transform', n=rivetName ) 
    mc.createNode( 'locator', n=nameLocator+'Shape' ,p=nameLocator )
    ## maybe the locator itself is a shape..

    nameAC = mc.createNode( 'aimConstraint', n=nameLocator+'_rivetAimConstraint1', p=nameLocator ) 
    mc.setAttr ('.tg[0].tw' ,1) ## target.targetWeight
    

    ## Determine the axial orientation of the locator itself
    
    mc.setAttr ('.a' ,0, 1, 0 , type='double3') ## maybe aim vector
    mc.setAttr ('.u' ,0, 0, 1 , type='double3') ## up vector
    
    mc.setAttr ('.tx' , k=0)
    mc.setAttr ('.ty' , k=0)
    mc.setAttr ('.tz' , k=0)
    mc.setAttr ('.rx' , k=0)
    mc.setAttr ('.ry' , k=0)
    mc.setAttr ('.rz' , k=0)
    mc.setAttr ('.sx' , k=0)
    mc.setAttr ('.sy' , k=0)
    mc.setAttr ('.sz' , k=0)
    mc.setAttr ('.v' , k=0)


    mc.connectAttr( namePOSI+'.position' , nameLocator+'.translate' , f=1 ) ## position


    ## Match the normal movement of the NURBS face to the aim constraint target.
    ## Set the flow direction of the plane as the reference coordinates of the upvector
    
    mc.connectAttr( namePOSI+'.n' , nameAC+'.tg[0].tt' , f=1 ) ## normal target[0].targetTranslate
    mc.connectAttr( namePOSI+'.tv' , nameAC+'.wu' , f=1 )   ## tangentV worldUpVector
    mc.connectAttr( nameAC+'.crx' , nameLocator+'.rx' , f=1 ) ## constraintRotateZ
    mc.connectAttr( nameAC+'.cry' , nameLocator+'.ry' , f=1 )
    mc.connectAttr( nameAC+'.crz' , nameLocator+'.rz' , f=1 )
    
    mc.select (nameLocator,r=1)
    return nameLocator


def run():
    return rivet()
    
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
import time 


#print ('read fn module')

#=======================================================#
#               create_new_transform
#=======================================================#    
# work_time = WorkTime()
# work_time.s()
# work_time.e()

class WorkTime():
    def __init__(self):
        self.worktime_start = 0
        self.worktime_end = 0

    def s(self):
        # Measurement Start
        self.worktime_start = time.time()
        
    def e(self, type = 2):
        # Measurement Complete
        self.worktime_end = time.time()
        
        if type == 1:        
            WorkTime = int(self.worktime_end - self.worktime_start)
        elif type == 2:
            WorkTime = float(self.worktime_end - self.worktime_start)
            
        WorkTimeStr = '------ Work time ------ Data\n\n'
        if WorkTime >= 60:
            WorkTimeStr = str(WorkTime // 60) + ' minutes ' + str(WorkTime % 60) + ' seconds .'
        else:
            WorkTimeStr = str(WorkTime) + ' seconds.'
        stdout.write('Work Time : ' + str(WorkTimeStr))   

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
# 'non' in the mins and maxs means undefined.
def add_attrs(objs, attrs, ats, mins, maxs, dvs, IsString='no', enumVals=[]): 
    
    objAttrs=[]
    
    for n, obj in enumerate(objs):
    
        if mc.attributeQuery(attrs[n], node = obj, ex = 1):  # if not exist, add None
            objAttrs.append(None)
            continue
    
        if IsString == 'no':
                
            if ats[n] != 'enum':
                if maxs[n]=='non' and mins[n]!='non': 
                    mc.addAttr(obj, ln=attrs[n], at=ats[n], min=mins[n], dv=dvs[n])
                    
                elif mins[n]=='non'and maxs[n]!='non': 
                    mc.addAttr(obj, ln=attrs[n], at=ats[n], max=maxs[n], dv=dvs[n])
                    
                elif mins[n]=='non'and maxs[n]=='non': 
                    mc.addAttr(obj, ln=attrs[n], at=ats[n],dv=dvs[n])
                    
                else: 
                    mc.addAttr(obj, ln=attrs[n], at=ats[n], min=mins[n], max=maxs[n], dv=dvs[n])
                             
            else : 
                mc.addAttr(obj, ln=attrs[n], at=ats[n], en=enumVals[n])               
            
            mc.setAttr(obj+'.'+attrs[n],k=1) 
            
        else:
            mc.addAttr(obj, ln = attrs[n], dt = 'string')        
            mc.setAttr(obj + '.' + attrs[n], dvs[n], type = 'string') 
            
        objAttrs.append(obj + '.' + attrs[n])
        
    return objAttrs
    
# simple version for string type    
def add_attrs_str(objs, attrs, values):
   
    objAttrs=[]
    
    for n, obj in enumerate(objs):
    
        if mc.attributeQuery(attrs[n], node = obj, ex = 1):  # if not exist, add None
            objAttrs.append(None)
            continue

        else :
            mc.addAttr(obj, ln = attrs[n], dt = 'string')        
            mc.setAttr(obj + '.' + attrs[n], values[n], type = 'string') 
            objAttrs.append(obj + '.' + attrs[n])
   
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
# ex) grp('joint1', 2)
# return value : ['joint1_grp', 'joint1_grp_grp']
# ex) grp(['joint1', 'joint2'], 2)
# return value : ['joint1_grp', 'joint2_grp', 'joint1_grp_grp', 'joint2_grp_grp']

# 풀네임 경우 (동일이름이 있는 경우든 아니든 풀네임이면) 에러남. 계층구조가 바뀌기에 담아놓았던 변수의 풀네임이 없다고 에러가 남.
# 풀네임은 고려 안함. 나후 고려한다면 계층구조가 바뀌기전 메세지 연결을 해서 바껴도 원하는 오브젝트를 찾을 수 있게

def grp( sels, repeat = 1, suffix = 'grp' ):  
    
    not_list = 0
    if not isinstance(sels, list): 
        not_list = 1
        sels = [sels]
    
    final_grp_list = []
    for n in range(repeat):
        sels_new_for_repeat = [] 
        i = 0
        for sel in sels:
        
            if mc.objExists(sel) == 'joint': # 기존 미러 스크립트 등이 제대로 안되는 것 같아 새로운 방식으로 

                parent = mc.listRelatives(sel, p = 1, f = 1)
                grp = mc.group(em=1)
                grp = mc.rename(grp, sel + '_' + suffix)
                mc.parent(grp, sel)
                mc.setAttr(grp + '.t', 0, 0, 0)
                mc.setAttr(grp + '.r', 0, 0, 0)
                mc.setAttr(grp + '.s', 1, 1, 1)

                if parent :
                    mc.parent(grp, parent[0])
                else : mc.parent(grp, w=1) 
                
                mc.parent(sel, grp) # child is selected..
                grp_name = mc.listRelatives(p = 1, path = 1)[0] # grp full name
    
                mc.makeIdentity(sel, apply=1, t=0, r=1, s=0, n=0)
                
            else : # ksCleanTransOfTrans.mel 그대로 
                
                aPos = mc.xform(sel, q=1, ws=1, a=1, piv=1)
                grp = mc.group(sel)
                grp = mc.rename(grp, sel + '_' + suffix)
                mc.move(aPos[0], aPos[1], aPos[2], (grp + '.scalePivot'), (grp + '.rotatePivot'))

                tempTrans_a = mc.xform(sel, ws=1 ,q=1, a=1, piv=1)
                tempRotate = mc.xform(sel, q=1, ro=1)

                mc.xform(sel, t=(0,0,0))
                tempTrans_2a = mc.xform(sel, ws=1, q=1, a=1, piv=1)

                dis=[]
                dis.append(tempTrans_2a[0] - tempTrans_a[0])
                dis.append(tempTrans_2a[1] - tempTrans_a[1])
                dis.append(tempTrans_2a[2] - tempTrans_a[2])

                tempTrans = mc.xform(sel, q=1, ws=1, a=1, piv=1)
                mc.move(tempTrans[0], tempTrans[1], tempTrans[2], (sel + '_' + suffix + '.scalePivot'), (sel + '_' + suffix + '.rotatePivot'))

                mc.move( -1*dis[0], -1*dis[1], -1*dis[2], sel + '_' + suffix, r=1)
                mc.xform(sel, ro=(0,0,0))

                mc.xform(sel + '_' + suffix, ro=(tempRotate[0], tempRotate[1], tempRotate[2]))
                
                grp_name = grp
                mc.select(sel, r=1)     
        

            sels_new_for_repeat.append(grp_name)
            final_grp_list.append(grp_name)
            
            i = i + 1
        sels = sels_new_for_repeat  

    if not_list == 1 and repeat == 1:
        final_grp_list = final_grp_list[0]
        
        
    return final_grp_list  

#====================================
#            parent_shape
#==================================== 
def parent_shape(sels):

    n = len(sels)
    shapeNamesList = []
    
    for sel in sels : 
        if sel != sels[-1] : 

            ## 아마 자식될 컨트롤과 부모의 공간이 달라 컨트롤을 부모에 먼저 종속(parent)시킨다. 
            # case : have parent
            if mc.listRelatives(sel, p=1) != None: 
            
                # 그 부모가 마지막 선택한 오브젝트라면
                if mc.listRelatives(sel, p=1)[0] == sels[-1]: 
                    #sel = mc.parent (sel, sels[-1])[0] ## 이미 패런트되어 있어, 경고창이 뜨고 오작동해서 생략.
                    ## 쉐입을 복사하기전 형태변형(이동,회전,스케일의 변화)을 막기 위해 freeze
                    mc.makeIdentity( sel, apply=True, t=1, r=1, s=1 )                            
                    shps = mc.listRelatives( sel, typ='shape',f=1, ad=1 )  ## 쉐입들을 찾아 담는다       
                    shapeNames = mc.parent (shps,  sels[-1],add=1 , s=1) ## 쉐입만 복사시킨다.
                    shapeNamesList.extend(shapeNames)
                    mc.delete (sel) ## 마지막으로 원본 컨트롤은 지운다.
                    
                else : # 그 부모가 마지막 선택한 오브젝트가 아닌 경우, 패런트한다.
                    sel = mc.parent (sel, sels[-1])[0] 
                    mc.makeIdentity( sel, apply=True, t=1, r=1, s=1 )
                    shps = mc.listRelatives( sel, typ='shape',f=1, ad=1 )        
                    shapeNames = mc.parent (shps,  sels[-1],add=1 , s=1) 
                    shapeNamesList.extend(shapeNames)
                    mc.delete (sel)                  
      
            # case : world
            elif mc.listRelatives(sel,p=1) == None:            
                    ## 이미 패런트되어 있는 경우, 경고창이 떠 에러가 나는 경우가 있다. 
                    sel = mc.parent (sel,  sels[-1])[0] 
                    mc.makeIdentity( sel, apply=True, t=1, r=1, s=1 )
                    shps = mc.listRelatives( sel, typ='shape',f=1, ad=1 )       
                    shapeNames = mc.parent (shps,  sels[-1],add=1 , s=1) 
                    shapeNamesList.extend(shapeNames)
                    mc.delete (sel) 
                    
    return shapeNamesList 
    
#=======================================================#
#               create_new_transform
#=======================================================# 
def create_tr(node_name, parent=None):
    node = mc.createNode('transform', p=parent)
    return mc.rename(node, node_name)    
    
  
#=======================================================#
#            multi_cst ( 기존 기본모듈의 v2 버전임)
#=======================================================# 
'''
# multi_cst('L_Frt_foot_ctrl',
    'follow', 
    ['Chest', 'Root', 'All', 'World'],
    ['chest_ctrl','root_ctrl','all_ctrl','world_Node'],
    parentNullGrp,
    'pa',
    default_index = 2)

# direct는 직접적. base 자체에 걸지 그 상위에 그룹을 씌워 걸지.
'''
def multi_cst(ctrl,
            attrName,
            enumAttrs, 
            targets, 
            base, 
            cstType, 
            default_index = 0, 
            direct = 0, 
            mirror = 0, 
            cstDetailType = 'both', 
            baseGrp_suffix = 'csted_grp'):
    
    suffix = {'po':'po_cster', 'ori':'ori_cster', 'pa':'pa_cster'}
    suffix[cstType]
    
    csts=[]
    for n, e in enumerate(targets):
        cst = mc.duplicate(base, st=1, po=1)[0]
        cst = mc.rename(cst, base + '_by_' + e + '_' + suffix[cstType])
        csts.append(cst)
        mc.parent(cst,e)

    if direct == 0: # direct=1는 직접적. base 자체에 걸지 그 상위에 그룹을 씌워 걸지.                
    
        if not mc.listRelatives(base, p=1): # 상위그룹이 없다면 하나 만듬.
            grp(base)
    
        if not 'csted_grp' == mc.listRelatives(base, p=1)[0][-9:]:
            if mirror == 0:
                #baseCsted = Grping_BA([base], 1, baseGrp_suffix)[0]
                baseCsted = grp(base, suffix = baseGrp_suffix)
    
            elif mirror == 1: 
                #mc.select(base)
                #Grp2_BA(baseGrp_suffix) # 현재 선택된 것을 그루핑해 그룹에 첨미어를 _와 함께 붙여서 반환.
                grp(base, suffix = baseGrp_suffix)
                baseCsted = mc.listRelatives(base, p=1)[0]
                     
        else : baseCsted = mc.listRelatives(base, p=1)[0]
    else : baseCsted = base
    
    if cstType == 'po':
        constraint = mc.pointConstraint(csts, baseCsted, mo=1)[0]
        
    elif cstType == 'ori':
        constraint = mc.orientConstraint(csts, baseCsted, mo=1)[0]
        
    elif cstType == 'pa':
        if cstDetailType == 'both':
            constraint=mc.parentConstraint(csts,baseCsted,mo=1)[0]
            
        elif cstDetailType == 'onlyT':
            constraint=mc.parentConstraint(csts,baseCsted,mo=1, sr=['x','y','z'])[0]
            
        elif cstDetailType == 'onlyR':
            constraint=mc.parentConstraint(csts,baseCsted,mo=1, st=['x','y','z'])[0]

    add_attrs([ctrl],
        [attrName],
        ['enum'],
        [0],
        [1],
        [0],
        IsString = 'no',
        enumVals = [':'.join(enumAttrs)] )
    
    driver = ctrl + '.' + attrName
    drivens = []
    
    for n, e in enumerate(csts):
        drivens.append(constraint + '.w' + str(n)) # [poCst+'.w0', poCst+'.w1', poCst+'.w2']
    drivens_Set = set(drivens)

    for n, e in enumerate(csts):
        # 해당 driver값 설정
        mc.setAttr(ctrl + '.' + attrName, n)
        # 해당 drive값 설정 weight1 
        mc.setAttr(constraint + '.w' + str(n), 1)
        
        # 나머지 weight 0
        drivenOn_Set = set([constraint + '.w' + str(n)])
        drivenOffs = list(drivens_Set.difference(drivenOn_Set))
        
        for e2 in drivenOffs:
            mc.setAttr(e2, 0)
            
        mc.setDrivenKeyframe(drivens, currentDriver = driver)
        
    mc.setAttr(ctrl+'.'+attrName, default_index)
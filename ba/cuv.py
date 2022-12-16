# -*- coding: utf-8 -*-

'''
def ____Comment____():pass
# by kim sung rock

py2.7/3.7
'''

def ______Import_Module_________():pass

# -------- python ---------

import sys 

# -------- maya ---------

import maya.cmds as mc
import maya.api.OpenMaya as om2

# -------- custom ---------
  
modules = [
    'k.ba.fn',
    ]

for e in modules:
    if isinstance(e, tuple):
        str_='''
import %s as %s
if sys.version_info > (3,7,0): 
    import importlib
    importlib.reload(%s)
else :
    import imp
    imp.reload(%s)
''' % (e[0], e[1], e[1], e[1])

    else :
        str_='''
import %s
if sys.version_info > (3,7,0): 
    import importlib
    importlib.reload(%s)
else :
    import imp
    imp.reload(%s)
''' % (e, e, e)
    
    exec(str_)


print ('read cuv module')


#====================================
#               Curve
#====================================
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
        


# ========================================
#     get_crossed_points_on_cuv 
# ========================================
'''
======= 중간값 parameter 설정을 통한 커브와 직선 근사값 구하기 =======

- 개선할 사항 : 로컬 계산을 벡터계산으로 바꿈

- 만약 오브젝트의 축 연장선에 걸리는 점들이 무수히 많을 경우에는
등분수대로 다 나옴. 오류라고도 볼 수 있는데 사용자가 가려서 하면 될듯.

- 초기 구상 : 처음 타겟오브젝트와 min, max와의 (거리차) 비교로 근사값을 구하려 했으나 곡선 parameter의 특성으로
원하는 위치의 근사값이 안 나옴. 그래서 타겟오브젝트의 (앞뒤) 비교를 통해 구함.

- 추가 구상 : 월드축 x,y,z 방향 외 사선 방향으로도 되기 위해 타겟오브젝트의 방위를 이용.
그러기 위해 로컬방향으로 상대적 차이를 계산. 타겟오브젝트보다 앞에 있느냐, 뒤에 있느냐.
orientConstraint를 이용하고. min, max, half간 한 축으로 위치차이를 이용. 

-------------- Execution Code -------------------

# ~~ caution ~~ 
# 1. first function parameter : 
# Axis orthogonal to the direction to cross
# 2. second function parameter : sampling_division

pos_list = get_crossed_points_on_cuv('z', 5)[0]  

if pos_list:
        
    intersecton_objs = []
    
    for e in pos_list:
        mc.select( cl = 1 )
        intersecton_objs.append( mc.spaceLocator()[0] )
        mc.xform( t = e ) 
        
    mc.select(intersecton_objs)
        
------------------------------------------------        
'''
# select object 1 and curve 1.

def get_crossed_points_on_cuv(axis, sampling_division=5, loopNum = 20):

    sels = mc.ls(sl=1)
    
    # ----------- selection check ----------
    
    if not len(sels) == 2 : 
        mc.warning('Select 1 object and 1 curve !!')
        return None
        
    obj = sels[0]
    cuv = sels[1]
    
    if not mc.listRelatives(cuv, s=1, ni=1):
        mc.warning('Second selection should be nurCurve type object !!')
        return None
        
    else : 
        shp = mc.listRelatives(cuv, s=1, ni=1)[0] 
        if not mc.nodeType(shp) == 'nurbsCurve':
            mc.warning('Second selection should be nurCurve type object !!')
            return None   
    
    # ------ temp grps for local space --------
    
    xformTemp = mc.group(em=1,n='xformTemp') # half
    mc.delete(mc.orientConstraint(obj, xformTemp))
    mc.parent(xformTemp, obj)

    xformTemp2 = mc.group(em=1,n='xformTemp2') # min
    mc.delete(mc.orientConstraint(obj, xformTemp2))
    xformTemp3 = mc.group(em=1,n='xformTemp3') # max
    mc.delete(mc.orientConstraint(obj, xformTemp3))    
    mc.parent(xformTemp3, xformTemp2)    
    
    # To use curve parameter-position
    
    mSel = om2.MSelectionList()
    mSel.add(cuv)
    fnCuv = om2.MFnNurbsCurve(mSel.getDagPath(0))     
        
    # Proceed in equal parts ..(dividen by sampling number)
    
    maxU = mc.getAttr(cuv+'.max')
    values_list = []
    
    for i in range(sampling_division):    
    
        unit_para = maxU / float(sampling_division)
        
        values = get_crossed_points_on_cuv_per_unit( 
            unit_para*(i), 
            unit_para*(i+1),
            obj,
            fnCuv,
            axis,
            xformTemp,
            xformTemp2,
            xformTemp3,
            loopNum
            )
            
        values_list.append(values) # (parameter, MPoint)
        print (values) # 샘플링 수대로.

    # positions except things with None
    pos_list = []    
    para_list = []
    for e in values_list :    
        if not isinstance(e[1], om2.MPoint): # Excluding the None type
            continue        
        pos = fnCuv.getPointAtParam(e[0], space=om2.MSpace.kWorld)
        pos_list.append((pos[0], pos[1], pos[2]))
        para_list.append(e[0])

    mc.delete(xformTemp, xformTemp2)
   
    return pos_list, para_list 

    
# ========================================
#    get_crossed_points_on_cuv_per_unit 
# ========================================    

def get_crossed_points_on_cuv_per_unit(
    min, 
    max, 
    targetObj, 
    fnCuv, 
    axis, 
    xformTemp, 
    xformTemp2, 
    xformTemp3, 
    loopNum ):

    # ------------ min, max ( local space ) -------------------------    
    # - for 열린 커브에서 or 샘플링을 위해 등분할때도 효과 있는.
    # 하지만 등분해 찾는 경우 해당 단위범위안에 없는 경우 등분 끝에 걸림
    # - 최종 축 길이차를 비교해 0에 너무 동떨어져 있는 경우 제외하는 식으로.
    
    min_mPos = fnCuv.getPointAtParam(min, space = om2.MSpace.kWorld)
    max_mPos = fnCuv.getPointAtParam(max, space = om2.MSpace.kWorld)
    
    # set min, max position & get local trnaslate in one axis
    mc.xform(xformTemp2, ws=1, t = ( min_mPos[0], min_mPos[1], min_mPos[2]) )
    mc.xform(xformTemp3, ws=1, t = ( max_mPos[0], max_mPos[1], max_mPos[2]) )    
    max_local_one_axis_t = mc.getAttr(xformTemp3 + '.t' + axis)
    
    # -----------------------------------------
    
    # 문제점은 열린 커브에서 2개점이 있다면 파라미터 가운데와 가까운 점쪽을 찾음.
    # 해결법은 범위를 좁혀 찾는다 ( 샘플링 )
    for x in range(loopNum):
        
        # parameter mid.
        half = (max - min) / 2.0 + min
        
        # set half position & get local trnaslate in one axis ( half )
        mPos = fnCuv.getPointAtParam( half, space = om2.MSpace.kWorld )
        mc.xform( xformTemp, ws=1, t = (mPos[0],mPos[1],mPos[2]) )
        local_one_axis_t = mc.getAttr( xformTemp + '.t' + axis )        
        
        # 좌편으로 붙일 경우 if와 elif의 부등호를 바꿔줌.
        # 열린 커브도 부등호의 방향에 따라 2가지 점을 얻을 수 있겠다. (2개가 걸린다면)
        if max_local_one_axis_t < 0 :
        
            # Is it in front of or behind the target object..
            if local_one_axis_t < 0 : 
                max = half 
                
            elif local_one_axis_t >= 0 : 
                min = half
       
        else :    
        
            if local_one_axis_t > 0 : 
                max = half 
                
            elif local_one_axis_t <= 0 : 
                min = half
    
    # - 등분된 단위 파라미터 끝에 걸리거나 근사된 값이 0.0001보다 큰 경우를 제외하기 위해.
    # - 두 경우를 따로 구분 안했음.
    if abs(local_one_axis_t) > 0.0001: 
        mPos = None  # set to None to exclude later  
    
    return half, mPos # approximation parameter, the postion
    

# ========================================
#     get_crossed_points_on_cuv  ( Orthogonal to world axis )
# ========================================
'''
-------------- Execution Code -------------------

# ~~ caution ~~ 
# 1. first function parameter : 
# Axis orthogonal to the direction to cross
# 2. second function parameter : sampling_division

pos_list = get_crossed_points_on_cuv_nonOblique('z', 5)[0]

if pos_list:
        
    intersecton_objs = []
    
    for e in pos_list:
        mc.select( cl = 1 )
        intersecton_objs.append( mc.spaceLocator()[0] )
        mc.xform( t = e ) 
        
    mc.select(intersecton_objs)

------------------------------------------------ 
'''

def get_crossed_points_on_cuv_nonOblique(axis, sampling_division=5, loopNum = 20):

    sels = mc.ls(sl=1)
    
    # ----------- selection check ----------
    
    if not len(sels) == 2 : 
        mc.warning('Select 1 object and 1 curve !!')
        return None
        
    obj = sels[0]
    cuv = sels[1]
    
    if not mc.listRelatives(cuv, s=1, ni=1):
        mc.warning('Second selection should be nurCurve type object !!')
        return None
        
    else : 
        shp = mc.listRelatives(cuv, s=1, ni=1)[0] 
        if not mc.nodeType(shp) == 'nurbsCurve':
            mc.warning('Second selection should be nurCurve type object !!')
            return None    
    
    # To use curve parameter-position
    
    mSel = om2.MSelectionList()
    mSel.add(cuv)
    fnCuv = om2.MFnNurbsCurve(mSel.getDagPath(0))     
    
    # Proceed in equal parts ..(dividen by sampling number)
    
    maxU = mc.getAttr(cuv+'.max')
    values_list = []
    for i in range(sampling_division):
        unit_para = maxU/float(sampling_division)
        values = get_crossed_points_on_cuv_nonOblique_per_unit( 
            unit_para*(i), 
            unit_para*(i+1),
            obj,
            fnCuv,
            axis,
            loopNum
            )
            
        values_list.append(values) # (parameter, MPoint)
        print (values) # 샘플링 수대로.
    
    # positions except things with None
    pos_list = []
    para_list = []
    for e in values_list :
        if not isinstance(e[1], om2.MPoint): continue
        pos = fnCuv.getPointAtParam(e[0], space=om2.MSpace.kWorld)
        pos_list.append((pos[0], pos[1], pos[2]))
        para_list.append(e[0])
        
    return pos_list, para_list 
    
# ==================================================
#    get_crossed_points_on_cuv_nonOblique_per_unit ( Orthogonal to world axis )
# ==================================================     

def get_crossed_points_on_cuv_nonOblique_per_unit(
    min, 
    max, 
    targetObj, 
    fnCuv, 
    axis, 
    loopNum ):
    
    # 한 축으로 위치차 계산     
    index = {'x':0, 'y':1, 'z':2}    
    tar_pos = mc.xform(targetObj, q=1, ws=1, t=1) # 타겟을 절대위치값.
    tar_tz = tar_pos[ index[axis] ]
    
    # -------------- min, max ( world space ) ----------------------    
    # - for 열린 커브에서 or 샘플링을 위해 등분할때도 효과 있는.
    # 하지만 등분해 찾는 경우 해당 단위범위안에 없는 경우 등분 끝에 걸림
    # - 최종 축 길이차를 비교해 0에 너무 동떨어져 있는 경우 제외하는 식으로.
    
    min_z = fnCuv.getPointAtParam(min, space=om2.MSpace.kWorld)[index[axis]]
    max_z = fnCuv.getPointAtParam(max, space=om2.MSpace.kWorld)[index[axis]]
    # max_z - min_z 으로 해서 if < 0, elif > == 0 으로도 할 순 있겠음.
    
    # -----------------------------------------
    
    # 문제점은 열린 커브에서 2개점이 있다면 파라미터 가운데와 가까운 점쪽을 찾음.
    # 해결법은 범위를 좁혀 찾는다 ( 샘플링 )
    for x in range(loopNum):
        
        # parameter mid.
        half = (max - min) / 2.0 + min
        
        # get world trnaslate in one axis ( half )
        world_one_axis_t = fnCuv.getPointAtParam(half, space=om2.MSpace.kWorld)[index[axis]]
                
        # 좌편으로 붙일 경우 if와 elif의 부등호를 바꿔줌.
        # 열린 커브도 부등호의 방향에 따라 2가지 점을 얻을 수 있겠다. (2개가 걸린다면)
        if min_z < max_z :
        
            if tar_tz < world_one_axis_t : 
                max = half 
                
            elif tar_tz >= world_one_axis_t : 
                min = half

        else :
        
            if tar_tz > world_one_axis_t : 
                max = half 

            elif tar_tz <= world_one_axis_t : 
                min = half
        
    mPos = fnCuv.getPointAtParam(half, space=om2.MSpace.kWorld)
    
    # - 등분된 단위 파라미터 끝에 걸리거나 근사된 값이 0.0001보다 큰 경우를 제외하기 위해.
    # - 두 경우를 구분 안했음.
    if abs(tar_tz - mPos[index[axis]]) > 0.0001: 
        mPos = None # set to None to exclude later 
    
    return half, mPos # approximation parameter, the postion    
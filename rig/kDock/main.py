# -*- coding: utf-8 -*-

'''
py2.7 py3.7
/////////////////////////////////////////////////
//                 kDock  Info                   
/////////////////////////////////////////////////

This script is for personal use only

'''

'''
openDir 우클릭 첫 메뉴아이템은 현재 파일의 경로에 해당하는 파일목록들을 취합해 창을 띄움. 혹은 fileDialog창을 원하는 경로로 띄울수 있다면 그게 간편 나을듯.
이하 경로 메뉴아이템들은 선택 경로파일의 경로에 해당하는 파일목록들을 취합해 창을 띄움. 혹은 fileDialog창을 원하는 경로로 띄울수 있다면 그게 간편 나을듯.

import/ export도 마찬가지... 경로를 따로 저장을 해야 될듯... 그리고 위에처럼 그 파일경로의 파일들을 취합해 창을 띄울지, fileDialog로 띄울지 결정 
reference도 있었으면 하는데 ... 경로를 따로 저장을 해야 될듯... 그리고 위에처럼 그 파일경로의 파일들을 취합해 창을 띄울지, fileDialog로 띄울지 결정 
reference는 import 개념이랑 import쪽이랑 취합할지 결정. 
'''

import maya.cmds as mc
import subprocess
from sys import stdout
from functools import partial
import os, re
from os.path import isfile, join, isdir # 그냥 join이랑 겹치지 않는지 궁금.

# -------- kFaceTool dock에 넓어진 dock 너비를 좁히기 위해 필요 -------
from maya import OpenMayaUI
from shiboken2 import wrapInstance     
from PySide2 import QtCore 


# KimstoolRoot_Ki, BasicFuncsRoot_Ki 는 마야 띄울때 킴스툴 실행될때 정의된듯.

KimstoolRoot_Ki = "C:/kimstools"
BasicFuncsRoot_Ki = "W:/ref/Eyescream_Module/basic_functions"

with open(KimstoolRoot_Ki+"/library/scripts_py/SoulPalette.py", "rb") as f:
    exec(f.read(),globals())
 
# -------- ui에 의해  
def update_recent_opened_files():


    if mc.popupMenu('openDir_pM_dockKSR',q=1,ex=1):       
        items=mc.popupMenu('openDir_pM_dockKSR',q=1,ia=1)
        if items:
            mc.deleteUI(items) 
    
        filePath = mc.file(q=1, sn=1)
        if not filePath == '':        
            fileName = filePath.split('/')[-1]
            CurrentFilePath = filePath.split(fileName)[0]
            mc.menuItem(p='openDir_pM_dockKSR', l='--- Current File Dir Win ---', c=partial(Float_CurrentFileListWin_dockKSR, CurrentFilePath) )
        recentFiles=mc.optionVar(q='RecentFilesList')
        
        # 마야가 크래쉬되거나 설정파일이 초기화되면 값이 리스트가 아니라 0인 int로 반환됨
        if type(recentFiles) != int : # 'int' 아님 주의.
            recentFiles=list(reversed(recentFiles))
            for e in recentFiles:
                mc.menuItem(p='openDir_pM_dockKSR', l=e, c=partial(Open_File_dockKSR, e))
                mc.menuItem(p='openDir_pM_dockKSR', ob=1, c=partial(Float_CurrentFileListWin_dockKSR, e))   


def save_as_to_current_location():
    full_sn = mc.file( q=1, sn=1 )
    full_sn_split = full_sn.split( '/' )
    path = full_sn.replace( full_sn_split[-1], '' )
    multipleFilters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)"
    new_file_name = mc.fileDialog2( startingDirectory=path, fileFilter=multipleFilters )

    if new_file_name:
        #rename scene to new_file_name
        full_sn = mc.file( rename=new_file_name[0] )
     
        #save scene
        mc.file( save = 1 )

        stdout.write(new_file_name[0]+ ' is saved. ')
        
 
# exec(f.read(),globals()) 의 global이 아마 ui 버튼을 통해 모듈안 함수 실행될 경우 적어줘야 하는듯. 그렇지 않으면 못찾음. 
def load_ES_Daz_Rig_Tool_dockKSR():
    with open(BasicFuncsRoot_Ki.split('/basic_functions')[0] + "/app/Rig/ES_Daz_Rig_Tool/ES_Daz_Rig_Tool.py", "rb") as f: exec(f.read(),globals())

def load_Pan_dockKSR():
    mel.eval('source "'+ KimstoolRoot_Ki +'/library/scripts/ksPAN.mel";') 


def load_MatchPoint_dockKSR():
    with open(BasicFuncsRoot_Ki + "/ksMatchPoint.py", "rb") as f: exec(f.read(),globals());matchPoint_ui()

def load_SimShpEditor_dockKSR():
    with open(BasicFuncsRoot_Ki.split('/basic_functions')[0] + "/app/Rig/SR_Blend_Edit_Tool/SR_Blend_Edit_Tool.py", "rb") as f: exec(f.read(),globals());SR_Blend_Edit_Tool() 

def open_PoseEditor_dockKSR():
    # 리로드가 안되 창을 삭제후 다시 띄움.
    for e in mc.lsUI(type='window'):
        if 'posePanel' in e:
            mc.deleteUI(e)
    mel.eval("PoseEditor;")

def TextureMode_dockKSR():
    currentPanel = mc.getPanel(withFocus=1)
    panelType = mc.getPanel(to=currentPanel)
    if panelType == 'modelPanel':
        val=mc.modelEditor(currentPanel, q=1,displayTextures=1)
        if val == 1:
            mc.modelEditor(currentPanel, e=1,displayTextures=0, displayAppearance='smoothShaded')
        else:
            mc.modelEditor(currentPanel, e=1,displayTextures=1, displayAppearance='smoothShaded')
            
#=============================================================================#
#                       p. Get Files From Path
#=============================================================================# 
import locale     
def Get_Files_From_Path_dockKSR(path,exts):
    files_=[]  
    if isdir(path): 
        files=[f for f in os.listdir(path) if isfile(join(path,f))]    
        for e in files :
            for ext in exts:
                if '.'+ext in e: # 해당 확장자파일만 추출 
                    files_.append(e)  # 바로 files에 담으면 루프걸림.
                
    files_.sort() # 기본적으로 알파벳순으로 정렬. 
    #files_.sort(key = len) # 길이정렬. 01 02 010 순으로 정렬되지만 길이가 같은 앞부분이 다른 파일까지도 껴들어 오류 발생.
    #print files_
    #files_.sort(key=str.lower) #  ['aa_01', 'aa_010', 'aa_11', 'aa_2', 'bb_01', 'c_1'] 이런식으로됨. 그리고 파일이름이 한글이 되어있을 경우. str.lower    
    # 는 TypeError: descriptor 'lower' requires a 'str' object but received a 'unicode' # 에러남.
    # 인터넷에 찾아보니 밑에 식으로 하란다. 하지만 이렇게 하면 유니코드 에러는 비할 수 있지만 원하는 정렬결과는 안됨.
    #files_.sort(key=unicode.lower) # . 01 010 02 이렇게 됨.
    '''
    import locale
    locale.setlocale(locale.LC_ALL, '')
    list.sort(cmp=locale.strcoll)
    '''
    #locale.setlocale(locale.LC_ALL, '')
    #files_.sort(cmp=locale.strcoll)

    return files_            
            
def Float_CurrentFileListWin_dockKSR(file,  *args):
    path='/'.join(file.split('/')[:-1])
    multipleFilters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
    files=mc.fileDialog2(startingDirectory = path, fileFilter=multipleFilters, cap='Open', okc='Open',fileMode=1)
    
    if files:
        Open_File_dockKSR(files[0])
    
    
''' 목록창을 새로 만드는 것보다 파일다이얼로그를 활용하는게 나은듯. 
    if mc.window('CurrentFileListWin_dockKSR_Win', q=1, ex=1):
        mc.deleteUI('CurrentFileListWin_dockKSR_Win')
    mc.window('CurrentFileListWin_dockKSR_Win',title=u'')
    mc.columnLayout(adj=1)
       
    mc.text('tT_path_dockKSR', l='files', h=20,bgc=(0,0,0))

    mc.textScrollList('tSF_CurrentFileListWin_dockKSR', w=800, ams=0 ,fn='fixedWidthFont',dcc='Open_Folder_dockKSR()')
        
    path='/'.join(file.split('/')[:-1])
    files= Get_Files_From_Path_dockKSR(path,['ma'])
    files.extend(Get_Files_From_Path_dockKSR(path,['mb']))
    files.sort()
    for e in files:
        mc.textScrollList('tSF_CurrentFileListWin_dockKSR', e=1, append=e)
        
    heightV = len(files) * 15 + 50
    
    mc.textScrollList('tSF_CurrentFileListWin_dockKSR', e=1, h=heightV)
 
    #mc.popupMenu( button=0 )
    #mc.menuItem(l=' Import File',c="Import_File_SR_Recent_Folders()")   
    #mc.menuItem(l=' Open File',c="Open_File_SR_Recent_Folders()")

    mc.setParent('..') # cL
       
    mc.window('CurrentFileListWin_dockKSR_Win',e=1,w=70,h=heightV)   
    mc.showWindow('CurrentFileListWin_dockKSR_Win')             
'''    

def Import_File_dockKSR():
    #path='/'.join(file.split('/')[:-1])
    multipleFilters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
    files=mc.fileDialog2(fileFilter=multipleFilters, cap='Import', okc='Import',fileMode=1)
    
    if files:    
        if not isfile(files[0]) : 
            mc.warning(files[0]+ ' is not exist !!!')
            return    
            
        # import 과정중 문제가 있을 수 있으니 미리 저장
        Save_ImportFileList_dockKSR(files[0])    
        
        stdout.write( 'Importing...\n')

        try: # 이 방법으로 업데이트가 잘 안되고 그 에러 다음단계 진행안되는 문제 해결되나.. 에러메세지 알수 없음.
            mc.file(files[0], i=1, ignoreVersion=1)

        except Exception as e2 : # 에러발생시 특별한 예외 조항없음.
            print('Exception Msg: '+str(e2))
          
        stdout.write( files[0] + " tried importing asset !!\n")
        
# 어떤 경로로 내보냈는지 기록하기 위해선...
# 다이얼로그를 써야할듯. 그와 export 관련된 file 명령 프래그들도 많은듯...
# 차후 개선
def Export_File_dockKSR():
    mel.eval('ExportSelection;')
    '''
    sel=mc.ls(sl=True)
    # check if it is something selected otherwise it gets an error;
    # a message can be printed if case nothing is selected
    if sel:
        multipleFilters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
        filename = mc.fileDialog2(fileFilter=multipleFilters, dialogStyle=2)
        mc.file( rename=filename[0] )
        mc.file( save=True, type='mayaAscii' )
    '''
        
def Import_File_fromMenuitem_dockKSR(file, *args):
   
    if not isfile(file) : 
        mc.warning(file+ ' is not exist !!!')
        return    
        
    # ~~ import 과정중 문제가 있을 수 있으니 미리 저장 ~~
    # mc.evalDeferred('Save_ImportFileList_dockKSR("'+file+'")')     
    # evalDeferred 이거 안하면 메뉴아이템을 통해 import 여러번 하는 순간 마야 다운됨.
    # mc.evalDeferred 사용한 것이 또 2022에선 Save_ImportFileList_dockKSR 함수가 정의 안되었다고 에러가 나서 partial로 다시 대체. 
    partial(Save_ImportFileList_dockKSR, file)
    
    
    stdout.write( 'Importing...\n')

    try: # 이 방법으로 업데이트가 잘 안되고 그 에러 다음단계 진행안되는 문제 해결되나.. 에러메세지 알수 없음.
        mc.file(file, i=1, ignoreVersion=1)

    except Exception as e2 : # 에러발생시 특별한 예외 조항없음.
        print('Exception Msg: '+str(e2))
      
    stdout.write( file + " tried importing asset !!!!\n")    
    



def Save_ImportFileList_dockKSR(file):

    # 먼저 저장한게 있으면 읽고 덧붙임. 함수 끝에 메뉴아이템으로 리스트도 붙임.

    localMayaDirPath=mc.internalVar(userAppDir=1)
    kimsEnvDir= localMayaDirPath + 'kimsSet/'
    filePath=kimsEnvDir+'docking_ksrWin_env.txt'
    
    if not os.path.isdir(kimsEnvDir):
        os.mkdir(kimsEnvDir)
    
    list1=[]
    if isfile(filePath):
        # ----------데이다 읽음. 적용
        f = open(filePath,'r') #  일단 rb로 안함 
        # a. 줄별 데이타를 리스트로 담는다   
        lines = f.readlines()[1:] # 첫줄 제외
        f.close() 
        
        for e in lines:            
            list1.append(e.strip('\n'))
  
    else : 'file not exist',

    list1.append(file) # 가장 마지막께 최신것.
    list1_rev=list(reversed(list1)) # 우선 역순으로 놓고.
    # 중복제거. 같은 거라도 최신 순번꺼는 살아남음. 그래서 앞서 역순으로 놓음.
    new_list1=[]
    for ele in list1_rev:
        if not ele in new_list1:
            new_list1.append(ele)
         
    # 다시 뒤집음.     
    list1=list(reversed(new_list1))        
    
    line1 = '~~ [Import List] docking_ksrWin Ver 1 ~~'

    f = open(filePath,'w') # 파일생성, 추가는 w대신 a이용, 일단 wb로 안함 
    f.writelines(line1+'\n')
    for e2 in list1:
        if e2 == list1[-1]:
            f.writelines(e2)
        else :
            f.writelines(e2+'\n')         
    f.close()
    
    # Imp 버튼에 팝업메뉴 달기 
    if mc.popupMenu('pUM_import_dockKSR',q=1,ex=1):       
        mc.deleteUI('pUM_import_dockKSR',menu=1)
    mc.popupMenu('pUM_import_dockKSR', button=0, p='import_bT_dockKSR')
    for e in new_list1:
        mc.menuItem(l=e,c=partial(Import_File_fromMenuitem_dockKSR, e) )    
        

def Load_ImportFileList_dockKSR():

    # 먼저 저장한게 있으면 읽고 덧붙임. 함수 끝에 메뉴아이템으로 리스트도 붙임.

    localMayaDirPath=mc.internalVar(userAppDir=1)
    kimsEnvDir= localMayaDirPath + 'kimsSet/'
    filePath=kimsEnvDir+'docking_ksrWin_env.txt'
    
    list1=[]
    if isfile(filePath):
        # ----------데이다 읽음. 적용
        f = open(filePath,'r') #  일단 rb로 안함 
        # a. 줄별 데이타를 리스트로 담는다   
        lines = f.readlines()[1:] # 첫줄 제외
        f.close() 
        
        for e in lines:            
            list1.append(e.strip('\n'))
  
    else : 
        stdout.write( 'file not exist...\n')
        return 

    list1_rev=list(reversed(list1)) # 우선 역순으로 놓고.

    # Imp 버튼에 팝업메뉴 달기 
    if mc.popupMenu('pUM_import_dockKSR',q=1,ex=1):       
        mc.deleteUI('pUM_import_dockKSR',menu=1)
    mc.popupMenu('pUM_import_dockKSR', button=0, p='import_bT_dockKSR')
    for n, e in enumerate(list1_rev):
        if n == 15: # Limit to 15
            break
        mc.menuItem(l=e,c=partial(Import_File_fromMenuitem_dockKSR, e))  

def Open_File_dockKSR(file, *args):    

    stdout.write( 'Opening...\n')
    
    if not isfile(file) : 
        mc.warning(file+ ' is not exist !!!')
        return
    
    try: # 이 방법으로 업데이트가 잘 안되고 그 에러 다음단계 진행안되는 문제 해결되나.. 에러메세지 알수 없음.            
        #mc.file(path_[0], o=True) 
        # Unsaved changes 메세지가 뜨면서 잘 안된다면.
        #mc.file(new=True, force=1) 
        #mc.file(file, open=True)
        
        # 열기전에 현재 씬을 저장할지 묻기 위해서는 mel로 실행해야함.
        if file.split('.')[-1] == 'ma': ext = 'mayaAscii'
        elif file.split('.')[-1] == 'mb': ext = 'mayaBinary'
        else : return 
            
        mel.eval('openRecentFile("'+file+'", "'+ext+'");')
        
    except Exception as e2 : # 에러발생시 특별한 예외 조항없음.
        print('Exception Msg: '+str(e2))   
        
    stdout.write( file + " tried Opening asset !!!\n")
    
def Float_SelectedFileListWin_dockKSR(file):
        print (file)   
       
    
def WireFrameMode_dockKSR():
    currentPanel = mc.getPanel(withFocus=1)
    panelType = mc.getPanel(to=currentPanel)
    if panelType == 'modelPanel':
        mc.modelEditor(currentPanel, e=1, displayAppearance='wireframe')


def Open_Dir_CurrentFile_dockKSR():
    filePath = mc.file(q=1, sn=1)
    if filePath == '':
        return
    fileName = filePath.split('/')[-1]
    dirPath = filePath.split(fileName)[0]
    # mc.launch(dir=dirPath) 
    filePath=filePath.replace('//','/') # 끝에만 슬래시 2개를 1개로
    filePath=filePath.replace('/','\\') # 슬래시를 역슬래시로. 2개인 점 주의.
    subprocess.Popen(r'explorer /select,"'+filePath+'"') 


def Only_kDock_dockKSR():
    ui()



#=======================================================#
#                   kDock UI
#=======================================================# 
def ui():
    dockControlKSR='K' # 너비를 최소화하기 위해
    dockingKSR_win='dockingKSR_win'
    if mc.dockControl(dockControlKSR ,q=1,ex=1):
        mc.deleteUI(dockControlKSR)   
  
        # ~ dock들이 여러개 있을때 가장 너비가 넓은 dock에 전체 dock틀이 맞춰지기에 
        # 현재 kFaceTool과 kDock 간에서 
        # kFaceTool로 넓혀진 너비를 줄이기 위해서 kFaceTool Dock를 삭제해 
        # Dock틀에서 보여지지 않게 하는수 밖에 없어서 
        # kFaceTool Dock를 지움. 지우기전에 먼저 세팅값 저장을 위해 qt형식으로 닫아야함.
        if mc.dockControl('kFaceTool_dock' ,q=1,ex=1):
            maya_ui_name_kFaceTool= mc.dockControl('kFaceTool_dock',q=1,con=1)

            qt_ui_pt_kFaceTool = OpenMayaUI.MQtUtil.findControl(maya_ui_name_kFaceTool) # pointer
            if qt_ui_pt_kFaceTool:
                qt_ui_kFaceTool = wrapInstance(int(qt_ui_pt_kFaceTool), QtCore.QObject)
                qt_ui_kFaceTool.close() # kFaceTool 세팅값 저장하기 위해 

            mc.deleteUI('kFaceTool_dock') # 

        
    if mc.window(dockingKSR_win, q=1,ex=1): # 존재하는데 showWindow가 안됨.
        mc.deleteUI(dockingKSR_win)        
        
    win = mc.window(dockingKSR_win)

    mc.columnLayout(adj=1) 
    
    mc.rowColumnLayout(nc=2 )
    mc.button('import_bT_dockKSR', l='Imp',c=lambda x: Import_File_dockKSR(), w=48,h=40)
    # Imp 우클릭 메뉴아이템은 ui함수 마지막에 목록으로 추가.
    
    mc.button('export_bT_dockKSR', l='Exp',c=lambda x: Export_File_dockKSR(), w=48,h=40)
    mc.setParent('..') #---- rL
    
    # ------- openDir -----------
    mc.button('openDir_bT_dockKSR', l='openDir',c=lambda x: Open_Dir_CurrentFile_dockKSR(), w=20,h=40)
    mc.popupMenu('openDir_pM_dockKSR', button=0, p='openDir_bT_dockKSR', pmc=lambda x, *args: update_recent_opened_files() )

    # ------------------------
    
    mc.text(l='',h=5)
    mc.button(l='Save As',c=lambda x: save_as_to_current_location(),w=20, ann='save as to current scene location')
    mc.text(l='',h=15)    
    
    mc.button(l='selCBox In', c=lambda x: Select_ChannelBox_Conned_Input_SOULP(), h=20,bgc=(.2,.2,.2))
    mc.button(l='selCBox Out', c=lambda x: Select_ChannelBox_Conned_Output_SOULP(), h=20,bgc=(.2,.2,.2))
        
    mc.text(l='',h=5)
    mc.button(l='Pan', c=lambda x:load_Pan_dockKSR(), h=40,bgc=(1,1,0))  
    
    mc.text(l='',h=5)
    mc.button(l='MatchP', c=lambda x:load_MatchPoint_dockKSR(), h=40,bgc=(0,0,0.5))      
    mc.text(l='',h=5)
    mc.rowColumnLayout(nc=2 )
    mc.iconTextButton( image1='Smooth.png' ,w=45,h=45,l='', bgc=(0.2,0.2,0.2),c='mel.eval("SetMeshSmoothTool;")',dcc='mel.eval("ShowMeshSmoothToolOptions;")',ann='Smooth Tool: Even out surface detail')    
    mc.iconTextButton( image1='Sculpt.png' ,w=45,h=45,l='', bgc=(0.2,0.2,0.2),c='mel.eval("SetMeshSculptTool;")',dcc='mel.eval("ShowMeshSculptToolOptions;")',ann='Sculpt Tool: Lift a surface')
    mc.iconTextButton( image1='Relax.png' ,w=45,h=45,l='', bgc=(0.2,0.2,0.2),c='mel.eval("SetMeshRelaxTool;")',dcc='mel.eval("ShowMeshRelaxToolOptions;")',ann='Relax Tool: Smooth the surface of a mesh without affecting its shape')
    mc.iconTextButton( image1='Grab.png' ,w=45,h=45,l='', bgc=(0.2,0.2,0.2),c='mel.eval("SetMeshGrabTool;")',dcc='mel.eval("ShowMeshGrabToolOptions;")',ann='Grab Tool: Pull a single vertex along a surface in any direction')    
    mc.iconTextButton( image1='Flatten.png' ,w=45,h=45,l='', bgc=(0.2,0.2,0.2),c='mel.eval("SetMeshFlattenTool;")',dcc='mel.eval("ShowMeshFlattenToolOptions;")',ann='Flatten Tool: Level a surface')
    mc.iconTextButton( image1='putty.png' ,w=45,h=45,l='', bgc=(0.2,0.2,0.2),c='mel.eval("SculptGeometryToolOptions;")',dcc='mel.eval("SculptGeometryToolOptions;")',ann='Sculpt geometry tool options')    
    
    mc.text(l='')
    mc.iconTextButton( image1='move_M.png' ,w=45,h=45,l='', bgc=(0.2,0.2,0.2),c='mel.eval("MoveToolOptions;")',dcc='mel.eval("MoveToolOptions;")',ann='Move tool options')
    mc.setParent('..') #---- rL
    
    mc.text(l='',h=5)
    mc.rowColumnLayout(nc=2 ) 
    # 2017의 경우. 경고창이 나타나면서 없다고 메세지가 뜨면 휴먼ik메뉴를 먼저 실행하면 해결되지만... 굳이. 그냥 대체 이미지로.
    mc.iconTextButton( image1=BasicFuncsRoot_Ki.split('/basic_functions')[0]+'/app/Rig/ES_Daz_Rig_Tool/DazfaceStancePose.png' ,w=45,h=45, sic=1,bgc=(0.2,0.2,0.2),c=lambda : [x for x in [load_ES_Daz_Rig_Tool_dockKSR(), Set_DefaultPose_FaceCtrls_EDZRT()]] ,ann=u'페이셜 컨트롤 기본포즈로(최근)')      
    mc.iconTextButton( image1=BasicFuncsRoot_Ki.split('/basic_functions')[0]+'/app/Rig/ES_Daz_Rig_Tool/hikStancePose.png' ,w=45,h=45, sic=1,bgc=(0,0,0),c='mel.eval("hikStancePose;")',dcc='mel.eval("HIKCharacterControlsTool;")',ann=u'휴먼 IK 컨트롤 기본포즈로')  
    mc.setParent('..') #---- rL
    
    mc.text(l='',h=5)  
    mc.button(l='SimShp',c=lambda x: load_SimShpEditor_dockKSR(), h=50,bgc=(1,0,0) )
    mc.text(l='',h=5)    
    
    mc.rowColumnLayout(nc=2 )  
    mc.iconTextButton( image1='blendShapeEditor.png',w=45,h=45, l='', bgc=(0.2,0.2,0.2),c='mel.eval("ShapeEditor;")', dcc='mel.eval("ShapeEditor;")',ann='blendShapeEditor')
    mc.iconTextButton( image1='poseEditor.png' ,l='',w=45,h=45, bgc=(0.2,0.2,0.2),c=lambda : open_PoseEditor_dockKSR(), dcc='mel.eval("PoseEditor;")',ann='poseEditor')

    mc.button(l='Wire', c=lambda x: WireFrameMode_dockKSR(), w=45,h=45)       
    mc.button(l='Tex', c=lambda x: TextureMode_dockKSR(), w=45,h=45,bgc=(0.5,0.5,0.5))   
    mc.button(l='ExT', c='mel.eval("toggle_CES;")',w=45,h=45,bgc=(0,0,.5),ann='external utility')     
    mc.button(l='SOUL', c='mel.eval("Toggle_SoulPalette_NKT;")',w=45,h=45,bgc=(0,0,.5))     
    mc.button(l='___', c='',w=45,h=45)     
    mc.button(l='Sets', c='mel.eval("CreateSet;")',w=45,h=45,bgc=(0,0,0))  
    
    mc.button(l='FitW', c=lambda x: Only_kDock_dockKSR() ,w=45,h=45,bgc=(.2,.2,.2), ann='look only kDock for width fit')
         
    mc.setParent('..') #---- rL 
    
    
    allowedAreas = ['right', 'left']

    dockControl = mc.dockControl(dockControlKSR, area='left', content=win, allowedArea=allowedAreas) # w=로는 조절이 안되는듯.
    
    # advanced skeleton 참조함. 강제로 너비를 줄어줌 맞춰줌. 이거 안하면 마야 실행시 너비가 넓어짐
    mc.dockControl(dockControlKSR, e=1, fixedWidth=1)
    mc.evalDeferred('mc.dockControl("%s", e=1, r=1)'%(dockControlKSR)) # look forward
    
    
    Load_ImportFileList_dockKSR() # Imp 우클릭시 메뉴아이템
   


#=======================================================#
#          run ( executed by kDock shelf button )
#=======================================================#  
def run():
    ui()
   
   

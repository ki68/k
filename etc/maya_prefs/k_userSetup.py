# -*- coding: utf-8 -*-

import maya.cmds as mc
import maya.mel as mel
import os
import sys

kRootUpperPath='C:/'
if not kRootUpperPath in sys.path:
    sys.path.append(kRootUpperPath)

try:
    mel.eval('source "C:/kimstools/ksKimstools.mel";') # 공용에 있어도 여기다 안 써주니 kims 메뉴 안뜸.
    mel.eval('source "C:/kimstools/NewKimstools.mel";') 
    mel.eval('layout -e -height 100 "ShelfLayout";') # 그냥 씬에서 실행하면 마야 닫으면 저장이 안되서..    
except : pass    

# set maya window bg color based on number of maya windows.
import k.com.set_maya_window_color.main
k.com.set_maya_window_color.main.run()

# docking kDock
import k.rig.kDock.main
k.rig.kDock.main.run()

# delete the chinese virus when the file is opened.
import k.com.del_chinese_virus.main
k.com.del_chinese_virus.main.run()


# For some files, when I open it and select something in the outliner,
# I get an error saying that I can't find the look function, so I added a phrase to get rid of it . 
'''
try :
    print ("")
    mel.eval('outlinerEditor -edit -selectCommand "" "outlinerPanel1";')
except : pass
'''


# set scriptEditor font size .
# (없어진듯. 에러 때문에 안된듯) 단점 마우스스크롤로 폰트사이즈 조절 안됨.
# 2022에서 long 관련 에러가 나 해당파일에서 long을 int로 고침. python3에서 int로 바뀌었음.
# (Hold.. 잘 안돼 막음) 
# with open('C:/kimstools/Set_Fontsize_ScriptEditor.py','rb') as f: exec(f.read()); launchFromCmdWndIcon(45)




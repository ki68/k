# -*- coding: utf-8 -*-

'''
py2.7 py3.7
/////////////////////////////////////////////////
//                 kTools  Info                   
/////////////////////////////////////////////////

soulstation1966.blogspot.com
nextsoulstation@gmail
Creation Date: October 13th, 2022

-------------------------------------------------------------------
MIT License

Copyright (C) 2022 Sung Rock Kim

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
-----------------------------------------------------------------


Installation Method:
    -  Drag and drop "C:/k/etc/kTools/main.py" file to maya viewport. 
       Then kTools shelfbar icon will be registered.
       Or use the "kTools Icon Register Code" below to register. 
       
       
       
# ---------- kTools Icon Register Code ------------

import sys

kRootUpperPath = 'C:/' # C:/k <-- kRootUpperPath is path except "k".

if not kRootUpperPath in sys.path:
    sys.path.append(kRootUpperPath)

import k.etc.kTools.main
if sys.version_info > (3,7,0):  
    import importlib
    importlib.reload(k.etc.kTools.main)
else :
    import imp
    imp.reload(k.etc.kTools.main) 

import traceback
try: k.etc.kTools.main.onMayaDroppedPythonFile() 
except:
    traceback.print_exc()
    
# --------------------------------------------------



///////////////////////////////////////////////
//                  Note
///////////////////////////////////////////////

- v1.0
22.10.13 - kTools.py creation        

How to add new subTool(=shelfbar icon) to the kTools:
    0. Make subTool folder in mod(modeling) or rig or ani or moc(mocap) or sim(simulation) or com(common)
    1. __init__.py file shoud be exsist in subTool folder.
    2. Name of the subTool file to run shoud be "main.py"
    3. Function name to run in main.py shoud be "run()"
    4. Icon image name shoud be the same as the subTool folder name

----- role note ----
kTool help - md file
subTool help (pdf) - in the help folder of the repository
subTool help (movie)- youtube link

'''

import maya.cmds as mc
import maya.mel as mel
import os
import sys
import ast
from os.path import isfile, isdir
from sys import stdout

print ('read kTools module.')


#=======================================================#
#                Get Icons Label & Annotation
#=======================================================#
def get_icons_data():

    kToolsDirPath = os.path.dirname(__file__)
    kToolsDirPath = kToolsDirPath.replace('\\','/')    

    labels_annotations_File=kToolsDirPath + '/labels_annotations.txt' 
    
    data_lines=[]
    if isfile(labels_annotations_File):
        f = open(labels_annotations_File,'rb')
        lines = [line.strip() for line in f.readlines()]  
            
        for line in lines:   
            # If the line is not a blank line.
            # have to add b so that no "range error" occurs.
            if not line == b'':             
                line = line.decode('utf-8') # unicode -> utf
                
                if not line[0] == '#' : # except line that start with "#"
                    data_lines.append(line)

    else : stdout.write('labels_annotations.txt not exist.\n')
        
    if data_lines==[]:
        return 
        
    dic1={}  
    
    # put data in dic
    for e in data_lines:
        splits=e.split(',') 
        dic1[splits[0].strip()]=(splits[1].strip(), splits[2].strip())


    return dic1


#=======================================================#
#         Load Env Values ( Last selected tab )
#=======================================================#

def load_ui_env(): 

    localMayaDirPath=mc.internalVar(userAppDir=1)
    esEnvDir= localMayaDirPath + 'kTools_Envs/'
    filePath=esEnvDir+'kTools.txt'

    if isfile(filePath):
        f = open(filePath,'r')
        lines = f.readlines()
        f.close() 

        line2 = lines[1].strip('\n')

        return line2
  
    else : stdout.write('file not exist !!\n')
    

#=======================================================#
#                    Save Env Values
#=======================================================#

def save_ui_env(): 

    localMayaDirPath=mc.internalVar(userAppDir=1)
    esEnvDir= localMayaDirPath + 'kTools_Envs/'
    filePath=esEnvDir+'kTools.txt'
    
    if not os.path.isdir(esEnvDir):
        os.mkdir(esEnvDir)

    line1 = '~~ UI kTools Ver 1.0 ~~'
    currentTab = mc.shelfTabLayout( 'mainShelfTab', q=1, st=1)    
    line2 ='{' +'"currentTab"' + ':"' + currentTab + '"}'
    
    f = open(filePath,'w') 
    f.writelines(line1+'\n')
    f.writelines(line2)
    f.close()


#=======================================================#
#                   Set RootPath
#=======================================================#
# - list icons of selected part tab

def load_icons():

    kToolsDirPath = os.path.dirname(__file__)
    kToolsDirPath = kToolsDirPath.replace('\\','/')
    kRootUpperPath = '/'.join(kToolsDirPath.split('/')[:-3]) + '/'
    kRootPath = kRootUpperPath + 'k'

    if not os.path.exists(kRootPath): 
        mc.warning(kRootPath + u' path does not exist.' )
        return 
                
    currentTab = mc.shelfTabLayout( 'mainShelfTab', q=1, st=1)
    # { tab name :folder name }
    currentTab_dic={
    'Model_':'mod', 
    'Ani__':'ani', 
    'Rig__': 'rig',
    'Mocap_':'moc',
    'Simul_':'sim',
    'Common':'com'
    }
    
    partDir=kRootPath+'/'+ currentTab_dic[currentTab]
        
    subdirs = [os.path.join(partDir, dirName ).replace('\\','/') for dirName in os.listdir(partDir) if os.path.isdir(os.path.join(partDir,dirName))]
    
    part_pyList=[]
    part_iconImageList=[]
    part_moduleFolderList=[]
    
    
    for subdir in subdirs:
        pyFile = subdir+'/'+'main.py'
        pyFile_pureName = subdir+'/'+subdir.split('/')[-1]

        if os.path.isfile(pyFile):
            part_pyList.append(pyFile)
            part_moduleFolderList.append(subdir.split('/')[-1])
            if os.path.isfile(pyFile_pureName + '.png'):
                part_iconImageList.append(pyFile_pureName + '.png')
            elif os.path.isfile(pyFile_pureName + '.jpg'):
                part_iconImageList.append(pyFile_pureName + '.jpg')
            else:
                part_iconImageList.append('none')        
                
    child_icons=mc.shelfLayout( currentTab, q=1, ca=1)
    if not child_icons == None : 
        mc.deleteUI(child_icons)
    
    dic_LabelsAnnotations = get_icons_data() or {}
    keys_dic_LabelsAnnotations = dic_LabelsAnnotations.keys()
    
    

    for n, moduleFolder in enumerate(part_moduleFolderList): 
        
        # app_cmd_str have to reset in loop
        
        # I don't know why, but in the "kDock" script execution with mc.dockControl,
        # need "import maya.cmds as mc", otherwise, there will be an next error
        # Error: name 'mc' is not defined
        app_cmd_str='''\
import sys
import maya.cmds as mc
import maya.mel as mel
import %s
if sys.version_info > (3,7,0): 
    import importlib
    importlib.reload(%s)
else :
    import imp
    imp.reload(%s) 

import traceback
try: %s.run() 
except:
    traceback.print_exc()            
'''   
        importModuleStr = ('k.' + currentTab_dic[currentTab] +
            '.'+ moduleFolder + '.main' )
                      

        app_cmd_str = app_cmd_str % (importModuleStr, importModuleStr, importModuleStr, importModuleStr)   
  
        # If have a script line for that app
        if moduleFolder in keys_dic_LabelsAnnotations: 
            iconLabel = dic_LabelsAnnotations[moduleFolder][0]
            if iconLabel == '':
                iconLabel = moduleFolder[:5] # get just five characters
            annotationVal = dic_LabelsAnnotations[moduleFolder][1]
            
        else :                   
            iconLabel = moduleFolder[:5]
            annotationVal = ''

        # If icon image does not exists, attach label
        if part_iconImageList[n] == 'none': 
            mc.shelfButton(
            p = currentTab, 
            iol = iconLabel, 
            c = app_cmd_str,
            image1 = 'commandButton.png',
            annotation = annotationVal,
            overlayLabelColor = (1,1,1)
            )

        # If icon image exists, attach no label
        else : 
            mc.shelfButton(
            p = currentTab,
            c = app_cmd_str, 
            image1 = part_iconImageList[n],
            annotation = annotationVal
            ) 


#=======================================================#
#                         Help
#=======================================================# 
def help( ext ):
    
    
    subToolDirPath = os.path.dirname(__file__)
    subToolDirPath = subToolDirPath.replace('\\','/')
    subToolName = subToolDirPath.split('/')[-1]
    part = subToolDirPath.split('/')[-2]
    kRootPath = '/'.join(subToolDirPath.split('/')[:-2])
    
    path = kRootPath + '/help/' + part + '/' + subToolName + '.'+ ext    
    
    
    os.startfile(path)     


#=======================================================#
#                   kTools UI
#=======================================================#    
def ui():

    if mc.window('kTools_Win', q=1, ex=1):
        mc.deleteUI('kTools_Win')        
    mc.window('kTools_Win',title='kTools')

    mc.columnLayout(adj=1) 
    
    # -------------- upper layout ---------------
    
    mc.rowColumnLayout(nc=12,h=30)
    mc.text(l='',bgc=(.26,.26,.26),w=63)
    mc.text(l='',bgc=(.26,.26,.26),w=63)
    mc.text(l='',bgc=(.26,.26,.26),w=63)
    mc.text(l='',bgc=(.26,.26,.26),w=63)
    mc.text(l='',bgc=(.26,.26,.26),w=63)
    mc.text(l='',bgc=(.26,.26,.26),w=63)
    mc.text(l='',w=37)
    mc.symbolButton( image='help.png' ,w=30,h=30,bgc=(0.2,0.2,0.2),c=lambda x:help('pdf'), ann=u'Help')
    #mc.symbolButton( image='hotkeySetSettings.png' ,w=30,h=30,bgc=(0.2,0.2,0.2),c=lambda x:kTools_Setting_ui())
    mc.setParent( '..' )
    
    
    # ---------- lower layout (kTools shelfbar) --------
    
    mc.shelfTabLayout( 'mainShelfTab', h=102 , sc=lambda : [x for x in [load_icons(),save_ui_env()]] ) 

    mc.shelfLayout('Model_' ,cwh=[36,34])
    mc.setParent( '..' )

    mc.shelfLayout('Ani__' ,cwh=[36,34]) # Fit to 5 spaces
    mc.setParent( '..' )

    mc.shelfLayout('Rig__' ,cwh=[36,34])
    mc.setParent( '..' )

    mc.shelfLayout('Mocap_' ,cwh=[36,34])
    mc.setParent( '..' )

    mc.shelfLayout('Simul_' ,cwh=[36,34])
    mc.setParent( '..' )
    
    mc.shelfLayout('Common' ,cwh=[36,34])
    mc.setParent( '..' )

    mc.setParent( '..' ) # shelfTabLayout    
    mc.setParent( '..' ) # columnLayout
    
    # --------------- layout end ---------------------
    
    # when window pops up, cc comand is executed 
    mc.window('kTools_Win',e=1,w=450,h=110, cc=lambda :save_ui_env())   
    mc.showWindow()

    # ---------- load recent env ------------

    envVal = load_ui_env()
    if not envVal == None :
        dic1 = ast.literal_eval(envVal)
        mc.shelfTabLayout( 'mainShelfTab', e=1, st=dic1['currentTab'])
     
    # ---------- load sub tools ------------
    
    load_icons() 
    

#=======================================================#
#          run ( executed by kTools shelf button )
#=======================================================#  
def run():

    ui()
   
   
#=======================================================#
#             install kTools shelf button  
#=======================================================# 
def onMayaDroppedPythonFile(*args, **kwargs):  
    """
    This function is only supported since Maya 2017 Update 3.
    Maya requires this in order to successfully execute.
    """     
    
    # ex) C:/k/etc
    kToolsDirPath = os.path.dirname(__file__)
    kToolsDirPath = kToolsDirPath.replace('\\','/')
    kRootUpperPath = '/'.join(kToolsDirPath.split('/')[:-3]) + '/'

    # ------------ pathTool execute script ------------
    
    pathToolIconCmdStr='''import sys
kRootUpperPath="%s"
if not kRootUpperPath in sys.path:
    sys.path.append(kRootUpperPath)

import k.etc.kTools.main
if sys.version_info > (3,7,0):
    import importlib  
    importlib.reload(k.etc.kTools.main)
else :
    import imp
    imp.reload(k.etc.kTools.main) 

import traceback
try: k.etc.kTools.main.run() 
except:
    traceback.print_exc()'''  % (
        kRootUpperPath
        )

    # ---------- make pathTool icon ---------
    
    gShelfTopLevel = mel.eval("$tmpVar=$gShelfTopLevel")
    currentShelf=mc.tabLayout(gShelfTopLevel,q=1,selectTab=1)
    mc.shelfButton(
        command=pathToolIconCmdStr,
        annotation="kTools",
        iol="kTools",
        olc=(1,1,1),
        parent=currentShelf,
        image=(kToolsDirPath+"/kTools.png"),
        image1=(kToolsDirPath+"/kTools.png"),
        sourceType="python"
        )


    
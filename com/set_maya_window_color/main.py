# -*- coding: utf-8 -*-
# py2.7 py3.7

'''
# 21.8.14 fix 
# 22.2.16 fix colors value as slider bar color

------------ background coloring script -----------

Usage : Add the following line in userSetup.mel(s) and execute Maya.

python("with open('E:/...saved path.../Set_Color_MayaWindow.py','rb') as f: exec(f.read())");

--------------- Custom Color Specification ------------
navy, dark green, black 


-------- Aspects of Results -----------
1. open first maya >> navy 
2. second maya >> dark green 
3. third maya >> black 
4. 4th maya >> maya basic 
5. 5th maya >> navy 
6. all mayas closed, next, open the two mayas at the same time.
>> dark green ,black 
6 or, open single maya >> navy 


# (0.2666, 0.2666, 0.2666) 마야 기본 컬라와 같은 색이지만 기본 컬라와 차이점은 배경색은 같지만 글자색이 인위적인 흰색이다. 그래서 이는 적용 안하는 걸로.

# (폐기된 아이디어1) maya.exe 수량 기준으로만 하는 건 근시간차로 동시에 띄울때나 여닫기를 반복할때 색이 같아지는 경우가 금방 찾아옴. 
# (폐기된 아이디어2) 마야가 닫을때 마야기본설정파일 수정시간을 파악하는 것 기준. 마야가 갑자기 꺼지는 경우는 수정시간이 기록이 안되니 힘듬

# (시도) 다른 아이디어. 시작할때마다 사용자 설정파일에 컬러를 1개를 지정해 계속 기록. 
기록전 먼저 읽어 기록된 컬러(들)를 총 컬러 리스트에서 제외하고 남은 컬러리스트 첫칸에서 1개를 뽑아 지정하고, 그 지정값을 기록.
마야를 여러개 계속 실행시킬 경우 이제 지정할 컬러가 더 이상 없다면 기본색으로 계속 지정.
이렇게 되면 설정파일에 꽉찬 컬러색들 찌꺼기가 남아 모든 마야창을 다 닫고 다시 시작하면 기본색으로만 계속 띄워질테니
그래서... maya.exe 수를 계산해 1개일때 리셋하는게 좋을듯. 그러면 항상 처음 띄울때는 네이비로 항상 지정됨.
# (이슈) 한 개 이상 마야가 남아 있고 다른 마야를 여러번 여닫을때 역시 꽉 찬 컬러데이타 찌꺼기가 파일에 남아 최종적으로 기본색으로만 창이 떠질 수 있음. 
그리고 떠진 갯수랑 기록된 컬러 갯수랑 달라질 수... 결국 완벽 못함. 꺼지는 경우 수량이 달라지는 것 때문에... 일단 이대로.
두개 동시에 띄울때도 마야 2개가 실행후, 스크립트가 두번 실행되기에.. 첫 스크립트 실행시 이미 maya.exe 2개로 파악하기에.. 찌꺼기 설정이 reset 안됨. 
이는 마야 구동과 스크립트 실행 시간차 때문에 생기는 문제..
'''
import maya.cmds as mc
from sys import stdout
import ast
import subprocess
import os
from os.path import isfile, isdir

def set_maya_window_color():

    # all maya bg color list - 3 color ( navy, dark green, black )
    bgcList=[(0.1, 0.18, 0.3), (0.1, 0.22, 0), (0.1, 0.17, 0.1)] 
    colorNames = {(0.1, 0.18, 0.3):'Navy',(0.1, 0.22, 0):'Green',(0.1, 0.17, 0.1):'Black'} # use dict type for printing 

    # file path set
    localMayaDirPath=mc.internalVar(userAppDir=1)  # C:/...Documents/maya/
    esEnvDir= localMayaDirPath + 'Es_Envs/'
    filePath = esEnvDir + 'mayaBgColor.txt'
    
    # make folder to save extra color to use as background color
    if not os.path.isdir(esEnvDir):
        os.mkdir(esEnvDir)  
        
    # 파일이 없으면 3색에서 시작, 그중 하나를 빼가 색지정. 2개 기록. 
    # 두번째 마야는 2색중 하나를 빼가 색지정. 나머지 1개 기록.
    # 세번째 마야는 1색을 빼가 색지정. 빈값을 기록.
    # 네번째 마야는 빈걸 확인하고, 다시 3개 색을 채워넣고, 기본색으로 색지정한다. 
    # 5번째 마야는.. 다시 .. 반복.
    
    # 만약 두번째 마야(녹색)를 닫고 세번째 마야(블랙)를 열면, 닫은 마야색을 모르니, 계속 기록된 값들에서 지정색을 얻음. 네번째 마야는 기본색, 5번째 마야는 네이비.. 그럼 첫번재 네이비마야랑 2개 생김. 여튼. 앞서 세번째 마야를 다시 닫았더라면 그래도 계속. 진행.
    # 마야를 실행한 수대로 색깔이 순서대로 진행됨.(닫힘에 관계없이..) 
    
    # 창을 다 닫아도 기록은 남는다. 몇개의 갯수가 남는다. 
    # 이때는 다시 리셋하기 위해 maya.exe 갯수가 1개라면 리셋. 새로 채워넣어서 빼가는 것으로 시작. 다만 두개 거의 동시에 띄우면 exe가 2개 생긴후 스크립트가 실행되어 빼가기 때문에 리셋은 안될듯하나 색이 다른 2색이 나올 것임. 
    
    
     # If there is no setting file, create a new one, fill in 3 colors, and designate the first one of them as bg color. The other two are recorded. 
    if not isfile(filePath): # Whether you launch two Maya at the same time or one. 
    
        print (' type 1 ')
    
        f=open(filePath,'w')  # first create  
        line1 =' ~~~~~~ Maya BackGround Color Extra Set ~~~~~~~ '
        f.write(line1)
        
        for color in bgcList[1:]:
            f.write('\n'+ str(color))
        f.close 
        
        mc.window('MayaWindow', e=1, bgc=bgcList[0] )
        stdout.write('Maya bg color : '+ colorNames[bgcList[0]]+'\n')
        stdout.write('Color set record : First create, remove & write.\n\n')
        
    else : # If there is a setting file, read it first and get the recorded colors.

        # 그 전에 마야.exe를 파악해 1개라면 설정값이 무엇이든 상관없이 다시 처음부터 3개 색을 채워넣고 첫 한 색을 지정해서 시작.
        # 2개 이상이라면 빼가서 지정하는 식으로 감. 0개는 나올 수 없음. 마야가 스크립트보다 먼저 실행되므로.
        
        # get the number of maya.exe
        taskStr=subprocess.check_output('tasklist', shell=True)
        # mayaExeNum=taskStr.count('maya.exe') # Error in Python 3.7. 
        mayaExeNum=taskStr.count(b'maya.exe') # b' is a byte string        
                            
        if mayaExeNum <= 1:  # If the number of Maya is one, fill in three colors and record. reset. 
        
            print (' type 2 ')
            
            mc.window('MayaWindow', e=1, bgc=bgcList[0] )            
        
            f=open(filePath,'w')  # overwrite   
            line1 =' ~~~~~~ Maya BackGround Color Extra Set ~~~~~~~ '
            f.write(line1)
            
            for color in bgcList[1:]:
                f.write('\n'+ str(color))
            f.close 
            
            stdout.write('Color set record : Reset & overWrite.\n\n') 
            stdout.write('Maya bg color : '+ colorNames[bgcList[0]]+'\n')

                            
        else : # If the number of Maya is not one
            # Read the file to get the colors.
            f=open(filePath,'r') # read first
            lines=f.readlines()[1:]
            f.close
                        
        
            if lines: # If the color remains, take the first one and designate it as bg color, and record the extras.
            
                print (' type 3 ' )
            
                mc.window('MayaWindow', e=1, bgc=ast.literal_eval(lines[0].rstrip('\n')) ) #  literal_eval - convert string to tuple                
                stdout.write('Color set record : Remove & overWrite.\n\n')
                stdout.write('Maya bg color : '+ colorNames[ast.literal_eval(lines[0].rstrip('\n'))]+'\n')
                                
                f=open(filePath,'w')  # overwrite   
                line1 =' ~~~~~~ Maya BackGround Color Extra Set ~~~~~~~ '
                f.write(line1)
                
                # print (lines) # Except for the last line, escape string (back slash  n) are attached.
                lines.remove(lines[0]) # as it is with a back escape string
                for color in lines:
                    f.write('\n'+ str(color.rstrip('\n'))) # remove back escape string, attach front escape string
                f.close 
            
            else : # if [] is, set basic color , and  Fill in 3 colors and record. reset.

                # pass >> mc.window('MayaWindow', e=1, bgc= ...
                
                print (' type 4 ' )
                
                stdout.write('Maya bg color : Reset & overWrite, Basic(Dark Gray)\n\n')
                
                f=open(filePath,'w')  # overwrite   
                line1 =' ~~~~~~ Maya BackGround Color Extra Set ~~~~~~~ '
                f.write(line1)
                
                for color in bgcList:
                    f.write('\n'+ str(color))
                f.close     
            
    # f.flush()  # If you use a function, you don't need to write it.
    
    #스크립트창이나 idle 혹은 usetSetup.mel을 통해 실행되는 py파일내에서 안해주면 w모드 0kb가 되고, a모드는 한템포씩 실행 반응이 늦음. 파일내에서 그냥 뿌리면 안됨.
    # 그전까진 다른툴에선 되었던 이유는?  함수로 묶어서 그럼.
    # 함수 없이 쓰기할때는 f.flush()를 해줘야 함. 
    
  

def run():
    set_maya_window_color()  

# ----------- maye.exe 갯수를 이용한 색지정은 아래와 같은 이유로 패기 ------------
# 동시에나 시간차이 없의 띄울 경우. 스크립트가 마지막에 실행되기에 마야 exe 2개가 존재한 이후에
# 각자 스크립트가 실행되어 하는 경우가 생겨 둘 다 green으로 되기도 함. 
# 그리고 1개 green일때 나머지 마야를 다 닫고, 다시 마야를 띄우면 또 green이 됨. 
'''
import subprocess

taskStr=subprocess.check_output('tasklist', shell=True)

# mayaExeNum=taskStr.count('maya.exe') # 파이썬 3.7에서 에러. 
mayaExeNum=taskStr.count(b'maya.exe') # b'는 바이트 문자열이라고 함.


# Write down a list of color values you want!
bgcList=[(0.1, 0.18, 0.3), (0.1, 0.22, 0), (0.1, 0.17, 0.1), 'basic'] # (0.2666, 0.2666, 0.2666)
colorNames = ['navy','green','black','basic']
color_index=mayaExeNum % len(bgcList) - 1

if color_index == 3:
    pass
else:     
    stdout.write('maya bg color : ' + str(colorNames[color_index]) + '\n')
    mc.window('MayaWindow', e=1, bgc=bgcList[color_index])
'''

# --------------------------
''' 또 다른 표식들

tasks = subprocess.check_output(['tasklist']).decode('cp866', 'ignore').split("\r\n")
    p = []
for task in tasks:
    print (task)  

========================= ======== ================ =========== ============
System Idle Process              0 Services                   0          8 K
System                           4 Services                   0      1,876 K
Registry                       140 Services                   0     97,568 K
smss.exe                       496 Services                   0      1,252 K
csrss.exe                      644 Services                   0      5,788 K
... 이런 표식에서 문자열 처리를 할 수도 있겠고. 


task1=[line.split() for line in taskStr.splitlines()] # splitlines 줄바꿈 단위로 끊음.
for e in task1:
    if len(e) > 0:
        if b'maya.exe' in e[0] :
            print (e)
            
[b'maya.exe', b'1544', b'Console', b'1', b'888,620', b'K']
[b'maya.exe', b'5672', b'Console', b'1', b'862,844', b'K']
이렇게 짤라 리스트로 담을 수도 있겠고. 

'''    

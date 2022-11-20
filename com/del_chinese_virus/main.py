# -*- coding: utf-8 -*-
# py2.7 py3.7

# - Used when saving a yellow warning in Chinese or when a virus file named vacine appears in the Maya>Script folder.


import maya.cmds as mc 
import os
from os.path import isfile
from sys import stdout
import maya.mel as mel

def delete_chinese_virus():
    jobs = mc.scriptJob(lj=True)
    for job in jobs:
        if "leukocyte.antivirus()" in job:
            id = job.split(":")[0]
            if id.isdigit():
                mc.scriptJob(k=int(id), f=True)

    script_nodes = mc.ls("vaccine_gene*","breed_gene*", type="script")
    if script_nodes:
        mc.delete(script_nodes)


    localMayaDirPath=mc.internalVar(userAppDir=1) 

    filePath=localMayaDirPath+'scripts/vaccine.py'
    filePath3=localMayaDirPath+'scripts/vaccine.pyc'
    filePath2=localMayaDirPath+'scripts/userSetup.py'

    VirusExist=0
    if isfile(filePath):
        os.remove(filePath)
        os.remove(filePath2)   
        VirusExist=1
        stdout.write(u'~~ There are Chinese virus files, so I deleted them !!! ~~')
        
    if isfile(filePath3): 
        os.remove(filePath3) 
        VirusExist=1
        stdout.write(u'~~ There are Chinese virus files, so I deleted them !!! ~~')
    
    if VirusExist == 0:
        stdout.write(u'~~ There are no Chinese viruses. ~~')
        

    
def run():
    delete_chinese_virus()
import sys
sys.path.append('/home/hector/Documents/JUAN/I-Simpa-master/build/bin/')
import libsimpa as ls
import subprocess as sp
import math   
from enum import Enum
import transformation as tr
import xml.etree.ElementTree as ET
import os
import statistics
import shutil 
from time import gmtime, strftime
import random
import re


class SUM_OPERATION(Enum):
  SUM_OPERATION_X   = 1
  SUM_OPERATION_Y   = 2
  SUM_OPERATION_XY  = 3
  SUM_OPERATION_X2  = 4

def get_platform():
  platforms = {
      'linux1' : 'Linux',
      'linux2' : 'Linux',
      'darwin' : 'OS X',
      'win32' : 'Windows'
  }
  if sys.platform not in platforms:
      return sys.platform
  
  return platforms[sys.platform]
platform=get_platform()

p_0=1/pow(20*pow(10,-6),2) #spl do arr
def to_deciBel(wjVal):
  return 10*math.log10(wjVal)
def to_deciBelP0(wjVal):
  return 10*math.log10(wjVal*p_0)
def to_deciBelRsurf(wjVal):
  return 10*math.log10(wjVal/(math.log10(10,-12)))
def GetSumLimit(idBandeFreq,fromTime,toTime,timeTable,tab_wj, operation = SUM_OPERATION.SUM_OPERATION_Y.value):
  sumJ=0
  for idStep in range(len(timeTable)):
    currentTime=timeTable[idStep]
    if currentTime >= fromTime and (currentTime<=toTime or float(toTime) == float(1) ):
      # if counter:
      #   counter=counter+1
      if operation ==SUM_OPERATION.SUM_OPERATION_Y.value:
        sumJ+=tab_wj[idBandeFreq][idStep]
      elif operation ==SUM_OPERATION.SUM_OPERATION_XY.value:
        sumJ+=(tab_wj[idBandeFreq][idStep]*currentTime)
      elif operation ==SUM_OPERATION.SUM_OPERATION_X.value:
        sumJ+=currentTime
      elif operation ==SUM_OPERATION.SUM_OPERATION_X2.value:
        sumJ+=currentTime*currentTime
    if currentTime>toTime and toTime != float(-1.0):
      break
  return sumJ

def runsimulation(path,filepathSpps='C:\\ISIMPA\\Isimpa\\bin\\core\\spps\\spps.exe'):
  sp.check_call([filepathSpps,path])

def getDbReceiver(filepath):
  reader=ls.Gabe_rw()
  if reader.Load(filepath):
    data=reader.ToList()
    if map(len,data)==[len(data[0])]*len(data):
      data=zip(*data)
    return to_deciBelP0(sum(map(lambda x: x[1],data)[1:]))
  return False

def getParameterFromGrid(filePathRoot):
  sl=[]
  for receiverName in os.listdir(filePathRoot+'/Punctual receivers'):
    sl.append(getDbReceiver(filePathRoot+'/Punctual receivers/'+receiverName+'/Sound level.recp'))
  return sl
def function_fitness_grid(sl,alpha=1,beta=1,gamma=1):
  
  minimo=min(sl)
  desta=statistics.stdev(sl)
  return alpha*min(sl)+beta*statistics.mean(sl)-gamma*desta,minimo,desta
def GabeToCsv(filepath,csvpath):
  reader=ls.Gabe_rw()
  if reader.Load(filepath):
    data=reader.ToList()
    if map(len,data)==[len(data[0])]*len(data):
      data=zip(*data)
    fich=open(csvpath,'w')
    for line in data:
      firstcol=True
      for col in line:
        if not firstcol:
          fich.write(",")
        else:
          firstcol=False
        fich.write(str(col))
      fich.write("\n")
    fich.close()
def copytree(src, dst, symlinks=False, ignore=None):
  for item in os.listdir(src):
    s = os.path.join(src, item)
    d = os.path.join(dst, item)
    if os.path.isdir(s):
        shutil.copytree(s, d, symlinks, ignore)
    else:
        shutil.copy2(s, d)
def createDirectory(path):
  try:
    os.mkdir(path)
  except OSError:
      print ("Creation of the directory %s failed" % path)
  else:
      print ("Successfully created the directory %s " % path)
class manager:
  def __init__(self):
    self.dict_sr={}
    self.tree=None
    self.root=None
    self.src=[]
    self.indexscr=0
    self.rootPath=''
    self.rootPathRef='./plantilla/'
    self.rootPathSimulation='C:\\ISIMPA\\Isimpa\\bin\\UserScript\\test1\\simulated-2020-01-22-22-39-27\\'
    self.pathSpps='C:\\ISIMPA\\Isimpa\\bin\\core\\spps\\spps.exe'
    self.platforms=get_platform()
  def rP(self,path):
    if self.platforms=='Linux':
      return  re.sub(r'(\/+|(\\+\/*))', '/', path)
    return path
  def loadRoot(self,path):
    self.tree=ET.parse(path)
    self.root=self.tree.getroot()
    self.getListSources()
  def save(self,path):
    self.tree.write(path)
  def getListSources(self):
    sources=filter(lambda x: x[1].tag=='sources',list(enumerate(self.root.getchildren())))
    if len(sources)>0:
      self.indexscr=sources[0][0]
      self.src=sources[0][1].getchildren()
  def getDirection(self,srcIndex):
    return [float(self.root[self.indexscr][srcIndex].attrib['u']),float(self.root[self.indexscr][srcIndex].attrib['v']),float(self.root[self.indexscr][srcIndex].attrib['w'])]
  def getDirections(self):
    salida=[]
    for i in range(len(self.src)):
      salida+=self.getDirection(i)
    return salida
  def setDirection(self,srcIndex,direction):
    self.root[self.indexscr][srcIndex].set('u', str(direction[0]))
    self.root[self.indexscr][srcIndex].set('v', str(direction[1]))
    self.root[self.indexscr][srcIndex].set('w', str(direction[2]))
    return True
  def setDirections(self,x):
    for i in range(len(self.src)):
      self.setDirection(i,x[int(i*3):int(i*3)+3])
  def createDirectorySimulation(self):
    directoryName=strftime("simulated  %Y-%m-%d-%H-%M-%S/", gmtime())
    self.rootPathSimulation=self.rP(self.rootPath+'/'+directoryName)
    createDirectory(self.rootPathSimulation)
    copytree(self.rootPathRef, self.rootPathSimulation)
    self.loadRoot(self.rP(self.rootPathSimulation+'/config.xml'))
    self.root.set('workingdirectory',self.rootPathSimulation)

  def hillAngleGrid(self,startt=-25,endt=25,alpha=1,beta=1,gamma=1,path='./'):
    directoryName=strftime("hillTest  %Y-%m-%d-%H-%M-%S", gmtime()) +'alpha {} gamma {} beta {}'.format(alpha,gamma,beta)
    self.rootPath=path+directoryName
    #crear carperta general del test
    createDirectory(self.rootPath)
    filename= strftime("hillAngleGrid %Y%m%d%H%M%S", gmtime())+'.csv'
    filename1= strftime("hillAngleGridDebug %Y%m%d%H%M%S", gmtime())+'.csv'
    
    
    
    #creado la primera del tes
    self.createDirectorySimulation()


    state=self.getDirections()
    state=tr.cartesian2sph(state)

    self.save(self.rP(self.rootPathSimulation+'/config.xml'))
    runsimulation(self.rP(self.rootPathSimulation+'/config.xml'),self.pathSpps)
    sl=getParameterFromGrid(self.rootPathSimulation)
    cost,minimo,desta=function_fitness_grid(sl,alpha,beta,gamma)
    with open(self.rP(self.rootPath+'/'+filename),'w') as fd:
      fd.write("speakers {} start {}  end {} alpha {}  beta {} gamma {} minimo {} desviacion estandar {} \n".format(str(len(self.src)),str(startt),str(endt),str(alpha),str(beta),str(gamma),str(minimo),str(desta)))
      fd.write('\n'+','.join(map(str,state))+','+str(cost))
    with open(self.rP(self.rootPath+'/'+filename1),'w') as fd:
      fd.write("speakers {} start {}  end {} alpha {}  beta {} gamma {}  minimo {} desviacion estandar {} \n".format(str(len(self.src)),str(startt),str(endt),str(alpha),str(beta),str(gamma),str(minimo),str(desta)))
    estado=0
    estadot=0
    selSpeaker=0
    repet=10
    j=0
    start=startt*math.pi/180
    end=endt*math.pi/180
    
    while not (estado==len(self.src)-1):
      j=0
      estadot=0
      while j<repet:
        deltaElevation=random.uniform(start,end)
        deltaAzimut=random.uniform(start,end)
        deltas=[(a,b) for a in list([0,deltaElevation]) for b in list([0,deltaAzimut])][1:]
        costoDelta=-1
        stateDelta=list(state)
        for delta in deltas:
          self.createDirectorySimulation()
          self.setDirections(tr.sph2cartesian(state))
          new_state=list(state)
          new_state[2*selSpeaker],new_state[2*selSpeaker+1]=tr.deltasph(state[2*selSpeaker],state[2*selSpeaker+1],delta[0],delta[1])
          self.setDirections(tr.sph2cartesian(new_state)) #cargar las direcciones de los alto farlantes
          
          self.save(self.rP(self.rootPathSimulation+'/config.xml'))
          runsimulation(self.rP(self.rootPathSimulation+'/config.xml'),self.pathSpps)
          
          
          sl=getParameterFromGrid(self.rootPathSimulation)
          new_cost, minimo, desta=function_fitness_grid(sl,alpha,beta,gamma)
          with open(self.rP(self.rootPath+'/'+filename1),'a') as fd:
              fd.write('\n'+'estado {} j {} speaker {} minimo {} desviacion {} '.format(str(estado),str(j),str(selSpeaker),str(minimo),str(desta))+ ','.join(map(str,new_state))+','+str(new_cost))
          if costoDelta==-1 or (costoDelta>0 and costoDelta<new_cost):
              costoDelta=new_cost
              stateDelta=list(new_state)
        if  cost<costoDelta and costoDelta>0:
          cost=costoDelta
          state=list(stateDelta)
          with open(self.rP(self.rootPath+'/'+filename),'a') as fd:
              fd.write('\n'+','.join(map(str,state))+','+str(cost))
          estadot=1           
        else:
            j=j+1
    if estadot==0:
        estado=estado+1
    else:
        estado=0
    selSpeaker=(selSpeaker+1)%len(self.src)
print("hola")
s1=manager()
s1.pathSpps='/home/hector/Documents/JUAN/I-Simpa-master/build/bin/core/spps/spps'
s1.hillAngleGrid()

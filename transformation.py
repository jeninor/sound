import numpy as np
import math

def cartesian2sph(state):
        angle=[0.0]*int(2*len(state)/3)
        for i in range(int(len(state)/3)):
            angle[2*i], angle[2*i+1], r=cart2sph(state[i*3],state[i*3+1],state[i*3+2])
        return angle

def sph2cartesian(state):
    xyz=[0.0]*int(3*len(state)/2)
    for i in range(int(len(state)/2)):
        xyz[3*i], xyz[3*i+1], xyz[3*i+2]=sph2cart(state[i*2],state[i*2+1],1.73)
    return xyz

def cart2sph(x, y, z):
    hxy = np.hypot(x, y)
    r = np.hypot(hxy, z)
    el = math.acos(z/r)
    az = np.arctan2(y, x)
    return az, el, r

def sph2cart( az, el, r):
    rcos_theta = r * np.sin(el)
    x = rcos_theta * np.cos(az)
    y = rcos_theta * np.sin(az)
    z = r * np.cos(el)
    return round(x,2), round(y,2), round(z,2)

def deltasph(az,el,deltaaz=0,deltael=0):
    outaz=az+deltaaz
    
    if outaz>math.pi:
        while outaz>math.pi:
            outaz=outaz-2*math.pi
    elif outaz<math.pi*-1:
        while outaz<math.pi*-1:
            outaz=outaz+2*math.pi
    outel=el+deltael
    if outel>math.pi or  outel<0:
        if outel>=2*math.pi:
            while outel>=2*math.pi:
                outel=outel-2*math.pi
        if outel< -1*math.pi:
            while outel< -1*math.pi:
                outel=outel+2*math.pi
        if outel>math.pi or  outel<0:
            outel=math.pi-(outel%math.pi)
            if outaz>0:
                outaz=outaz-math.pi
            else:
                outaz=outaz+math.pi 
    return outaz,outel
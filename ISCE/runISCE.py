# usr/bin/python3
'''
Title: ISCE processing program
Author: S.W.
Version: 2.3
Describe:
The program based on python3, processing ALOS images(2000 later) with ISCE tools.
'''

import shutil
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
from datetime import datetime
from itertools import combinations

# Initial Data
imageHome = '/media/willie/DDD/ALOS_AVNIR-2PALSAR_data/20161224/'
dataDate = 'Data_date.txt'
DEM = '/media/willie/DDD/SAR/Data/DTM/demLat_N22_N25_Lon_E120_E123.dem.wgs84.xml'
polor = 'HH'
unwrapMethod = 'snaphu_mcf'
max_daydiff = 1000
max_perpendicular_baseline = 1500


def runscript(path, bash_file):  # run bash file
    os.chdir(path)
    start = datetime.now()
    os.system('sh '+bash_file)
    end = datetime.now()
    time = (end-start).seconds
    os.system('echo " - Time taken: %f min -" >> runISCE.log' % (time/60.0))


def imagedata(type, path, polar):  # read IMG or LED data from ALOS image folder
    files = os.listdir(path)
    for fileName in files:
        if type+'-'+polar in fileName:
            imageType = os.path.join(path, fileName)
        elif type+'-ALPSRP' in fileName:
            imageType = os.path.join(path, fileName)
    return imageType


def fbd2fbs(fdb2fbs):
    if fdb2fbs == True:
        FBD2FBS = '<property name="RESAMPLE_FLAG">dual2single</property>'
    else:
        FBD2FBS = ''
    return FBD2FBS


def xml_tmp():  # template of insarApp,xml
    xml_tmp = """<?xml version="1.0" encoding="UTF-8"?>
<insarApp>
    <component name="insar">
        <property name="Sensor name">ALOS</property>
        <component name="master">
            <property name="IMAGEFILE">{masterIMG}</property>
            <property name="LEADERFILE">{masterLED}</property>
            <property name="OUTPUT">{masterDate}.raw</property>
            {mFBD2FBS}
        </component>
        <component name="slave">
            <property name="IMAGEFILE">{slaveIMG}</property>
            <property name="LEADERFILE">{slaveLED}</property>
            <property name="OUTPUT">{slaveDate}.raw</property>
            {sFBD2FBS}
        </component>
        <component name="Dem">
            <catalog>{DEM}</catalog>
        </component>
    </component>
</insarApp>"""
    return xml_tmp


def xml_tmp2():  # template of insarApp,xml
    xml_tmp = """<?xml version="1.0" encoding="UTF-8"?>
<insarApp>
    <component name="insar">
        <property name="Sensor name">ALOS</property>
        <component name="master">
            <property name="IMAGEFILE">{masterIMG}</property>
            <property name="LEADERFILE">{masterLED}</property>
            <property name="OUTPUT">{masterDate}.raw</property>
            {mFBD2FBS}
        </component>
        <component name="slave">
            <property name="IMAGEFILE">{slaveIMG}</property>
            <property name="LEADERFILE">{slaveLED}</property>
            <property name="OUTPUT">{slaveDate}.raw</property>
            {sFBD2FBS}
        </component>
        <component name="Dem">
            <catalog>{DEM}</catalog>
        </component>
            <property name="unwrap">False</property>
            <property name="geocode list">['filt_topophase.flat']</property>
    </component>
</insarApp>"""
    return xml_tmp


def xml_tmp3():  # the isce xml template
    xml_tmp = """<?xml version="1.0" encoding="UTF-8"?>
<insarApp>
    <component name="insar">
        <property name="Sensor name">ALOS</property>
        <property name="doppler method">useDOPIQ</property>
        <property name="posting"> 25 </property>
        <component name="master">
            <property name="IMAGEFILE">{masterIMG}</property>
            <property name="LEADERFILE">{masterLED}</property>
            <property name="OUTPUT">{masterDate}.raw</property>
            {mFBD2FBS}
        </component>
        <component name="slave">
            <property name="IMAGEFILE">{slaveIMG}</property>
            <property name="LEADERFILE">{slaveLED}</property>
            <property name="OUTPUT">{slaveDate}.raw</property>
            {sFBD2FBS}
        </component>
        <component name="Dem">
            <catalog>{DEM}</catalog>
        </component>
        <property name="unwrap">True</property>
        <property name="unwrappername">{unwrapMethod}</property>
        <property name="geocode bounding box">[22.810402, 23.835562, 120.240019, 121.170132]</property>
		<property name="geocode list">['filt_topophase.flat', 'los.rdr', 'topophase.cor', 'phsig.cor']</property>
    </component>
</insarApp>"""
    return xml_tmp


def userfn_tmp():
    userfn = '''import os, sys

def makefnames(date1,date2,sensor):
    dirname = '{DIR}'     #Relative path provided. Change to absolute path if needed.
    root = os.path.join(dirname, date1+'_'+date2)
    iname = os.path.join(root, 'filt_topophase.unw.geo')
    cname = os.path.join(root, 'topophase.cor.geo')
    return iname,cname

def timedict():
    rep = [['ISPLINES',[3],[48]]]
    return rep'''
    return userfn


def example_tmp():
    example = '''<insarProc>
    <master>
        <frame>
            <SENSING_START>{UTC}</SENSING_START>
        </frame>
    </master>
    <runTopo>
        <inputs>
            <RADAR_WAVELENGTH>{wavelength}</RADAR_WAVELENGTH>
            <PEG_HEADING>{heading}</PEG_HEADING>
        </inputs>
    </runTopo>
    <runGeocode>
        <outputs>
            <GEO_WIDTH>{width}</GEO_WIDTH>
            <GEO_LENGTH>{length}</GEO_LENGTH>
        </outputs>
    </runGeocode>
</insarProc>'''
    return example

def readxml(xml):
    tree = ET.ElementTree(file=xml)
    return tree


def xml_kv(xml, nodes):
    for elem in xml.iterfind(nodes):
        text = elem.text.strip()
    return text


def readtable(table):
    with open(table, 'r') as f:
        data = f.readlines()
        row = len(data)
        column = len(data[0].split()) + 1
        record = np.zeros([row, column])
        for i in range(row):
            info = data[i].split()
            try:
                infoYMD = info[0].split('_')
                record[i] = [int(infoYMD[0]), int(infoYMD[1]), info[1], info[2]]
            except:
                None
    if sum(record[0]) == 0:
        table = np.delete(record, 0, 0)
    else:
        table = record
    return table


def str2date(string):
    date = datetime(int(string[:4]), int(string[4:6]), int(string[6:8]))
    return date


def preproc(dataDate, imageHome, DEM, polor):  # do preprocessing to get perpendicular baseline
    global root, log
    imagePath = os.listdir(imageHome)
    bash = open('01_calBperp.sh', 'w')
    os.system('echo "\n- - - - - - - - - - start preprocessing - - - - - - - - - - \n" >> %s' % log)

    # make perpendicular baseline folder
    if not os.path.isdir('Bperp'):
        os.mkdir('Bperp')

    # create pairs (master and slave image)
    with open(dataDate, 'r') as f:
        dates = f.read().strip().split()
    pairs = [[dates[0], d2] for d2 in dates[1:]]
    for pair in pairs:
        pair_folder = os.path.join(root+'/Bperp/', pair[0]+'_'+pair[1])
        if not os.path.isdir(pair_folder):
            os.mkdir(pair_folder)
        for i in imagePath:
            if pair[0] in i:
                if i[-1] == '3':
                    master = os.path.join(imageHome, i)
                    mfbd2fbs = True
                else:
                    master = os.path.join(imageHome, i)
                    mfbd2fbs = False
            if pair[1] in i:
                if i[-1] == '3':
                    slave = os.path.join(imageHome, i)
                    sfbd2fbs = True
                else:
                    slave = os.path.join(imageHome, i)
                    sfbd2fbs = False

        # create xml file
        with open(pair_folder+'/insarApp.xml', 'w') as xml:
            xml.write(xml_tmp().format(masterIMG=imagedata('IMG', master, polor), masterLED=imagedata('LED', master, polor), masterDate=pair[0][2:],
                                       slaveIMG=imagedata('IMG', slave, polor), slaveLED=imagedata('LED', slave, polor), slaveDate=pair[1][2:],
                                       DEM=DEM, mFBD2FBS=fbd2fbs(mfbd2fbs), sFBD2FBS=fbd2fbs(sfbd2fbs)))

            os.system('echo " - create insarApp.xml in %s" >> %s' % (pair_folder, log))

        # write script to process
        bash.write('cd %s\ninsarApp.py insarApp.xml --end=preprocess\necho " - %s preprocessing finished" >> %s\n' %
                   (pair_folder, pair_folder, log))
    bash.close()


def calbperp(pairsFolder, dataDate):
    global root, log
    os.chdir(root)
    dictT = {}
    dictS = {}
    ts = open('TStable.txt', 'w')
    ts.write('       pair  \t\t  Temperal \t\t  Spatial  \n')
    with open(dataDate, 'r') as f:
        d = f.read().strip().split()
        allpairs = list(combinations(d, 2))
        dictT[d[0]] = 0
        dictS[d[0]] = 0
    pairs = os.listdir(pairsFolder)
    for pair in pairs:
        dates = pair.split('_')
        date1 = str2date(dates[0])
        date2 = str2date(dates[1])
        diff_date = (date2 - date1).days
        dictT[date2.strftime('%Y%m%d')] = diff_date
        pair_folder = os.path.join(pairsFolder, pair)
        with open(pair_folder+'/insarProc.xml', 'r') as f:
            for line in f.readlines():
                if line.find('<perp_baseline_top>') != -1:
                    top = float(line[27:42])
                elif line.find('<perp_baseline_bottom>') != -1:
                    bottom = float(line[30:45])
            dictS[date2.strftime('%Y%m%d')] = (top + bottom)/2
    for pair in allpairs:
        ts.write('%-20s %6d %18f \n' %
                 (pair[0]+'_'+pair[1], dictT[pair[1]]-dictT[pair[0]], dictS[pair[1]]-dictS[pair[0]]))
    ts.close()
    os.system('echo " - Create TStable completed - " >> %s' % log)


def geobox(TStable, imageHome, DEM, polor, unwrapMethod):
    table = readtable(TStable)
    temporal = np.sort(table[:, 2])
    spatial = sorted(list(table[:, 3]), key=abs)
    sortT = [list(temporal).index(i) for i in table[:, 2]]
    sortS = [list(spatial).index(i) for i in table[:, 3]]
    sortTS = [sortT[i]+sortS[i] for i in range(len(sortT))]
    index = sortTS.index(min(sortTS))
    ref_master, ref_slave = str(int(table[index, 0])), str(int(table[index, 1]))
    if not os.path.isdir('ref'):
        os.mkdir('ref')
    refgeo = os.path.join('ref', ref_master+'_'+ref_slave)
    os.mkdir(refgeo)
    imagePath = os.listdir(imageHome)
    for path in imagePath:
        if path.find(ref_master) != -1:
            if path[-1] == '3':
                master = os.path.join(imageHome, path)
                mfbd2fbs = True
            else:
                master = os.path.join(imageHome, path)
                mfbd2fbs = False
        if path.find(ref_slave) != -1:
            if path[-1] == '3':
                slave = os.path.join(imageHome, path)
                sfbd2fbs = True
            else:
                slave = os.path.join(imageHome, path)
                sfbd2fbs = False

    with open(refgeo+'/insarApp.xml', 'w') as f:
        f.write(xml_tmp2().format(masterIMG=imagedata('IMG', master, polor), masterLED=imagedata('LED', master, polor), masterDate=ref_master[2:],
                                  slaveIMG=imagedata('IMG', slave, polor), slaveLED=imagedata('LED', slave, polor), slaveDate=ref_slave[2:],
                                  DEM=DEM, mFBD2FBS=fbd2fbs(mfbd2fbs), sFBD2FBS=fbd2fbs(sfbd2fbs)))
    bash = open('02_geobox.sh', 'w')
    bash.write('cd %s\n' % refgeo)
    bash.write('insarApp.py insarApp.xml --steps\n')
    bash.write('echo " - find geobox completed. -" >> %s' % log)
    bash.close()


def runinsar(time, space, TStable, imageHome, DEM, polor, unwrapMethod):  # give threshold
    global root, log
    if not os.path.isdir('isce_out'):
        os.mkdir('isce_out')
    bash = open('03_runinsar.sh', 'w')
    table = readtable(TStable)
    temporal = list(table[:, 2])
    spatial = list(table[:, 3])
    imagePath=os.listdir(imageHome)
    for i in range(len(temporal)):
        if temporal[i] < time and abs(spatial[i]) < space:
            ref_master = str(int(table[i, 0]))
            ref_slave = str(int(table[i, 1]))
            pairname=ref_master+'_'+ref_slave
            pairdir=os.path.join(root, 'isce_out/'+pairname)
            os.mkdir(pairdir)
            for path in imagePath:
                if path.find(ref_master) != -1:
                    if path[-1] == '3':
                        master=os.path.join(imageHome, path)
                        mfbd2fbs=True
                    else:
                        master=os.path.join(imageHome, path)
                        mfbd2fbs=False
                if path.find(ref_slave) != -1:
                    if path[-1] == '3':
                        slave=os.path.join(imageHome, path)
                        sfbd2fbs=True
                    else:
                        slave=os.path.join(imageHome, path)
                        sfbd2fbs=False
            with open(pairdir+'/insarApp.xml', 'w') as f:
                f.write(xml_tmp3().format(masterIMG=imagedata('IMG', master, polor), masterLED=imagedata('LED', master, polor), masterDate=ref_master[2:],
                                          slaveIMG=imagedata('IMG', slave, polor), slaveLED=imagedata('LED', slave, polor), slaveDate=ref_slave[2:],
                                          DEM=DEM, unwrapMethod=unwrapMethod, mFBD2FBS=fbd2fbs(mfbd2fbs), sFBD2FBS=fbd2fbs(sfbd2fbs)))
            bash.write('cd '+pairdir+'\n')
            bash.write('insarApp.py insarApp.xml --steps\n')
            bash.write('echo " - %s processing end" >> %s\n' % (pairdir, log))
    bash.close()


def draw(dataDate, TStable, time, space): #draw the pairs within Time-Space baseline
    table = readtable(TStable)
    day = {}
    with open(dataDate, 'r') as f:
        dates = f.read().strip().split()
        ref_date = str2date(dates[0])
    
    for i in range(len(table)):
        date1 = str2date(str(int(table[i,0])))
        date2 = str2date(str(int(table[i,1])))
        day_diff = table[i,2]
        Bperp = table[i,3]
        if date1 == ref_date:
            day[date1] = 0
            day[date2] = Bperp
        if abs(Bperp) < space and day_diff < time:
            plt.plot([date1,date2], [day[date1],day[date2]], 'c-')

    X = list(day.keys())
    Y = [day[i] for i in X]
    plt.plot(X,Y,'yo', label='ALOS image')
    plt.plot([date1,date2], [day[date1],day[date2]], 'c-', label='Pair')
    plt.legend(loc='lower right')
    plt.title('Temporal-Spatial Baseline (base on 2007.08.18)')
    plt.xlabel('year')
    plt.ylabel('perpendicular baseline (m)')
    #plt.grid(linestyle='-.')
    plt.show()


def ifglist(TStable, time, space):
    if not os.path.isdir('2giant'):
        os.mkdir('2giant')
    table = readtable(TStable)
    with open('2giant/ifg.list', 'w') as f:
        for i in range(len(table)):
            date1 = table[i,0]
            date2 = table[i,1]
            day_diff = table[i,2]
            Bperp = table[i,3]
            if abs(Bperp) <= space and day_diff <= time:
                f.write('%-10d%-10d%-12.4f%-4s\n' %(date1, date2, Bperp, 'ALOS'))

def isce2giant():
    if not os.path.isdir('2giant'):
        os.mkdir('2giant')    
    with open('2giant/userfn.py', 'w') as f:
        f.write(userfn_tmp().format(DIR=os.path.join(root, 'isce_out')))
    xml1 = readxml(os.path.join(root+'/isce_out', os.listdir('isce_out')[0])+'/insarProc.xml')
    xml2 = readxml(os.path.join(root+'/isce_out', os.listdir('isce_out')[0])+'/filt_topophase.flat.geo.xml')
    with open('2giant/example.xml', 'w') as f:
        UTC = xml_kv(xml1, 'master/frame/sensing_start')
        wavelength = xml_kv(xml1, 'runTopo/inputs/radar_wavelength')
        heading = xml_kv(xml1, 'runTopo/inputs/peg_heading')
        width = xml_kv(xml2, 'property[@name="width"]/value')
        length = xml_kv(xml2, 'property[@name="length"]/value')
        f.write(example_tmp().format(UTC=UTC, wavelength=wavelength, heading=heading, width=width, length=length))
      


def log(logfile):
    os.system('echo "  = = = = = = = = = = = = = = = = = = = = = = = = = = =" > runISCE.log')
    os.system('echo "  |                                                   |" >> runISCE.log')
    os.system('echo "  |                                                   |" >> runISCE.log')
    os.system('echo "  |               - ISCE InSAR Project -              |" >> runISCE.log')
    os.system('echo "  |                                                   |" >> runISCE.log')
    os.system('echo "  |                                                   |" >> runISCE.log')
    os.system('echo "  = = = = = = = = = = = = = = = = = = = = = = = = = = =" >> runISCE.log')


if __name__ == '__main__':
    root=os.getcwd()
    log=os.path.join(root, 'runISCE.log')
    #preproc(dataDate, imageHome, DEM, polor)
    #runscript(root, '01_calBperp.sh')
    #calbperp('Bperp', dataDate)
    #geobox('TStable.txt', imageHome, DEM, polor, unwrapMethod)
    #runscript(root, '02_geobox.sh')
    runinsar(max_daydiff, max_perpendicular_baseline, 'TStable.txt', imageHome, DEM, polor, unwrapMethod)
    #runscript(root, '03_runinsar.sh')
    #draw(dataDate, 'TStable.txt', max_daydiff, max_perpendicular_baseline)
    #ifglist('TStable.txt', max_daydiff, max_perpendicular_baseline)
    #isce2giant()

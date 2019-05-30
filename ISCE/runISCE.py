# usr/bin/python3
'''
Title: ISCE processing program
Author: S.W.
Version: 1.0

Describe:
The program based on python3, processing ALOS images(2000 later) with ISCE tools.

'''
import shutil
import sys, os
import numpy as np
import matplotlib.pyplot as plt
#from usrfunc import *
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

def IMG(path, polar):
    files = os.listdir(path)
    for fileName in files:
        if 'IMG-'+polar in fileName:
            break
    return path + '/' + fileName

def LED(path):
    files = os.listdir(path)
    for fileName in files:
        if 'LED-' in fileName:
            break
    return path + '/' + fileName

def xml_tmp(): #the isce xml template
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
        </component>
        <component name="slave">
            <property name="IMAGEFILE">{slaveIMG}</property>
            <property name="LEADERFILE">{slaveLED}</property>
            <property name="OUTPUT">{slaveDate}.raw</property>
        </component>
        <component name="Dem">
            <catalog>{DEM}</catalog>
        </component>
        <property name="unwrap">True</property>
        <property name="unwrappername">{unwrapMethod}</property>
        <property name="geocode bounding box">[22.81040210956758, 23.835561740571222, 120.24001890274782, 121.17013224371266]</property>
		<property name="geocode list">['filt_topophase.flat', 'los.rdr', 'topophase.cor', 'phsig.cor']</property>
    </component>
</insarApp>"""
    return xml_tmp

def runScript(path, bash_file): #run bash file
    os.chdir(path)
    os.system('sh '+bash_file)

def steps1(imageDate, imageHome, DEM, polor, unwrapMethod): #create xml file and script for pairs
    global root
    imagePath = os.listdir(imageHome)
    bash = open('01_calperpbl.sh', 'w')
    bash.write('echo "- - - - start preprocessing - - - " >> '+root+'/runISCE.log\n')
    # make perpendicular baseline folder
    if not os.path.isdir('pbl'):
        os.mkdir('pbl')

    # create pairs (master and slave image)
    with open(imageDate, 'r') as f:
        dates = f.read().strip().split()
    pairs = list(combinations(dates, 2))
    for pair in pairs:
        pair_folder = pair[0][2:] + '_' + pair[1][2:]
        if not os.path.isdir(root + '/pbl/' + pair_folder):
            os.mkdir(root + '/pbl/' + pair_folder)
        os.chdir(root + '/pbl/' + pair_folder)
        for i in imagePath:
            if pair[0] in i:
                master = i
            elif pair[1] in i:
                slave = i
                break

        # create xml file
        with open('insarApp.xml', 'w') as xml:
            xml.write(xml_tmp().format(masterIMG=IMG(imageHome+master,polor), masterLED=LED(imageHome+ \
                master), masterDate=pair[0][2:], slaveIMG=IMG(imageHome+slave,polor), \
                slaveLED=LED(imageHome+slave), slaveDate=pair[1][2:], DEM=DEM, \
                unwrapMethod=unwrapMethod))

        # write script to process
        bash.write('cd ' + os.getcwd() + '\n')
        bash.write('insarApp.py insarApp.xml --end=preprocess\n')
        bash.write('echo "'+pair_folder+' preprocessing end" >> '+root+'/runISCE.log\n')
    bash.close()

def steps2(time, space): # give threshold
    global root
    if not os.path.isdir('isce_out'):
        os.mkdir('isce_out')
    pairs = os.listdir('pbl')
    bash = open('02_runDInSAR.sh', 'w')
    bash.write('echo "- - - - start processing - - - - " >> '+root+'/runISCE.log\n')
    pbl_txt = open('perp_baseline.txt', 'w')
    pbl_txt.write('    pair  \t\t  perp_bl_bottom \t\t  perp_bl_top  \t\t  prep_bl_ave\n')
    for pair in pairs:
        dates = pair.split('_')
        date1 = datetime(int('20'+dates[0][:2]), int(dates[0][2:4]), int(dates[0][4:6]))
        date2 = datetime(int('20'+dates[1][:2]), int(dates[1][2:4]), int(dates[1][4:6]))
        diff_date = (date2-date1).days
        with open('pbl/'+pair+'/isce.log', 'r') as f:
        #with open('/home/willie/DATA/isce_output/'+pair+'/isce.log', 'r') as f:
            for line in f:
                if 'baseline.perp_baseline_bottom' in line:
                    perp_bl_b = line[32:].strip()
                elif 'baseline.perp_baseline_top' in line:
                    perp_bl_t = line[29:].strip()
                    break
        perp_bl_ave = (float(perp_bl_b)+float(perp_bl_t)) / 2
        pbl_txt.write('%-15s %-20s %-20s %-20s \n' %(pair, perp_bl_b, perp_bl_t, str(perp_bl_ave)))
        if abs(perp_bl_ave) <= space and diff_date <= time:
            shutil.copytree(root+'/pbl/'+pair, root+'/isce_out/'+pair)
            bash.write('cd '+root+'/isce_out/'+pair+'\n')
            bash.write('insarApp.py insarApp.xml --start=verifyDEM\n')
            bash.write('echo "'+pair+' preprocessing end" >> '+root+'/runISCE.log\n')
    pbl_txt.close()
    bash.close()

def draw(imageDate, tableTS, time, space): #draw the pairs within Time-Space baseline
    day = {}
    with open(imageDate, 'r') as f:
        dates = f.read().strip().split()
        ref_date = dates[0]

    with open(tableTS, 'r') as f:
        tb = f.readlines()
        for i in range(len(tb)):
            if i > 0:
                line = tb[i].split()
                dates = line[0].split('_')
                date1 = datetime(int('20'+dates[0][:2]), int(dates[0][2:4]), int(dates[0][4:6]))
                date2 = datetime(int('20'+dates[1][:2]), int(dates[1][2:4]), int(dates[1][4:6]))
                perp_bl_ave = float(line[3])
                if int('20'+dates[0]) == int(ref_date):
                    day[date1] = 0
                    day[date2] = perp_bl_ave
        for i in range(len(tb)):
            if i > 0:
                line = tb[i].split()
                dates = line[0].split('_')
                date1 = datetime(int('20'+dates[0][:2]), int(dates[0][2:4]), int(dates[0][4:6]))
                date2 = datetime(int('20'+dates[1][:2]), int(dates[1][2:4]), int(dates[1][4:6]))
                diff_date = (date2-date1).days
                perp_bl_ave = float(line[3])
                if abs(perp_bl_ave) <= space and diff_date <= time:
                    plt.plot([date1,date2],[day[date1], day[date2]], 'b-')
    X = day.keys()
    Y = [day[i] for i in X]
    plt.plot(X,Y,'o', label='ALOS image')
    plt.legend(loc='lower right')
    plt.title('Time-Space Baseline (base on 2007.08.18)')
    plt.xlabel('year')
    plt.ylabel('perpendicular baseline (m)')
    plt.show()

def ifglist(ilist):
    pairs = os.listdir('isce_out')
    ifglist = open(ilist, 'w')
    for pair in pairs:
        dates = pair.split('_')
        date1 = '20' + dates[0][:2] + dates[0][2:4] + dates[0][4:6]
        date2 = '20' + dates[1][:2] + dates[1][2:4] + dates[1][4:6]
        with open('isce_out/'+pair+'/isce.log', 'r') as f:
        #with open('/home/willie/DATA/isce_output/'+pair+'/isce.log', 'r') as f:
            for line in f:
                if 'baseline.perp_baseline_bottom' in line:
                    perp_bl_b = line[32:].strip()
                elif 'baseline.perp_baseline_top' in line:
                    perp_bl_t = line[29:].strip()
                    break
        perp_bl_ave = (float(perp_bl_b)+float(perp_bl_t)) / 2
        ifglist.write('%-10s%-10s%-12.4f%-4s\n' %(date1, date2, perp_bl_ave, 'ALOS'))
    ifglist.close()

if __name__ == '__main__':
    root = os.getcwd()
    #os.system('echo "- - - - ISCE InSAR Project - - - -" > runISCE.log')
    #steps1(dataDate, imageHome, DEM, polor, unwrapMethod)
    #runScript(root, '01_calperpbl.sh')
    #steps2(max_daydiff, max_perpendicular_baseline)
    #runScript(root, '02_runDInSAR.sh')
    #draw(dataDate, 'perp_baseline.txt', max_daydiff, max_perpendicular_baseline)
    ifglist('ifg.list')

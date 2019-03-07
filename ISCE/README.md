# ISCE2.2.0 安裝說明

>最後更新：03/08/2019<br>

[ISCE](https://github.com/isce-framework/isce2) 安裝可分為三部份，分別為安裝前設定、安裝主程式與環境變數設定。  
本說明是將ISCE2.2.0安裝於Ubuntu16.04上，其他版本與系統可能會有不相容的問題，請見諒。
<br><br>

## 1. 安裝前設定 
ISCE是由Python3所架構的程式，它由許多函式庫組成，因此在安裝主程式之前，須先將關聯函式庫裝好。  
以下為ISCE需要用到的函式庫：
* gcc >= 4.8+
* fftw >= 3.2.2
* Python >= 3.5（GDAL、Scipy、h5py、matplotlib）
* scons >= 2.0.1
* curl - 自動下載DEM
* GDAL >= 2.2
* Motif、hdf5、cython3  

<br>利用apt直接安裝（除了GDAL）。
<pre>
sudo apt update
sudo apt upgrade
sudo apt install -y gfortran libmotif-dev libhdf5-dev libfftw3-dev scons python3 cython3 python3-scipy python3-matplotlib python3-h5py python3-gdal python3-pip curl
</pre>
因apt下載下來的GDAL版本會過舊無法使用，故GDAL需獨立安裝，本說明所使用版本為2.2.4。
<pre>
wget http://download.osgeo.org/gdal/2.2.4/gdal-2.2.4.tar.gz
tar -zxvf gdal-2.2.4.tar.gz
sudo ./configure
sudo make
sudo make install
</pre>

## 2. 安裝主程式
主程式是利用scons進行安裝，故需建立ISCE的scons設定檔，檔名為SConfigISCE。
本說明是將ISCE安裝於 /opt 目錄下，可自行改變安裝位置。
<pre>
PRJ_SCONS_BUILD=/opt/isce-2.2.0/build
PRJ_SCONS_INSTALL=/opt/isce-2.2.0/install/isce

LIBPATH=/usr/lib/x86_64-linux-gnu /usr/lib /usr/lib/x86_64-linux-gnu/hdf5/serial
CPPPATH=/usr/include/x86_64-linux-gnu /usr/include /usr/include/python3.6m /usr/include/hdf5/serial /usr/include/gdal
FORTRANPATH=/usr/include /usr/lib/gcc/x86_64-linux-gnu/7/finclude

FORTRAN=/usr/bin/gfortran
CC=/usr/bin/gcc
CXX=/usr/bin/g++

MOTIFLIBPATH = /usr/lib/x86_64-linux-gnu
X11LIBPATH = /usr/lib/x86_64-linux-gnu
MOTIFINCPATH = /usr/include/Xm
X11INCPATH = /usr/include/X11

ENABLE_CUDA=False
</pre>

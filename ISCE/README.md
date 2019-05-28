# ISCE2.2.0 安裝說明

>最後更新：05/28/2019

[ISCE官方GitHub](https://github.com/isce-framework/isce2)

ISCE安裝可分為三部份，分別為安裝前設定、安裝主程式與環境變數設定。  
本說明是將ISCE2.2.0安裝於Ubuntu16.04上，其他版本與系統可能會有不相容的問題，請見諒。
<br><br>

## 1. 安裝前設定 
ISCE是由Python3所架構的程式，它由許多函式庫組成，因此在安裝主程式之前，須先將關聯函式庫裝好。  
以下為ISCE需要用到的函式庫：
* gcc >= 4.8+
* fftw >= 3.2.2
* Python >= 3.5（GDAL、Scipy、h5py、matplotlib）
* scons >= 2.0.1
* cURL - 自動下載DEM
* GDAL >= 2.2
* Motif、hdf5、cython3  

<br>利用apt安裝（除了GDAL）。
<pre>
$ sudo apt update
$ sudo apt upgrade
$ sudo apt install -y gfortran libmotif-dev libhdf5-dev libfftw3-dev scons python3 cython3 python3-scipy python3-matplotlib  python3-h5py python3-gdal python3-pip curl
</pre>  
因利用apt下載下來的GDAL版本會過舊無法使用，故GDAL需獨立安裝，本說明所使用版本為2.2.4。
<pre>
$ wget http://download.osgeo.org/gdal/2.2.4/gdal-2.2.4.tar.gz
$ tar -zxvf gdal-2.2.4.tar.gz
$ sudo ./configure
$ sudo make
$ sudo make install
</pre>

## 2. 安裝主程式
主程式是利用scons進行安裝，故需建立ISCE的scons設定檔，將檔名命名為SConfigISCE，並放置於isce2.2.0主目錄下。  
>本說明是將ISCE安裝於 /opt 目錄下，可自行改變安裝位置。
<pre>
# SConfigISCE
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
編輯完後，便能開始安裝程序。
<pre>
$ cd /opt/isce-2.2.0
$ export PYTHONPATH=/opt/isce-2.2.0/configuration
$ export SCONS_CONFIG_DIR=/opt/isce-2.2.0
$ scons install --skipcheck
</pre>
## 3. 設定環境變數
程式安裝完後，需將其加至環境變數才能直接使用。
<pre>
$ export ISCE_ROOT=/opt/isce-2.2.0/install
$ export ISCE_HOME=$ISCE_ROOT/isce
$ export PATH=$ISCE_HOME/bin:$ISCE_HOME/applications:$PATH
$ export PYTHONPATH=$ISCE_ROOT:$ISCE_HOME/applications:$ISCE_HOME/component
</pre>  
由於在計算干涉時，ISCE會自動從EarthData下載干涉所需的DEM，故我們需將連線與權限設定好，才不會執行錯誤。
1. 首先至[EarthData](https://urs.earthdata.nasa.gov/)申請帳密。
2. 把LPDAAC的權限打開。（LP DAAC Data Pool 、 LP DAAC OpenDAP）  
>Applications -> Authorized Apps -> Search LP DAAC -> APPROVE
3. 設定.netrc (user_id 與 user_password 為使用者自行輸入)。
<pre>
$ cd ~
$ touch .netrc
$ echo “machine urs.earthdata.nasa.gov login user_id passward user_password” > .netrc
$ chmod 0600 .netrc
</pre>

以上都做完後，ISCE便安裝完成，可開始使用。


insarApp.py insarApp.xml --steps

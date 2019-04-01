# GIAnT 安裝說明

>最後更新：04/01/2019

[GIAnT官方網站](http://earthdef.caltech.edu/projects/giant)

GIAnT安裝可分為兩部份，分別為安裝前設定與環境變數設定。  
本說明是將GIAnT安裝於Ubuntu16.04上，其他版本與系統可能會有不相容的問題，請見諒。
<br><br>

## 1. 安裝前設定 
GIAnT是由Python2所架構的程式，它由許多函式庫組成，因此在安裝主程式之前，須先將關聯函式庫裝好。  
以下為GIAnT需要用到的函式庫：
* gcc >= 4.6+
* Python >= 2.6（Numpy、Scipy、h5py、matplotlib、pygrib、pywavelets）
* cython
* LXML
* ffmpeg、mencoder、pyresample、HDFview、pykml、ImageMagick (optional)

<br>利用apt跟easy_install安裝。
<pre>
$ sudo apt update
$ sudo apt upgrade
$ sudo apt install -y python-dev python-pip
$ sudo apt install -y python-numpy python-scipy cython python-matplotlib python-h5py zlib1g zlib1g-dev libpng12-0 libpng12-dev libjasper1 libjasper-dev libopenjpeg-dev libgrib-api-dev libgrib-api-tools python-mpltoolkits.basemap python-grib python-pywt python-lxml
$ pip install pyproj
$ sudo apt install -y ffmpeg mencoder hdfview imagemagick
$ sudo easy_install pyresample
$ sudo easy_install pykml
</pre>  


## 2. 設定環境變數與安裝主程式
將主程式下載至欲安裝目錄下，設定環境變數後執行setup.py即完成。
>本說明是將GIAnT安裝於 /opt 目錄下，可自行改變安裝位置。

<pre>
$ mkdir /opt/giant
$ cd /opt/giant
$ svn co http://earthdef.caltech.edu/svn/giant
$ cd giant/GIAnT
$ svn co http://earthdef.caltech.edu/svn/pyaps

$ export GIAnT=/opt/giant/GIAnT
$ export PATH=$GIAnT:$PATH
$ export PYTHONPATH=$GIAnT

$ python setup.py build_ext
</pre>

以上都做完後，GIAnT便安裝完成，可開始使用。

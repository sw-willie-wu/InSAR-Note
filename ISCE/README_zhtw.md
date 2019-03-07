# ISCE2.2.0 安裝說明

>最後更新：03/08/2019<br>

[ISCE](https://github.com/isce-framework/isce2) 安裝可分為三部份，分別為安裝前設定、安裝主程式與環境變數設定。  
本說明是將ISCE2.2.0安裝於Ubuntu16.04上，其他版本與系統可能會有不相容的問題，請見諒。
<br><br>

## 1. 安裝前設定 
ISCE是由Python3所架構的程式，它由許多函式庫組成，因此在安裝主程式之前，須先將關聯函式庫裝好。  
以下為ISCE需要用到的函式庫需求：
* gcc >= 4.8+ (with C++11 support)
* fftw >= 3.2.2 (with single precision support)
* Python >= 3.5 (3.6 preferred)
* scons >= 2.0.1
* curl - for automatic DEM downloads
* GDAL and its Python bindings >= 2.2






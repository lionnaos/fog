import os
from datetime import datetime
import re
import copy
import glob
from models import session, Observation
outformat = [
    'year', 'month', 'day', 'hour', 'minute', 'secend', 'wind_direction', 'wind_speed', 'wind_range',
    'rvr', 'vis', 'cloud_heigt', 'cloud', 'qnh', 'qfe', 'tem', 'td', 'rh', 'weather'
]
       
weather = [
    'NSW', 'IC', 'FG', 'BR', 'SA', 'DU', 'HZ', 'FU', 'VA', 'SQ',
    'PO', 'FC', 'TS', 'FZFG', 'BLSN', 'BLSA', 'BLDU', 'DRSN', 'DRSA',
    'DRDU', 'MIFG', 'BCF', 'PRFG'
]
weatherWithIntensity = [
    'RA', 'DZ', 'SN', 'SG', 'PL', 'DS', 'SS', 'TSRA', 'TSSN', 'TSPL',
    'TSGR', 'TSGS', 'SHRA', 'SHSN', 'SHGR', 'SHGS', 'FZRA', 'FZDZ'
]

class Grammar(object):
    R09data = re.compile(r'(.*)MID')  
    weatherdata = re.compile(r'R27(.*)')  
    time = re.compile(r'(\d{4}:\d{2}:\d{2})')
    wind = re.compile(r'((?:VRB|\d{3})/\d{1,2})\s+(\d{3}V\d{3})?')   #包含风向、风速、风向范围
    rvr_vis_cloudheigt = re.compile(r'(\d{4})\s((?:P2000|\d{4}[DNU]|\d{4}V\d{4}[DNU]))?\s*(\d{4,5})\s*(\d{2,4})')    
    cloud = re.compile(r'NCD|((?:FEW|SCT|BKN|OVC)\d{1,3})+') 
    qnh_qfe_te_td_rh = re.compile(r'(\d{4}.\d)(\d{4}.\d)(\d{2}.\d|\d{1}.\d)/(\d{2}.\d|\d{1}.\d)\s*(\d{2}.\d|\d{2,3})')   #qnh修正海平面气压 qfe场压             
    weather = re.compile(r'([-+]?{}|{})'.format('|'.join(weatherWithIntensity), '|'.join(weather)))                    


def main():    
    filenames = find_filenames('./awosdata01')
    for files in filenames:
        with open(files, encoding='gb18030', errors='ignore') as f:
            print(files)
            filename = os.path.basename(files)
            filename, _ = os.path.splitext(filename)
            for lines in f:
                #print(line)
                validator(filename,lines)
        session.commit()
        session.close()
        f.close()

def find_filenames(path):
    pathname = os.path.join(path, '*.RTW')
    filenames = glob.glob(pathname)
    return filenames

def validator(filename, lines):
    grammar = Grammar
    ob = Observation()
    if grammar.R09data.match(lines):
        line = grammar.R09data.match(lines).group(1)
        if grammar.time.search(line):
            tw = grammar.time.search(line)
            time = filename + tw.group(1)
            ob.created = datetime.strptime(time, "%Y-%m%d%H:%M:%S")

        if grammar.wind.search(line):
            ob.wind = grammar.wind.search(line).group(0)

        if grammar.rvr_vis_cloudheigt.search(line):
            ob.rvr = grammar.rvr_vis_cloudheigt.search(line).group(1)
            ob.rvrtrend = grammar.rvr_vis_cloudheigt.search(line).group(2)
            ob.vis = grammar.rvr_vis_cloudheigt.search(line).group(3)
            ob.clh = grammar.rvr_vis_cloudheigt.search(line).group(4)

        if grammar.cloud.search(line):
            ob.cloud = grammar.cloud.search(line).group(1)

        if grammar.qnh_qfe_te_td_rh.search(line):
            ob.qnh = grammar.qnh_qfe_te_td_rh.search(line).group(1)
            ob.qfe = grammar.qnh_qfe_te_td_rh.search(line).group(2)
            ob. tem = grammar.qnh_qfe_te_td_rh.search(line).group(3)
            ob.td = grammar.qnh_qfe_te_td_rh.search(line).group(4)
            ob.rh = grammar.qnh_qfe_te_td_rh.search(line).group(5)
        
    if grammar.weatherdata.search(lines):
        line = grammar.weatherdata.search(lines).group(1)
        if grammar.weather.search(line):
            ob.weather = grammar.weather.search(line).group(1)

    session.add(ob)

                                                       

if __name__ == '__main__':
    main()
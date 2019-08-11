import os
import datetime
import re
import copy
import glob
from models import session, Observation
outformat = [
    'year', 'month', 'day', 'hour','minute','secend','wind_direction','wind_speed',
    'wind_range','rvr','vis','cloud_heigt','cloud','qnh','qfe','tem','td','rh','weather'
]
       
weather = [
    'NSW', 'IC', 'FG', 'BR', 'SA', 'DU', 'HZ', 'FU', 'VA', 'SQ',
    'PO', 'FC', 'TS', 'FZFG', 'BLSN', 'BLSA', 'BLDU', 'DRSN', 'DRSA',
    'DRDU', 'MIFG', 'BCF', 'PRFG'
]
weatherWithIntensity = [
    'DZ', 'RA', 'SN', 'SG', 'PL', 'DS', 'SS', 'TSRA', 'TSSN', 'TSPL',
    'TSGR', 'TSGS', 'SHRA', 'SHSN', 'SHGR', 'SHGS', 'FZRA', 'FZDZ'
]

class Grammar(object):
     time = re.compile(r'(\d{4}:\d{2}:\d{2})R09')
     wind = re.compile(r'(R09:\d{}')
     wind_range = re.compile(r'\b(\d{3}V\d{3})\b')
     rvr = re.compile(r'\b(2000|[0-1][0-9][0-9][0-9])\b')
     vis_cloud_heigt = re.compile(r'\b(\d{2}000)(\d{3})\b')
     vis = re.compile(r'\b(\d{4}|0\d{3})\b')
     cloud_heigt = re.compile(r'\b(\d{3}|\d{4})\b')
     cloud = re.compile(r'\b(?:FEW|SCT|BKN|OVC|VV)\d{3}\b') 
     qnh_qfe_tem_td = re.compile(r'\b(\d{4}.\d)(\d{4}.\d)(\d{2}.\d|\d{1}.\d)/(\d{2}.\d|\d{1}.\d)\b')   #qnh修正海平面气压 qfe场压   
     rh = re.compile(r'\b(\d{2}.\d|\d{2})\b')              
     weather = re.compile(r'([-+]?({})[0-9]?)|(({})[0-9]?)'.format('|'.join(weatherWithIntensity), '|'.join(weather)))                    

def main():
    outputfile()
    filenames = find_filenames('E:/fcf/awosdata')
    #print(filenames)
    open_file(filenames[0])

#输出文件
def outputfile():    
    outfile = 'e:/fcf/fog/outfile.txt'
    w = open(outfile,'w+')
    w.write('year  month  day  hour  minute  secend  wind_direction  wind_speed  wind_range  rvr  vis  cloud_heigt  cloud  qnh  qfe  tem  td  rh  weather \n')

def find_filenames(path):
    pathname = os.path.join(path, '*.RTW')
    filenames = glob.glob(pathname)
    return filenames

def open_file(filepath, grammar=Grammar):

    #for filename in filenames:
    with open(filepath) as f:
        filename = os.path.basename(filepath)
        filename, _ = os.path.splitext(filename)
        for line in f:
            lines = line.strip().split() #strip去除收尾的空格或换行符，split对字符串中间的空格进行切片
            #print(lines)
            def validator(lines):
                #print(lines)
                cloud = []     
                out = dict.fromkeys(outformat, 999999)  
                for key in lines:
                    if key == 'MID':
                        break

                    ob = Observation()

                    if grammar.weather.match(key):
                        out['weather'] = key[0:3]

                    pattern = getattr(grammar, 'time')
                    if grammar.time.match(key):
                        tw = grammar.time.match(key)
                        time = filename + tw.group(1)
                        dt = datetime.datetime.strptime(time, "%Y-%m%d%H:%M:%S")
                        ob.created = dt
                        #print(dt)
                    if grammar.wind_range.match(key):
                        out['wind_range'] = key
                        #print(wind_range.group(1)) 

                    if grammar.wind_range.match(key):
                        out['wind_range'] = key
                        #print(wind_range.group(1)) 

                    if grammar.rvr.match(key) and ((grammar.wind_range.match(key) == None and line.index(key) == 1) or (grammar.wind_range.match(key) and line.index(key)==2)):
                        out['rvr'] = key
                        viss = line[line.index(key)+1]
                        clh = line[line.index(key)+2]
                        if grammar.vis_cloud_heigt.match(viss): 
                            vis_clh =grammar.vis_cloud_heigt.match(viss)
                            out['vis'] = vis_clh.group(1)
                            out['cloud_heigt'] = vis_clh.group(2)
                            #print('vis_cloud_heigt:vis',vis.group(1))
                            #print('vis_cloud_heigt:cloud_heigt',vis.group(2))                     
                        elif grammar.vis.match(viss) and grammar.cloud_heigt.match(clh):
                            out['vis'] = viss
                            out['cloud_heigt'] = clh                    
                            #print('vis',vis.group(1))
                            #print('cloud_heigt',cloud_heigt.group(1))                   
                    if grammar.cloud.match(key):
                        clo = grammar.cloud.match(key)
                        cloud.append(key)
                        out['cloud'] = cloud
                        #print(cloud)        

                    if grammar.qnh_qfe_tem_td.match(key):
                        q = grammar.qnh_qfe_tem_td.match(key)
                        out['qnh'] = q.group(1)
                        out['qfe'] = q.group(2)
                        out['tem'] = q.group(3)
                        out['td'] = q.group(4)
                        #print(qnh,qfe,tem,td)
                        rhh = line[line.index(key)+1]

                        if grammar.rh.match(rhh):
                            out['rh'] = rhh
                            #print(rh) 

                    session.add(ob)
                    #print(out)
                session.commit()

            
                                        
            validator(lines)

            # out = dict.fromkeys(outformat, 999999)  
            # out['year'] = year
            # out['month'] = month

            
#         
#                 

#                 if int(out['vis']) <= 800:
#                     print(out)
#                     for i in out:
#                         w.write(str(out[i])+'  ')
#                     w.write('\n')



if __name__ == '__main__':
    main()

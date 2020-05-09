import os
import sqlite3
import numpy
import datetime
import csv

class SQL_method:
    '''
    function: 可以实现对数据库的基本操作
    '''
    def __init__(self, sqlName, tableName, start, end):
    #def __init__(self, dbName, tableName, data, columns, COLUMNS, Read_All=True):   
        '''
        function: 初始化参数
        dbName: 数据库文件名 
        tableName: 数据库中表的名称
        data: 从csv文件中读取且经过处理的数据
        '''

        self.dbName = dbName
        self.tableName = tableName
        self.daystart = start
        self.dayend = end

    def searchData(self):
        '''
        function: 查找特定的数据
        '''
        # 连接数据库
        connect = sqlite3.connect(dbName)
        # 创建游标
        cur = connect.cursor()
        cur.execute("select * from {} where created >='{}' and created <= '{}' and vis3>0 and vis3<1000 ".format(self.tableName, self.daystart, self.dayend))
        data = cur.fetchall()
        # print(data)
        # for item in cur:
        #     print(item)
        # 关闭游标
        cur.close()
        #断开数据库连接
        connect.close()
        return data

def fogendtime(data):
    '''
    function: 查找每次大雾过程的结束时间
    '''
    newdata = []  #生成一个空列表，用来放加入每次过程的结束时间数据
    newdata = data
    for i in range(len(data)):
        if i == range(len(data)):   #最后一个数据
            id = int(data[i][0])+1
            enddata = SQL.searchEnddata(id)
            newdata.extend(enddata)
        else:
            dnumber = int(data[i][0]) - int(data[i-1][0])  #判断大雾id数据是否连续
            if dnumber != 1:  #数据不连续提取结束时间
                id = int(data[i-1][0])+1
                enddata = SQL.searchEnddata(id)
                newdata.extend(enddata)
    newdata.sort()
    # for i in range(len(newdata)):
    #     print(newdata[i])
    return newdata

def fogDuration(outfilename, data):
    '''
    function: 查找每次大雾过程的持续时间
    '''
    fogcollection = {}
    count = num = 1
    for i in range(len(data)):
        fogcollection.setdefault(count,[]).append(data[i])
        if (i < len(data)-1):
            curtime = datetime.datetime.strptime(data[i][1], '%Y-%m-%d %H:%M:%S') #当前时次
            nexttime = datetime.datetime.strptime(data[i+1][1], '%Y-%m-%d %H:%M:%S')  #后一时次
            dtime = nexttime- curtime #后者减前者
            if dtime > datetime.timedelta(hours=4):  #判断当大雾的间隔时间在4小时以内时，按一场大雾统计
                count = count+1
    fognum = 0
    for i in range(1,count+1):
        # print(len(fogcollection[i]))
        starttime = datetime.datetime.strptime(fogcollection[i][0][1], '%Y-%m-%d %H:%M:%S')
        endtime = datetime.datetime.strptime(fogcollection[i][len(fogcollection[i])-1][1], '%Y-%m-%d %H:%M:%S')
        durationtime = endtime - starttime 
        #print( durationtime)
        if durationtime > datetime.timedelta(hours = 0.5):
            fognum = fognum + 1
            output_data(outfilename, [fognum] + [starttime] + [endtime] + [durationtime])
            for j in range(0,len(fogcollection[i])):
                output_data(outfilename, fogcollection[i][j])
                # print(fogcollection[i][j])


def output_data(outfilename, data):
    '''
    function: 导出大雾的数据 并 将结果返回
    '''
    # 打开文件
    #self.outfilename = outfileName_data
    with open(outfilename,"a",newline="") as file:   #只需要将之前的”w"改为“a"即可，代表追加内容
            write = csv.writer(file)
            write.writerow(data)


if __name__ == "__main__":

    dbName = "IMS_VIS.sqlite3"
    tableName = "VIS_1min"
    outfileName = "IMS_vis3_fog_duration.csv"

    #按日期查找
    start = '2019-12-01'
    end = '2020-03-01'
    EN_columns = "id", "time", "vis1", "vis2", "vis3", "vis4"
    start = datetime.datetime.strptime(start,'%Y-%m-%d')
    end = datetime.datetime.strptime(end,'%Y-%m-%d')
    
    # ================= 创建数据库对象 ==================
    # 如果文件存在,删除文件
    if os.path.exists(outfileName):  
        print("删除文件")
        os.remove(outfileName) 
    #打开输出文件，并EN_columns用于数据的格式化输出，为输出的表头
    output_data(outfileName, EN_columns)

    # ================= 创建数据库对象 ==================
    SQL = SQL_method(dbName, tableName, start, end)
    data = SQL.searchData()
    # add_enddata = fogendtime(data)
    # print(data)
    fogDuration(outfileName, data)
    # SQL.fogData(start, end, tableName)

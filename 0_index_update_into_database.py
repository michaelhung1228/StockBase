import requests, os, bs4, sys
import re, time
from datetime import datetime
from datetime import timedelta
import sqlite3

input_arg = sys.argv

conn = sqlite3.connect('TAIEX.db')
c = conn.cursor()

#TEMP date clean up
sql_cmd = 'DELETE FROM TAIEX WHERE TEMP = 1'
c.execute(sql_cmd)
conn.commit()

url1_base = 'http://www.twse.com.tw/exchangeReport/FMTQIK?response=html&date=' #成交金額, 收盤指數, 漲跌點數
url2_base = 'http://www.twse.com.tw/indicesReport/MI_5MINS_HIST?response=html&date=' #開盤, 最高, 最低, 收盤指數
DateSearch = re.compile(r'(\d\d\d\d)(\d\d)(\d\d)')
delta_1day = timedelta(days = 1) #delta_1day
cursor = c.execute('SELECT max(date_ID) FROM TAIEX')
max_id = cursor.fetchone()[0]
max_id = max_id.replace('-','')
print(max_id)
Date = DateSearch.search(max_id)
Start_date = datetime(int(Date.group(1)), int(Date.group(2)), int(Date.group(3)))
Start_date = Start_date + delta_1day

former_url = None
Start_date_ptr = Start_date
End_date = datetime.today()
print('Print index from ' + str(Start_date) + ' to ' + str(End_date))

while Start_date_ptr <= End_date:
    
    url = url2_base + str(Start_date_ptr.year) + Start_date_ptr.strftime("%m")
    if url != former_url:
        url = url2_base + str(Start_date_ptr.year) + Start_date_ptr.strftime("%m%d")
        print('Cool down for requesting web content for url1')
        time.sleep(3)
        res = requests.get(url)
        former_url = url2_base + str(Start_date_ptr.year) + Start_date_ptr.strftime("%m")
        if res.raise_for_status() != None:
            continue
    soup = bs4.BeautifulSoup(res.text, "lxml")
    trs = soup.find_all('tr')
    #print(trs[0])
    for tr in trs:
        soup1 = bs4.BeautifulSoup(str(tr), "lxml")
        tds = soup1.find_all('td')
        if tds == []:
        	continue
        #print(tds[0].getText().strip())
        date_str_from_table = tds[0].getText().strip()
        date_str = str(Start_date_ptr.year - 1911) + '/' + Start_date_ptr.strftime("%m") + '/' + Start_date_ptr.strftime("%d")
        if date_str == date_str_from_table:
            sql_cmd = 'INSERT INTO TAIEX (date_ID, open_index, highest_index, lowest_index, close_index) VALUES (\'' + str(Start_date_ptr.year) + '-' + \
            Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d") + '\',' + tds[1].getText().strip().replace(',','') + ',' \
                                                                                + tds[2].getText().strip().replace(',','') + ',' \
                                                                                + tds[3].getText().strip().replace(',','') + ',' \
                                                                                + tds[4].getText().strip().replace(',','') + ')'
            print(sql_cmd)
            c.execute(sql_cmd)
            conn.commit()
            print(date_str + ' ' + tds[1].getText().strip() + ' ' + tds[2].getText().strip() + ' ' + tds[3].getText().strip() + ' ' + tds[4].getText().strip())
            break

    Start_date_ptr = Start_date_ptr + delta_1day

Start_date_ptr = Start_date
former_url = None
while Start_date_ptr <= End_date:
    url = url1_base + str(Start_date_ptr.year) + Start_date_ptr.strftime("%m")
    if url != former_url:
        url = url1_base + str(Start_date_ptr.year) + Start_date_ptr.strftime("%m%d")
        print('Cool down for requesting web content for url2')
        time.sleep(3)
        res = requests.get(url)
        former_url = url1_base + str(Start_date_ptr.year) + Start_date_ptr.strftime("%m")
        if res.raise_for_status() != None:
            continue
    soup = bs4.BeautifulSoup(res.text, "lxml")
    trs = soup.find_all('tr')
    for tr in trs:
        soup1 = bs4.BeautifulSoup(str(tr), "lxml")
        tds = soup1.find_all('td')
        if tds == []:
            continue
        date_str_from_table = tds[0].getText().strip()
        date_str = str(Start_date_ptr.year - 1911) + '/' + Start_date_ptr.strftime("%m") + '/' + Start_date_ptr.strftime("%d")
        if date_str == date_str_from_table:
            sql_cmd = 'UPDATE TAIEX set Volume =' + tds[2].getText().strip().replace(',','') +\
                                  ',Total =' + tds[5].getText().strip().replace(',','') + ' where date_ID =\''\
                                   + str(Start_date_ptr.year) + '-' + Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d") + '\''
            print(sql_cmd)
            c.execute(sql_cmd)
            conn.commit()
            print(date_str + ' ' + tds[2].getText().strip() + ' ' + tds[5].getText().strip())
            break
    Start_date_ptr = Start_date_ptr + delta_1day

MA_list = [3,6,18,54,108,216]
for mean_average in MA_list:
    Start_date_ptr = Start_date
    while Start_date_ptr <= End_date:
        cur_date_str = str(Start_date_ptr.year) + '-' + Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d")
        sql_cmd = 'select rowid from TAIEX where date_ID =\'' + cur_date_str + '\''
        c.execute(sql_cmd)
        rowid = c.fetchone()
        if rowid != None:
            #print(str(rowid[0]) + ' ' + cur_date_str)
            total = 0.0
            for i in range(mean_average):
                #print(i)
                if rowid[0] < mean_average:
                    break
                sql_cmd = 'select close_index from TAIEX where rowid =' + str(rowid[0] - i)
                #print(sql_cmd)
                c.execute(sql_cmd)
                total = total + c.fetchone()[0]
                #print(total)
            if rowid[0] < mean_average:
                Start_date_ptr = Start_date_ptr + delta_1day
                continue
            total = total / mean_average
            print(str(rowid[0]) + ' ' + cur_date_str + ' ' + str(total))
            sql_cmd = 'UPDATE TAIEX set MA' + str(mean_average) + '=' + str(total) + ' where rowID =' + str(rowid[0])
            #print(sql_cmd)
            c.execute(sql_cmd)
            conn.commit()
        Start_date_ptr = Start_date_ptr + delta_1day

# DI computation
Start_date_ptr = Start_date
while Start_date_ptr <= End_date:
    cur_date_str = str(Start_date_ptr.year) + '-' + Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d")
    sql_cmd = 'select rowid from TAIEX where date_ID =\'' + cur_date_str + '\''
    c.execute(sql_cmd)
    rowid = c.fetchone()
    if rowid != None:
        sql_cmd = 'select highest_index from TAIEX where rowid =' + str(rowid[0])
        c.execute(sql_cmd)
        highest_index = c.fetchone()[0]
        sql_cmd = 'select lowest_index from TAIEX where rowid =' + str(rowid[0])
        c.execute(sql_cmd)
        lowest_index = c.fetchone()[0]
        sql_cmd = 'select close_index from TAIEX where rowid =' + str(rowid[0])
        c.execute(sql_cmd)
        close_index = c.fetchone()[0]
        DI = (highest_index + lowest_index + close_index*2)/4
        sql_cmd = 'UPDATE TAIEX set DI =' + str(DI) + ' where rowID =' + str(rowid[0])
        c.execute(sql_cmd)
        conn.commit()
        print(DI)
    Start_date_ptr = Start_date_ptr + delta_1day
#EMA12 computation
Start_date_ptr = Start_date
while Start_date_ptr <= End_date:
    cur_date_str = str(Start_date_ptr.year) + '-' + Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d")
    sql_cmd = 'select rowid from TAIEX where date_ID =\'' + cur_date_str + '\''
    c.execute(sql_cmd)
    rowid = c.fetchone()
    if rowid != None:
        sql_cmd = 'select EMA12 from TAIEX where rowid =' + str(rowid[0] - 1)
        c.execute(sql_cmd)
        EMA12_preday = c.fetchone()
        print(EMA12_preday)
        if (EMA12_preday != None) and (EMA12_preday[0] != None):
            sql_cmd = 'select DI from TAIEX where rowid =' + str(rowid[0])
            c.execute(sql_cmd)
            DI = c.fetchone()[0]
            EMA12 = (EMA12_preday[0]*11 + DI*2)/13
            sql_cmd = 'UPDATE TAIEX set EMA12 =' + str(EMA12) + ' where rowID =' + str(rowid[0])
            c.execute(sql_cmd)
            conn.commit() 
            print(EMA12)
        else:
            if rowid[0] < 12:
                Start_date_ptr = Start_date_ptr + delta_1day
                continue
            DI_total = 0.0
            for i in range(12):
                sql_cmd = 'select DI from TAIEX where rowid =' + str(rowid[0] - i)
                c.execute(sql_cmd)
                DI_total = DI_total + c.fetchone()[0]
            DI_total = DI_total/12
            sql_cmd = 'UPDATE TAIEX set EMA12 =' + str(DI_total) + ' where rowID =' + str(rowid[0])
            c.execute(sql_cmd)
            conn.commit()            
    Start_date_ptr = Start_date_ptr + delta_1day
#EMA26 computation
Start_date_ptr = Start_date
while Start_date_ptr <= End_date:
    cur_date_str = str(Start_date_ptr.year) + '-' + Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d")
    sql_cmd = 'select rowid from TAIEX where date_ID =\'' + cur_date_str + '\''
    c.execute(sql_cmd)
    rowid = c.fetchone()
    if rowid != None:
        sql_cmd = 'select EMA26 from TAIEX where rowid =' + str(rowid[0] - 1)
        c.execute(sql_cmd)
        EMA26_preday = c.fetchone()
        print(EMA26_preday)
        if (EMA26_preday != None) and (EMA26_preday[0] != None):
            sql_cmd = 'select DI from TAIEX where rowid =' + str(rowid[0])
            c.execute(sql_cmd)
            DI = c.fetchone()[0]
            EMA26 = (EMA26_preday[0]*25 + DI*2)/27
            sql_cmd = 'UPDATE TAIEX set EMA26 =' + str(EMA26) + ' where rowID =' + str(rowid[0])
            c.execute(sql_cmd)
            conn.commit() 
            print(EMA26)
        else:
            if rowid[0] < 26:
                Start_date_ptr = Start_date_ptr + delta_1day
                continue
            DI_total = 0.0
            for i in range(26):
                sql_cmd = 'select DI from TAIEX where rowid =' + str(rowid[0] - i)
                c.execute(sql_cmd)
                DI_total = DI_total + c.fetchone()[0]
            DI_total = DI_total/26
            sql_cmd = 'UPDATE TAIEX set EMA26 =' + str(DI_total) + ' where rowID =' + str(rowid[0])
            c.execute(sql_cmd)
            conn.commit()            
    Start_date_ptr = Start_date_ptr + delta_1day
#MACD_12_26 computation
Start_date_ptr = Start_date
while Start_date_ptr <= End_date:
    cur_date_str = str(Start_date_ptr.year) + '-' + Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d")
    sql_cmd = 'select rowid from TAIEX where date_ID =\'' + cur_date_str + '\''
    c.execute(sql_cmd)
    rowid = c.fetchone()
    if rowid != None:
        sql_cmd = 'select EMA26 from TAIEX where rowid =' + str(rowid[0])
        c.execute(sql_cmd)
        EMA26 = c.fetchone()
        sql_cmd = 'select EMA12 from TAIEX where rowid =' + str(rowid[0])
        c.execute(sql_cmd)
        EMA12 = c.fetchone()
        if (EMA26 != None) and (EMA26[0] != None) and (EMA12 != None) and (EMA12[0] != None):
            MACD_12_26 = EMA12[0] - EMA26[0]
            sql_cmd = 'UPDATE TAIEX set MACD_12_26 =' + str(MACD_12_26) + ' where rowID =' + str(rowid[0])
            print(sql_cmd)
            c.execute(sql_cmd)
            conn.commit()
    Start_date_ptr = Start_date_ptr + delta_1day

#MACD9 and MACD diff computation

Start_date_ptr = Start_date
while Start_date_ptr <= End_date:
    cur_date_str = str(Start_date_ptr.year) + '-' + Start_date_ptr.strftime("%m") + '-' + Start_date_ptr.strftime("%d")
    sql_cmd = 'select rowid from TAIEX where date_ID =\'' + cur_date_str + '\''
    c.execute(sql_cmd)
    rowid = c.fetchone()
    if rowid != None:
        sql_cmd = 'select MACD_9 from TAIEX where rowid =' + str(rowid[0] - 1)
        c.execute(sql_cmd)
        MACD_9_pre = c.fetchone()
        print(MACD_9_pre)
        if (MACD_9_pre != None) and (MACD_9_pre[0] != None):
            sql_cmd = 'select MACD_12_26 from TAIEX where rowid =' + str(rowid[0])
            c.execute(sql_cmd)
            MACD_12_26 = c.fetchone()[0]
            MACD_9 = (MACD_9_pre[0]*8 + MACD_12_26*2)/10
            sql_cmd = 'UPDATE TAIEX set MACD_9 =' + str(MACD_9) + ' where rowID =' + str(rowid[0])
            c.execute(sql_cmd)
            conn.commit()
            MACD_DIFF = MACD_12_26 - MACD_9
            sql_cmd = 'UPDATE TAIEX set MACD_DIFF =' + str(MACD_DIFF) + ' where rowID =' + str(rowid[0])
            c.execute(sql_cmd)
            conn.commit()
            print(sql_cmd)
        else:
            if rowid[0] < 34: #the first day we can have MACD9 value is the 34th day
                Start_date_ptr = Start_date_ptr + delta_1day
                continue
            MACD_12_26_total = 0.0
            for i in range(9):
                sql_cmd = 'select MACD_12_26 from TAIEX where rowid =' + str(rowid[0] - i)
                c.execute(sql_cmd)
                MACD_12_26_total = MACD_12_26_total + c.fetchone()[0]
            MACD_12_26_total = MACD_12_26_total/9
            sql_cmd = 'UPDATE TAIEX set MACD_9 =' + str(MACD_12_26_total) + ' where rowID =' + str(rowid[0])
            c.execute(sql_cmd)
            conn.commit()
            sql_cmd = 'select MACD_12_26 from TAIEX where rowid =' + str(rowid[0])
            c.execute(sql_cmd)            
            MACD_DIFF = c.fetchone()[0] - MACD_12_26_total
            sql_cmd = 'UPDATE TAIEX set MACD_DIFF =' + str(MACD_DIFF) + ' where rowID =' + str(rowid[0])
            c.execute(sql_cmd)
            conn.commit()
    Start_date_ptr = Start_date_ptr + delta_1day

conn.close()    

import requests, os, bs4, sys
import re, time
from datetime import datetime
from datetime import timedelta
import sqlite3

f= open('log_stock_volume_validation.txt',"a", encoding="utf-8")

delta_30day = timedelta(days = 30) #delta_1day
DateSearch = re.compile(r'(\d\d\d\d)/(\d\d)/(\d\d)')

conn = sqlite3.connect('stock_list.db')
c = conn.cursor()

path = os.getcwd()
path = path + '\\stock_db'
os.chdir(path)
print(os.getcwd())

stock_data_delete_list = []

cursor = c.execute("SELECT stock_id, start_date, stock_type, business  from stock_list")

for current_entry in cursor:
    if ((current_entry[2] == '上櫃') or (current_entry[2] == '上市')) and (current_entry[3] != 'ETF'):
        db_name = current_entry[0] + '.db'
        conn_stock = sqlite3.connect(db_name)
        c_stock = conn_stock.cursor()
        cursor_stock = c_stock.execute('SELECT max(rowid) FROM stock_day')
        rowid = cursor_stock.fetchone()
        if rowid != None:
            volume_total = 0
            for i in range(30):
                if (rowid[0] - i) == 0:
                    break
                sql_cmd = 'select volume from stock_day where rowid =' + str(rowid[0] - i)
                c_stock.execute(sql_cmd)
                volume_tmp = c_stock.fetchone()[0]
                volume_total = volume_total + volume_tmp
                #print(volume_tmp)
            volume_total = volume_total / 1000 #換算成張數
            if (volume_total / 30) < 20:
                stock_data_delete_list.append([current_entry[0], (volume_total / 30)])
        conn_stock.close()
#delete stock with too low daily volume in the stock list
for stock_id in stock_data_delete_list:
    sql_cmd = 'DELETE FROM stock_list where stock_id =' + stock_id[0]
    print(sql_cmd)
    c.execute(sql_cmd)
    conn.commit()
    f.write(str(datetime.today()) + ':' + 'remove stock id =' + stock_id[0] + ' avg daily volume =' + str(stock_id[1]) + '\n')

f.close()
conn.close()
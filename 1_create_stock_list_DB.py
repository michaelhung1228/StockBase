import requests, os, bs4, sys
import re, time
import sqlite3

url1_base = 'http://isin.twse.com.tw/isin/C_public.jsp?strMode=2' #上市股票代碼列表
url2_base = 'http://isin.twse.com.tw/isin/C_public.jsp?strMode=4' #上櫃股票代碼列表
current_tag = ''

conn = sqlite3.connect('stock_list.db')
c = conn.cursor()

sql_cmd = 'CREATE TABLE if not exists stock_list\
           (stock_ID       TEXT PRIMARY KEY     NOT NULL,\
            stock_name     TEXT,\
            start_date     TEXT,\
            stock_type     TEXT,\
            business       TEXT,\
            last_update_date    TEXT,\
            checked_on_list    INTEGER,\
            observation INTEGER);'
c.execute(sql_cmd)
conn.commit()

#在database裡面的股票都要檢查還在不在清單上
sql_cmd = 'UPDATE stock_list set checked_on_list = 0 where checked_on_list = 1'
c.execute(sql_cmd)
conn.commit()

DataSearch = re.compile(r'(.*)　(.*)')

res = requests.get(url1_base)
if res.raise_for_status() != None:
    print('URL download error')
soup = bs4.BeautifulSoup(res.text, "lxml")
trs = soup.find_all('tr')
#上市股票列表
print('Stock List')
for tr in trs:
    soup1 = bs4.BeautifulSoup(str(tr), "lxml")
    tds = soup1.find_all('td')
    if tds == []:
        continue
    #此表格為股票或ETF列表
    if len(tds) == 1:
        current_tag = tds[0].getText().strip()
        continue
    if current_tag == '股票' or current_tag == 'ETF':
        #每個tr包含 代碼 股票名 產業 上市日期
        mo = DataSearch.search(tds[0].getText())
        stock_ID = mo.group(1).strip()
        stock_name = mo.group(2).strip()
        start_date = tds[2].getText().strip()
        stock_type = tds[3].getText().strip()
        if current_tag == 'ETF':
            business = 'ETF'
        else:
            business = tds[4].getText().strip()
        #rowid 已經在database 裡面 就update, 不在裡面就新增
        sql_cmd = 'select rowid from stock_list where stock_ID =\'' + stock_ID + '\''
        c.execute(sql_cmd)
        rowid = c.fetchone()
        if rowid == None:
            sql_cmd = 'INSERT INTO stock_list (stock_ID, stock_name, start_date, stock_type, business, checked_on_list, observation) VALUES (\'' + stock_ID + '\',' \
                                                                                    + '\'' + stock_name + '\',' \
                                                                                    + '\'' + start_date + '\',' \
                                                                                    + '\'' + stock_type + '\',' \
                                                                                    + '\'' + business +   '\',' \
                                                                                    +  '1' + ',' \
                                                                                    +  '0' + ')'
        else:
            sql_cmd = 'UPDATE stock_list set start_date =' + '\'' + start_date + '\',' + 'stock_type = ' + '\'' + stock_type + '\',' + 'business = ' + '\'' + business +   '\',' + 'checked_on_list = 1'\
            ' WHERE rowID =' + str(rowid[0])
        c.execute(sql_cmd)
        conn.commit()
        print(stock_ID + ' ' + stock_name + ' ' + start_date + ' ' + stock_type + ' ' + business)

#上櫃股票列表
res = requests.get(url2_base)
if res.raise_for_status() != None:
    print('URL download error')
soup = bs4.BeautifulSoup(res.text, "lxml")
trs = soup.find_all('tr')
for tr in trs:
    soup1 = bs4.BeautifulSoup(str(tr), "lxml")
    tds = soup1.find_all('td')
    if tds == []:
        continue
    if len(tds) == 1:
    	current_tag = tds[0].getText().strip()
    	continue
    if current_tag == '股票' or current_tag == 'ETF':
        mo = DataSearch.search(tds[0].getText())
        stock_ID = mo.group(1).strip()
        stock_name = mo.group(2).strip()
        start_date = tds[2].getText().strip()
        stock_type = tds[3].getText().strip()
        if current_tag == 'ETF':
            business = 'ETF'
        else:
            business = tds[4].getText().strip()
        sql_cmd = 'select rowid from stock_list where stock_ID =\'' + stock_ID + '\''
        c.execute(sql_cmd)
        rowid = c.fetchone()
        if rowid == None:
            sql_cmd = 'INSERT INTO stock_list (stock_ID, stock_name, start_date, stock_type, business, checked_on_list, observation) VALUES (\'' + stock_ID + '\',' \
                                                                                    + '\'' + stock_name + '\',' \
                                                                                    + '\'' + start_date + '\',' \
                                                                                    + '\'' + stock_type + '\',' \
                                                                                    + '\'' + business +   '\',' \
                                                                                    +  '1' + ',' \
                                                                                    +  '0' + ')'
        else:
            sql_cmd = 'UPDATE stock_list set start_date =' + '\'' + start_date + '\',' + 'stock_type = ' + '\'' + stock_type + '\',' + 'business = ' + '\'' + business +   '\',' + 'checked_on_list = 1'\
            ' WHERE rowID =' + str(rowid[0])
        c.execute(sql_cmd)
        conn.commit()
        print(stock_ID + ' ' + stock_name + ' ' + start_date + ' ' + stock_type + ' ' + business)


sql_cmd = 'DELETE from stock_list where checked_on_list = 0'
c.execute(sql_cmd)
conn.commit()

conn.close()

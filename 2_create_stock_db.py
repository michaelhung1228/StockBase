import requests, os, bs4, sys
import re, time
from datetime import datetime
from datetime import timedelta
import sqlite3

conn = sqlite3.connect('stock_list.db')
c = conn.cursor()

path = os.getcwd()
path = path + '\\stock_db'
os.chdir(path)
print(os.getcwd())

cursor = c.execute("SELECT stock_id, business  from stock_list")
for row in cursor:
    if row[1] != 'ETF':
        db_name = row[0] + '.db'
        conn_stock = sqlite3.connect(db_name)
        c_stock = conn_stock.cursor()
        print(db_name)
        print(row[1])
        sql_cmd = 'CREATE TABLE if not exists stock_day\
           (date_ID       TEXT PRIMARY KEY     NOT NULL,\
            open_price     REAL,\
            highest_price     REAL,\
            lowest_price     REAL,\
            close_price     REAL,\
            volume           INTEGER,\
            Total            REAL,\
            MA3            REAL,\
            MA6            REAL,\
            MA18           REAL,\
            MA54           REAL,\
            MA108          REAL,\
            MA216          REAL,\
            DI             REAL,\
            EMA12          REAL,\
            EMA26          REAL,\
            MACD_12_26     REAL,\
            MACD_9         REAL,\
            MACD_DIFF      REAL,\
            foreign_buy    INTEGER,\
            foreign_sell    INTEGER,\
            foreign_total    INTEGER,\
            invest_trust_buy    INTEGER,\
            invest_trust_sell    INTEGER,\
            invest_trust_total INTEGER);'
        c_stock.execute(sql_cmd)
        sql_cmd = 'CREATE TABLE if not exists stock_week\
           (date_ID       TEXT PRIMARY KEY     NOT NULL,\
            holder100_per        REAL,\
            holder400_per        REAL,\
            holder1000_per       REAL,\
            total_people INTEGER);'
        c_stock.execute(sql_cmd)
        sql_cmd = 'CREATE TABLE if not exists stock_month\
           (date_ID       TEXT PRIMARY KEY     NOT NULL,\
            revenue          INTEGER);'
        c_stock.execute(sql_cmd)
        sql_cmd = 'CREATE TABLE if not exists stock_quarter\
           (date_ID       TEXT PRIMARY KEY     NOT NULL,\
            EPS     REAL,\
            gross_margin     REAL,\
            operating_profit_margin    REAL,\
            net_profit_margin    REAL);'
        c_stock.execute(sql_cmd)
        sql_cmd = 'CREATE TABLE if not exists stock_info\
           (date_ID       TEXT PRIMARY KEY     NOT NULL,\
            capital_amount     INTEGER);'
        c_stock.execute(sql_cmd)
        conn_stock.commit()
        conn_stock.close()
conn.close()
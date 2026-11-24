import mysql.connector
from config import Config
def conn(): return mysql.connector.connect(**Config.DB)
def one(sql,args=()):
    c=conn()
    try:
        q=c.cursor(dictionary=True); q.execute(sql,args); return q.fetchone()
    finally: q.close(); c.close()
def all(sql,args=()):
    c=conn()
    try:
        q=c.cursor(dictionary=True); q.execute(sql,args); return q.fetchall()
    finally: q.close(); c.close()
def run(sql,args=()):
    c=conn()
    try:
        q=c.cursor(); q.execute(sql,args); c.commit(); return q.lastrowid
    finally: q.close(); c.close()

import sqlite3


# 连接到SQLite数据库
# 如果文件不存在，会自动在当前目录创建一个db的数据库文件

class SqlUtils:
    print("Opened database successfully")

    conn = None
    c = None

    def open_conn(self):
        self.conn = sqlite3.connect('radomimgs.db')

        # 创建一个Cursor对象
        self.c = self.conn.cursor()

    def close_conn(self):
        # 关闭Cursor和Connection
        self.c.close()
        self.conn.close()

    def create_table(self):
        # 使用Cursor执行SQL命令
        # 创建表
        self.c.execute('''CREATE TABLE IF NOT EXISTS marker
                            (marker text PRIMARY KEY, remark text)''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS paths
                     (folder_path text PRIMARY KEY, remark text)''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS files
                    (keyname text PRIMARY KEY, hash text,  fsize real,mimeType text,
                    putTime text ,typename real,status text,md5 text)''')

    def insert_data(self, table_name, data):
        if table_name == "paths":
            self.c.executemany("INSERT OR IGNORE INTO paths VALUES (?, ?)", data)
        if table_name == "files":
            # 插入一行记录
            self.c.executemany("INSERT OR IGNORE INTO files VALUES (?, ?, ?, ?,?,?,?,?)", data)

        if table_name == "marker":
            self.c.execute("INSERT OR IGNORE INTO marker VALUES (?,?)", data)
            # 提交事务
        self.conn.commit()

    def query_data(self, table_name):
        # 查询并打印所有记录
        self.c.execute('SELECT * FROM ' + table_name)
        print("query_data---"+table_name)
        res = self.c.fetchall()
        res.reverse()
        return res

    def clear_data(self, table_name):
        self.c.execute('DELETE FROM ' + table_name)
        self.conn.commit()
        print("clear_data:")
        print(self.c.fetchall())
        self.c.close()
        self.conn.close()

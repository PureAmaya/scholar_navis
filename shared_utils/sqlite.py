# add by scholar_navis(@PureAmaya)

from enum import Enum
from crazy_functions.scholar_navis.scripts.tools.article_library_ctrl import get_data_dir


import os
import sqlite3


class db_type(Enum):
    article_doi_title = 'article_doi_title.db'
    doi_fulltext_ai_understand = 'doi_fulltext_ai_understand.db'
    doi_emulate_polish = 'doi_emulate_polish.db'
    user_useage_log = 'user_useage_log.db'


class SQLiteDatabase:
    # ! 功能并不完整，有需要的时候才会补充功能
    def __init__(self, type: db_type):

        self.db_type = type.value
        self.conn = None
        self.cur = None

        if self.db_type == db_type.article_doi_title.value:
            self.table = 'articles'
            self.primary_key_column ='doi'
        elif self.db_type == db_type.doi_fulltext_ai_understand.value:
            self.table = 'fulltext'
            self.primary_key_column ='doi'
        elif self.db_type == db_type.doi_emulate_polish.value:
            self.table = 'emulated_content'
            self.primary_key_column ='doi'
        elif self.db_type == db_type.user_useage_log.value:
            self.table = 'user_useage'
            self.primary_key_column =''
        else:
            raise ValueError('Unacceptable database')

        try:
            db_path = os.path.join(get_data_dir('db'),self.db_type)
            self.conn = sqlite3.connect(db_path)
            self.cur = self.conn.cursor()

            # 检查一下是否可用，不能用就创建一个新的
            if not self.__check_table_exist():self.__create_table()

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.cur.close()
            self.conn.close()

    def __check_table_exist(self):

        check_table_sql = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"

        try:
            self.cur.execute(check_table_sql,(self.table,))
            self.conn.commit()

            # 获取查询结果
            table_exists = self.cur.fetchone() is not None
            return table_exists

        except sqlite3.Error as e:
            print(f"An error occurred when checking a table: {e}")
            return False

    def __create_table(self):

        # 创建的是标题、doi对应的数据库
        if self.db_type == db_type.article_doi_title.value:

            # 创建一个包含  title, doi, inf 的表
            create_table_sql = f'''
            CREATE TABLE IF NOT EXISTS {self.table} (
                {self.primary_key_column} TEXT PRIMARY KEY NOT NULL, 
                title TEXT,
                info TEXT
            )
            '''
        elif self.db_type == db_type.doi_fulltext_ai_understand.value:
            # 创建一个包含  doi,  全文 的表
            create_table_sql = f'''
            CREATE TABLE IF NOT EXISTS {self.table} (
                {self.primary_key_column} TEXT PRIMARY KEY NOT NULL, 
                fulltext TEXT
            )
            '''
        elif self.db_type == db_type.doi_emulate_polish.value:
            # 创建一个包含  doi,  全文 的表
            create_table_sql = f'''
            CREATE TABLE IF NOT EXISTS {self.table} (
                {self.primary_key_column} TEXT PRIMARY KEY NOT NULL, 
                emulated_content TEXT
            )
            '''
        elif self.db_type == db_type.user_useage_log.value:
            # 创建一个包含  doi,  全文 的表
            create_table_sql = f'''
            CREATE TABLE IF NOT EXISTS {self.table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                username TEXT,
                ip TEXT,
                datetime TEXT,
                llm_model TEXT,
                function_name TEXT,
                prompt TEXT,
                input TEXT
            )
            '''

        else:
            raise ValueError('Unacceptable database')


        try:
            self.cur.execute(create_table_sql)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred when creating a table: {e}")

    def select(self,PRIMARY_KEY_VAL:str,search_key : tuple[str]):
        assert len(search_key) != 0

        if PRIMARY_KEY_VAL:
            return None

        try:
            query_sql = f"SELECT {', '.join(search_key)} FROM {self.table} WHERE {self.primary_key_column} = ?"
            self.cur.execute(query_sql,(PRIMARY_KEY_VAL,))
            # 获取查询结果
            return self.cur.fetchone()
        except sqlite3.Error as e:
            print(f"An error occurred when selecting a value: {e}")

    def insert_ingore(self,PRIMARY_KEY_VAL:str,insert_key : tuple[str],insert_key_val : tuple[str]):
        """向目标数据库中插入键值
            如果PRIMARY_KEY已经存在，则忽略
        """
        assert len(insert_key) != 0
        assert len(insert_key) == len(insert_key_val)

        if self.primary_key_column and (not PRIMARY_KEY_VAL): # 定义了主键列，但是没有提供主键
            raise KeyError('missing primary key')

        try:
            value_question = ', '.join(['?' for _ in range(len(insert_key_val))]) # 给主键之外的键生成一个占位用 ? 
            value = []
            if self.primary_key_column:value.append(PRIMARY_KEY_VAL)
            value.extend(insert_key_val)

            if self.primary_key_column:query_sql = f"INSERT OR IGNORE INTO {self.table} ({self.primary_key_column}, {', '.join(insert_key)}) VALUES (? , {value_question});"
            else:query_sql = f"INSERT OR IGNORE INTO {self.table} ({', '.join(insert_key)}) VALUES ({value_question});"

            self.cur.execute(query_sql,tuple(value,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred when insert: {e}")

    def update(self,PRIMARY_KEY_VAL:str,insert_key : tuple[str],insert_key_val : tuple[str]):
        assert len(insert_key) != 0
        assert len(insert_key) == len(insert_key_val)

        if PRIMARY_KEY_VAL:return

        try:
            value = list(insert_key_val)
            value.append(PRIMARY_KEY_VAL)

            query_sql = f"UPDATE {self.table} SET {' = ?, '.join(insert_key)} = ? WHERE {self.primary_key_column} = ?"
            self.cur.execute(query_sql,tuple(value,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred when update: {e}")

    def delete(self,PRIMARY_KEY_VAL:str):

        if PRIMARY_KEY_VAL:return
        try:
            query_sql = f"DELETE FROM {self.table} WHERE {self.primary_key_column} = ?"
            self.cur.execute(query_sql,(PRIMARY_KEY_VAL,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred when delete: {e}")
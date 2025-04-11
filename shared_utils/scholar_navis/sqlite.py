# add by scholar_navis(@PureAmaya)


from typing import Literal
import os
import sqlite3

DB_TYPE = Literal['user_account','article_doi_title', 'doi_fulltext_ai_understand', 'doi_emulate_polish', 'user_useage_log']


class SQLiteDatabase:
    # ! 功能并不完整，有需要的时候才会补充功能
    def __init__(self, type: DB_TYPE):

        self.db_type = type
        self.conn = None
        self.cur = None

        if self.db_type == 'article_doi_title':
            self.table = 'articles'
            self._primary_field ='doi'
        elif self.db_type == 'doi_fulltext_ai_understand':
            self.table = 'fulltext'
            self._primary_field ='doi'
        elif self.db_type == 'doi_emulate_polish':
            self.table = 'emulated_content'
            self._primary_field ='doi'
        elif self.db_type == 'user_useage_log':
            self.table = 'user_useage'
            self._primary_field =''
        elif self.db_type == 'user_account':
            self.table = 'user_account'
            self._primary_field ='username'
        else:
            raise ValueError('Unacceptable database')

        try:
            db_path = os.path.join('data','db',f"{self.db_type}.db")
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
        if self.db_type == 'article_doi_title':

            # 创建一个包含  title, doi, inf 的表
            create_table_sql = f'''
            CREATE TABLE IF NOT EXISTS {self.table} (
                {self._primary_field} TEXT PRIMARY KEY NOT NULL, 
                title TEXT,
                info TEXT
            )
            '''
        elif self.db_type == 'doi_fulltext_ai_understand':
            # 创建一个包含  doi,  全文 的表
            create_table_sql = f'''
            CREATE TABLE IF NOT EXISTS {self.table} (
                {self._primary_field} TEXT PRIMARY KEY NOT NULL, 
                fulltext TEXT
            )
            '''
        elif self.db_type == 'doi_emulate_polish':
            # 创建一个包含  doi,  全文 的表
            create_table_sql = f'''
            CREATE TABLE IF NOT EXISTS {self.table} (
                {self._primary_field} TEXT PRIMARY KEY NOT NULL, 
                emulated_content TEXT
            )
            '''
        elif self.db_type == 'user_useage_log':
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
        elif self.db_type == 'user_account':
            # 创建一个包含  username, password 的表
            create_table_sql = f'''
            CREATE TABLE IF NOT EXISTS {self.table} (                
                {self._primary_field} TEXT PRIMARY KEY NOT NULL, 
                password TEXT NOT NULL,
                token TEXT NOT NULL UNIQUE,
                token_expiry DATETIME,
                registration_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                llm_kwargs TEXT,
                user_custom_data TEXT
                )
            '''
        else:
            raise ValueError('Unacceptable database')


        try:
            self.cur.execute(create_table_sql)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred when creating a table: {e}")

    def easy_select(self,primary_key_val:str,search_key : tuple[str] | str):
        '''找不到返回None'''
        return self.select(self._primary_field,primary_key_val,search_key)
            
    def select(self,field_to_query: str,field_value: str,search_key : tuple[str] | str):
        """稍微标准一些的搜索

        Args:
            field_to_query (str): 要用来检索的列
            field_value (str): 这个列的值
            search_key (tuple[str] | str): 搜索的键

        Returns:
            搜索的键对应的值（找不到就是None)
        """

        if isinstance(search_key,str):search_key = (search_key,)
        
        assert len(search_key) != 0

        if not field_to_query or not field_value:
            return None

        try:
            query_sql = f"SELECT {', '.join(search_key)} FROM {self.table} WHERE {field_to_query} = ?"
            self.cur.execute(query_sql,(field_value,))
            # 获取查询结果
            result = self.cur.fetchone()
            if not result:return None
            if len(result) == 1:return result[0]
            else:return result
            
        except sqlite3.Error as e:
            print(f"An error occurred when selecting a value: {e}")

    def insert_ingore(self,PRIMARY_KEY_VAL:str,insert_key : tuple[str] |str,insert_key_val : tuple[str] | str):
        """向目标数据库中插入键值
            如果PRIMARY_KEY已经存在，则忽略
        """
        if isinstance(insert_key,str):insert_key = (insert_key,)
        if isinstance(insert_key_val,str):insert_key_val = (insert_key_val,)
        
        assert len(insert_key) != 0
        assert len(insert_key) == len(insert_key_val)

        if self._primary_field and (not PRIMARY_KEY_VAL): # 定义了主键列，但是没有提供主键
            raise KeyError('missing primary key')

        try:
            value_question = ', '.join(['?' for _ in range(len(insert_key_val))]) # 给主键之外的键生成一个占位用 ? 
            value = []
            if self._primary_field:value.append(PRIMARY_KEY_VAL)
            value.extend(insert_key_val)

            if self._primary_field:query_sql = f"INSERT OR IGNORE INTO {self.table} ({self._primary_field}, {', '.join(insert_key)}) VALUES (? , {value_question});"
            else:query_sql = f"INSERT OR IGNORE INTO {self.table} ({', '.join(insert_key)}) VALUES ({value_question});"

            self.cur.execute(query_sql,tuple(value,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred when insert: {e}")

    def update(self,PRIMARY_KEY_VAL:str,update_key : tuple[str] |str,update_key_val : tuple[str] |str):
        
        if isinstance(update_key,str):update_key = (update_key,)
        if isinstance(update_key_val,str):update_key_val = (update_key_val,)
        
        assert len(update_key) != 0
        assert len(update_key) == len(update_key_val)

        if not PRIMARY_KEY_VAL:return

        try:
            value = list(update_key_val)
            value.append(PRIMARY_KEY_VAL)

            query_sql = f"UPDATE {self.table} SET {' = ?, '.join(update_key)} = ? WHERE {self._primary_field} = ?"
            self.cur.execute(query_sql,tuple(value,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred when update: {e}")

    def delete(self,PRIMARY_KEY_VAL:str):

        if not PRIMARY_KEY_VAL:return
        try:
            query_sql = f"DELETE FROM {self.table} WHERE {self._primary_field} = ?"
            self.cur.execute(query_sql,(PRIMARY_KEY_VAL,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred when delete: {e}")
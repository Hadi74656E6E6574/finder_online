import sqlite3
import pandas as pd
import data_from_excel


class DatabaseManager:
    def __init__(self, db_path, excel_path=None):
        self.db_path = db_path
        self.in_tupel = None
        self.output = None

        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()

        self.excel_path = excel_path

    def use_sql(self, sql_query, params=None, outer_tup=None):
        # Verbindung zur SQLite-Datenbank herstellen

        if params is None:
            self.cur.execute(sql_query)
        elif params == 'insert':
            self.cur.executemany(sql_query, self.in_tupel)
        elif params == 'select':
            self.output = []
            try:
                sql_data = self.cur.execute(sql_query)
                for data in sql_data:
                    print(data)
                    self.output.append(data)
            except sqlite3.OperationalError:
                print('!!! sqlite3.OperationalError !!!')
        elif params == 'select_plus':
            self.output = []
            sql_data = self.cur.execute(sql_query, outer_tup)
            for data in sql_data:
                print(data)
                self.output.append(data)

        # Commit der Änderungen
        self.conn.commit()
    
    # Wenn man kein use_sql mehr nutzt 
    def close_db(self):
        self.cur.close()
        self.conn.close()


    def set_tupel(self, tupel):
        self.in_tupel = tupel

    def convert_txt_into_tupel(self, data_txt, count_start=0):
        # Erstellen der Tupel mit IDs
        tupel_list = [(index + count_start, value) for index, value in enumerate(data_txt)]
        self.in_tupel = tupel_list

    def convert_list_into_tupel(self, data_li, count_start=0):
        tup = []

        for counter, item in enumerate(data_li):
            tup.append((counter + count_start, item))

        self.in_tupel = tup

    def create_hat_tupel(self, spec, adm_li):
        tup = []

        for item in adm_li:
            tup.append((self.get_sid(spec), self.get_aid(item)))

        self.in_tupel = tup

    def get_id(self, primary_key, table, col_name, value):
        try:
            self.use_sql(f'''SELECT {primary_key} FROM {table} WHERE {col_name} = '{value}' ''', params='select')
            return self.output[0][0]
        except IndexError: 
            print('!!! INDEX ERROR !!!')

    def get_keywords_by_similarity_check(self, keyword):
        self.output = []
        sql_data = self.cur.execute(f'''
        SELECT * FROM Keywords WHERE title LIKE '%{keyword}%'
        ''')
        for data in sql_data:
            print(data)
            self.output.append(data)

        self.output = [item[1] for item in self.output]
    
    def get_all_titles(self):
        # self.use_sql('SELECT title FROM Standards', params='select')
        # result = [item[0] for item in self.output]
        # return result
        col_title = data_from_excel.extract_column_from_excel(self.excel_path, 'Title')
        return col_title
    
    def set_titles_in_db(self):
        df = pd.read_excel(self.excel_path)
        titles = self.get_all_titles()
        print(titles)

        for title in titles:
            self.use_sql(f"SELECT * FROM Standards WHERE title = '{title}'", 'select')
            # print('EXISTING: ', self.output)
            if not self.output:
                print('NORM EXISTIERT NICHT: ', title)
                self.cur.execute(f"INSERT INTO Standards (title) VALUES ('{title}')")
                self.conn.commit()
    
    def set_headings_in_db(self):
        df = pd.read_excel(self.excel_path)
        titles = self.get_all_titles()
        for title in titles:
            heading = data_from_excel.get_heading_from_title(self.excel_path, df, title)
            print(title, heading)
            try:
                self.use_sql(f'''
                        UPDATE Standards SET heading = '{heading}' WHERE title = '{title}'
                        ''')
            except sqlite3.OperationalError:
                # FEHLER DURCH ' 
                self.use_sql(f'''
                        UPDATE Standards SET heading = 'ERROR' WHERE title = '{title}'
                        ''')
    
    def set_keywords_in_db(self):
        keywords = data_from_excel.extract_keywords_from_excel(self.excel_path)
        self.convert_list_into_tupel(keywords)
        # print(self.in_tupel)
        for item in self.in_tupel:
                print(item)
                self.cur.execute("INSERT OR IGNORE INTO Keywords (title) VALUES (?)", (item[1],))
                self.conn.commit()
    
    def set_hat_in_db(self):
        df = pd.read_excel(self.excel_path)
        standards = self.get_all_titles()

        for standard in standards:
            keywords = data_from_excel.get_keywords_for_stanadard(df, standard)
            standard_id = self.get_id('SID', 'Standards', 'title', standard)
            
            keyword_ids = []
            for keyword in keywords:
                keyword_ids.append(self.get_id('KID', 'Keywords', 'title', keyword))
            print('s_id: ', standard_id)
            print('k_ids: ', keyword_ids)
        
            for id in keyword_ids:
                sql_query = f"INSERT OR IGNORE INTO hat (SID, KID) VALUES ('{standard_id}', '{id}')"
                # print(f"Debug: SQL query = {sql_query}")
                try:
                    self.cur.execute(sql_query)
                    self.conn.commit()
                except sqlite3.OperationalError: 
                    pass

        



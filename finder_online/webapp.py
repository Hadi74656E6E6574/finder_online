import streamlit as st
import pandas as pd
import db
import csv
import ast
import os 

base_path = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_path, 'database', 'standard_finder.db')
session_tags_path = os.path.join(base_path, 'csv_files', 'session_tags.csv')

class DataMaker:
    def __init__(self):
        self.dbm = db.DatabaseManager(db_path)
    
    def get_tag_list_by_search_input(self, keyword):
        self.dbm.get_keywords_by_similarity_check(keyword)
        return self.dbm.output
    
# ------------------------------------------------------------------------------------------------

# Initialisierung des DataMaker-Objekts
dm = DataMaker()

st.set_page_config(page_title="Advanced search", page_icon='🔎')
st.title('Willkommen zur Normensuche')

search_term = st.text_input("Suche", "")
print(search_term)
search_result = dm.get_tag_list_by_search_input(search_term)

tags = st.multiselect(
    'Vorgeschlagene Tags',
    search_result
)

st.write(f"Wenn man du fertig bist mit der Eingabe '{search_term}' auf ADD klicken:")
if st.button('ADD'):

    # CSV ---------------------------------------------------------

    fieldnames = ['tags']

    with open(session_tags_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow({
            'tags': tags
        })

    # ------------------------------------------------------------------

option = st.radio(
    "Verknüpfung wählen",
    ["OR", "AND"]
)

# CSV ---------------------------------------------------------
tag_li = []
li = []
with open(session_tags_path, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        # Überspringen der ersten Zeile
        next(csv_reader, None)
        for row in csv_reader: 
            for item in row:
                mini_li = ast.literal_eval(item)
                li.append(mini_li)
for item in li:
     tag_li.extend(item)

tag_li = list(set(tag_li))

# print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! tag_li: ', tag_li)

# ---------------------------------------------------------

st.write('Das sind deine tags:', tag_li)

if st.button('SEARCH'):
    result_li1 = []
    result_li2 = []
    tags = tuple(tag_li)
    placeholder = ','.join(['?' for item in tags])
    if option == 'OR':
        dm.dbm.use_sql(
            f"SELECT DISTINCT * FROM Standards INNER JOIN hat ON Standards.SID = hat.SID INNER JOIN "
            f"Keywords ON hat.KID = Keywords.KID WHERE Keywords.title IN ({placeholder})", params='select_plus',
            outer_tup=tags)
    elif option == 'AND':
        dm.dbm.use_sql(f'''
        SELECT * FROM Standards
        INNER JOIN hat ON Standards.SID = hat.SID
        INNER JOIN Keywords ON hat.KID = Keywords.KID
        WHERE Keywords.title IN ({placeholder})
        GROUP BY Standards.SID
        HAVING COUNT(DISTINCT Keywords.title) = {len(tags)}
        ''', params='select_plus', outer_tup=tags)
    print(dm.dbm.output)
    # result = [''.join((item[1], ' || ', item[2])) for item in dm.dbm.output]
    for item in dm.dbm.output: 
        result_li1.append(item[1])
        result_li2.append(item[2])
    df_result = pd.DataFrame(columns=['Title', 'heading'])
    df_result['Title'] = result_li1
    df_result['heading'] = result_li2
    # print(result)
    # CSV ---------------------------------------------------------
    # CSV-Datei einlesen
    df = pd.read_csv(session_tags_path)

    # Nur die Header-Zeile behalten
    df = df.iloc[0:0] # Start- und Endindex 

    # Ergebnis in eine neue CSV-Datei schreiben
    df.to_csv(session_tags_path, index=False)

    
    # st.write('Gefundene Normen: ', result)
    st.write('Gefundene Normen: ', df_result)
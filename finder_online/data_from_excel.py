import pandas as pd


def extract_column_from_excel(excel_path, col_name: str, unique: bool = True):
    df = pd.read_excel(excel_path)
    if unique:
        col = df[col_name].unique()
    else:
        col = df[col_name]
    return col

def get_heading_from_title(excel_path, dataframe:pd.DataFrame, title):
    df = dataframe.fillna('None')
    try:
        index = df[df['Title'] == title].index[0]
        return df.iloc[index, 2] 
    except IndexError:
        print(title, 'existiert nicht !')

def extract_keywords_from_excel(excel_path):
    col_keywords = extract_column_from_excel(excel_path, 'Keywords')
    keywords = []
    for item in col_keywords: 
        try:
            keywords.append(item.split(', '))
        except AttributeError:
            pass
    zw = []
    for keyword in keywords:
        zw.extend(keyword)
    keywords = zw
    keywords = [keyword.strip() for keyword in keywords]
    return keywords

def get_keywords_for_stanadard(dataframe, standard):
    df = dataframe
    index = df[df['Title'] == standard].index[0]
    print("Index: ", index)
    keywords = df.iloc[index, 6]
    if pd.isnull(keywords):
        print('check')
        return []

    try:
        keywords = keywords.split(', ')
        keywords = [keyword.strip() for keyword in keywords]
    except AttributeError: 
        pass
    print(keywords)
    return keywords

if __name__ == '__main__':
    get_keywords_for_stanadard(r'excel_files\SDB.xlsx', 'DIN 14461-2')
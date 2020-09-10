"""
Resize Graph-axis code.
Input variable
  - comma separated text. (ex: T07-170-A7, U05-096-AY)
  - make spaces. only allow 'Y' or 'N'
Output
  - DataFrame having ['ManagementCode', 'OriginCol/Row', ResizeCol/Row']
  - variable name : df_ret
"""

import pyodbc
import numpy as np
import pandas as pd
import sys
from itertools import product

def text_to_sqltext(text: str) -> str:
    _text_list = map(lambda x: x.strip(), text.split(','))
    _sqltext = "','".join(_text_list)
    return "'" + _sqltext + "'"

def dbconnection(server, uid, pwd, db):
    return pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+db+';UID='+uid+';PWD='+pwd)

def DataLoad(query):
    try:
        conn = dbconnection(server, uid, pwd, db)
        # cursor = conn.cursor()
        _data = pd.read_sql(query, conn)
    finally:
        # cursor.close()
        conn.close()
    return _data

if __name__ == '__main__':

    server = '16.100.6.170,1437'
    uid = 'serviceadmin'
    pwd = 'rhksflwk1!'
    db = 'MESAI'

    colsize = 50
    rowsize = 50
    strip_row_count = 2

    managementcode = text_to_sqltext(input('Enter Management Codes : '))
    space = input('Do you want make spaces? answer just Y or N : ')
    if space.upper() in ['Y', 'N']:
        space = space.upper() == 'Y'
    else:
        print("you entered wrong word. just enter 'Y' or 'N'")
        sys.exit(1)

    query = f"""
    SELECT
        *
    FROM
        sms.ManagementSizeBclIndex
    WHERE
        ManagementCode IN ({managementcode})
    """

    df = DataLoad(query)
    df['ManagementCode'] = df['ManagementCode'].apply(lambda x: x.strip())  #공백제거

    ### 관리번호 별 OriginCol, OriginRow의 Max 값 받기 (Min 값은 1로 고정)
    df_max_val = df.groupby(['ManagementCode'])[['OriginCOl', 'OriginRow', 'StripNo']].max()

    df_ret = pd.DataFrame()

    for code, val in df_max_val.iterrows():
        max_col = val[0]
        max_row = val[1]
        strip_count = val[2]
        strip_col_count = strip_count // strip_row_count

        col_interval = (colsize-1) / (max_col-1 + space*(strip_col_count-1))
        row_interval = (rowsize-1) / (max_row-1 + space*(strip_row_count-1))

        OriginCOl = np.arange(1, max_col+1)
        OriginRow = np.arange(1, max_row+1)
        if space:
            ResizeCol = [i for idx, i in enumerate(np.arange(1, colsize+col_interval, col_interval)) if (idx+1)%(max_col//strip_col_count+1) != 0]
            ResizeRow = [i for idx, i in enumerate(np.arange(1, rowsize+row_interval, row_interval)) if (idx+1)%(max_row//strip_row_count+1) != 0]
        else :
            ResizeCol = np.arange(1, colsize+col_interval, col_interval)
            ResizeRow = np.arange(1, rowsize+row_interval, row_interval)

        Origin = product(OriginCOl, OriginRow)
        Resize = product(ResizeCol, ResizeRow)

        for i, j in zip(Origin, Resize):
            i_col, i_row = i
            j_col, j_row = j

            Data = dict(ManagementCode=code,
                        OriginCOl=i_col,
                        OriginRow=i_row,
                        ResizeCol=j_col,
                        ResizeRow=j_row)

            df_ret = df_ret.append(Data, ignore_index=True)

"""
    pd.merge(left=df, right=df_ret, how='inner',
             left_on=['ManagementCode', 'OriginCOl', 'OriginRow'],
             right_on=['ManagementCode', 'OriginCOl', 'OriginRow']).to_csv('N1.csv', index=False)
"""
## T08-094-A6
## B03111397
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 18:23:37 2018

@author: Denny.Lehman
"""

# packages
import pandas as pd
import numpy as np
import datetime

#==============================================================================
# df = pd.read_excel(r'C:\Users\denny.lehman\Documents\18_01 Monthly Portfolio Report\datatape.xlsx')
# df_clean = pd.DataFrame(columns=['System Project','Contract','Committed Capital','Recurring Payment','Escalator','InService Date','Term (Months)','First Payment Date'])
# df_clean['Committed Capital'] = df['Capital ($)']
# df_clean['System Project'] = df['ID']
# df_clean['Contract'] = df['Type']
# df_clean['Escalator'] = df['%']
# df_clean['InService Date'] = df['Month.1']
# df_clean['Term (Months)'] = 300
# df_clean['First Payment Date'] = df_clean['InService Date']
# df_clean['Recurring Payment'] = df['Year 1']
# 
# rng1 = pd.date_range(start='1/1/2013',end='1/1/2045',freq='M')
# df4 = pd.DataFrame()
#==============================================================================

# interest rate
# duration of loan
# 

def main():
    rng = pd.date_range('2/28/2018', periods= 300, freq= 'M')
    Escalator = 0.029
    Recurring_Payment = 95
    Committed_Capital = -1500
    CC_date = pd.to_datetime('01/31/2018')
    Start_Date = pd.to_datetime('02/28/2018')
    
    df2 = pd.DataFrame(index= rng, columns= ['Cash Flow'])
    #df2['Start Date'] = pd.to_datetime('02/28/2018')
    df2['Date Diff'] = df2.index - Start_Date  #rng - pd.to_datetime('02/28/2018')
    #df2['Recurring Payment'] = 95
    #df2['Escalator'] = 0.029
    df2['Year Diff'] = (df2.index - Start_Date) / np.timedelta64(365,'D')
    df2['Year Diff'] = df2['Year Diff'].astype(int)
    df2['Cash Flow'] = (Recurring_Payment * (1 + Escalator)**df2['Year Diff'])
    df2.to_csv(r'C:\Users\denny.lehman\Documents\18_01 Monthly Portfolio Report\test.csv')
    
    print('numpy npv model:')
    print(np.npv(0.06,df2['Cash Flow']))
    
    print('Denny npv model:')
    print(npv(0.06,df2['Cash Flow']))
    # df2['Curr Date'] = df2.index
    
    df2.loc[CC_date] = [Committed_Capital,0,0]
    df2 = df2.sort_index()
    #df2.append(pd.DataFrame([CC_date, Committed_Capital, 0, 0]))
    print('numpy irr:')
    print(np.irr(df2['Cash Flow']))
    
    

def npv(rate,df):
    value = 0
    for i in range(0,df.size - 1):
        value += df.iloc[i] / (1+rate)**(i + 1)
    return value
    
if __name__ == "__main__":
    main()
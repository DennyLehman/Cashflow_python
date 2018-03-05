# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 15:18:57 2018

@author: Denny.Lehman
"""

import pandas as pd
import numpy as np
import datetime
import time
from pandas.tseries.offsets import MonthEnd


def npv(rate, df):
    value = 0
    for i in range(0, df.size):
        value += df.iloc[i] / (1 + rate) ** (i + 1)
    return value

# use this function if finance wants to use the faster CSV version. This version requires proper data cleaning steps
def get_datatape_csv(filepath):
    list_of_column_names_required = ['System Project: Sunnova System ID', 'Committed Capital', 'Quote: Recurring Payment', 'Quote: Contract Type' ,'Quote: Payment Escalator', 'InService Date', 'Asset Portfolio - Partner']
    rename_list = {'System Project: Sunnova System ID':'ID','Committed Capital':'Committed Capital', 'Quote: Contract Type' :'Contract Type', 'Quote: Recurring Payment':'Recurring Payment','Quote: Payment Escalator':'Escalator'}
    d_types = {'System Project: Sunnova System ID':str, 'Committed Capital':np.float64, 'Quote: Recurring Payment': np.float64, 'Quote: Contract Type':str,  'Quote: Payment Escalator':str, 'Asset Portfolio - Partner':str }
    parse_dates = ['InService Date']
    names=['ID', 'CC', 'RP', 'CT', 'PE', 'InS', 'AP']
    
    df3 = pd.read_csv(filepath, sep=',', skiprows=0, header=2) #, usecols=list_of_column_names_required, thousands=',', dtype=d_types) #, parse_dates=parse_dates) # , nrows=10) 
    df3 = df3.rename(columns=rename_list)
    
def get_datatape(filepath):
    list_of_column_names_required = ['Asset Portfolio', 'ID', 'Capital ($)', 'Type',  '%', 'Partner', 'Interconnected', 'Year 1']
    
    # dtypes = {'ID': 'str', 'Interconnected': 'str'}
    # df1 = pd.read_excel(filepath, names=list_of_column_names_required)
    # df1 = pd.read_excel(filepath, header=0, names=['ID','Type'], na_values=['NA'])
    start = time.time()
    
    # df1 = pd.read_excel(filepath, sheetname = 'Active header1', index_col=None, na_values=['NA'], parse_cols="A:D,J,N,T,AG")
    df1 = pd.read_excel(filepath, sheetname='Active', header=4, index_col=None, na_values=['N/A'], parse_cols="C:F,J,L,P,V,AI") #, converters={'Interconnected': pd.to_datetime})
    print(time.time()-start)
    # df1 = pd.read_excel(filepath, index_col=None, na_values=['NA'], parse_cols="A:D,J,N,T,AG", dtype=dtypes)
    # df1 = pd.read_excel(io=filepath, header=None, names=list_of_column_names_required, dtype=dtypes)
#    list_of_columns = list(df1.columns)
#    for i in range(0, len(list_of_column_names_required)):
#        list_of_columns.remove(list_of_column_names_required[i])
#        
#    df1 = df1.drop(list_of_columns, axis=1) 
    
    df1 = df1.rename(columns= {'Interconnected':'InService Date', 'Type':'Contract Type', 'Capital ($)':'Committed Capital', 'Estimate':'Annual Attribute', '%':'Escalator', 'Year 1':'Recurring Payment'})
    return df1
    

def get_contract_type(df1, target_contracts):
    # Make contracts not null
    
    # targets = ['Lease', 'Loan', 'EZ Own']
    
    # df1['Contract Type'].apply(lambda sentence: any(word in sentence for word in targets))
    df1 = df1[df1['Contract Type'].str.contains('|'.join(target_contracts), na=False)]
   
    return df1

def remove_non_inService_Systems(df):
    remove = []
    for i in range(1, df['InService Date'].size):
        if type(df['InService Date'].iloc[i]) == datetime.time:
            remove.append(i)
    df = df.drop(df.index[remove])
    df['InService Date'] = pd.to_datetime(df['InService Date'])
    return df

def remove_blank_inservice_date(df):
    remove = []
    for i in range(1, df['InService Date'].size):
        if df['InService Date'].iloc[i] == datetime.time(0,0):
            remove.append(i)
    df = df.drop(df.index[remove])
    df['InService Date'] = pd.to_datetime(df['InService Date'])
    return df


def convert_date_to_EOM(ser):
    ser = ser + MonthEnd(1)
    return ser

def create_first_payment_and_last_payment_date(df):
    # Make first payment date
    df['First Payment Date'] = df['InService Date'].apply(pd.DateOffset(months=1))
    
    # Convert First Payment Date to datetime
    df['First Payment Date'] = pd.to_datetime(df['First Payment Date']) + MonthEnd(1)
    
    # Make End date
    df['End Date'] = df['First Payment Date'].apply(pd.DateOffset(months=299))
    
    # Convert End date to date time
    df['End Date'] = pd.to_datetime(df['End Date'])# Make first payment date
    
    return df

def year_diff(i):
    r = range(df['First Payment Date'], df['End Date'])
    year_d = r - ins
    return 1
def calculate_production():
    Sens = 0.975
    DF = 0.005
    curr_date = datetime.date('2017',)
    year_diff = 0
    annual_attribute = 5888 
    seasonality_curve_factor = get_seasonality_curve()
    
    production = annual_attribute * (1 - Sens) * (1 - DF) ** year_diff * seasonality_curve_factor


    return 1

def get_seasonality_curve():
    val = 1/12
    return val

   

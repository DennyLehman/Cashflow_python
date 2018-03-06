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
    list_of_column_names_required = ['System Project: Sunnova System ID', 'Committed Capital', 'Quote: Recurring Payment', 'Quote: Contract Type' ,'Quote: Payment Escalator', 'InService Date', 'Asset Portfolio - Partner', 'Location']
    rename_list = {'System Project: Sunnova System ID':'ID','Committed Capital':'Committed Capital', 'Quote: Contract Type' :'Contract Type', 'Quote: Recurring Payment':'Recurring Payment','Quote: Payment Escalator':'Escalator', 'Location' : 'State'}
    d_types = {'System Project: Sunnova System ID':str, 'Committed Capital':np.float64, 'Quote: Recurring Payment': np.float64, 'Quote: Contract Type':str,  'Quote: Payment Escalator':str, 'Asset Portfolio - Partner':str }
    parse_dates = ['InService Date']
    names=['ID', 'CC', 'RP', 'CT', 'PE', 'InS', 'AP']
    
    df3 = pd.read_csv(filepath, sep=',', skiprows=0, header=2) #, usecols=list_of_column_names_required, thousands=',', dtype=d_types) #, parse_dates=parse_dates) # , nrows=10) 
    df3 = df3.rename(columns=rename_list)
    
def get_datatape(filepath):
    list_of_column_names_required = ['Asset Portfolio', 'ID', 'Capital ($)', 'Type',  '%', 'Partner', 'Interconnected', 'Year 1', 'State']
    
    # dtypes = {'ID': 'str', 'Interconnected': 'str'}
    # df1 = pd.read_excel(filepath, names=list_of_column_names_required)
    # df1 = pd.read_excel(filepath, header=0, names=['ID','Type'], na_values=['NA'])
    start = time.time()
    
    # df1 = pd.read_excel(filepath, sheetname = 'Active header1', index_col=None, na_values=['NA'], parse_cols="A:D,J,N,T,AG")
    df1 = pd.read_excel(filepath, sheetname='Active', header=4, index_col=None, na_values=['N/A'], parse_cols="C:F,J,L,P,V,AI,N") #, converters={'Interconnected': pd.to_datetime})
    print(time.time()-start)
    # df1 = pd.read_excel(filepath, index_col=None, na_values=['NA'], parse_cols="A:D,J,N,T,AG", dtype=dtypes)
    # df1 = pd.read_excel(io=filepath, header=None, names=list_of_column_names_required, dtype=dtypes)
#    list_of_columns = list(df1.columns)
#    for i in range(0, len(list_of_column_names_required)):
#        list_of_columns.remove(list_of_column_names_required[i])
#        
#    df1 = df1.drop(list_of_columns, axis=1) 
    
    df1 = df1.rename(columns= {'Interconnected':'InService Date', 'Type':'Contract Type', 'Capital ($)':'Committed Capital', 'Estimate':'Annual Attribute', '%':'Escalator', 'Year 1':'Recurring Payment', 'Location':'State'})
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

def create_first_production_first_payment_and_last_payment_for_ppa(df):
    
    ins_eom = pd.to_datetime(df['InService Date']) + MonthEnd(1)
    
    df['First Production Date'] = ins_eom.apply(pd.DateOffset(months=1))
    
    df['First Payment Date'] = ins_eom.apply(pd.DateOffset(months=2))
    
    df['Last Payment Date'] = ins_eom.apply(pd.DateOffset(months=301))
    
#==============================================================================
#     # Make first production date
#     df['First Production Date'] = df['InService Date'].apply(pd.DateOffset(months=1))
#     
#     # Convert First Payment Date to datetime
#     df['First Production Date'] = pd.to_datetime(df['First Production Date']) + MonthEnd(1)
#     
#     # Make first payment date
#     df['First Payment Date'] = df['InService Date'].apply(pd.DateOffset(months=2))
# 
#     # Convert First Payment Date to datetime
#     df['First Payment Date'] = pd.to_datetime(df['First Payment Date']) + MonthEnd(1)
#     
#     # Make Last Payment date
#     df['Last Payment Date'] = df['InService Date'].apply(pd.DateOffset(months=301))
# 
#     # Convert Last Payment Date to datetime
#     df['Last Payment Date'] = pd.to_datetime(df['Last Payment Date']) + MonthEnd(1)
#==============================================================================

    return df
    
def create_first_payment_and_last_payment_date(df):
    # Make first payment date
    df['First Payment Date'] = df['InService Date'].apply(pd.DateOffset(months=1))
    
    # Convert First Payment Date to datetime
    df['First Payment Date'] = pd.to_datetime(df['First Payment Date']) + MonthEnd(1)
    
    # ********************************************  Rewrite this code **************************************
    # Make End date
    df['Last Payment Date'] = df['First Payment Date'].apply(pd.DateOffset(months=299))
    
    # Convert End date to date time
    df['Last Payment Date'] = pd.to_datetime(df['Last Payment Date'])# Make first payment date
    
    return df

def year_diff(first_date, last_date):
    
    #convert last date to timestamp
    last_date = pd.to_datetime(last_date)
    
    # convert first date to timestamp
    first_date = pd.to_datetime(first_date)
    
    # calculate year difference
    yd = ((last_date - first_date) / np.timedelta64(365, 'D')).astype(int) 
    
    return yd
    
def calculate_production(annual_attribute, Sens, DF, ins_date, curr_date, df_state_curve):
    df_state_curve = get_state_curve_data(r'C:\Users\denny.lehman\Documents\18_01 Monthly Portfolio Report\Cashflow_Modeling_Python\AP6WII_StateCurves_2018.02.23.xlsx')
    Sens = 0.975
    DF = 0.005
    curr_date = datetime.date(2018,1,1)
    ins_date = datetime.date(2012,8,1)
    year_difference = year_diff(ins_date, curr_date)
    annual_attribute = 5888 
    state = 'CA'
    seasonality_curve_factor = get_seasonality_curve(df_state_curve, state, curr_date.month, 1)
    
    production = annual_attribute * (1 - Sens) * (1 - DF) ** year_difference * seasonality_curve_factor


    return production

# Based on the state and month, return the value of the production factor. This factor
# will then be multiplied to the annual_attribute year 1 production
def get_seasonality_curve(df_state_curves, state, month_num, asset_portfolio_factor):
    ratio_val =  df_state_curves[(df_state_curves['month'] == month_num) & (df_state_curves['state'] == state)]['value'].iloc[0]
    return ratio_val
    
# function returns the state curve data and does formatting (if needed)
def get_state_curve_data(filepath):
    return pd.read_excel(filepath)

   

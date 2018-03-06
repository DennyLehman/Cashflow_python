# -*- coding: utf-8 -*-
"""
Created on Mon Mar 6 17:29:43 2018

@author: Denny.Lehman
"""


import pandas as pd
import numpy as np
import datetime
import cash_flow_functions
import time

# This file shows the framework for using a python based cash flow model to measure the fleet performance, calculate values like NPV
# and output data into excel. In this file, a datatape of assets is imported and used as a data source


# Requirements:
# datatape.xlsx
# cash_flow_functions.py
#%%
print('Hello World')

# Initialize the starttime for entire process
start_process = time.time()

# Import datatape into the datatape dataframe
df_tape = cash_flow_functions.get_datatape('datatape.xlsx')

print('Import time of datatape: {0} seconds'.format(time.time()-start_process))
#%%
# Set Constants for Model Run
# get state curve data
df_state_curve = cash_flow_functions.get_state_curve_data(r'C:\\Users\\denny.lehman\\Documents\\18_01 Monthly Portfolio Report\\Cashflow_Modeling_Python\\AP6WII_StateCurves_2018.02.23.xlsx')

# Sens
Sens = 0.975

# DF
DF = 0.005

# Discount Rate
Discount_rate = 0.06/12
#%%
# Remove systems not yet InService
df_tape = cash_flow_functions.remove_non_inService_Systems(df_tape)

# Target Contract Types
Lease_Loan_EZOwn_contracts = ['Lease', 'Loan', 'EZ Own', 'Lease Storage']

# Only pull lease, loan ez own contract types
df_lease_loan_ezown = cash_flow_functions.get_contract_type(df_tape, Lease_Loan_EZOwn_contracts)

# Only pull ppa
df_ppa_ppaez = cash_flow_functions.get_contract_type(df_tape, ['PPA', 'PPA-EZ', 'EZ PPA-Connect'])

# df_tape = cash_flow_functions.create_first_payment_and_last_payment_date(df_tape)

df_lease_loan_ezown = cash_flow_functions.create_first_payment_and_last_payment_date(df_lease_loan_ezown)

df_ppa_ppaez = cash_flow_functions.create_first_production_first_payment_and_last_payment_for_ppa(df_ppa_ppaez)

# Store tape for review
df_tape1 = df_tape
#%%
# Empty NPV array for later storing NPV values
npv_arr = [0] * (df_tape['ID'].size)

# Empty array to store the time of each cash flow creation. This will be used to optimize performance
time_array = [0] * (df_tape['ID'].size)

# build a date range
rng = pd.date_range(df_tape['InService Date'].min(), end=df_ppa_ppaez['Last Payment Date'].max() , freq= 'M')

# build the data frame with dates as indecies and a system name for each column
df_cf = pd.DataFrame(index= rng, columns= df_tape['ID'])

print('Time to setup is {0} seconds'.format(time.time() - start_process))


# rename the index as the date column
df_cf.index.name = 'Date'


# calculate the npv of the total cash flow
total_npv = cash_flow_functions.npv(Discount_rate, df_cf['Monthly Cash Flow'][df_cf['Monthly Cash Flow'].notnull()== True])

# prints the total npv as output
print('The total NPV: {0}'.format(round(float(total_npv),2)))

# calcculate the total cash flow for the fleet
df_cf['Monthly Cash Flow'] = df_cf.sum(axis=1)

# calculate the accumulated cash flow
df_cf['Cumulative Cash Flow'] = df_cf['Monthly Cash Flow'].cumsum()

# saves the model into a csv file
# df_cf.to_csv('test_nosum.csv')

df_cf.T.to_csv('test_transpose.csv')

print('Total time taken for {0} systems: {1} seconds'.format(0, time.time() - start_process))
print('Average time taken for a cash flow: {0}'.format(np.mean(time_array[1:700])))
#%%


df_production = pd.DataFrame(index = pd.date_range(df_ppa_ppaez['InService Date'].min(), df_ppa_ppaez['Last Payment Date'].max(), freq='M'), columns = df_ppa_ppaez['ID'])

# loop through each ppa type system and calculate production, then cashflow
for i in range(0, df_ppa_ppaez['ID'].size):
    # start timer
    loop_start_time = time.time()
    
    first_date = df_ppa_ppaez['First Production Date'].iloc[i]
    last_date = df_ppa_ppaez['Last Payment Date'].iloc[i]
    curr_date = df_production.loc[first_date:last_date].index
    yd = cash_flow_functions.year_diff(first_date, curr_date)
    
    state = df_ppa_ppaez['State'].iloc[i]
    month_num = curr_date.month
    sc = cash_flow_functions.get_seasonality_curve(df_state_curve, state=state, )
    annual_attribute = df_ppa_ppaez['Annual Attribute'].iloc[i]
    inservice_date = df_ppa_ppaez['InService Date'].iloc[i]

    
    
    # calculate production
    production = cash_flow_functions.calculate_production(annual_attribute=1, Sens=1, DF=0.05, ins_date=1, curr_date=1, df_state_curve=1 )

# for loop builds the cash flow for each system
for i in range(0, df_tape['ID'].size):
    
    # Start timer
    loop_start_time = time.time()
    
    # Print system name for debugging
    # print(df_tape['ID'].iloc[i])
    
    # make one data pull from df_tape
    first_date = df_tape['First Payment Date'].iloc[i]
    end_date = df_tape['End Date'].iloc[i]
    sys_name = df_tape['ID'].iloc[i]
    escalator = df_tape['Escalator'].iloc[i]
    recur_payment = df_tape['Recurring Payment'].iloc[i]
    
    # For performance, check if the escalator is 0. If so, skip the escalator function
    if escalator == 0:
        df_cf.loc[first_date:end_date, sys_name] = recur_payment
    else:
        
        # Create Int64Index of 
        # year_diff = ((df_cf.loc[ins_date:end_date].index - ins_date) / np.timedelta64(365, 'D')).astype(int)
        
        # Make year_diff integers
        # year_diff = year_diff.astype(int)
        
        # Build a series called cash_flow based on the equation payment * (1 + escalator) ^ (time difference)
        # cash_flow = df_tape['Recurring Payment'].iloc[i] * (1 + df_tape['Escalator'].iloc[i]) ** year_diff
        
        # add the cashflow to the dataframe in the system name's column
        # df_cf.loc[ins_date:end_date, sys_name] = cash_flow
        
        # This code performs the above manipulations in one line to save time
        df_cf.loc[first_date:end_date, sys_name] = recur_payment * (1 + escalator) ** ((df_cf.loc[first_date:end_date].index - first_date) / np.timedelta64(365, 'D')).astype(int)
        

    # Calculate the npv of the system and store it in the npv array
    npv_arr[i] = cash_flow_functions.npv(Discount_rate, df_cf.loc[first_date:end_date, sys_name])
    
    # End timer and store data
    time_array[i] = time.time() - loop_start_time
    
    # Print time of loop
    if i < 10:
        print('Cash flow took {0} seconds to complete'.format(time_array[i]))
    if i % 100 == 0:
        print('{0} systems processed. Time is {1} ...'.format(i, time.time() - start_process))

df_cf.T.to_csv('test_transpose.csv')
print('Total time taken for {0} systems: {1} seconds'.format(i, time.time() - start_process))
print('Average time taken for a cash flow: {0}'.format(np.mean(time_array[1:17000])))

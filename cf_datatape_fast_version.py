# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 17:29:43 2018

@author: Denny.Lehman
"""


import pandas as pd
import numpy as np
import datetime
import cash_flow_functions
import time

# This file shows the framework for using a python based cash flow model to measure the fleet performance, calculate values like NPV
# and output data into excel. In this file, a datatape of assets is imported and used as a data source

print('Hello World')

# Initialize the starttime for entire process
start_process = time.time()

# Import datatape into the datatape dataframe
df_tape = cash_flow_functions.get_datatape('datatape.xlsx')

print('Import time of datatape: {0} seconds'.format(time.time()-start_process))


# Target Contract Types
target_contracts = ['Lease', 'Loan', 'EZ Own']

# Only pull contract types
df_tape = cash_flow_functions.get_contract_type(df_tape, target_contracts)

# Remove systems not yet InService
df_tape = cash_flow_functions.remove_non_inService_Systems(df_tape)

df_tape = cash_flow_functions.create_first_payment_and_last_payment_date(df_tape)

# Store tape for review
df_tape1 = df_tape

# Empty NPV array for later storing NPV values
npv_arr = [0] * (df_tape['End Date'].size)

# Empty array to store the time of each cash flow creation. This will be used to optimize performance
time_array = [0] * (df_tape['End Date'].size)

# Discount Rate
Discount_rate = 0.06/12

# build a date range
rng = pd.date_range(df_tape['InService Date'].min(), end=df_tape['End Date'].max() , freq= 'M')

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

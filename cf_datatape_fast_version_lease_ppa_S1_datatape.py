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
df_tape = cash_flow_functions.get_S1_datatape('datatapeS1Feb.xlsx')

print('Import time of datatape: {0} seconds'.format(time.time()-start_process))
#%%
# Set Constants for Model Run
# get state curve data
df_state_curve = cash_flow_functions.get_state_curve_data('AP6WII_StateCurves_2018.02.23.xlsx')

# Sensitivity
Sens = 0.975

# Degradation factor
Degradation_Factor = 0.005

# Discount Rate
Discount_rate = 0.06/12

# Array of year difference for escalators
year_difference = cash_flow_functions.year_diff_300()

# MSA Master Servicing Agreement- agreement between AP and Sunnova
#MSA = $20 per year per kw (system size) with 2% escalator take it out every month (kw is system size)
#

#%%
# Remove systems not yet InService
df_tape = cash_flow_functions.remove_non_inService_Systems(df_tape)

# Escaltor results to decimal
df_tape['Escalator'] = df_tape['Escalator']/100

df_tape = cash_flow_functions.create_first_production_first_payment_and_last_payment_date(df_tape)

# Only pull lease, loan ez own contract types
df_lease_ezown = cash_flow_functions.get_contract_type(df_tape, ['Lease', 'EZ-Own', 'Lease Storage'])

# Only pull ppa, ppa-ez, ez ppa connect
df_ppa_ppaez = cash_flow_functions.get_contract_type(df_tape, ['PPA', 'PPA-EZ', 'EZ PPA-Connect'])

#%*******************change this code**********************
df_lease_ezown = cash_flow_functions.create_first_payment_and_last_payment_date(df_lease_ezown)

df_ppa_ppaez = cash_flow_functions.create_first_production_first_payment_and_last_payment_for_ppa(df_ppa_ppaez)


#%%
# Empty NPV array for later storing NPV values
# Empty array to store the time of each cash flow creation. This will be used to optimize performance
financial_dictionary = {'NPV':[0] * (df_tape['ID'].size), 'Calc Time':[0] * (df_tape['ID'].size), 'IRR':[0] * (df_tape['ID'].size)}
df_fin = pd.DataFrame(financial_dictionary, index=df_tape['ID'])


# build a date range
cf_date_rng = pd.date_range(df_tape['InService Date'].min(), end=df_ppa_ppaez['Last Payment Date'].max() , freq= 'M')

# build the data frame with dates as indecies and a system name for each column
df_cf = pd.DataFrame(index= cf_date_rng, columns= df_tape['ID'])

print('Time to setup is {0} seconds'.format(time.time() - start_process))


# rename the index as the date column
df_cf.index.name = 'Date'

# calcculate the total cash flow for the fleet
df_cf['Monthly Cash Flow'] = df_cf.sum(axis=1)

# calculate the accumulated cash flow
df_cf['Cumulative Cash Flow'] = df_cf['Monthly Cash Flow'].cumsum()

# calculate the npv of the total cash flow
total_npv = cash_flow_functions.npv(Discount_rate, df_cf['Monthly Cash Flow'][df_cf['Monthly Cash Flow'].notnull()== True])

# prints the total npv as output
print('The total NPV: {0}'.format(round(float(total_npv),2)))

# saves the model into a csv file
#df_cf.T.to_csv('empty.csv')

print('Total time taken for {0} systems: {1} seconds'.format(0, time.time() - start_process))
print('Average time taken for a cash flow: {0}'.format(np.mean(time_array[1:700])))
#%%

# loop through each ppa type system and calculate production, then cashflow
for i in range(0, df_ppa_ppaez['ID'].size):
    # start timer
    loop_start_time = time.time()
    
    first_date = df_ppa_ppaez['First Payment Date'].iloc[i]
    last_date = df_ppa_ppaez['Last Payment Date'].iloc[i]
    power_rate = df_ppa_ppaez['Power Rate'].iloc[i]
    escalator = df_ppa_ppaez['Escalator'].iloc[i]
    power_rate_escalator = power_rate * (1+escalator)**year_difference
    sys_name = df_ppa_ppaez['ID'].iloc[i]
    state = df_ppa_ppaez['State'].iloc[i]
    seasonality_curve = cash_flow_functions.get_seasonality_curve_300(df_state_curve, state, first_date.month)
    annual_attribute = df_ppa_ppaez['Annual Attribute'].iloc[i]
    # inservice_date = df_ppa_ppaez['InService Date'].iloc[i]

    
    
    # calculate production
    production = cash_flow_functions.calculate_production(annual_attribute, Sens, Degradation_Factor, year_difference, seasonality_curve)
    cash = production * power_rate_escalator
    
    try:
        df_cf.loc[first_date:last_date, sys_name] = cash
    except:
        print('The program stopped working on the system {0} on the interation i = {1}'.format(sys_name,i))
    
    
    # End timer and store data
    time_array[i] = time.time() - loop_start_time
    
    # Print time of loop
    if i < 10:
        print('Cash flow took {0} seconds to complete'.format(time_array[i]))
    if i % 100 == 0:
        print('{0} systems processed. Time is {1} ...'.format(i, time.time() - start_process))



#%%
        
# for loop builds the cash flow for each system
for i in range(0, df_lease_ezown['ID'].size):
    
    # Start timer
    loop_start_time = time.time()
    
    # Print system name for debugging
    # print(df_tape['ID'].iloc[i])
    
    # make one data pull from df_tape
    first_date = df_lease_ezown['First Payment Date'].iloc[i]
    end_date = df_lease_ezown['Last Payment Date'].iloc[i]
    sys_name = df_lease_ezown['ID'].iloc[i]
    escalator = df_lease_ezown['Escalator'].iloc[i]
    recur_payment = df_lease_ezown['Recurring Payment'].iloc[i]
    
    # if df_lease_loan_ezown['Contract Type'].iloc[i] == 'Loan':
        
    
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
        #df_cf.loc[first_date:end_date, sys_name] = recur_payment * (1 + escalator) ** ((df_cf.loc[first_date:end_date].index - first_date) / np.timedelta64(365, 'D')).astype(int)
        df_cf.loc[first_date:end_date, sys_name] = recur_payment * (1 + escalator) ** year_difference
        

    # Calculate the npv of the system and store it in the npv array
    npv_arr[i] = cash_flow_functions.npv(Discount_rate, df_cf.loc[first_date:end_date, sys_name])
    
    # End timer and store data
    time_array[i] = time.time() - loop_start_time
    
    # Print time of loop
    if i < 10:
        print('Cash flow took {0} seconds to complete'.format(time_array[i]))
    if i % 100 == 0:
        print('{0} systems processed. Time is {1} ...'.format(i, time.time() - start_process))

#%%
df_loan = cash_flow_functions.get_contract_type(df_tape, ['Loan'])
df_loan = cash_flow_functions.create_first_payment_and_last_payment_date(df_loan)

df_loan['Last Initial Billing Date'] = df_loan['First Payment Date'] + pd.DateOffset(months=12)
df_loan['New Billing Date'] = df_loan['First Payment Date'] + pd.DateOffset(months=13)
#pd.date_range(df_loan['First Payment Date'].iloc[i], periods=12, freq='M')
for i in range(0, df_loan['ID'].size):
    first_date = df_loan['First Payment Date'].iloc[i]
    end_of_init_pay = df_loan['Last Initial Billing Date'].iloc[i]
    start_of_new_pay = df_loan['New Billing Date'].iloc[i]
    last_date = df_loan['Last Payment Date'].iloc[i]
    sys_name = df_loan['ID'].iloc[i]
    df_cf.loc[first_date:end_of_init_pay, sys_name] = df_loan['Recurring Payment'].iloc[i]
    df_cf.loc[start_of_new_pay:last_date, sys_name] = df_loan['Monthly Pmt Without PPMT'].iloc[i]

#%%
# Write to file
print('Writing to file ...')
df_cf.T.to_csv('test_transpose.csv')
print('Total time taken for {0} systems: {1} seconds'.format(i, time.time() - start_process))
print('Average time taken for a cash flow: {0}'.format(np.mean(time_array[1:47000])))

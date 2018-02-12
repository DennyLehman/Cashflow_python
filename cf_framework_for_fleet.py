# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 21:10:45 2018

@author: Denny.Lehman
"""

import pandas as pd
import numpy as np
import datetime
import cfprocess

# This file shows the framework for using a python based cash flow model to measure the fleet performance, calculate values like NPV
# and output data into excel


# initialize system information
# System name
sys_name = ['1','2', '3']

# InService Date
ins_date = [pd.to_datetime('02/28/2018'), pd.to_datetime('04/30/2014'), pd.to_datetime('02/28/2013')]

# End date of the 300 month term
end_date = [pd.to_datetime('1/31/2043'), pd.to_datetime('3/31/2039'), pd.to_datetime('1/31/2038')]
#ins_date = [datetime.date(2018, 2, 28) , pd.to_datetime('04/30/2014')]
#end_date = [datetime.date(2043, 1, 31), datetime.date(2039, 3, 31)]

# Escalator
esc = [.029, 0, 0.19]

# Recurring Payment
recur_pmt = [95, 105, 80]

# Committed Capital
com_cap = [-1500, -20000, -30000]

# Empty NPV array for later storing NPV values
npv_arr = [0, 0, 0]

# Discount Rate
Discount_rate = 0.06

# build a date range
rng = pd.date_range('01/01/2013', end='01/01/2050' , freq= 'M')

# build the data frame with dates as indecies and a system name for each column
df = pd.DataFrame(index= rng, columns= sys_name)

# reset the index if using periods instead of dates as the index
#df.reset_index(inplace=True)

# Set index to start at 1 based on financial analysis best practices
#df.index += 1

# for loop builds the cash flow for each system
for i in range(0, len(sys_name)):
    
    # Print system name for debugging
    print(sys_name[i])
    
    # Create Int64Index of 
    year_diff = ((df.loc[ins_date[i]:end_date[i]].index - ins_date[i]) / np.timedelta64(365, 'D')).astype(int)
    
    # Make year_diff integers
    year_diff = year_diff.astype(int)
    
    # Build a series called cash_flow based on the equation payment * (1 + escalator) ** (time difference)
    cash_flow = recur_pmt[i] * (1 + esc[i]) ** year_diff
    
    # add the cashflow to the dataframe in the system name's column
    df.loc[ins_date[i]:end_date[i], sys_name[i]] = cash_flow

    # Calculate the npv of the system and store it in the npv array
    npv_arr[i] = cfprocess.npv(Discount_rate, df.loc[ins_date[i]:end_date[i], sys_name[i]])

# rename the index as the date column
df.index.name = 'Date'

#Print the date range used for the fleet
print(df.loc[min(ins_date):max(end_date)])

# calcculate the total cash flow for the fleet
df['Total Cash Flow'] = df[sys_name].sum(axis=1)

# calculate the npv of the total cash flow
total_npv = cfprocess.npv(Discount_rate, df['Total Cash Flow'][df['Total Cash Flow'].notnull()== True])

# prints the total npv as output
print('The total NPV: {0}'.format(round(float(total_npv),2)))

# saves the model into a csv file
df.to_csv('test.csv')

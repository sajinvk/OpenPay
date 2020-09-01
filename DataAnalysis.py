import argparse
import logging 
import pandas as pd 
import numpy as np 
#!pip install pandasql
import pandasql as ps 
from pathlib import Path
import os, sys 
import logging 

def GetArgs():
        """
        Supports  command-line arguments as the location of source file.
        """
        parser = argparse.ArgumentParser(
           description='Reads 2 arguments  -d (directory name ) -f (file name)')
        parser.add_argument('-d', '--input_dir_name', action='store',default = "c:\\openpay",
                                           help='CSV FILE name.')
        parser.add_argument('-f', '--input_file_name', action='store',default = "sample_data.xlsx",
                                           help='CSV FILE name.')
        
        args = parser.parse_args()
      # print (args)
        return args 
        
def CheckAccesstoFiles(v_source_file):
    """"
      Check Basic Operating System permission for source file 
    """
    try:
        source_file=Path(v_source_file)
        if os.path.isfile(source_file):
            logging.info("Source File available. Continue " + v_source_file)
        else:
            logging.error("Issue opening Source file .Check Location " + v_source_file)
            sys.exit(1)
    except:
        logging.error("I/O error or OS error.Check path  " + v_source_file )
        logging.error(sys.exc_info()[0])
        sys.exit(1)

def ReadExcel(v_source_file,v_sheetname):
    """
    Read xlsx file . Pass file name and sheet name 
    """
    try:
        df=pd.read_excel(v_source_file,sheet_name=v_sheetname)
        logging.info("Success Loading data Sheet "+v_sheetname+" into dataframe")
        return df 
    except:
        logging.error("Error reading file into dataframe ")
        sys.exit(1)
        
def RunSQL(v_sql):
    """
    execute sql and return dataframe using pandassql 
    """
    try:
        df_out = ps.sqldf(v_sql)
        logging.info("Executed SQL successfully " +v_sql )
        return df_out 
        
    except:
        logging.error("Error executing SQL query " +v_sql)
        logging.error(sys.exc_info()[0])
        sys.exit(1)

def WriteCSV(v_dataframe, v_out_file):
    """
    Write datframe to CSV in the working directory 
    """
    try:
        if len(v_dataframe) > 0:
            logging.info("Writing output to CSV File " + v_out_file )
            if (v_dataframe.to_csv(v_out_file, header=True, encoding='utf-8', index=False)):
                logging.info(v_out_file + " Written sucessfully")
    except:
        logging.error("Error Writing output to CSV File for " + v_out_file)
        logging.error(sys.exc_info()[0])
        sys.exit(1)
    
        
def main():
    v_input_file_name = ""
    v_input_dir_name= ""
    v_args = GetArgs() 
    v_input_dir_name=v_args.input_dir_name
    v_input_file_name=v_args.input_file_name
    return v_input_dir_name, v_input_file_name


# MAIN Function 
#Set up logging
v_input_dir_name,v_input_file_name   = main()
v_log_file = "aws_pos.log" 
v_log_file_path=Path(v_input_dir_name +"\\"+ v_log_file)
try:
    os.chdir(v_input_dir_name)
    v_get_dir = os.getcwd()
    print ( "Current working directory " + v_get_dir)
    logging.basicConfig(filename=v_log_file_path, 
                    level=logging.INFO, 
                    filemode='w',
                    format='%(asctime)s - %(name)s - %(threadName)s -  %(levelname)s - %(message)s') 
except IOError:
    print ("Cannot open a file in the directory. Check Directory Permission in " + v_input_dir_name  )
v_input_file_name = "sample_data.xlsx"
v_source_file =  v_input_dir_name + "\\" + v_input_file_name   
CheckAccesstoFiles(v_source_file)

#Read Files 
df_Merchant=ReadExcel(v_source_file,'tblMerchant')
df_Trans=ReadExcel(v_source_file,'tblTrans')
df_Cust=ReadExcel(v_source_file,'tblCust')


#SQL Data Model 
# Week Starts on Sunday and ends on Sat 
# Assumption : PlanRecievedOnUTC - Date sales has been made 

v_weekly_sales_retailer = """
select 
strftime('%Y', PlanReceivedOnUTC) Year,
strftime('%W', PlanReceivedOnUTC) WeekNumber,
max(date(strftime('%Y-%m-%d',PlanReceivedOnUTC), 'weekday 0', '-7 day')) WeekStart,
max(date(strftime('%Y-%m-%d',PlanReceivedOnUTC), 'weekday 0', '-1 day')) WeekEnd,
RetailerName, 
count(PurchasePrice) as Count_Sales, 
round(sum(PurchasePrice),2) as Total_Sales 
from df_Trans 
inner join df_Merchant  
where df_Trans.RetailerID = df_Merchant.RetailerID
group by Year, WeekNumber, RetailerName
order by Year, WeekNumber, RetailerName 
"""


Weekly_Sales_retailer = RunSQL(v_weekly_sales_retailer)



# WEEKLY REFUNDS BY RETAILER 
# Assumption : Refund Amount = Deposit Amount 
# NULL Data is handled in SQL statement 

v_weekly_refunds_retailer = """
select 
strftime('%Y', RefundedOn) Year,
strftime('%W', RefundedOn) WeekNumber,
max(date(strftime('%Y-%m-%d',RefundedOn), 'weekday 0', '-7 day')) WeekStart,
max(date(strftime('%Y-%m-%d',RefundedOn), 'weekday 0', '-1 day')) WeekEnd,
RetailerName, 
count(Deposit) as Count_Refund, 
round(sum(Deposit),2) as Total_Sales 
from df_Trans 
inner join df_Merchant  
where 
df_Trans.RetailerID = df_Merchant.RetailerID 
and RefundedOn is not null  
group by Year, WeekNumber, RetailerName
order by Year, WeekNumber, RetailerName 
"""

Weekly_Refund_retailer = RunSQL(v_weekly_refunds_retailer)


#Active Customer Per week 
#Active Customer = Atleast 1 plan per week . A customer active multiple times a week will be counted as 1.
#Assumption : LastUpdated column in tbltrans 
# Not taking TblCust Data as the history is lost in noramlised table 

v_active_customer = """
select 
strftime('%Y', LastUpdated) Year,
strftime('%W', LastUpdated) WeekNumber,
max(date(strftime('%Y-%m-%d',LastUpdated), 'weekday 0', '-7 day')) WeekStart,
max(date(strftime('%Y-%m-%d',LastUpdated), 'weekday 0', '-1 day')) WeekEnd,
count(distinct CustomerID) as Active_Customer_Count 
from df_Trans 
group by Year, WeekNumber
order by Year, WeekNumber 

"""

Weekly_Active_Customer = RunSQL(v_active_customer)


# Write output in dataframe to CSV in the same directory 

WriteCSV(Weekly_Sales_retailer , 'WeeklySalesRetailer.csv')
WriteCSV(Weekly_Refund_retailer , 'WeeklyRefundRetailer.csv')
WriteCSV(Weekly_Active_Customer , 'WeeklyActiveCustomer.csv')

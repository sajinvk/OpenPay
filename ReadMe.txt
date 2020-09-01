1. Uploaded ipython notebook in  git for working logic link : https://github.com/sajinvk/OpenPay/blob/master/DataAnalysis.ipynb
2. Testing environment 
   Operating System : Windows 
   Python : 3.8 
3. packages imported : pandasql argparse logging  pandas  numpy pathlib os sys 
4. Data Cleaning : Null data is not handled 
5. In the working directory , the script will create 4 files :
   aws_pos = Log file 
   3 CSV Files : WeeklyActiveCustomer , WeeklyRefundRetailer , WeeklySalesRetailer

How to run :
  1. Install packages outside standard python library .
     pip install -r requirements.txt 
     or pip install pandasql 
        pip install logging 
 2. Unizp the files to windows and copy the contents to local directory : c:\openpay 
 3. Run in command prompt C:\Users\Administrator>python C:\openpay\DataAnalysis.py
 4. the file takes 2 arguments . Working directory and source file name which is set to default value 
python C:\openpay\DataAnalysis.py -d c:\openpay -f sample_data.xlsx 
 

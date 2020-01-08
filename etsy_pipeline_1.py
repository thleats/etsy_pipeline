"""
Your module description
"""
"""
Your module description
"""
import requests
import json
import csv
import time
import math
import sys
import datetime
import subprocess
from datetime import date
from twilio.rest import Client
import calendar

account_sid = '##############################'
auth_token = '##############################'
client2 = Client(account_sid, auth_token)


def send_message(body_in):
    message = client2.messages \
                    .create(
                         body=body_in,
                         from_='+#########,
                         to='+#################'
                     )
                     

def write_the_stuff(all_data,written):
    
    with open(str(date.today()) + '_file_' + ".csv", "a",  encoding="utf-8",newline="") as f:
        writer = csv.writer(f)
        writer.writerows(all_data)
        
        all_data=[]
        print('printed')
        subprocess.run(['aws','s3','cp',str(date.today()) + '_file_' + ".csv",'s3://thleats-bucket/csvs/' + str(date.today()) + '_file_watercolor' + ".csv"])
        written=written+1
        return(written)

def request_stuff(request_count,z,keywords):
    param={'api_key': '######################','limit': 100,'keywords':keywords,'sort_on':'score','page':z+1}
    time.sleep(0.05)
    alllistingstemp=requests.get('https://openapi.etsy.com/v2/listings/active',params=param)
    request_count+=1
    try:
        temp1=json.loads(alllistingstemp.text)
        results=temp1['results']
    except:
        results=0
        print('json error in request_stuff()')
    return(results,request_count)
    
def initialize(keywords):
    param={'api_key': '#######################','limit': 100,'keywords':keywords,'sort_on':'score'}
    alllistingstemp=requests.get('https://openapi.etsy.com/v2/listings/active',params=param)
    temp1=json.loads(alllistingstemp.text)
    count_main=temp1['count']
    return(count_main)
    
def append_data(j):
    seperator=','
    epoch_time = calendar.timegm(time.gmtime())
    try:
        data=([[j['url'].replace(',',''),j['listing_id'],j['price'].replace('\'',''),j['views'],j['num_favorers'],j['quantity'],j['creation_tsz'],epoch_time,j['ending_tsz'],j['last_modified_tsz'],j['original_creation_tsz'],j['state_tsz'],j['user_id'],j['title'].replace(',',' '),seperator.join(j['tags']).replace(',','##'),seperator.join(j['description']).replace(',',''),j['featured_rank'],j['taxonomy_id']]])
        return(data)
    except:
        print('error in append_data')
        return(0)
        
def error_catching(error,written):
    if error>10:
        written=write_the_stuff(all_data,written)
        message = 'error_catching error'
        send_message(message)
        sys.exit()
            
all_data=[]

written=1
request_count=0
keywords=['watercolor','portrait']
file_length=10000

count_main=initialize(keywords)
error2=0
limit=10000
for z in range(count_main):
    try:
        print('page: ' + str(z))
        print('request count is: ' + str(request_count))
        ###test for writing
        if len(all_data)>=file_length:
                written=write_the_stuff(all_data,written)
                all_data=[]
                
        ###reset number of errors        
        error = 0
        
        ###check for number of requests
        if request_count>0.95*limit:
            sys.exit()
            message = 'limit reached'
            send_message(message)
        
        ###get the results from the page (count of 100)    
        results,request_count = request_stuff(request_count,z,keywords)    
        
        ###check if their was an error in the request_stuff
        if results != 0:  
            if error2>0:
                    error2-=1
                    
            for j in results:
                out=append_data(j)
                if out!=0:
                    all_data.append(out)
                else:
                    error+=1
                    error_catching(error,written)
        else:
            error2+=1
            error_catching(error2,written)
    
    except:
        if len(all_data)>0:
            write_the_stuff(all_data,written)
        else:
            print('error, no file length')
            message = 'error and no file length'
            send_message(message)
            sys.exit()



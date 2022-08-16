
import uuid
import boto3
import os
import codecs
import csv
import json
from datetime import datetime
from unicodedata import decimal
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
ses = boto3.client('ses', region_name=str(os.environ['REGION_NAME']))
dbtable = str(os.environ['DYNAMO_TABLE'])
dynamodb = boto3.resource(
    'dynamodb', region_name=str(os.environ['REGION_NAME'])
)

def transactions(event, context):
    print(event)
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    #get the file data from the s3.
    csv_data = get_s3_csvdata(bucket, key)
    summary = process_transactions(csv_data)
    send_email(summary)
    print(summary)

def get_s3_csvdata(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    csv_content = response['Body']
    return csv.DictReader(codecs.getreader("utf-8")(csv_content))

def process_transactions(csv_data):
    balance = debit_total = credit_total = 0
    total_by_month = dict()
    summary_data = dict()
    for transaction in csv_data:
        try:
            #The month name is used as key in order to count transactions. 
            key = get_key(transaction['Date'])
            amount = float(transaction['Transaction'])
            total_by_month[key] = total_by_month.get(key, 0) + 1
            if amount  > 0:
                credit_total += amount
            else:
                debit_total += amount
            balance += amount
        except Exception as e:
            print("Transaction not processed  Id: {} Error: {}".format(transaction['Id'], e))
        else:
            #Save transaction info to db
            save_transaction_to_db(transaction)    

    month_count = len(total_by_month)       
    summary_data['balance'] = balance
    summary_data['total_by_month'] = total_by_month
    summary_data['debit_average'] = debit_total/month_count
    summary_data['credit_average'] = credit_total/month_count
    return summary_data  
       
def get_key(date):
    datetime_obj = datetime.strptime(date, '%m/%d')
    return datetime_obj.strftime('%B')

def save_transaction_to_db(transaction):
    table = dynamodb.Table(dbtable)
    response = table.put_item(
        Item={
            'id': str(uuid.uuid4()),
            'transactionId': str(transaction['Id']),
            'date': str(transaction['Date']),
            'transaction': str(transaction['Transaction']),
            'createdAt': str(datetime.now()),
            'updatedAt': str(datetime.now())
        }
    )

def send_email(summary_data):
    try:
        response = ses.send_email(
             Destination={
                'ToAddresses': [str(os.environ['SES_SENDER'])],
            },
            Message={
                'Body': {
                    'Html': { 
                        'Data': template_html(summary_data)
                    }
                },
                'Subject': {
                    'Data': 'Summary Report'
                },
            },
            Source=str(os.environ['SES_SENDER'])
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print('Messge sent {}'.format(response['MessageId']))    


def template_html(summary):
    transactions_html = ''
    for month, count in summary['total_by_month'].items():
        transactions_html += '<p>Number of transactions in {}: {} </p>'.format(month, count)

    return """
        <html>
            <head></head>
            <body>
            <p>Total Balance is: {}</p>
            <div style="float: left; width: 40%;">{}</div>
            <div style="float: left; width: 50%;"> 
                <p>Average debit amount:{}</p>
                <p>Average credit amount:{}</p>
            </div>
            </body>
        </html>
        """.format(summary['balance'], transactions_html, summary['debit_average'], summary['credit_average'])
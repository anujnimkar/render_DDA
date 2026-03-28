import json
import boto3
import urllib.request
from datetime import datetime
from urllib.error import HTTPError, URLError

s3 = boto3.client('s3')

def get_date_12_months_ago():
    """Calculate date exactly 12 months ago using only stdlib"""
    now = datetime.utcnow()
    year, month, day = now.year, now.month, now.day
    
    # Subtract 12 months
    if month > 1:
        month -= 1
    else:
        month = 12
        year -= 1
    
    # Ensure valid day (handles month-end cases)
    try:
        return datetime(year, month, 1, 0, 0, 0)
    except ValueError:
        # If day doesn't exist in target month, use last day
        from calendar import monthrange
        last_day = monthrange(year, month)[1]
        return datetime(year, month, last_day, 0, 0, 0)

BUCKET = 'sf-fire-feeds'

def lambda_handler(event, context):
    date_str = datetime.now().strftime('%Y/%m/%d')
    twelve_months_ago = get_date_12_months_ago()
    date_filter = twelve_months_ago.strftime('%Y-%m-%dT00:00:00.000')
    
    URL = f'https://data.sfgov.org/resource/nuek-vuh3.csv?$where=received_dttm>\'{date_filter}\'&$limit=100000'
    key = f"raw/date={date_str}/fire_ems_calls_12mo.csv"
    
    print(f"Fetching data since: {date_filter}")
    print(f"URL: {URL}")
    
    try:
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=120) as resp:
            content = resp.read()
        
        s3.put_object(
            Bucket=BUCKET,
            Key=key,
            Body=content,
            ContentType='text/csv',
            Metadata={
                'source': 'data.sfgov.org', 
                'download_date': date_str,
                'data_since': date_filter
            }
        )
        print(f"Uploaded {len(content)} bytes to s3://{BUCKET}/{key}")
        return {
            'statusCode': 200, 
            'key': key, 
            'data_since': date_filter,
            'bytes': len(content)
        }
    except (HTTPError, URLError) as e:
        print(f"HTTP error: {str(e)}")
        raise
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

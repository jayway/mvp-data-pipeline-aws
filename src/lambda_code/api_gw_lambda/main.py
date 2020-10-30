import os
import json
import time
import boto3
from base64 import b64decode

_device_fields = ['CloudFront-Is-Desktop-Viewer', 'CloudFront-Is-Mobile-Viewer', 'CloudFront-Is-SmartTV-Viewer',
                  'CloudFront-Is-Tablet-Viewer']

_region = os.environ['region']
_stream_name = os.environ['stream_name']
_firehose_client = boto3.client('firehose', region_name=_region)


# Function to extract the device using the fields in _device_fields list
def _get_device(event: dict) -> str:
    for field in _device_fields:
        if event['headers'].get(field, None) == 'true':
            return field.split('-')[2]
    return 'Unknown'


# Function to extract the b64 encoded payload part of the event (the custom part)
def _get_payload(event: dict) -> dict:
    return json.loads(b64decode(event['queryStringParameters']['data']).decode())


def _post_to_firehose(data: dict) -> dict:
    # Add a newline (\n) at the end of the json as firehose will create json line documents
    record = {'Data': json.dumps(data) + '\n'}
    return _firehose_client.put_record(DeliveryStreamName=_stream_name, Record=record)


def _get_geo_country(data: dict) -> str:
    return data['headers'].get('CloudFront-Viewer-Country', None)


def _get_user_agent(data: dict) -> str:
    return data['headers'].get('User-Agent', None)


def handler(event: dict, _) -> dict:
    try:
        payload = _get_payload(event)
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'No "data" field found.'})
        }

    data_package = {
        'geo_country': _get_geo_country(event),
        'device': _get_device(event),
        'user_agent': _get_user_agent(event),
        'event_data': payload,
        'utc_timestamp': time.time()
    }

    _post_to_firehose(data_package)

    return {
        'statusCode': 200,
        'body': json.dumps(data_package)
    }

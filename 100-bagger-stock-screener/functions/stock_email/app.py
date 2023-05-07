import os
from typing import Dict, List

import boto3


def create_email_body(data: List[Dict]) -> str:
    """based on list of input data, create an email body"""

    list_of_strings = []
    
    for record in data:

        # extract data from dictionary as list of strings
        record_as_list = [f'{key}: {value}' for key, value in record.items()]

        # append a newline onto the list
        record_as_list.append('\n')

        # append onto main list
        list_of_strings.extend(record_as_list)

    # join the list of strings into a single string, separating each record by new line
    return '\n'.join(list_of_strings)


def lambda_handler(event, context):
    """
    Sends an email to a recipient (stored privately in env),
    returning data contained within event argument
    """

    # Get the recipient from the input event
    # TODO: get recipient from email-list (hardcode into function?)
    recipient = event['RECIPIENT']

    # Create an SES resource
    ses = boto3.client('ses')

    # loop through recipients from email-list
    response = ses.send_email(
        Source=recipient,
        Destination={
            'ToAddresses': [
                recipient,
            ],
        },
        Message={
            'Subject': {
                'Data': 'Stock list',
            },
            'Body': {
                'Text': {
                    'Data': create_email_body(event['data'])
                },
            },
        },
    )

    return response
    
    




"""
This script is designed to receive a post from Okta via an API gateway.
It takes the username from Okta and checks via an API call if the proposed
 username already exists. If it does, it appends a number 1-9 to the end
 and tries again until it finds a username that isn't taken.
"""
import json
import os
from botocore.vendored import requests


def make_okta_response(username):
    """
    Takes the response format Okta is looking for and injects
    the new username into the corresponding fields.
    :param username (string): string that is resulting email
    :return: created response dictionary
    """
    response = {
        "commands": [{
            "type": "com.okta.user.profile.update",
            "value": {
                "login": username,
                "email": username
            }
        }]
    }
    return response


def user_api_call(username, api_headers):
    """
    :param api_headers (dictionary): dictionary that contains the API request headers
    :param username (string):  username to check in the Okta API
    :return: response of the api call
    """
    url = f'https://vivintsolar.okta.com/api/v1/users/{username}'
    request = requests.get(url, headers=api_headers)
    response = request.status_code
    return response


def check_okta_user(username, api_headers):
    """
    Checks proposed username, if exists, append a number and check again.
    :return: string for the okta username that
    """
    status_code = user_api_call(username, api_headers)
    if status_code == 200:
        i = 0
        exists = False
        while not exists:  # Need to revisit this to make more scalable solution
            i += 1
            new_username = username + str(i)
            url1 = f'https://vivintsolar.okta.com/api/v1/users/{new_username}'
            request2 = requests.get(url1, headers=api_headers)
            status_code = request2.status_code
            if status_code == 404:
                new_username = new_username + "@vivintsolar.com"
                exists = True
                return new_username

    elif status_code == '404':
        return username


def main_handler(event, context):
    """main handler for lambda script"""
    api_key = os.environ['API_KEY']
    okta_headers = {'Accept': 'application/json', 'Content-Type': 'application/json',
                    'Authorization': f"SSWS {api_key}"}

    body = json.loads(event['body'])
    profile = body['profile']
    email = profile['login']
    username = email.split('@')[0]
    new_username = check_okta_user(username, okta_headers)
    response = make_okta_response(new_username)


    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

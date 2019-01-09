from gfypy.constants import (TOKEN_ENDPOINT, REQUEST_ENDPOINT, FILE_UPLOAD_ENDPOINT,
                FILE_UPLOAD_STATUS_ENDPOINT, GFY_URL, GFY_REQUEST_ENDPOINT, USER_CHECK_ENDPOINT, USER_ENDPOINT)

from gfypy.errors import GfyCatAuthError, GfyPyClientError

import requests as req


import logging, time


def check_user_avaliability(username, headers):
    '''
    Check if a username is avaliable based on response codes from
            The api

    Parameters
    -----------
    username : String
        String containing the username
    headers : dict
        our authentication headers we need for everything
    '''
    r = req.head(USER_CHECK_ENDPOINT + username, headers=headers)
    return r.status_code


def check_email_verified(headers):
    '''
    Check if the email is verified.

    Parameters
    ----------
    headers : dict
        auth headers
    
    Returns
    -------
    int
        Status code
    '''
    r = req.get(USER_ENDPOINT + "email_verified/")
    return r.status_code

def send_verification_email(headers):
    '''
    Send Verification email to user. We wont perform a verified check, if
            someone needs to use this class they are likely overwriting my
            handler and can include the check as they wish there
    
    Parameters
    ----------
    '''
    r = req.post(USER_ENDPOINT + "send_verification_email/")
    return r.status_code

def get_auth_headers(auth_header_request_body):
    '''
    Grab an authentication header for us to use

    Parameters
    ----------
    auth_header_request_body : dict
        Dictionary containing the client id/secret and user/pass

    Returns
    ----------
    auth_header : dict
        Dictionary containing the auth header
    '''
    body = auth_header_request_body
    logging.debug(body)
    # Get a token
    r = req.post(TOKEN_ENDPOINT, json=body)


    if r.status_code != 200:
        if r.status_code == 401:
            raise GfyCatAuthError('Incorrect Credentials')
        else:
            raise GfyPyClientError('Error requesting authentication headers', r.status_code)

    response = r.json()
    if 'error' in response:
        raise GfyPyClientError(response['error'])


    access_token = r.json().get("access_token")

    logging.debug("access_token: " + access_token)

    auth_header = {
        "Authorization": "Bearer {}".format(access_token)
    }

    return auth_header


def get_url(headers, gif_param):
    '''
    Request a GfyCat URL for us to use

    Parameters
    ----------
    headers : dict
        Auth headers we requested earlier
    gif_param : dict
        Specific settings for the upload

    Return
    ----------
    gfy_id : str
        The ID we will interact with for the gif we are uploading
    '''
    # Ask GfyCat for an URL
    r = req.post(REQUEST_ENDPOINT, json=gif_param, headers=headers)

    if r.status_code != 200:
        raise GfyPyClientError('Error fetching the URL', r.status_code)

    response = r.json()
    if 'error' in response:
        raise GfyPyClientError(response['error'])

    # Get the name out of the data it sends
    gfy_id = r.json().get("gfyname")



    logging.debug("gfyID: " + gfy_id)

    return gfy_id
def fetch_gfy(gfy_id):
    return req.get(GFY_REQUEST_ENDPOINT + gfy_id)
def upload_file(gfy_id, video_name):
    '''
    Actual uploading of the file goes on here

    Paramaters
    ----------
    gfy_id : str
        gfycat id we grabbed earlier
    video_name : str
        path to the video we're uploading
    '''
    logging.debug("Attempting to Upload to GfyCat")
    # We will use this to check whether the video is uploading or not
    upload_status = "encoding"

    # Put the entire file in a dict because logic
    with open(video_name, 'rb') as payload:
        files = {
            'file': (video_name, payload),
            'key': gfy_id,
        }
        # Upload dict
        res = req.post(FILE_UPLOAD_ENDPOINT, files=files)
        if res.status_code != 200:
            raise GfyPyClientError('Error fetching the URL', res.status_code)

    response = res.json()
    if 'error' in response:
        raise GfyPyClientError(response['error'])
    logging.debug(res.text)
    # Hang the program till the upload finishes
    while upload_status != "complete":
        check_return = req.get(FILE_UPLOAD_STATUS_ENDPOINT + gfy_id)
        upload_status = check_return.json().get("task")

        logging.debug("Status: " + upload_status)
        time.sleep(5)

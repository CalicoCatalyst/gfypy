from gfypy.constants import (TOKEN_ENDPOINT, REQUEST_ENDPOINT, FILE_UPLOAD_ENDPOINT,
                FILE_UPLOAD_STATUS_ENDPOINT, GFY_URL)
from gfypy.errors import GfyPyClientError

import requests as req
import time, json

import logging

class GfyCatClient(object):
    def __init__(self, client_id, client_secret, username, password):
        # Store the authentication and the dict needed to request an auth header

        self._client_id = client_id
        self._client_secret = client_secret
        self._username = username
        self._password = password
        self._auth_header_request_body= {
            "grant_type": "password",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "username": self._username,
            "password": self._password
        }
    def upload_file(self, file_name, title="Title", desc="Description", noMd5 = True, private = True):
        '''
        Upload a file based on the given name

        Parameters
        ----------
        file_name : str
            The path to the file we will be uploading
        title : str
            Title of the gif
        desc : str
            Description of the gif
        noMd5 : bool
            Ignore checking to see if an upload already exists
        private : bool
            Prevent the image from being published to the public gallery

        Returns
        ----------
        str
            String containing a link to the uploaded file

        '''



        gif_param = {
            "title": title,
            "description": desc,
            "private": private,
            "noMd5": noMd5
            }


        auth_headers = _auth_headers(self._auth_header_request_body)
        gfy_id = _get_url(auth_headers, gif_param)
        _upload_file(gfy_id, file_name)
        return gfyUrl.format(gfy_id)

    def _get_auth_headers(self, auth_header_request_body):
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
        token = req.post(TOKEN_ENDPOINT, json=body)


        if req.status_code != 200:
            raise GfyPyClientError('Error fetching the URL', req.status_code)

        response = req.json()
        if 'error' in response:
            raise GfyPyClientError(response['error'])


        access_token = token.json().get("access_token")

        logging.debug("access_token: " + access_token)

        auth_header = {
            "Authorization": "Bearer {}".format(access_token)
        }

        return auth_header


    def _get_url(self, headers, gif_param):
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
        gfy_return = req.post(REQUEST_ENDPOINT, json=gif_param, headers=headers)

        if req.status_code != 200:
            raise GfyPyClientError('Error fetching the URL', req.status_code)

        response = req.json()
        if 'error' in response:
            raise GfyPyClientError(response['error'])

        # Get the name out of the data it sends
        gfy_id = gfy_return.json().get("gfyname")



        logging.debug("gfyID: " + gfy_id)

        return gfy_id
    def _upload_file(self, gfy_id, video_name):
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

class GfyCat(object):
    '''
    Represents a GfyCat (uploaded gif) and provides variables to view it. 
    '''

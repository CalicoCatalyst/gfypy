from gfypy.constants import GFY_URL
from gfypy.errors import GfyPyClientError, GfyCatAuthError
import gfypy.utils as util

import logging
from gfypy.utils import fetch_gfy

class GfyCatClient(object):
    def __init__(self, client_id, client_secret, username, password):
        # Store the authentication and the dict needed to request an auth header

        self._client_id = client_id
        self._client_secret = client_secret
        self._username = username
        self._password = password
        self._auth_header_request_body = {
            "grant_type": "password",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "username": self._username,
            "password": self._password
        }
    def get_ah(self):
        return util.get_auth_headers(self._auth_header_request_body)
        
    # This file is going to follow a noticable pattern
    # There is a forward facing method that calls on a similarly named utility
    #       method. API interaction mainly occurs in the back methods. The forward
    #       facing methods should be basic

    def check_user_avaliability(self, username):
        '''
        Check if a username is available

        Paramaters
        ----------
        username : str
            Username to check

        Returns
        -------
        bool
            True if its available, false if its not or isn't a valid username

        Raises
        ------
        GfyCatAuthError
            If the credentials go bad or aren't there in the first place
        GfyPyClientError
            If a bad response from the server is received
        '''

        # 404 Not Found	The username was not found which means that it is available.
        # 422 Unprocessable Entity	The username was invalid.
        # 2** No Content	The username was found which means that the username is unavailable.
        # 401 Unauthorized	You need to provide a valid token to perform this action
        auth_header = util.get_auth_headers(self._auth_header_request_body)
        code = util.check_user_avaliability(username, auth_header)
        if code == 404:
            return True
        elif code == 422:
            return False
        elif  200 <= code <= 299:
            return False
        elif code == 401:
            # This should never happen, we catch it grabbing headers
            raise GfyCatAuthError('Bad credentials or none provided')
        else:
            # GfyCat *says* this shouldn't happen but GfyCat API docs aren't that
            #       great
            raise GfyPyClientError('Bad response received', code)

    def check_email_verified(self):
        # 404 Not Found    The email attached to the token bearer’s username is not verified.
        # 2** No Content    The email attached to the token bearer’s username is verified.
        # 401 Unauthorized    You need to provide a valid token to perform this action
        auth_header = self.get_ah()
        code = util.check_email_verified(auth_header)
        if 200 <= code <= 299:
            return True 
        elif code == 404:
            return False 
        elif code == 401:
            raise GfyCatAuthError('Bad Credentials or none provided')
        else:
            raise GfyPyClientError('Bad response received', code)
        
    def send_verification_email(self, check_verified=True):
        email_verified = True if (200 <= util.check_email_verified(util.get_auth_headers(self._auth_header_request_body)) <= 299) else False 
        if check_verified and not email_verified:
            logging.info("Email already verified. Set check_verified = False to force it anyways (why?)")
            return
        util.send_verification_email(self._auth_header_request_body)
        

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
        GfyCat
            Object containing as much data as gfycat will give us on the uploaded image

        '''

        gif_param = {
            "title": title,
            "description": desc,
            "private": private,
            "noMd5": noMd5
            }

        auth_headers = util.get_auth_headers(self._auth_header_request_body)
        gfy_id = util.get_url(auth_headers, gif_param)
        util.upload_file(gfy_id, file_name)
        return GfyCat(gfy_id)

class GfyCat(object):
    '''
    Represents a GfyCat (uploaded gif) and provides variables to view it.
    '''
    def __init__(self, gfy_id):
        # {"gfyItem": {"gfyId":"{gfyid}","gfyName":"{gfyname}","gfyNumber":"{gfynumber}","webmUrl":"", 
        # "gifUrl":"","mobileUrl":"","mobilePosterUrl":"","miniUrl":"","miniPosterUrl":"",
        # "posterUrl":"","thumb100PosterUrl":"", "max5mbGif":"","max2mbGif":"","max1mbGif":"",
        # "gif100px":"","width":0, "height":0,"avgColor":"#000000","frameRate":1,"numFrames":1,"mp4Size":1,
        # "webmSize":1, "gifSize":1,"source":1,"createDate":1,"nsfw":"0","mp4Url":"","likes":"0","published":1,
        #  "dislikes":"0","extraLemmas":"","md5":"0","views":0,"tags":[""],"userName":"anonymous", "title":"","description":"",
        # "languageText":"","languageCategories":null,"subreddit":"", "redditId":"","redditIdText":"","domainWhitelist":[]}}
        self.gfy_id = gfy_id
        self.valid = True
        
        response = fetch_gfy(gfy_id)
        if response.status_code == 404:
            self.valid = False
        elif response.status_code == 200:
            self._info = response.json()
            self._gfyitem = self._info.get("gfyItem")
            
            
            self.gfyId = self._gfyitem.get("gfyId")
            self.gfyName = self._gfyitem.get("gfyName")
            self.gfyNumber = self._gfyitem.get("gfyNumber")
            self.webmUrl = self._gfyitem.get("webmUrl")
            self.gifUrl = self._gfyitem.get("gifUrl")
            self.mobileUrl = self._gfyitem.get("mobileUrl")
            self.mobilePosterUrl = self._gfyitem.get("mobilePosterUrl")
            self.miniUrl = self._gfyitem.get("miniUrl")
            self.miniPosterUrl = self._gfyitem.get("miniPosterUrl")
            self.posterUrl = self._gfyitem.get("posterUrl")
            self.thumb100PosterUrl = self._gfyitem.get("thumb100PosterUrl")
            self.max5mbGif = self._gfyitem.get("max5mbGif")
            self.max2mbGif = self._gfyitem.get("max2mbGif")
            self.max1mbGif = self._gfyitem.get("max1mbGif")
            self.gif100px = self._gfyitem.get("gif100px")
            self.width = self._gfyitem.get('width')
            self.height = self._gfyitem.get('height')
            self.avgColor = self._gfyitem.get('avgColor')
            self.frameRate = self._gfyitem.get('frameRate')
            self.numFrames = self._gfyitem.get('numFrames')
            self.mp4Size = self._gfyitem.get('mp4Size')
            self.webmSize = self._gfyitem.get('webmSize')
            self.gifSize = self._gfyitem.get('gifSize')
            self.source = self._gfyitem.get('source')
            self.createDate = self._gfyitem.get('createDate')
            self.nsfw = False if (self._gfyitem.get('nsfw') == "0") else True
            self.mp4Url = self._gfyitem.get('mp4Url')
            self.likes = self._gfyitem.get('likes')
            self.published = self._gfyitem.get('published')
            self.dislikes = self._gfyitem.get('dislikes')
            # I have no idea what this is 
            self.extraLemmas = self._gfyitem.get('extraLemmas')
            self.md5 = self._gfyitem.get('md5')
            self.views = self._gfyitem.get('views')
            self.tags = self._gfyitem.get('tags')
            self.userName = self._gfyitem.get('userName')
            self.title = self._gfyitem.get('title')
            self.description = self._gfyitem.get('description')
            self.languageText = self._gfyitem.get('languageText')
            self.languageCategories = self._gfyitem.get('languageCategories')
            self.subreddit = self._gfyitem.get('subreddit')
            self.redditId = self._gfyitem.get('redditId')
            self.redditIdText = self._gfyitem.get('redditIdText')
            self.domainWhitelist = self._gfyitem.get('domainWhitelist')
    def __str__(self):   
        return self.gfy_id     

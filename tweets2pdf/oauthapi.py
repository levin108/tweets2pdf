#!/usr/bin/python
# -*- coding:utf8 -*-
"""
Copyright (C) 2011 by lwp
levin108@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the
Free Software Foundation, Inc.,
51 Franklin Street, Suite 500, Boston, MA 02110-1335, USA.
"""

import oauth
import config
import Image
import types
import os, time, urllib2, urllib
from xml.dom import minidom

CONSUMER_KEY = 'V3r08E6kXGWFKDM72yl66g'
CONSUMER_SECRET = 's3R6uQuadL91TulXwvUW2773hgePfQ2zHOmCNKuOjU'

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
SIGNIN_URL = 'https://api.twitter.com/oauth/authenticate'
RESOURCE_URL = 'http://api.twitter.com/1/%s.xml'

class tpOAuth(oauth.OAuthClient):
    
    def __init__(self, http_proxy = None):
        self.request_token_url = REQUEST_TOKEN_URL
        self.access_token_url = ACCESS_TOKEN_URL
        self.authorization_url = AUTHORIZATION_URL
        self.consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
        self.signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
        self.http_proxy = http_proxy

    def _set_http_proxy(self, proxy_type = 'http'):
        try:
            if self.http_proxy is None:
                null_handler = urllib2.ProxyHandler({})
                opener = urllib2.build_opener(null_handler, urllib2.HTTPHandler)
                urllib2.install_opener(opener)
                return
            proxy = 'http://' + self.http_proxy['host'] + ':' + self.http_proxy['port']
            proxy_support = urllib2.ProxyHandler({proxy_type: proxy})
            opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
        except:
            null_handler = urllib2.ProxyHandler({})
            opener = urllib2.build_opener(null_handler, urllib2.HTTPHandler)
        finally:
            urllib2.install_opener(opener)

    
    def save_access_token(self):

        token_file = open(config.get_app_dir() + '/token.xml', 'w')

        impl = minidom.getDOMImplementation()

        doc = impl.createDocument(None, 'twitter', None)
        root = doc.documentElement
        item = doc.createElement('access_token_key')
        text = doc.createTextNode(self.access_token.key)
        item.appendChild(text)
        root.appendChild(item)
        item = doc.createElement('access_token_secret')
        text = doc.createTextNode(self.access_token.secret)
        item.appendChild(text)
        root.appendChild(item)
        item = doc.createElement('screen_name')
        text = doc.createTextNode(self.access_token.screen_name)
        item.appendChild(text)
        root.appendChild(item)

        token_file.write(root.toxml())

        token_file.close()

    def restore_access_token(self):

        try:
            doc = minidom.parse(config.get_app_dir() + '/token.xml')
            root = doc.documentElement
            item = root.getElementsByTagName('access_token_key')
            token_key = item[0].childNodes[0].data
            item = root.getElementsByTagName('access_token_secret')
            token_secret = item[0].childNodes[0].data
            item = root.getElementsByTagName('screen_name')
            screen_name = item[0].childNodes[0].data

            self.access_token = oauth.OAuthToken(token_key, token_secret)
            self.access_token.set_screen_name(screen_name)

            return True
        except:
            return False

    def make_oauth_request(self, http_method = 'GET', http_url = {}, has_param = False, parameters = None, token = None):

        param = {
            'oauth_version': '1.0',
            'oauth_timestamp': int(time.time()),
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_consumer_key': self.consumer.key
            }
        
        if(parameters):
            param.update(parameters)

        if(token):
            param.update({ 'oauth_token': token.key })

        oauth_request = oauth.OAuthRequest(http_method = http_method, http_url = http_url, parameters = param)
        oauth_request.sign_request(self.signature_method, self.consumer, token)

        oauth_header = oauth_request.to_header()

        if http_method == 'POST':
            postdata = oauth_request.to_postdata()
            req = urllib2.Request(http_url, postdata, oauth_header)
        else:
            if has_param:
                url = oauth_request.to_url()
                req = urllib2.Request(url)
            else:
                url = http_url
                req = urllib2.Request(url, None, oauth_header)
        
        try:
            req = urllib2.urlopen(req)
            return req.read()
        except urllib2.URLError as e:
            return e
        except urllib2.HTTPError as e:
            return e

    def fetch_request_token(self):

        self._set_http_proxy('https')
        extra_param = { 'oauth_callback': 'oob' }
        response = self.make_oauth_request(http_method = 'GET', http_url = REQUEST_TOKEN_URL, parameters = extra_param)
        if type(response) != types.StringType:
            return None
        return oauth.OAuthToken.from_string(response)
    
    def fetch_access_token(self, request_token = {}, verifier = {}):

        self._set_http_proxy('https')
        extra_param = { 'oauth_verifier': verifier }
        response = self.make_oauth_request(http_method = 'POST', \
                               http_url = ACCESS_TOKEN_URL, \
                               parameters = extra_param, \
                               token = request_token)
        self.access_token = oauth.OAuthToken.from_string(response)
        return self.access_token

    def fetch_url_result(self, http_method = 'GET', http_path = {}, options = None):

        self._set_http_proxy('http')
        http_url = RESOURCE_URL % http_path
        try:
            return self.make_oauth_request(http_method = http_method, \
                                   http_url = http_url, \
                                   has_param = True, \
                                   parameters = options, \
                                   token = self.access_token)
        except:
            return None

    def fetch_retweeted_by_me(self, tweets_max_id = {}, tweets_min_id = {}, page = None):

        options = { 'include_entities': 'true' }
        
        if page:
            options['page'] = page

        if tweets_max_id != 0:
            options['max_id'] = tweets_max_id

        if tweets_min_id != 0:
            options['since_id'] = tweets_min_id

        return self.fetch_url_result(http_path = 'statuses/retweeted_by_me', options = options)

    def fetch_retweets_of_me(self, tweets_max_id = {}, tweets_min_id = {}, page = None):

        options = { 'include_entities': 'true' }
        
        if page:
            options['page'] = page

        if tweets_max_id != 0:
            options['max_id'] = tweets_max_id

        if tweets_min_id != 0:
            options['since_id'] = tweets_min_id

        return self.fetch_url_result(http_path = 'statuses/retweets_of_me', options = options)

    def fetch_user_timeline(self, screen_name = {}, tweets_max_id = {}, tweets_min_id = {}, page = None):
        
        options = {
            'screen_name': screen_name,        
            'count': 30,
            'include_entities': 'true',
            'include_rts': 'true'
            }

        if tweets_max_id != 0:
            options['max_id'] = tweets_max_id

        if tweets_min_id != 0:
            options['since_id'] = tweets_min_id

        if page:
            options['page'] = page

        return self.fetch_url_result(http_path = 'statuses/user_timeline', options = options)

    def fetch_user_information(self, screen_name = {}):

        options = {
            'screen_name': screen_name,
            'include_entities': 'true'
            }

        return self.fetch_url_result(http_path = 'users/show', options = options)

    def fetch_favorites(self, screen_name = {}, page = None):
        options = {
            'screen_name': screen_name,
            'include_entities': 'true'
            }

        if page:
            options['page'] = page

        return self.fetch_url_result(http_path = 'favorites', options = options)


    def fetch_followers(self, screen_name = {}, cursor = -1):

        options = {
            'screen_name': screen_name,
            'include_entities': 'true',
            'cursor': cursor
            }

        return self.fetch_url_result(http_path = 'statuses/followers', options = options)

    def fetch_friends(self, screen_name = {}, cursor = -1):

        options = {
            'screen_name': screen_name,
            'include_entities': 'true',
            'cursor': cursor
            }

        return self.fetch_url_result(http_path = 'statuses/friends', options = options)

    def fetch_profile_image(self, screen_name = {}, file_type = {}, size = None):

        filename = '%s/%s.%s' % ( config.get_icon_dir(), screen_name , file_type)
        outname  = '%s/%s.jpg' % (config.get_icon_dir(), screen_name)

        if os.path.exists(filename) and os.path.isfile(filename):
            try:
                Image.open(filename)
                if file_type == 'jpg' or file_type == 'jpeg' or \
                        file_type == 'JPG' or file_type == 'JPEG':
                    return filename
                else:
                    try:
                        Image.open(outname)
                        return outname
                    except:
                        return config.get_app_icon()
            except:
                return config.get_app_icon()

        if size is not None:
            options = { 'size': size}
        else:
            options = None

        retry = 0
        while True:
            img = self.fetch_url_result(http_path = 'users/profile_image/' + screen_name, options = options)
            retry += 1
            if type(img) != types.StringType:
                if retry == 3:
                    return config.get_app_icon()
                continue
            break

        try:
            file = open(filename, 'wb')
            file.write(img)
            file.close()
            Image.open(filename)
        except:
            return config.get_app_icon()

        if file_type == 'jpg' or file_type == 'jpeg' or \
                file_type == 'JPG' or file_type == 'JPEG':
            return filename

        count = 0
        while True:
            try:
                img = Image.open(filename)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(outname, 'JPEG')
                img = Image.open(outname)
                return outname
            except:
                count += 1
                if count == 4:
                    return filename
                continue

        return outname

    def authorization_token(self, token):
        oauth_request = oauth.OAuthRequest.from_token_and_callback(token, http_url = self.authorization_url)
        import webbrowser
        print oauth_request.to_url()
        webbrowser.open_new_tab(oauth_request.to_url())

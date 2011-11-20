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

import re
import template

class ttuser:

    def __init__(self):
        pass

    def load_user_info(self, xmlnode = {}):
        self.screen_name = xmlnode.getElementsByTagName('screen_name')[0].childNodes[0].data
        childnodes = xmlnode.getElementsByTagName('name')[0].childNodes
        if len(childnodes) > 0:
            self.name = childnodes[0].data

        childnodes = xmlnode.getElementsByTagName('profile_image_url')[0].childNodes
        if len(childnodes) > 0:
            self.profile_image_url = childnodes[0].data
        else:
            self.profile_image_url = ''

        if len(self.profile_image_url) > 0:
            index = self.profile_image_url.rfind('.')
            self.image_type = self.profile_image_url[index + 1:]
        else:
            self.image_type = 'jpg'

        childnodes = xmlnode.getElementsByTagName('location')[0].childNodes
        if len(childnodes) > 0:
            self.location = childnodes[0].data
        else:
            self.location = ''

        childnodes = xmlnode.getElementsByTagName('description')[0].childNodes
        if len(childnodes) > 0:
            self.description = childnodes[0].data
        else:
            self.description = ''

        childnodes = xmlnode.getElementsByTagName('url')[0].childNodes
        if len(childnodes) > 0:
            self.url = childnodes[0].data
        else:
            self.url = '#'

        self.friends_count = xmlnode.getElementsByTagName('friends_count')[0].childNodes[0].data
        self.followers_count = xmlnode.getElementsByTagName('followers_count')[0].childNodes[0].data
        self.status_count = xmlnode.getElementsByTagName('statuses_count')[0].childNodes[0].data

class ttstatus:

    def __init__(self, link_color = 'blue'):
        self.link_color = link_color

    def convert_link(self, link_str = {}):

        p = re.compile('rel=\".*[^\"].*\"')
        return p.sub('', link_str)

    def convert_time(self, time_str = {}):
        time_index = time_str.index('+')
        time_prefix = time_str[0:time_index]
        time_suffix = time_str[time_index:]
        time_index = time_suffix.index(' ')
        time_suffix = time_suffix[time_index:]

        time_str = time_prefix + time_suffix
        return time_str

        #create_at = time.strptime(create_at, '%a %b %d %H:%M:%S %Y')

    def _process_entities(self, status_entry = {}, status_text = {}):

        entities = status_entry.getElementsByTagName('entities')[0]
        mentions = entities.getElementsByTagName('user_mentions')[0]
        for mention in mentions.getElementsByTagName('user_mention'):
            mention_name = mention.getElementsByTagName('screen_name')[0].childNodes[0].data
            p = re.compile('@' + mention_name)
            status_text = p.sub(template.MENTION_TEMPLATE % \
                    (mention_name, self.link_color, mention_name), status_text)

        urls = entities.getElementsByTagName('urls')[0]
        for url in urls.getElementsByTagName('url'):
            url_childnodes = url.getElementsByTagName('url')
            if len(url_childnodes) == 0:
                continue
            url_value = url_childnodes[0].childNodes[0].data

            # in case of an url like 'talk.google.com' without a protocol prefix,
            # which causes the pdfdoc to throw out an exception.
            if (url_value.find('http://') != 0 and url_value.find("https://") != 0):
                continue

            p = re.compile(url_value)
            status_text = p.sub(template.URL_TEMPLATE % \
                    (url_value, self.link_color, url_value), status_text)
            print status_text
        
        return status_text

    def load_status(self, xmlnode = {}):

        self.source = xmlnode.getElementsByTagName('source')[0].childNodes[0].data
        self.source = self.convert_link(self.source)
        self.create_at = xmlnode.getElementsByTagName('created_at')[0].childNodes[0].data
        self.create_at = self.convert_time(self.create_at)
        self.tweets_id = long(xmlnode.getElementsByTagName('id')[0].childNodes[0].data)
        status_text_node = xmlnode.getElementsByTagName('text')[0]
        self.status_text = status_text_node.childNodes[0].data
        self.status_text = self._process_entities(xmlnode, self.status_text)

#!/usr/bin/python
# -*- coding=utf8 -*-
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
import os
import platform
from xml.dom import minidom

def get_home_dir():
    try:
        system = platform.system()
        if system == 'Windows':
            return os.getenv('ALLUSERSPROFILE')
        else:
            return os.environ['HOME']
    except:
        return None

def get_app_dir():
    home_dir = get_home_dir()
    if home_dir is None:
        return None
    system = platform.system()
    if system == 'Windows':
        app_dir = home_dir + '/tweets2pdf'
    else:
        app_dir = home_dir + '/.tweets2pdf'
    if not os.path.exists(app_dir):
        os.mkdir(app_dir)
    return app_dir

def get_icon_dir():
    app_dir = get_app_dir()
    if app_dir is None:
        return None
    icon_dir = app_dir + '/icons'
    if not os.path.exists(icon_dir):
        os.mkdir(icon_dir)
    return icon_dir

def get_app_icon():
    if os.path.exists('tweets2pdf.png'):
        return 'tweets2pdf.png'
    if os.path.exists('/usr/share/pixmaps/tweets2pdf.png'):
        return '/usr/share/pixmaps/tweets2pdf.png'
    if os.path.exists('/usr/local/share/pixmaps/tweets2pdf.png'):
        return '/usr/local/share/pixmaps/tweets2pdf.png'
    return None

class tp_cfg:

    def __init__(self):
        self.font_path = ''
        self.link_color = ''
        self.output_path = ''
        self.proxy_enable = False
        self.proxy_host = ''
        self.proxy_port = ''
        self.api_base = ''
        self.oauth_base = ''

    def set_font_path(self, font_path = {}):
        self.font_path = font_path

    def set_link_color(self, link_color = {}):
        self.link_color = link_color

    def set_output_path(self, output_path = {}):
        self.output_path = output_path

    def set_proxy_enable(self, proxy_enable = {}):
        self.proxy_enable = proxy_enable

    def set_proxy_host(self, proxy_host = {}):
        self.proxy_host = proxy_host

    def set_proxy_port(self, proxy_port = {}):
        self.proxy_port = proxy_port

    def set_api_base(self, api_base = {}):
        self.api_base = api_base

    def set_oauth_base(self, oauth_base = {}):
        self.oauth_base = oauth_base

    def load(self):
        app_dir = get_app_dir()
        if app_dir is None:
            return False
        cfg_path = app_dir + '/cfg.xml'
        try:
            doc = minidom.parse(cfg_path)
            root = doc.documentElement
            self.font_path = root.getElementsByTagName('font_path')[0].childNodes[0].data
            self.link_color = root.getElementsByTagName('link_color')[0].childNodes[0].data
            self.output_path = root.getElementsByTagName('output_path')[0].childNodes[0].data
            proxy = root.getElementsByTagName('proxy')[0]
            self.proxy_enable = True if proxy.getAttribute('enable') == 'True' else False
            host = proxy.getElementsByTagName('host')[0].childNodes
            if len(host) > 0:
                self.proxy_host = host[0].data
            else:
                self.proxy_host = ''
            port = proxy.getElementsByTagName('port')[0].childNodes
            if len(port) > 0:
                self.proxy_port = port[0].data
            else:
                self.proxy_port = ''
            self.api_base = root.getElementsByTagName('api_base')[0].childNodes[0].data
            self.oauth_base = root.getElementsByTagName('oauth_base')[0].childNodes[0].data
            return True
        except:
            return False

    def save(self):
        impl = minidom.getDOMImplementation()
        doc = impl.createDocument(None, 'cfg', None)
        root = doc.documentElement
        item = doc.createElement('font_path')
        text = doc.createTextNode(self.font_path)
        item.appendChild(text)
        root.appendChild(item)
        item = doc.createElement('output_path')
        text = doc.createTextNode(self.output_path)
        item.appendChild(text)
        root.appendChild(item)
        item = doc.createElement('link_color')
        text = doc.createTextNode(self.link_color)
        item.appendChild(text)
        root.appendChild(item)
        item = doc.createElement('proxy')
        item.setAttribute('enable', 'True' if self.proxy_enable else 'False')
        root.appendChild(item)
        subchild = doc.createElement('host')
        text = doc.createTextNode(self.proxy_host)
        subchild.appendChild(text)
        item.appendChild(subchild)
        subchild = doc.createElement('port')
        text = doc.createTextNode(self.proxy_port)
        subchild.appendChild(text)
        item.appendChild(subchild)
        item = doc.createElement('api_base')
        text = doc.createTextNode(self.api_base)
        item.appendChild(text)
        root.appendChild(item)
        item = doc.createElement('oauth_base')
        text = doc.createTextNode(self.oauth_base)
        item.appendChild(text)
        root.appendChild(item)
        app_dir = get_app_dir()
        if app_dir is None:
            return False
        cfg_file = open(app_dir + '/cfg.xml', 'w')
        cfg_file.write(root.toxml())
        cfg_file.close()
        return True

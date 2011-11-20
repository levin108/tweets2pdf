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

import pygtk
pygtk.require('2.0')
import gtk
import config
import oauthapi
import pdfgen
import gobject
from pdfgen import *

API_BASE = "http://api.twitter.com/1/"
OAUTH_BASE = "https://api.twitter.com/oauth/"

def generate_thread(param):
    tpdoc = param[0]
    if not tpdoc.generate_cover():
        return
    if not tpdoc.generate_body():
        param[1].show_done('Twitter limited, please retry later.')
        return
    tpdoc.dump()
    gtk.gdk.threads_enter()
    param[1].start_button.set_sensitive(True)
    gtk.gdk.threads_leave()
        

class mainwindow:

    def delete_event(self, widget, event, data = None):
        try:
            if self.thread.isAlive():
                dialog = gtk.MessageDialog(self.window, \
                        gtk.DIALOG_DESTROY_WITH_PARENT, \
                        gtk.MESSAGE_QUESTION, \
                        gtk.BUTTONS_OK_CANCEL, \
                        'Generating in progress.\nAre you sure to quit ?')
                ret = dialog.run()
                dialog.destroy()
                if ret == gtk.RESPONSE_OK:
                    gtk.main_quit()
                    return False
                else:
                    return True
            else:
                gtk.main_quit()
                return False
        except:
            gtk.main_quit()
        return False

    def update_progress(self, text = {}, fraction = {}):
        gtk.gdk.threads_enter()
        self.progress_bar.set_fraction(fraction)
        self.progress_bar.set_text(text)
        gtk.gdk.threads_leave()

    def show_fail(self, text = {}):
        gtk.gdk.threads_enter()
        self.progress_bar.set_fraction(fraction)
        self.progress_bar.set_text(text)
        gtk.gdk.threads_leave()

    def show_done(self, text = {}):
        gtk.gdk.threads_enter()
        self.progress_bar.set_fraction(1)
        self.progress_bar.set_text(text)
        self.status_bar.push(int(status_done), status_dic[status_done])
        self.start_button.set_sensitive(True)
        gtk.gdk.threads_leave()
    
    def update_status(self, status = {}):
        gtk.gdk.threads_enter()
        self.status_bar.push(int(status), status_dic[status])
        gtk.gdk.threads_leave()

    def show_warning(self, message):
        dialog = gtk.MessageDialog(self.window, \
                gtk.DIALOG_DESTROY_WITH_PARENT, \
                gtk.MESSAGE_WARNING, \
                gtk.BUTTONS_OK, \
                message)
        dialog.run()
        dialog.destroy()

    def get_id_from_entry(self, entry):
        try:
            if len(entry.get_text()) == 0:
                return 0
            return long(entry.get_text())
        except:
            return 0


    def start_button_clicked(self, widget, data= None):
        cfg = config.tp_cfg()
        if not cfg.load():
            self.show_warning('''
This is the first time you run tweets2pdf.
\nGo to Preference and do some settings.
''')
            return

        client = oauthapi.tpOAuth(http_proxy = {
            'host': cfg.proxy_host,
            'port': cfg.proxy_port
            } if cfg.proxy_enable else None)

        if not client.restore_access_token():
            token = client.fetch_request_token()
            if token is None:
                return
            client.authorization_token(token)
            verifier = raw_input("please input PIN code:")
            token = client.fetch_access_token(token, verifier)
            client.save_access_token()
        
        if self.tweets_type == TWEETS_OTHERS_TIMELINE or \
            self.tweets_type == TWEETS_OTHERS_FAVORITES:
            screen_name = self.sn_entry.get_text()
            if len(screen_name) == 0:
                self.show_warning('Please input screen name of the account')
                return
        else:
            screen_name = client.access_token.screen_name
        
        tweets_max_id = self.get_id_from_entry(self.matd_entry)
        tweets_min_id = self.get_id_from_entry(self.mitd_entry)
        if self.tweets_type == TWEETS_MY_TIMELINE or self.tweets_type == TWEETS_OTHERS_TIMELINE:
            default_name = 'tweets_%s.pdf' % screen_name
        elif self.tweets_type == TWEETS_RETWEETED_BY_ME:
            default_name = 'tweets_%s_rt.pdf' % screen_name
        elif self.tweets_type == TWEETS_MY_RETWEETED:
            default_name = 'tweets_%s_rted.pdf' % screen_name
        elif self.tweets_type == TWEETS_MY_FAVORITES or \
                self.tweets_type == TWEETS_OTHERS_FAVORITES:
            default_name = 'tweets_%s_fav.pdf' % screen_name

        path = cfg.output_path
        if len(path) > 0:
            if path[len(path) - 1] != '/':
                path += '/'

        pdf_name = path + default_name

        if self.wc_btn.get_active():
            has_cover = False
        else:
            has_cover = True

        tpdoc = tp_document(oauth_client = client, \
                screen_name = screen_name, \
                tweets_type = self.tweets_type, \
                pdf_name = pdf_name, \
                has_cover = has_cover, \
                tweets_min_id = tweets_min_id, \
                tweets_max_id = tweets_max_id, \
                font_path = cfg.font_path, \
                link_color = cfg.link_color, \
                main_panel = self)
        tpdoc.set_tweets_count(self.get_id_from_entry(self.tc_entry))

        self.start_button.set_sensitive(False)

        self.thread = threading.Thread(target = generate_thread, args = [[tpdoc, self]])
        self.thread.setDaemon(1)
        self.thread.start()

    def oauth_request_thread(self, param = None):
        cfg = config.tp_cfg()
        cfg.load()

        self.client = oauthapi.tpOAuth(http_proxy = {
            'host': cfg.proxy_host,
            'port': cfg.proxy_port
            } if cfg.proxy_enable else None)
        self.request_token = self.client.fetch_request_token()
        if self.request_token is None:
            gtk.gdk.threads_enter()
            self.progress_bar.set_text('Fetch Request Token Failed!')
            self.oauth_area_destroy()
            self.start_button.show()
            gtk.gdk.threads_leave()
            return False
        gtk.gdk.threads_enter()
        self.progress_bar.set_text('Fetch Request Token Success!')
        gtk.gdk.threads_leave()
        self.client.authorization_token(self.request_token)
        return True

    def oauth_area_show(self):
        fixed = self.button_in_fixed
        self.oauth_label = gtk.Label()
        self.oauth_label.set_markup('<b>Making OAuth, input PIN code: </b>')
        self.progress_bar.set_text('Fetching Request Token, Please wait...')
        self.oauth_label.show()
        fixed.put(self.oauth_label, 15, 170)
        self.oauth_entry = gtk.Entry()
        self.oauth_entry.set_size_request(100, 25)
        self.oauth_entry.show()
        fixed.put(self.oauth_entry, 250, 165)
        self.oauth_button = gtk.Button('OK')
        self.oauth_button.connect('clicked', self.oauth_access_clicked)
        self.oauth_button.set_size_request(90, 25)
        self.oauth_button.show()
        fixed.put(self.oauth_button, 360, 165)

    def oauth_area_destroy(self):
        self.oauth_label.destroy()
        self.oauth_entry.destroy()
        self.oauth_button.destroy()

    def oauth_access_thread(self, param = None):
        verifier = self.oauth_entry.get_text()
        try:
            token = self.client.fetch_access_token(self.request_token, verifier)
            self.client.save_access_token()
            gtk.gdk.threads_enter()
            self.oauth_area_destroy()
            self.progress_bar.set_text('Congratulations, OAuth Success!')
            self.start_button.set_label('Start Generate')
            self.start_button.disconnect(self.start_btn_handler_id)
            self.start_btn_handler_id = self.start_button.connect('clicked', self.start_button_clicked)
            self.start_button.show()
            gtk.gdk.threads_leave()
        except:
            gtk.gdk.threads_enter()
            self.progress_bar.set_text('Fetch Access Token Failed!')
            self.oauth_area_destroy()
            self.start_button.show()
            gtk.gdk.threads_leave()

    def oauth_access_clicked(self, button, data = None):
        button.set_sensitive(False)
        button.set_label('OAuthing...')
        if len(self.oauth_entry.get_text()) == 0:
            self.show_warning('Please input PIN code!')
            return
        self.progress_bar.set_text('Fetching Access Token, Please wait...')
        thread = threading.Thread(target = self.oauth_access_thread)
        thread.setDaemon(1)
        thread.start()

    def oauth_button_clicked(self, button, data = None):
        #button.set_sensitive(False)
        button.hide()
        self.oauth_area_show()
        thread = threading.Thread(target = self.oauth_request_thread)
        thread.setDaemon(1)
        thread.start()


    def radio_button_toggled(self, button, data):
        if button.get_active():
            self.tweets_type = data

        if self.tweets_type == TWEETS_OTHERS_TIMELINE or \
            self.tweets_type == TWEETS_OTHERS_FAVORITES:
            self.sn_entry.set_sensitive(True)
        else:
            self.sn_entry.set_sensitive(False)

        if self.tweets_type == TWEETS_MY_FAVORITES or \
            self.tweets_type == TWEETS_OTHERS_FAVORITES:
            self.matd_entry.set_sensitive(False)
            self.mitd_entry.set_sensitive(False)
        else:
            self.matd_entry.set_sensitive(True)
            self.mitd_entry.set_sensitive(True)

    def proxy_button_toggle(self, button, data = None):
        if button.get_active():
            self.ph_label.set_sensitive(True)
            self.ph_entry.set_sensitive(True)
            self.pp_label.set_sensitive(True)
            self.pp_entry.set_sensitive(True)
        else:
            self.ph_label.set_sensitive(False)
            self.ph_entry.set_sensitive(False)
            self.pp_label.set_sensitive(False)
            self.pp_entry.set_sensitive(False)

    def cover_button_toggle(self, button, data = None):
        if button.get_active():
            self.show_warning('''
We will generate a pdf without a cover as the first page,\n\
so you can\'t store the tweets id information in the pdf\n\
which will help you to backup your tweets, but it will run faster!''')

    def create_param_panel(self):
        # generate parameters area
        frame = gtk.Frame('Parameters')
        self.gen_panel.pack_start(frame, False, False, 5)
        fixed = gtk.Fixed()
        fixed.set_size_request(460, 200)
        frame.add(fixed)
        self.tweets_type = TWEETS_MY_TIMELINE
        # add radio button in the left
        radio_button = gtk.RadioButton(None, label = 'my timeline')
        radio_button.connect('toggled', self.radio_button_toggled, TWEETS_MY_TIMELINE)
        fixed.put(radio_button, 10, 10)
        radio_button = gtk.RadioButton(radio_button, 'my tweets,retweeted')
        radio_button.connect('toggled', self.radio_button_toggled, TWEETS_MY_RETWEETED)
        fixed.put(radio_button, 10, 35)
        radio_button = gtk.RadioButton(radio_button, 'tweets retweeted by me')
        radio_button.connect('toggled', self.radio_button_toggled, TWEETS_RETWEETED_BY_ME)
        fixed.put(radio_button, 10, 60)
        radio_button = gtk.RadioButton(radio_button, 'my favorites')
        radio_button.connect('toggled', self.radio_button_toggled, TWEETS_MY_FAVORITES)
        fixed.put(radio_button, 10, 85)
        radio_button = gtk.RadioButton(radio_button, 'other\'s timeline')
        radio_button.connect('toggled', self.radio_button_toggled, TWEETS_OTHERS_TIMELINE)
        fixed.put(radio_button, 10, 110)
        radio_button = gtk.RadioButton(radio_button, 'other\'s favorites')
        radio_button.connect('toggled', self.radio_button_toggled, TWEETS_OTHERS_FAVORITES)
        fixed.put(radio_button, 10, 135)
        # add tweets options in the right
        label = gtk.Label('screen name: @')
        fixed.put(label, 220, 10)
        self.sn_entry = gtk.Entry()
        self.sn_entry.set_size_request(130, 20)
        self.sn_entry.set_sensitive(False)
        fixed.put(self.sn_entry, 328, 8)

        label = gtk.Label('Max tweets ID:')
        fixed.put(label, 220, 33)
        self.matd_entry = gtk.Entry()
        self.matd_entry.set_size_request(130, 20)
        fixed.put(self.matd_entry, 328, 33)

        label = gtk.Label('Min  tweets ID:')
        fixed.put(label, 220, 58)
        self.mitd_entry = gtk.Entry()
        self.mitd_entry.set_size_request(130, 20)
        fixed.put(self.mitd_entry, 328, 58)

        label = gtk.Label('Tweets   count:')
        fixed.put(label, 220, 83)
        self.tc_entry = gtk.Entry()
        self.tc_entry.set_size_request(130, 20)
        fixed.put(self.tc_entry, 328, 83)

        self.wc_btn = gtk.CheckButton('Without cover')
        self.wc_btn.connect('toggled', self.cover_button_toggle)
        fixed.put(self.wc_btn, 250, 118)

        #add generate button in the middle
        self.client = oauthapi.tpOAuth()

        if not self.client.restore_access_token():
            self.start_button = gtk.Button('OAuth')
            self.start_button.set_sensitive(True)
            self.start_button.set_size_request(440, 30)
            self.start_btn_handler_id = self.start_button.connect('clicked', self.oauth_button_clicked)
        else:
            self.start_button = gtk.Button('Start Generate')
            self.start_button.set_size_request(440, 30)
            self.start_btn_handler_id = self.start_button.connect('clicked', self.start_button_clicked)
        fixed.put(self.start_button, 15, 160)
        self.button_in_fixed = fixed

        #genearate progress area
        frame = gtk.Frame('Progress')
        self.gen_panel.pack_start(frame, True, True, 5)
        vbox = gtk.VBox(False, 5)
        frame.add(vbox)
        self.progress_bar = gtk.ProgressBar()
        self.progress_bar.set_size_request(300, 50)
        self.progress_bar.set_text('Now Idle')
        vbox.pack_start(self.progress_bar, False, False, 10)

    def font_select_func(self, widget, data = None):
        filechooser = gtk.FileChooserDialog('Where\'s the font file ?', \
                parent = self.window, \
                action = gtk.FILE_CHOOSER_ACTION_OPEN, \
                buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, \
                            gtk.STOCK_SAVE, gtk.RESPONSE_OK))

        ret = filechooser.run()
        if ret == gtk.RESPONSE_CANCEL:
            filechooser.destroy()
            return
        name = filechooser.get_filename()
        self.fn_entry.set_text(name)
        filechooser.destroy()

    def path_select_func(self, widget, data = None):
        filechooser = gtk.FileChooserDialog('Where to save the pdf ?', \
                parent = self.window, \
                action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, \
                buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, \
                            gtk.STOCK_SAVE, gtk.RESPONSE_OK))

        ret = filechooser.run()
        if ret == gtk.RESPONSE_CANCEL:
            filechooser.destroy()
            return
        name = filechooser.get_filename()
        self.op_entry.set_text(name)
        filechooser.destroy()

    def color_select_func(self, widget, data = None):
        colorchooser = gtk.ColorSelectionDialog('What\'s the color of the link ?')
        ret = colorchooser.run()
        if ret == gtk.RESPONSE_OK:
            colorselection = colorchooser.get_color_selection()
            color = colorselection.get_current_color()
            red = ('%s' % hex(color.red / 256))[2:].upper()
            blue = ('%s' % hex(color.blue / 256))[2:].upper()
            green = ('%s' % hex(color.green / 256))[2:].upper()
            color_string = '#%s%s%s' % (red, green, blue)
            self.lc_entry.set_text(color_string)
        colorchooser.destroy()

    def save_btn_clicked(self, widget, data = None):
        cfg = config.tp_cfg()
        self.proxy_host = self.ph_entry.get_text()
        self.proxy_port = self.pp_entry.get_text()
        if self.hp_enable.get_active():
            self.proxy_enable = True
            if len(self.proxy_port) == 0 or len(self.proxy_host) == 0:
                self.show_warning('Please input proxy information')
                return
        else:
            self.proxy_enable = False

        self.font_path = self.fn_entry.get_text()
        if len(self.font_path) == 0:
            self.show_warning('Please input absolute path of the font file')
            return
        self.output_path = self.op_entry.get_text()
        self.link_color = self.lc_entry.get_text()
        self.api_base = self.ab_entry.get_text()
        self.oauth_base = self.ob_entry.get_text()
        if len(self.api_base) == 0:
            self.show_warning('Please input api base string')
            return
        if len(self.oauth_base) == 0:
            self.show_warning('Please input oauth base string')
            return
        cfg.set_proxy_enable(self.proxy_enable)
        cfg.set_proxy_host(self.proxy_host)
        cfg.set_proxy_port(self.proxy_port)
        cfg.set_output_path(self.output_path)
        cfg.set_font_path(self.font_path)
        cfg.set_link_color(self.link_color)
        cfg.set_api_base(self.api_base)
        cfg.set_oauth_base(self.oauth_base)
        cfg.save()
        self.show_warning('Save configuration successfully')

    def reset_btn_clicked(self, widget, data = None):
        cfg = config.tp_cfg()        
        cfg.set_api_base(API_BASE)
        cfg.set_oauth_base(OAUTH_BASE)
        cfg.set_output_path(config.get_home_dir())
        cfg.set_link_color('blue')
        cfg.set_proxy_enable(False)
        cfg.set_proxy_host('')
        cfg.set_proxy_port('')
        cfg.save()
        self.hp_enable.set_active(cfg.proxy_enable)
        self.ab_entry.set_text(cfg.api_base)
        self.ob_entry.set_text(cfg.oauth_base)
        self.fn_entry.set_text(cfg.font_path)
        self.op_entry.set_text(cfg.output_path)
        self.lc_entry.set_text(cfg.link_color)
        self.ph_entry.set_text(cfg.proxy_host)
        self.pp_entry.set_text(cfg.proxy_port)

    def create_pref_panel(self):
        frame = gtk.Frame('HTTP Proxy')
        frame.set_border_width(5)
        self.cfg_panel.pack_start(frame, False, False, 0)
        fixed = gtk.Fixed()
        fixed.set_size_request(400, 60)
        frame.add(fixed)
        self.hp_enable = gtk.CheckButton('Enable HTTP Proxy')
        self.hp_enable.connect('toggled', self.proxy_button_toggle)
        fixed.put(self.hp_enable, 34, 5)
        self.ph_label = gtk.Label('Host:')
        self.ph_label.set_sensitive(False)
        fixed.put(self.ph_label, 34, 32)
        self.ph_entry = gtk.Entry()
        self.ph_entry.set_sensitive(False)
        self.ph_entry.set_size_request(150, 20)
        fixed.put(self.ph_entry, 80, 30)
        self.pp_label = gtk.Label('Port:')
        self.pp_label.set_sensitive(False)
        fixed.put(self.pp_label, 250, 32)
        self.pp_entry = gtk.Entry()
        self.pp_entry.set_sensitive(False)
        self.pp_entry.set_size_request(85, 20)
        fixed.put(self.pp_entry, 290, 30)

        frame = gtk.Frame('Appearance')
        frame.set_border_width(5)
        self.cfg_panel.pack_start(frame, False, False, 0)
        fixed = gtk.Fixed()
        fixed.set_size_request(400, 100)
        frame.add(fixed)

        label = gtk.Label('Font File:')
        fixed.put(label, 10, 12)
        self.fn_entry = gtk.Entry()
        self.fn_entry.set_size_request(280, 20)
        fixed.put(self.fn_entry, 100, 8)
        font_choose_button = gtk.Button('...')
        font_choose_button.connect('clicked', self.font_select_func)
        font_choose_button.set_size_request(30, 20)
        fixed.put(font_choose_button, 390, 8)

        label = gtk.Label('Output Path:')
        fixed.put(label, 10, 37)
        self.op_entry = gtk.Entry()
        self.op_entry.set_size_request(280, 20)
        fixed.put(self.op_entry, 100, 33)
        path_choose_button = gtk.Button('...')
        path_choose_button.connect('clicked', self.path_select_func)
        path_choose_button.set_size_request(30, 20)
        fixed.put(path_choose_button, 390, 33)

        label = gtk.Label('Link Color:')
        fixed.put(label, 10, 62)
        self.lc_entry = gtk.Entry()
        self.lc_entry.set_size_request(280, 20)
        fixed.put(self.lc_entry, 100, 58)
        color_choose_button = gtk.Button('...')
        color_choose_button.connect('clicked', self.color_select_func)
        color_choose_button.set_size_request(30, 20)
        fixed.put(color_choose_button, 390, 58)

        frame = gtk.Frame('API Setting(Currently unavailable)')
        frame.set_border_width(5)
        self.cfg_panel.pack_start(frame, False, False, 0)
        fixed = gtk.Fixed()
        fixed.set_size_request(400, 75)
        frame.add(fixed)
        label = gtk.Label('API Base:')
        fixed.put(label, 10, 10)
        self.ab_entry = gtk.Entry()
        self.ab_entry.set_sensitive(False)
        self.ab_entry.set_size_request(200, 20)
        fixed.put(self.ab_entry, 100, 8)

        label = gtk.Label('OAuth Base:')
        fixed.put(label, 10, 40)
        self.ob_entry = gtk.Entry()
        self.ob_entry.set_sensitive(False)
        self.ob_entry.set_size_request(200, 20)
        fixed.put(self.ob_entry, 100, 38)

        hbox = gtk.HBox(False, 5)
        align = gtk.Alignment(1, 0, 0, 0)
        align.add(hbox)
        self.reset_btn = gtk.Button('Reset')
        self.reset_btn.connect('clicked', self.reset_btn_clicked)
        self.reset_btn.set_size_request(100, 25)
        hbox.pack_start(self.reset_btn, False, False, 5)

        self.cfg_panel.pack_end(align, False, False, 5)
        self.save_btn = gtk.Button('Save')
        self.save_btn.connect('clicked', self.save_btn_clicked)
        self.save_btn.set_size_request(100, 25)
        hbox.pack_start(self.save_btn, False, False, 5)

    def create_about_panel(self):
        fixed = gtk.Fixed()
        self.about_panel.pack_start(fixed, False, False, 5)
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(config.get_app_icon(), 128, 128)
        image = gtk.image_new_from_pixbuf(pixbuf)
        fixed.put(image, 176, 40)
        about_label = gtk.Label()
        about_label.set_size_request(width = 450, height = 140)
        about_label.set_markup(template.ABOUT_TEMPLATE)
        about_label.set_line_wrap(True)
        fixed.put(about_label, 20, 180)

    def fill_pref(self):
        cfg = config.tp_cfg()
        if not cfg.load():
            self.ab_entry.set_text(API_BASE)
            self.ob_entry.set_text(OAUTH_BASE)
            self.op_entry.set_text(config.get_home_dir())
            self.lc_entry.set_text('blue')
        else:
            self.ab_entry.set_text(cfg.api_base)
            self.ob_entry.set_text(cfg.oauth_base)
            self.op_entry.set_text(cfg.output_path)
            self.fn_entry.set_text(cfg.font_path)
            self.lc_entry.set_text(cfg.link_color)
            self.hp_enable.set_active(cfg.proxy_enable)
            self.ph_entry.set_text(cfg.proxy_host)
            self.pp_entry.set_text(cfg.proxy_port)

    def __init__(self):
        gtk.gdk.threads_init()

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('tweets2pdf')
        self.window.set_size_request(480, 380)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.connect('delete_event', self.delete_event)
        self.window.set_resizable(False)
        self.window.set_icon_from_file(config.get_app_icon())

        self.notebook = gtk.Notebook()

        self.gen_panel = gtk.VBox()
        self.create_param_panel()
        notebook_label = gtk.Label('Generate')
        self.notebook.append_page(self.gen_panel, notebook_label)

        self.cfg_panel = gtk.VBox(False)
        self.create_pref_panel()
        self.fill_pref()
        notebook_label = gtk.Label('Preference')
        self.notebook.append_page(self.cfg_panel, notebook_label)
        
        self.about_panel = gtk.VBox(False)
        self.create_about_panel()
        notebook_label = gtk.Label('About')
        self.notebook.append_page(self.about_panel, notebook_label)

        #create status bar
        self.status_bar = gtk.Statusbar()
        self.gen_panel.pack_start(self.status_bar, False, False, 0)
        self.status_bar.push(1, ' welcome to use tweets2pdf')

        self.window.add(self.notebook)
        self.window.show_all()
        gtk.gdk.threads_enter()
        gtk.main()
        gtk.gdk.threads_leave()

def main():
    window = mainwindow()

if __name__ == "__main__":
    main()

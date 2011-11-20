#/usr/bin/python
# -*- coding=utf8 -*-

TWEETS_TEMPLATE = '''<a color="%s" href="http://twitter.com/%s">@%s</a>
                   <font size="8">(<font color="grey">%s</font>)
                   at <font color="grey">%s</font>
                   through <font color="grey">%s</font></font><br/>%s'''

MENTION_TEMPLATE = '@<a href="http://twitter.com/%s" color="%s">%s</a>'

URL_TEMPLATE = '<a href="%s" color="%s">%s</a>'

PROFILE_TEMPLATE = '''<font size="16">%s</font><br/><font size="12">@%s</font> 
                    <font size="10">%s</font><br/>%s<br/> 
                    <a href="%s" color="%s"><i>%s</i></a>'''

PROFILE_TEMPLATE_NO_URL = '''<font size="16">%s</font><br/><font size="12">@%s</font> 
                    <font size="10">%s</font><br/>%s<br/>'''
ABOUT_TEMPLATE = '        <b>Tweets2pdf</b> is small tool to backup your tweets ' + \
                'into elegent PDF files, developed by ' + \
                '<a href="http://twitter.com/levin108">@levin108</a>. ' + \
                'If you like it, please join me to make it better.\n\n' + \
                'Project Host: <a href="http://code.google.com/p/tweets2pdf/">http://code.google.com/p/tweets2pdf/</a>\n\n' + \
                'Project Site:  <a href="http://basiccoder.com/tweets2pdf">http://basiccoder.com/tweets2pdf</a>'

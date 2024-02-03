# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------
# Plugin Tools v2.0.0
#---------------------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Based on code from youtube, parsedom and pelisalacarta addons
# Author: 
# Jesús and modified by Titan
# tvalacarta@gmail.com
# http://www.mimediacenter.info/plugintools
#---------------------------------------------------------------------------
# Changelog:
# 1.0.0
# - First release
# 1.0.1
# - If find_single_match can't find anything, it returns an empty string
# - Remove addon id from this module, so it remains clean
# 1.0.2
# - Added parameter on "add_item" to say that item is playable
# 1.0.3
# - Added direct play
# - Fixed bug when video isPlayable=True
# 1.0.4
# - Added get_temp_path, get_runtime_path, get_data_path
# - Added get_setting, set_setting, open_settings_dialog and get_localized_string
# - Added keyboard_input
# - Added message
# 1.0.5
# - Added read_body_and_headers for advanced http handling
# - Added show_picture for picture addons support
# - Added optional parameters "title" and "hidden" to keyboard_input
# 1.0.6
# - Added fanart, show, episode and infolabels to add_item
# 1.0.7
# - Added set_view function
# 1.0.8
# - Added selector
# 2.0.0
# Welcome matrix
#---------------------------------------------------------------------------

import xbmcimport xbmcvfs
import xbmcplugin
import xbmcaddon
import xbmcgui

import urllib.request, urllib.parse, urllib.error 
import re
import sys
import os
import time
import socket
from io import StringIO
import gzip  

module_log_enabled = False
http_debug_log_enabled = False

LIST = "list"
THUMBNAIL = "thumbnail"
MOVIES = "movies"
TV_SHOWS = "tvshows"
SEASONS = "seasons"
EPISODES = "episodes"
OTHER = "other"

# Suggested view codes for each type from different skins (initial list thanks to xbmcswift2 library)
ALL_VIEW_CODES = {
    'list': {
        'skin.confluence': 50, # List
        'skin.aeon.nox': 50, # List
        'skin.droid': 50, # List
        'skin.quartz': 50, # List
        'skin.re-touched': 50, # List
    },
    'thumbnail': {
        'skin.confluence': 500, # Thumbnail
        'skin.aeon.nox': 500, # Wall
        'skin.droid': 51, # Big icons
        'skin.quartz': 51, # Big icons
        'skin.re-touched': 500, #Thumbnail
    },
    'movies': {
        'skin.confluence': 515, # Thumbnail 515, # Media Info 3
        'skin.aeon.nox': 500, # Wall
        'skin.droid': 51, # Big icons
        'skin.quartz': 52, # Media info
        'skin.re-touched': 500, #Thumbnail
    },
    'tvshows': {
        'skin.confluence': 515, # Thumbnail 515, # Media Info 3
        'skin.aeon.nox': 500, # Wall
        'skin.droid': 51, # Big icons
        'skin.quartz': 52, # Media info
        'skin.re-touched': 500, #Thumbnail
    },
    'seasons': {
        'skin.confluence': 50, # List
        'skin.aeon.nox': 50, # List
        'skin.droid': 50, # List
        'skin.quartz': 52, # Media info
        'skin.re-touched': 50, # List
    },
    'episodes': {
        'skin.confluence': 503, # Media Info
        'skin.aeon.nox': 518, # Infopanel
        'skin.droid': 50, # List
        'skin.quartz': 52, # Media info
        'skin.re-touched': 550, # Wide
    },
}

# Write something on XBMC log
def log(message):
    xbmc.log(message)

# Write this module messages on XBMC log
def _log(message):
    if module_log_enabled:
        xbmc.log("plugintools."+message)

# Parse XBMC params - based on script.module.parsedom addon    
def get_params():
    _log("get_params")
    
    param_string = sys.argv[2]
    
    _log("get_params "+str(param_string))
    
    commands = {}

    if param_string:
        split_commands = param_string[param_string.find('?') + 1:].split('&')
    
        for command in split_commands:
            _log("get_params command="+str(command))
            if len(command) > 0:
                if "=" in command:
                    split_command = command.split('=')
                    key = split_command[0]
                    value = urllib.parse.unquote_plus(split_command[1])
                    commands[key] = value
                else:
                    commands[command] = ""
    
    _log("get_params "+repr(commands))
    return commands

# Fetch text content from an URL
def read(url):
    _log("read "+url)

    f = urllib.request.urlopen(url)
    data = f.read()
    f.close()
    
    return data

def read_body_and_headers(url, post=None, headers=[], follow_redirects=False, timeout=None):
    _log("read_body_and_headers "+url)

    if post is not None:
        _log("read_body_and_headers post="+post)

    if len(headers)==0:
        headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:18.0) Gecko/20100101 Firefox/18.0"])

    # Start cookie lib
    ficherocookies = os.path.join( get_data_path(), 'cookies.dat' )
    _log("read_body_and_headers cookies_file="+ficherocookies)

    cj = None
    ClientCookie = None
    cookielib = None

    # Let's see if cookielib is available
    try:
        _log("read_body_and_headers importing cookielib")
        import http.cookiejar
    except ImportError:
        _log("read_body_and_headers cookielib no disponible")
        # If importing cookielib fails
        # let's try ClientCookie
        try:
            _log("read_body_and_headers importing ClientCookie")
            import ClientCookie
        except ImportError:
            _log("read_body_and_headers ClientCookie not available")
            # ClientCookie isn't available either
            urlopen = urllib.request.urlopen
            Request = urllib.request.Request
        else:
            _log("read_body_and_headers ClientCookie available")
            # imported ClientCookie
            urlopen = ClientCookie.urlopen
            Request = ClientCookie.Request
            cj = ClientCookie.MozillaCookieJar()

    else:
        _log("read_body_and_headers cookielib available")
        # importing cookielib worked
        urlopen = urllib.request.urlopen
        Request = urllib.request.Request
        cj = http.cookiejar.MozillaCookieJar()
        # This is a subclass of FileCookieJar
        # that has useful load and save methods

    if cj is not None:
    # we successfully imported
    # one of the two cookie handling modules
        _log("read_body_and_headers Cookies enabled")

        if os.path.isfile(ficherocookies):
            _log("read_body_and_headers Reading cookie file")
            # if we have a cookie file already saved
            # then load the cookies into the Cookie Jar
            try:
                cj.load(ficherocookies)
            except:
                _log("read_body_and_headers Wrong cookie file, deleting...")
                os.remove(ficherocookies)

        # Now we need to get our Cookie Jar
        # installed in the opener;
        # for fetching URLs
        if cookielib is not None:
            _log("read_body_and_headers opener using urllib2 (cookielib)")
            # if we use cookielib
            # then we get the HTTPCookieProcessor
            # and install the opener in urllib2
            if not follow_redirects:
                opener = urllib.request.build_opener(urllib.request.HTTPHandler(debuglevel=http_debug_log_enabled),urllib.request.HTTPCookieProcessor(cj),NoRedirectHandler())
            else:
                opener = urllib.request.build_opener(urllib.request.HTTPHandler(debuglevel=http_debug_log_enabled),urllib.request.HTTPCookieProcessor(cj))
            urllib.request.install_opener(opener)

        else:
            _log("read_body_and_headers opener using ClientCookie")
            # if we use ClientCookie
            # then we get the HTTPCookieProcessor
            # and install the opener in ClientCookie
            try:
                opener = ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(cj))
                ClientCookie.install_opener(opener)
            except AttributeError:
                pass    

    # -------------------------------------------------
    # Cookies instaladas, lanza la petición
    # -------------------------------------------------

    # Contador 

    # Diccionario para las cabeceras
    txheaders = {}

    # Construye el request
    if post is None:
        _log("read_body_and_headers GET request")
    else:
        _log("read_body_and_headers POST request")
    
    # Añade las cabeceras
    _log("read_body_and_headers ---------------------------")
    for header in headers:
        _log("read_body_and_headers header %s=%s" % (str(header[0]),str(header[1])) )
        txheaders[header[0]]=header[1]
    _log("read_body_and_headers ---------------------------")

    req = Request(url, post, txheaders)
    if timeout is None:
        handle=urlopen(req)
    else:        
        #Disponible en python 2.6 en adelante --> handle = urlopen(req, timeout=timeout)
        #Para todas las versiones:
        try:
            import socket
            deftimeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(timeout)
            handle=urlopen(req)            
            socket.setdefaulttimeout(deftimeout)
        except:
            import sys
            for line in sys.exc_info():
                _log( "%s" % line )
    
    # Actualiza el almacén de cookies
    cj.save(ficherocookies)

    # Lee los datos y cierra
    if handle.info().get('Content-Encoding') == 'gzip':
        buf = StringIO( handle.read())
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
    else:
        data=handle.read()

    info = handle.info()
    _log("read_body_and_headers Response")

    returnheaders=[]
    _log("read_body_and_headers ---------------------------")
    for header in info:
        _log("read_body_and_headers "+header+"="+info[header])
        returnheaders.append([header,info[header]])
    handle.close()
    _log("read_body_and_headers ---------------------------")

    '''
    # Lanza la petición
    try:
        response = urllib2.urlopen(req)
    # Si falla la repite sustituyendo caracteres especiales
    except:
        req = urllib2.Request(url.replace(" ","%20"))
    
        # Añade las cabeceras
        for header in headers:
            req.add_header(header[0],header[1])

        response = urllib2.urlopen(req)
    '''
     
    return data,returnheaders

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        infourl = urllib.addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl
    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302

# Parse string and extracts multiple matches using regular expressions

def find_single_match(text, pattern, index=0, flags=re.DOTALL):
    try:
        matches = re.findall(pattern, text, flags)
        return matches[index]
    except Exception:
        return ''


def find_multiple_matches(text, pattern, flags=re.DOTALL):
    return re.findall(pattern, text, flags)

def add_item( action="" , title="" , plot="" , url="" , thumbnail="" , fanart="" , show="" , episode="" , extra="", page="", info_labels = None, isPlayable = False , folder=True ):
    _log("add_item action=["+action+"] title=["+title+"] url=["+url+"] thumbnail=["+thumbnail+"] fanart=["+fanart+"] show=["+show+"] episode=["+episode+"] extra=["+extra+"] page=["+page+"] isPlayable=["+str(isPlayable)+"] folder=["+str(folder)+"]")

    listitem = xbmcgui.ListItem( title ) 
    listitem.setArt({ 'poster': 'poster.png', 'banner' : 'banner.png' })
    listitem.setArt({'icon': thumbnail, 'thumb': thumbnail, 'poster': thumbnail,
                             'fanart': fanart}) 
    if info_labels is None:
        info_labels = { "Title" : title, "FileName" : title, "Plot" : plot }
    listitem.setInfo( "video", info_labels )

    if fanart!="":
        listitem.setProperty('fanart_image',fanart)
        xbmcplugin.setPluginFanart(int(sys.argv[1]), fanart)
    
    if url.startswith("plugin://"):
        itemurl = url
        listitem.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem( handle=int(sys.argv[1]), url=itemurl, listitem=listitem, isFolder=folder)
    elif isPlayable:
        listitem.setProperty("Video", "true")
        listitem.setProperty('IsPlayable', 'true')
        itemurl = '%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s' % ( sys.argv[ 0 ] , action , urllib.parse.quote_plus( title ) , urllib.parse.quote_plus(url) , urllib.parse.quote_plus( thumbnail ) , urllib.parse.quote_plus( plot ) , urllib.parse.quote_plus( extra ) , urllib.parse.quote_plus( page ))
        xbmcplugin.addDirectoryItem( handle=int(sys.argv[1]), url=itemurl, listitem=listitem, isFolder=folder)
    else:
        itemurl = '%s?action=%s&title=%s&url=%s&thumbnail=%s&plot=%s&extra=%s&page=%s' % ( sys.argv[ 0 ] , action , urllib.parse.quote_plus( title ) , urllib.parse.quote_plus(url) , urllib.parse.quote_plus( thumbnail ) , urllib.parse.quote_plus( plot ) , urllib.parse.quote_plus( extra ) , urllib.parse.quote_plus( page ))
        xbmcplugin.addDirectoryItem( handle=int(sys.argv[1]), url=itemurl, listitem=listitem, isFolder=folder)

def close_item_list():
    _log("close_item_list")

    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)

def play_resolved_url(url):
    _log("play_resolved_url ["+url+"]")

    listitem = xbmcgui.ListItem(path=url)
    listitem.setProperty('IsPlayable', 'true')
    return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)

def direct_play(url):
    _log("direct_play ["+url+"]")

    title = ""

    try:
        xlistitem = xbmcgui.ListItem( title,  path=url)
    except:
        xlistitem = xbmcgui.ListItem( title,  )
    xlistitem.setInfo( "video", { "Title": title } )

    playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
    playlist.clear()
    playlist.add( url, xlistitem )

    player_type = xbmc.PLAYER_CORE_AUTO
    xbmcPlayer = xbmc.Player( player_type )
    xbmcPlayer.play(playlist)

def show_picture(url):

    local_folder = os.path.join(get_data_path(),"images")
    if not os.path.exists(local_folder):
        try:
            os.mkdir(local_folder)
        except:
            pass
    local_file = os.path.join(local_folder,"temp.jpg")

    # Download picture
    urllib.request.urlretrieve(url, local_file)
    
    # Show picture
    xbmc.executebuiltin( "SlideShow("+local_folder+")" )

def get_temp_path():
    _log("get_temp_path")
    try:
        dev = xbmc.translatePath( "special://temp/" )    except:        dev = xbmcvfs.translatePath( "special://temp/" )
    _log("get_temp_path ->'"+str(dev)+"'")

    return dev

def get_runtime_path():
    _log("get_runtime_path")
    try:
        dev = xbmc.translatePath( __settings__.getAddonInfo('Path') )    except:        dev = xbmcvfs.translatePath( __settings__.getAddonInfo('Path') )
    _log("get_runtime_path ->'"+str(dev)+"'")

    return dev

def get_data_path():
    _log("get_data_path")
    try:
         dev = xbmc.translatePath( __settings__.getAddonInfo('Profile') )    except:         dev = xbmcvfs.translatePath( __settings__.getAddonInfo('Profile') )
    
    # Parche para XBMC4XBOX
    if not os.path.exists(dev):
        os.makedirs(dev)

    _log("get_data_path ->'"+str(dev)+"'")

    return dev

def get_setting(name):
    _log("get_setting name='"+name+"'")

    dev = __settings__.getSetting( name )

    _log("get_setting ->'"+str(dev)+"'")

    return dev

def set_setting(name,value):
    _log("set_setting name='"+name+"','"+value+"'")

    __settings__.setSetting( name,value )

def open_settings_dialog():
    _log("open_settings_dialog")

    __settings__.openSettings()

def get_localized_string(code):
    _log("get_localized_string code="+str(code))

    dev = __language__(code)

    try:
        dev = dev.encode("utf-8")
    except:
        pass

    _log("get_localized_string ->'"+dev+"'")

    return dev

def keyboard_input(default_text="", title="", hidden=False):
    _log("keyboard_input default_text='"+default_text+"'")

    keyboard = xbmc.Keyboard(default_text,title,hidden)
    keyboard.doModal()
    
    if (keyboard.isConfirmed()):
        tecleado = keyboard.getText()
    else:
        tecleado = ""

    _log("keyboard_input ->'"+tecleado+"'")

    return tecleado

def message(text1, text2="", text3=""):
    _log("message text1='"+text1+"', text2='"+text2+"', text3='"+text3+"'")

    if text3=="":
        xbmcgui.Dialog().ok( text1 , text2 )
    elif text2=="":
        xbmcgui.Dialog().ok( "" , text1 )
    else:
        xbmcgui.Dialog().ok( text1 , text2 , text3 )

def message_yes_no(text1, text2="", text3=""):
    _log("message_yes_no text1='"+text1+"', text2='"+text2+"', text3='"+text3+"'")

    if text3=="":
        yes_pressed = xbmcgui.Dialog().yesno( text1 , text2 )
    elif text2=="":
        yes_pressed = xbmcgui.Dialog().yesno( "" , text1 )
    else:
        yes_pressed = xbmcgui.Dialog().yesno( text1 , text2 , text3 )

    return yes_pressed

def entitiesfix(string):
    string = string.decode("utf-8")
    string = string.replace("&aacute", "&aacute;")
    string = string.replace("&eacute", "&eacute;")
    string = string.replace("&iacute", "&iacute;")
    string = string.replace("&oacute", "&oacute;")
    string = string.replace("&uacute", "&uacute;")
    string = string.replace("&Aacute", "&Aacute;")
    string = string.replace("&Eacute", "&Eacute;")
    string = string.replace("&Iacute", "&Iacute;")
    string = string.replace("&Oacute", "&Oacute;")
    string = string.replace("&Uacute", "&Uacute;")
    string = string.replace("&uuml", "&uuml;")
    string = string.replace("&Uuml", "&Uuml;")
    string = string.replace("&ntilde", "&ntilde;")
    string = string.replace("&#191", "&#191;")
    string = string.replace("&#161", "&#161;")
    string = string.replace(";;", ";")
    return string

def decodeHtmlentities(string): 
    string = entitiesfix(string)
    entity_re = re.compile("&(#?)(\d{1,5}|\w{1,8});")

    def substitute_entity(match):
        if sys.version_info[0] >= 3:
            from html.entities import name2codepoint as n2cp
        else:
            from htmlentitydefs import name2codepoint as n2cp
        ent = match.group(2)
        if match.group(1) == "#":
            ent = chr(int(ent)).encode('utf-8')
            if sys.version_info[0] >= 3 and isinstance(ent, bytes):
                ent = ent.decode("utf-8")
            return ent
        else:
            cp = n2cp.get(ent)

            if cp:
                cp = chr(cp).encode('utf-8')
                if sys.version_info[0] >= 3 and isinstance(cp, bytes):
                    cp = cp.decode("utf-8")
                return cp
            else:
                return match.group()

    return entity_re.subn(substitute_entity, string)[0]
def selector(option_list,title="Select one"):
    _log("selector title='"+title+"', options="+repr(option_list))

    dia = xbmcgui.Dialog()
    selection = dia.select(title,option_list)

    return selection

def set_view(view_mode, view_code=0):
    _log("set_view view_mode='"+view_mode+"', view_code="+str(view_code))

    # Set the content for extended library views if needed
    if view_mode==MOVIES:
        _log("set_view content is movies")
        xbmcplugin.setContent( int(sys.argv[1]) ,"movies" )
    elif view_mode==TV_SHOWS:
        _log("set_view content is tvshows")
        xbmcplugin.setContent( int(sys.argv[1]) ,"tvshows" )
    elif view_mode==SEASONS:
        _log("set_view content is seasons")
        xbmcplugin.setContent( int(sys.argv[1]) ,"seasons" )
    elif view_mode==EPISODES:
        _log("set_view content is episodes")
        xbmcplugin.setContent( int(sys.argv[1]) ,"episodes" )

    # Reads skin name
    skin_name = xbmc.getSkinDir()
    _log("set_view skin_name='"+skin_name+"'")

    try:
        if view_code==0:
            _log("set_view view mode is "+view_mode)
            view_codes = ALL_VIEW_CODES.get(view_mode)
            view_code = view_codes.get(skin_name)
            _log("set_view view code for "+view_mode+" in "+skin_name+" is "+str(view_code))
            xbmc.executebuiltin("Container.SetViewMode("+str(view_code)+")")
        else:
            _log("set_view view code forced to "+str(view_code))
            xbmc.executebuiltin("Container.SetViewMode("+str(view_code)+")")
    except:
        _log("Unable to find view code for view mode "+str(view_mode)+" and skin "+skin_name)

f = open( os.path.join( os.path.dirname(__file__) , "addon.xml") )
data = f.read()
f.close()
 

__settings__ = xbmcaddon.Addon()
__language__ = __settings__.getLocalizedString

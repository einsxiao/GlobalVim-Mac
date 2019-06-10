#!/usr/bin/env python

#from __future__ import unicode_literals

DEBUG = True
if DEBUG:
    import traceback
    def DE():
        print( traceback.format_exc() )
        INFO['GEEKEY'].onKeyboardClear()
        pass
    pass
else:
    def DE():
        INFO['GEEKEY'].onKeyboardClear()
        pass

######################################################################
INFO= {
    'Email':'einsxiao@hotmail.com',
    'Version':'3.1.3.0',
    #'ServerAddr' : "http://192.168.1.77:8573/",
    'ServerAddr' : "https://ovo.ltd/",
    'HomePage':"https://ovo.ltd/projects/globalvim/",
    'ImageChangePeriod': 50,
    'MacroRecordingMax': 9999,
}

INFO['VersionSrc'] = INFO['ServerAddr']+"image_ads/app_info/"
INFO['ImageSrc'] =INFO['ServerAddr'] + "image_ads/ads_image/"
INFO['LogInitText'] = """Double click to hide this log window."""
INFO['NetVersion'] = None 
######################################################################

import wx
import wx.adv 
#import wx.lib.agw.hyperlink as hyperlink
import base64
import os
import sys
import time
#import copy
import re

from wx.lib.embeddedimage import PyEmbeddedImage
import webbrowser
from functools import reduce

#from win32 import win32api
#from Foundation import *
#from AppKit import *
#from PyObjCTools import AppHelper
from Quartz import *

from localization import *
from locale import getdefaultlocale

from uuid import getnode
client_info = getnode()

#### coded image used in app
import image_logo
import image_mountain
import image_bridge

class log:
    log_func = None
    @classmethod
    def log(cls,*args):
        cont = ' '.join( str(i) for i in args )
        cls.log_func(cont)
        pass

def toInt(numstr,defaultvalue = 0):
    try:
        return int(numstr);
    except:
        return defaultvalue
    pass

def toFloat(numstr,defaultvalue = 0):
    try:
        return float(numstr);
    except:
        return defaultvalue
    pass

def toNumber(strnum='',num=0):
    try:
        num = float(strnum)
    except Exception as e:
        DE()
        pass
    return num

def potentialKeyOfDict(key,dic):
    for k in dic:
        if k.startswith(key): return True
    return False

INFO['APP'] = None
INFO['LOOP'] = None

def warning(message,title=''):
    style = wx.OK|wx.TE_MULTILINE
    dlg = wx.MessageDialog(INFO['APP'],message,title,style = style)
    dlg.ShowModal()
    dlg.Destroy()
    self.payImage.SetFocus()
    pass

import threading

class callLaterThread( threading.Thread):
    def __init__(self, func,*argv):
        threading.Thread.__init__(self)

        self.run = lambda argv=argv: func(*argv)
        pass
    pass

def ThreadCallLater(delay, func, *args, **kwargs):
    try:
        delay = max(0.001,toFloat(delay) )
        timer = threading.Timer( delay, func, args, kwargs )
        timer.start()
        return timer
    except Exception as e:
        DE()
        log.log('ThreadCallLater Failed for',e)
    return None

def WxCallLater(delay,func,*args,**kwargs):
    try:
        delay = max(1,toInt(delay*1000) )
        return wx.CallLater(delay, func, *args, **kwargs)
    except Exception as e:
        DE()
        log.log('WxCallLater Failed for',e)
    return None

def WxCallAfter(func,*args,**kwargs):
    try:
        return wx.CallAfter(func, *args, **kwargs)
    except Exception as e:
        DE()
        log.log('WxCallAfter Failed for',e)
    return None

import locale
lang = Language()
if locale.getlocale()[0] == 'zh_CN':
    lang.set_language('zh')
else:
    lang.set_language('en')
    pass

set_lang = lang.set_language
is_en = lambda: True if lang.lang_config == 'en' else False
add_lang = lang.add_lang
lt = lang.lang

def bitmapFromBase64( base64_str ):
    try:
        return wx.Bitmap( PyEmbeddedImage(base64_str).GetImage() );
    except Exception as e:
        log.log("bitmapFromBase64 wrong for:", e , base64_str[:20] )
        return wx.Bitmap( PyEmbeddedImage(image_mountain.img).GetImage() );

def boolFromStr( s ):
    if ( s == 'True' ): return True
    return False

########### keyboard basic information
RawKeyMap=[
    ('esc',53,'Esc'),

    ('f1',122),
    ('f2',120),
    ('f3',99),
    ('f4',118),
    ('f5',96),
    ('f6',97),
    ('f7',98),
    ('f8',100),
    ('f9',101),
    ('f10',109),
    ('f11',103),
    ('f12',111),
    ('f13',0x69),
    ('f14',0x6b),
    ('f15',0x71),
    ('f16',0x6a),
    ('f18',0x4f), 
    ('f19',0x50),
    ('f20',0x5a),
    ('help',0x72),
    ('function',0x3f),


    ('1',18,'1  !'),
    ('2',19,'2  @'),
    ('3',20,'3  #'),
    ('4',21,'4  $'),
    ('5',23,'5  %'),
    ('6',22,'6  ^'),
    ('7',26,'7  &&'),
    ('8',28,'8  *'),
    ('9',25,'9  ('),
    ('0',29,'0  )'),

    ('a',0),
    ('b',11),
    ('c',8),
    ('d',2),
    ('e',14),
    ('f',3),
    ('g',5),
    ('h',4),
    ('i',34),
    ('j',38),
    ('k',40),
    ('l',37),
    ('m',46),
    ('n',45),
    ('o',31),
    ('p',35),
    ('q',12,'REC'),
    ('r',15),
    ('s',1),
    ('t',17),
    ('u',32),
    ('v',9,'VIM'),
    ('w',13),
    ('x',7),
    ('y',16),
    ('z',6),


    ('`',50,'`  ~',),
    ('-',27,'-  _'),
    ('=',24,'=  +'),
    ('backspace',51,'Backspace'),

    ('tab',48,'Tab'),
    ('[',33,"[  {"),
    (']',30,"]  }"),
    ('\\',42,"\\  |"),

    ('caps lock',57,'CapsLock',),
    ('caps lock_up',255,'CapsLock'),
    (';',41,';  :'),
    ("'",39,"'  \""),
    ('return', 36,"Enter"),
    ('enter', 76,"Enter"),

    ('left shift',56,"Shift"),
    (',',43,',  <'),
    ('.',47,'.  >'),
    ('/',44,'/  ?'),
    ('right shift',60,"Shift"),

    ('left ctrl',59,'Ctrl'),
    ('left cmd',55,'Command'),
    ('left alt',58,'Option',),
    ('space',49,'Space'),
    ('right alt',61,'Option'),
    ('right cmd',54,'Command',),
    ('menu',110,'Menu'),
    ('right ctrl',62,'Ctrl'),

    ('insert',114,'Insert'),
    ('delete',117,'Delete'),
    ('home',115,'Home'),
    ('end',119,'End'),
    ('page up',116,'PageUp'),
    ('page down',121,'PageDown'),

    ('left',123,'←'),
    ('right',124,'→'),
    ('up',126,'↑'),
    ('down',125,'↓'),

    ('volume up',0x48,'Volume Up'),
    ('volume down',0x49,'Volume Down'),
    ('volume mute',0x4a,'Volume Mute'),
    ('print screen',105,'Print Screen'),
    ('unicode',555,'Unicode'),
    ('',-1,''),
]

Key2Code = {}
Code2Key = {}
Key2Name = {}
Name2Key = {}

######## rewrite Key2Code and KeyNameMap
for value in RawKeyMap:
    Key2Code[ value[0] ] = value[1]
    Code2Key[ value[1] ] = value[0]
    Key2Code[ value[0] ] = value[1]
    if len(value) > 2 :
        Key2Name[ value[0] ] = value[2]
        Key2Name[ value[0] ] = value[2]
        Name2Key[ value[2] ] = value[0]
    else:
        Key2Name[ value[0] ] = value[0]
        Name2Key[ value[0] ] = value[0]
        pass
    pass

def GetKeyText(key):
    if key in Key2Name: return Key2Name[key] 
    return key

##### simulate key events with fake scancode
#OUTPUT_SOURCE = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)
Masks = {
    'base'          : kCGEventFlagMaskNonCoalesced  ,#0x100  ,base mask
    'caps lock'     : kCGEventFlagMaskAlphaShift    ,#0x10000
    'shift'         : kCGEventFlagMaskShift         ,#0x20000
    'left shift'    : kCGEventFlagMaskShift         ,#0x20000
    'right shift'   : kCGEventFlagMaskShift         ,#0x20000
    'ctrl'          : kCGEventFlagMaskControl       ,#0x40000
    'left ctrl'     : kCGEventFlagMaskControl       ,#0x40000
    'right ctrl'    : kCGEventFlagMaskControl       ,#0x40000
    'alt'           : kCGEventFlagMaskAlternate     ,#0x80000
    'left alt'      : kCGEventFlagMaskAlternate     ,#0x80000
    'right alt'     : kCGEventFlagMaskAlternate     ,#0x80000
    'cmd'           : kCGEventFlagMaskCommand       ,#0x100000
    'left cmd'      : kCGEventFlagMaskCommand       ,#0x100000
    'right cmd'     : kCGEventFlagMaskCommand       ,#0x100000
    #'num lock'      : kCGEventFlagMaskNumericPad    ,#0x200000
    'help'          : kCGEventFlagMaskHelp          ,#0x400000
    'fn'            : kCGEventFlagMaskSecondaryFn   ,#0x800000
    #  f1 f2 f3...                                   #0x800100
    'revised'       : 0x1000000,                     #
    'replay'        : 0x2000000,                     #
    'final'         : 0x4000000,                     #
    'unicode'       : 0x8000000,                     #
}
RevisedMask = Masks['revised']
ReplayMask  = Masks['replay']
FinalMask   = Masks['final']
UnicodeMask = Masks['unicode']

M_B = Masks['base']
M_R = Masks['revised']
M_P = Masks['replay']
M_S = Masks['left shift']
M_A = Masks['left alt']
M_C = Masks['left ctrl']
M_M = Masks['left cmd']
M_F = Masks['final']

INFO['CF']   = Masks['base']
INFO['RCF']  = Masks['base']
INFO['EVCF'] = 0x0

ScanCodeRevised = 222
ScanCodeReplay  = 223
ScanCodeFinal   = 224 

def type_unicode(character):
    # Key down
    event = CGEventCreateKeyboardEvent(None, 0, True)
    CGEventSetFlags(event, UnicodeMask|M_B )
    CGEventKeyboardSetUnicodeString(event, len(character.encode('utf-16-le')) // 2, character)
    CGEventPost(kCGSessionEventTap, event )
    # Key up
    event = CGEventCreateKeyboardEvent(None, 0, False)
    CGEventSetFlags(event, UnicodeMask|M_B )
    CGEventKeyboardSetUnicodeString(event, len(character.encode('utf-16-le')) // 2, character)
    CGEventPost(kCGSessionEventTap, event )
    pass

INFO['covering'] = False

class GeeKeyBoard:
    def __init__(self):
        pass

    def setKeyEventDelay(self,delay):
        pass
        
    def coverKey(self):
        for key in ModifierKeys:
            if INFO['RCF'] & Masks[key]:
                #print('cover',key)
                INFO['covering'] = True 
                INFO['CF']=INFO['CF']&~Masks[key]
            pass

    def recoverKey(self):
        for key in ModifierKeys:
            if INFO['RCF'] & Masks[key]:
                #print('recover',key)
                INFO['CF']=INFO['CF']|Masks[key]
                INFO['covering'] = False
            pass
        
    def keyPress(self, key, flags=RevisedMask ):
        code = Key2Code.get(key,key)
        evt = CGEventCreateKeyboardEvent(None,code,True)
        CGEventSetFlags(evt, flags|INFO['CF']|INFO['EVCF'] )
        CGEventPost(kCGSessionEventTap,evt )
        pass

    def keyRelease(self, key, flags=RevisedMask ):
        code = Key2Code.get(key,key)
        evt = CGEventCreateKeyboardEvent(None,code,False)
        CGEventSetFlags(evt, flags|INFO['CF']|INFO['EVCF'] )
        CGEventPost(kCGSessionEventTap,evt )
        pass

    def keyStroke(self, key, flags=RevisedMask):
        code = Key2Code.get(key,key)
        self.keyPress(code, flags)
        self.keyRelease(code, flags)
        pass

    def repeatedNumber(self,num):
        if num == '' : return 1
        res = 1
        try: res = int(num)
        except: pass
        return res

    def keySend(self,key,keytype = 'key down',repeated = 1, flags= RevisedMask ):
        try:
            code = Key2Code.get(key,key)
            repeated = self.repeatedNumber(repeated )
            if code< 0: return
            if keytype in ('key down','d'):
                for i in range( repeated -1 ):
                    self.keyStroke(code, flags)
                    pass
                self.keyPress(key, flags)
            else:
                self.keyRelease(key, flags)
            pass
        except Exception as e:
            log.log('keySend error for:',e)
            de
            pass
        pass

    def textSend(self,text):
        try:
            for letter in text: type_unicode(letter)
        except Exception as e:
            log.log('textSend error for:',e)
            DE()
        pass
        
    pass

##############################################################
##############################################################
### map and choices initialize
FunctionKeys = ['f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f10','f11','f12']

NumberKeys = ['0','1','2','3','4','5','6','7','8','9']

CharKeys = ['a','b','c','d','e','f','g',
            'h','i','j','k','l','m','n',
            'o','p','q',    'r','s','t',
            'u','v','w',    'x','y','z']
SymbolKeys = ['`','-','=','[',']','\\',';','\'',',','.','/',]

SpecKeys = [',','.','/','\\','-','=','(',')','!','@','#','$','%','^','&','*','=','`',]

StringKeys = NumberKeys + CharKeys + SymbolKeys


ModifierKeys = [ 'left shift','left ctrl',
             'left cmd','left alt','right alt',
             'right cmd','right ctrl','right shift']

MenuKeys_1 = [ 'tab','caps lock','menu', ] + ModifierKeys

MenuKeys = [ 'esc' ] + MenuKeys_1

MenuKeysText = [ Key2Name[v] for v in MenuKeys ]

EditKeys = [ '','left','down','up','right','home','end','return',
             'page up','page down','backspace','delete','insert','print screen',
             'volume up','volume down','volume mute', #'num lock',
             'left shift','left ctrl','left alt','left cmd','tab','caps lock',
             'right shift','right ctrl','right alt','right cmd',
]
EditKeysText = [ Key2Name[v] for v in EditKeys ]


GlobalMaps = {}
GlobalMaps['macro'] = {
    "t":"",
    "y":"copy:0:_right cmd:_c:c:right cmd",
    "p":"paste:0:_right cmd:_v:v:right cmd",
    "f2":"save:0:_right cmd:_s:s:right cmd",
    "":"",
}
GlobalMaps['edit'] = {
    '-':'volume down','=':'volume up','backspace':'volume mute',
    "h":"left","j":"down","k":"up","l":'right',
    "n":"down",
    "p":"up",
    "b":"left",
    "f":"right",
    "a":"home",
    "e":"end", 
    '[':'page up',
    ']':'page down',
}
GlobalMaps['text'] = {
    "":"",
}
GlobalMaps['function'] = {
    '':'',
}

GlobalMaps['keytype'] = {
    'y':'macro', 'p':'macro', 'o':'macro', 'u':'macro', 'i':'macro','w':'macro','b':'macro',

    'f2':'macro',

    '0':'edit',
    '[':'edit',
    ']':'edit',
    '':'',
}

GlobalMaps['vim'] = {
    ### shift_ should ahead of ctrl_ 
    'esc':'esc',
    'space':'right',
    'backspace':'left',
    'return':'return',
    'h':'left',
    'j':'down',
    'k':'up',
    'l':'right',
    '0':'home line',
    'shift_\\':'jump bar',
    'shift_6':'home block',
    'shift_4':'end',

    "shift_'":'register',
    'shift_;':'command',
    'q':'record',
    'shift_2':'execute',

    'i':'insert',
    'shift_i':'insert begin',
    'a':'append',
    'shift_a':'append end',
    'o':'insert next line',
    'shift_o':'insert prev line',

    's':'change',
    'c__w':'change word',
    'c__e':'change word',
    'c__b':'change word back',
    'shift_s':'change line',
    'c__c':'change line',
    'c__0':'change begin',
    'c__shift_6':'change begin',
    'shift_c':'change end',
    'c__shift_4':'change end',

    #'r':'replace char', ## 
    #'shift_r':'replace mode',

    'y':'copy',
    'y__w':'copy word',
    'y__e':'copy word',
    'y__b':'copy word back',
    'y__y':'copy line',
    'shift_y':'copy line',
    'y__shift_6':'copy begin',
    'y__0':'copy begin',
    'y__shift_4':'copy end',

    'p':'paste',
    'shift_p':'paste prev', # if paste line paste on privous

    'x':'x cut',
    'shift_x':'x cut previous',

    'd':'cut', # only function in visual mode
    'd__d':'cut line',
    'd__w':'cut word',
    'd__e':'cut word',
    'd__b':'cut word back',
    'd__0':'cut begin',
    'd__shift_6':'cut begin',
    'shift_d':'cut end', # only function in visual mode
    'd__shift_4':'cut end',

    'u':'undo',
    'shift_u':'redo',
    'shift_j':'merge line', 

    'v':'visual mode',
    'shift_v':'line visual mode',
    'w':'next word',
    'e':'end word',
    'b':'prev word',
    'shift_[':'prev para',
    'shift_]':'next para',

    'g__g':'jump head',
    'shift_g':'jump tail',

    'y__g__g':'copy head',
    'y__shift_g':'copy tail',
    'd__g__g':'cut head',
    'd__shift_g':'cut tail',

    #'f2':'save',
    '/':'find',
    'shift_8':'find current',

    'z__z':'caret center',
    # 'z__t':'caret top',
    # 'z__b':'caret bottom',

    'ctrl_r':'redo',
    'ctrl_f':'page down',
    'ctrl_b':'page up',
}

GlobalMaps['vim_register'] = {
    '':'', #(content) 'k':'^xxxx' for pure text or 'k':'^:0:xxxxx' for operation record
}

vim_move_count ={
    'left' : -1,
    'right':  1,
    'up'   :-40,
    'down' : 40,
    'home' :-20,
    'end'  : 20,
    'word' :  6,
    'back' : -6,
}

GlobalMaps['layout'] = {'':'',}

ToolTipKeys = {'space','q','v'}

def GetMap( cat, key):
    if not cat in GlobalMaps: return ''
    if not key in GlobalMaps[cat]: return ''
    return GlobalMaps[cat][key]

def SetMap( cat, key, value):
    if not cat in GlobalMaps: return False
    GlobalMaps[ cat ][ key ] = value
    return True
   
Color_Map ={

    'layout_1':'#d2efe8',
    'layout_2':'#d3eee7',
    'layout_3':'#aee0d4',
    'layout_4':'#90d5c4',
    'layout_5':'#76cbb7',
    'layout_6':'#59c0a7', #deepskyblue
    'layout_selected':'#87cefa',

    'geekey' : '#c0f616',
    'rec': '#cb5bff',
    'space' : '#cfefa1',        

    'menu_key' : '#66cdef',

    'macro_key':'#D8BFD8',
    'macro_button':'#CD96CD',

    'text_key':'#D8BFff',
    'text_button':'#CD96ff',

    'edit_key':'#BFEFFF',
    'edit_button':'#87cefa',

    'function_key':'#9Fb6cd',
    'function_button':'#9bcd9b',

    'plain_key' : '#9Fb6cd',

    'candidate_texts':'#9Fb6cd',
    'candidate_selected':'#c0ff3e',

    'vim disable':'#ff6f5d',
    'vim normal':'#ebffb3',
    'vim insert':'#b3baff',
    'vim visual':'#eab3ff',
    'vim text':'#555555',
    'keyboard_panel':'#4a708b',
    'bottom_panel':'#698b69',
    '':'',
}
GlobalMaps['color'] = Color_Map
def GetColorMap(key,default='plain_key'): return GlobalMaps['color'].get(key,GlobalMaps['color'][default] )


def regesterGeeKey(action=True):
    if action: # add regedit
        pass
    else:
        pass
    win32api.RegCloseKey(key)
    pass
        
class GeeMouse:

    #def buttonEvent(self, pos=None, buttonStr='left' ):
    def buttonEvent(self, evttype, pos=None, wheel=0 ):
        if evttype in (kCGEventLeftMouseDown,
                       kCGEventLeftMouseUp):
            evt = CGEventCreateMouseEvent(None,evttype,pos,kCGMouseButtonLeft)
            CGEventPost(kCGSessionEventTap,evt )
            pass
        elif evttype in (kCGEventRightMouseDown,
                         kCGEventRightMouseUp):
            evt = CGEventCreateMouseEvent(None,evttype,pos,kCGMouseButtonRight)
            CGEventPost(kCGSessionEventTap,evt )
        elif evttype == kCGEventScrollWheel:
            evt = CGEventCreateScrollWheelEvent(None,kCGScrollEventUnitLine,1,wheel)
            CGEventPost(kCGSessionEventTap,evt )
        pass
        
    pass

geeKeyboard = GeeKeyBoard()
geeMouse = GeeMouse()

KeyStroke = lambda Key,flags=0x0,eflags=RevisedMask: geeKeyboard.keyStroke(Key,flags|eflags)
KeyPress = lambda Key,flags=0x0,eflags=RevisedMask: geeKeyboard.keyPress(Key,flags|eflags)
KeyRelease = lambda Key,flags=0x0,eflags=RevisedMask: geeKeyboard.keyRelease(Key,flags|eflags)

DelayKeyStroke = lambda t,Key,flags=0x0,eflags=RevisedMask: WxCallLater(t,geeKeyboard.keyStroke,Key,flags|eflags)
DelayKeyPress = lambda t,Key,flags=0x0,eflags=RevisedMask: WxCallLater(t,geeKeyboard.keyPress,Key,flags|eflags)
DelayKeyRelease = lambda t,Key,flags=0x0,eflags=RevisedMask: WxCallLater(t,geeKeyboard.keyRelease,Key,flags|eflags)

KeySend = lambda key,keytype='key down',repeated=1, flags=RevisedMask: geeKeyboard.keySend(key,keytype,repeated,flags)
SetKeyDelay = lambda delay: geeKeyboard.setKeyEventDelay(delay)
TextSend = lambda txt: geeKeyboard.textSend( txt )

GlobalMaps['menu'] = {}

mouseEventTypeMap = {
    kCGEventLeftMouseDown:'ld',
    kCGEventLeftMouseUp:'lu',
    kCGEventRightMouseDown:'rd',
    kCGEventRightMouseUp:'ru',
    kCGEventScrollWheel:'w',
}

rmouseEventTypeMap = dict( map( lambda ele:(ele[1],ele[0]), mouseEventTypeMap.items() ) )

def runAsAdmin(argv=None, debug=False):
    return False

class UpdateDialog( wx.Dialog):
    
    def __init__(self,cont,*args,**kwargs):
        self.textPanel = None
        self.contPanel = None
        self.sizer = None
        self.button = {}
        self.H = 30;
        self.W = 450; self.tH = 60; self.bH = 50;
        self.yP = 20; self.xP = 20;

        wx.Dialog.__init__(self,*args,**kwargs)
        self.SetTitle( _('_new_version_available') )
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.textPanel = wx.Panel(self,size=(self.W, self.tH) )
        self.bottomPanel = wx.Panel( self, size=(self.W, self.bH) )
        self.bottomPanel.SetBackgroundColour( "#E5E5E5" )

        self.sizer.Add( self.textPanel )
        self.sizer.Add( self.bottomPanel )

        text = wx.StaticText( self.textPanel, label='test', pos=(self.yP, self.xP), size=(self.W-20, self.tH-20 ), style= wx.ALIGN_CENTER)

        self.button['update'] = wx.Button(self.bottomPanel, label= _("Update"),pos=(self.W/2-60,self.H/3),size=(80,self.H ) )
        self.button['cancel'] = wx.Button(self.bottomPanel, label= _("Cancel"),pos=(self.W/2+40,self.H/3),size=(80,self.H) )

        self.SetSizerAndFit( self.sizer )
        pass
    pass

def rgbToHex(r,g,b):
    return "{0:02x}{1:02x}{2:02x}".format(r,g,b)

def hexToRgb(h):
    if h[0] != '#': raise Exception('hexToRgb failed for hex string not start with #')
    if len(h)<4: raise Exception('hexToRgb failed for hex string shorter than 4bits')
    if len(h)<7: h += h[1:4]
    return tuple( int(h[i:i+2],16) for i in(1,3,5) )

def hexReverse(h):
    rgb = hexToRgb( h )
    return rgbToHex( 255-rgb[0],255-rgb[1], 255-rgb[2] )
    
def getCbText():
    #print('try get cb')
    txt = wx.TextDataObject()
    while True:
        time.sleep(0.01)
        try:
            if not wx.TheClipboard.IsOpened():
                if wx.TheClipboard.Open():
                    wx.TheClipboard.GetData( txt )
                    wx.TheClipboard.Close()
                    break
                pass
            #print('no data get wait and try again')
        except Exception as e:
            DE()
            pass
        time.sleep(0.01)
        pass
    return txt.GetText()

def setCbText(txt):
    while True:
        time.sleep(0.01)
        try:
            if not wx.TheClipboard.IsOpened():
                if wx.TheClipboard.Open():
                    #print('set cb>>>',[txt,] )
                    wx.TheClipboard.Clear()
                    success = wx.TheClipboard.SetData( wx.TextDataObject(txt) )
                    wx.TheClipboard.Close()
                    #print('set result =',success)
                    break
            #print('no data set wait and try again')
        except Exception as e:
            DE()
            pass
        time.sleep(0.01)
    return

def SetRegister(register, txt):
    if not txt: return None
    #print('set register {0}:{1}'.format(register,txt) )

    if register[:6] == 'shift_':
        if register[7:] in CharKeys:
            # ignore the first ^ or <
            txt = GetMap('vim_register',register) + txt[1:] 
            pass
        pass

    return SetMap('vim_register',register,txt )

def GetRegister(register):
    if not register: return None#do nothing
    res = GetMap('vim_register',register )
    if not res: return None
    #print(type(res),res )
    return res


mapping = {'\a': r'\a', '\b': r'\b', '\f': r'\f', '\n': r'\n',
           '\r': r'\r', '\t': r'\t', '\v': r'\v'}

def escape(astr):
    for char, escaped in mapping.items():
        astr = astr.replace(char, escaped)
    return astr

UpperKeys = { #Key uppper chr, ie. 1 -> ! 
    '`':'~',
    '1':'!','2':'@','3':'#','4':'$','5':'%','6':'^','7':'&','8':'*','9':'(','0':')',
    '-':'_','=':'+',
    '[':'{',']':'}','\\':'|',
    ';':':','\'':'"',
    ',':'<','.':'>',
}

LowerKeys = { v:k for k,v in UpperKeys.items() }

def upper(ch):
    return UpperKeys.get(ch) or ch.upper()

def lower(ch):
    return LowerKeys.get(ch) or ch.lower()

KeyDisplays = { 'space':' ', }
def display(ch):
    if ch in KeyDisplays: return KeyDisplays.get(ch)
    return ch
    
def vim_search_scope(astr):
    num = ''
    while astr and astr[-1] in NumberKeys:
        num = astr[-1]+num
        astr = astr[:-1]
        pass
    if astr and astr[-1] in ('-','+'):
        d = astr[-1]
        astr = astr[:-1]
    else:
        d = ''
        pass
    if not d and num and astr: return False
    if not d and num: return [int(num),0]
    if num == '': num = 0
    else: num = int(d+num)

    return [astr,num]

import ctypes, objc
_objc = ctypes.PyDLL(objc._objc.__file__)

# PyObject *PyObjCObject_New(id objc_object, int flags, int retain)
_objc.PyObjCObject_New.restype = ctypes.py_object
_objc.PyObjCObject_New.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]

def objc_object(id):
    return _objc.PyObjCObject_New(id, 0, 1)

def SetFullScreenCapable(frame):
    frameobj = objc_object(frame.GetHandle())

    NSWindowCollectionBehaviorFullScreenPrimary = 1<<7
    window = frameobj.window()
    newBehavior = window.collectionBehavior() | NSWindowCollectionBehaviorFullScreenPrimary
    window.setCollectionBehavior_(newBehavior)

class windowManagement:
    def getActiveScreenSize(self):
        s = NSScreen.mainScreen().frame().size
        return (0,0,s.width, s.height)

    def getActiveAppPID(self):
        workspace = NSWorkspace.sharedWorkspace()
        app = workspace.frontmostApplication()
        pid  = app.processIdentifier() 
        return pid

    def getActiveWindow(self):
        workspace = NSWorkspace.sharedWorkspace()
        app = workspace.frontmostApplication()
        pid  = app.processIdentifier() 
        options = kCGWindowListOptionOnScreenOnly
        windowList = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
        rect =  None
        for window in windowList:
            if window['kCGWindowOwnerPID'] == pid :
                r = window['kCGWindowBounds']
                rect = (r['X'],r['Y'],r['Width'],r['Height'] )
                break
            pass
        return (rect,app)

    pass

geeWindow = windowManagement()

def keyboardCallBack(proxy, evttype, evt, refcon):
    try:
        KeyCode = CGEventGetIntegerValueField(evt,kCGKeyboardEventKeycode) 
        Key = Code2Key.get(KeyCode, KeyCode )
        if Key == 'caps lock_up': Key = 'caps lock'
        AutoKey = CGEventGetIntegerValueField(evt,kCGKeyboardEventAutorepeat)
        Flags = CGEventGetFlags(evt) 
        EvtScanCode = 0
        if Flags&RevisedMask: EvtScanCode = ScanCodeRevised#
        elif Flags&ReplayMask : EvtScanCode = ScanCodeReplay#
        elif Flags&FinalMask  : EvtScanCode = ScanCodeFinal#
        elif Flags&UnicodeMask: return evt
        EvtType = 'key down' if evttype == 10 else 'key up'
        mask = Masks.get(Key,0x0)
        if mask:
            if mask&Flags:
                EvtType = 'key down' 
                INFO['CF'] = INFO['CF']|mask
                if EvtScanCode == 0: INFO['RCF'] = INFO['RCF']|mask
            else:
                INFO['CF'] = INFO['CF']&~mask
                if EvtScanCode == 0: INFO['RCF'] = INFO['RCF']&~mask
                pass
            pass

        if EvtScanCode == ScanCodeFinal: return evt

        #print(EvtType,Key,'Flags:',hex(Flags),'CF:',hex(INFO['CF']),'RawCF:',hex(INFO['RCF']),EvtScanCode)
        #print(EvtType,Key,'Flags:',hex(Flags&M_S),EvtScanCode )

        if  INFO['GEEKEY'].getConfig('printkeyevent') == 'True':
            log.log('{1} {0} ScanCode: {2}'.format(EvtType,Key,EvtScanCode), )
            pass

        covering = INFO['covering']
        if not INFO['GEEKEY'].vim.vim_on: covering = True
        if INFO["GEEKEY"].vim.vim_on and INFO['GEEKEY'].vim.insert_mode:
            covering = True

        if not covering: geeKeyboard.coverKey()
        res = INFO['GEEKEY'].OnKeyboardEvent(Key,EvtType,EvtScanCode)
        if not covering: geeKeyboard.recoverKey()

        if res: return evt
        return None
    except Exception as e:
        DE()
        pass
    return evt



def mouseCallBack( proxy, evttype, evt, refcon):
    try:
        EvtType = CGEventGetType(evt)
        EvtPosition = CGEventGetLocation(evt)
        EvtPosition = ("%.2f"%EvtPosition.x,"%.2f"%EvtPosition.y)
        EvtWheel = CGEventGetIntegerValueField(evt,kCGScrollWheelEventDeltaAxis1)

        res = INFO['GEEKEY'].OnMouseEvent(EvtType,EvtPosition,EvtWheel)
        if res: return evt
        return None

    except Exception as e:
        DE()
        pass

    return evt

class Listener:
    def __init__(self):
        self.pool = NSAutoreleasePool.alloc().init()
        KeyEventsMask= CGEventMaskBit(kCGEventKeyDown)| CGEventMaskBit(kCGEventKeyUp) | CGEventMaskBit(kCGEventFlagsChanged )

        KeyEventsMask= CGEventMaskBit(kCGEventKeyDown)| CGEventMaskBit(kCGEventKeyUp) | CGEventMaskBit(kCGEventFlagsChanged )
        MouseEventsMask = CGEventMaskBit(kCGEventLeftMouseUp)| CGEventMaskBit(kCGEventLeftMouseDown)| CGEventMaskBit(kCGEventRightMouseUp)|CGEventMaskBit(kCGEventRightMouseDown)| CGEventMaskBit(kCGEventScrollWheel)

        self.keyboardTap = CGEventTapCreate(kCGSessionEventTap, kCGHeadInsertEventTap, kCGEventTapOptionDefault, KeyEventsMask, keyboardCallBack, None )
        self.mouseTap = CGEventTapCreate(kCGSessionEventTap, kCGHeadInsertEventTap, kCGEventTapOptionDefault, MouseEventsMask, mouseCallBack, None )

        if self.keyboardTap:
            self.keyboardSource = CFMachPortCreateRunLoopSource( kCFAllocatorDefault, self.keyboardTap,0)
            CFRunLoopAddSource( CFRunLoopGetCurrent(), self.keyboardSource, kCFRunLoopCommonModes);
        else:
            log.log('Can not make keyboard hook to system')
            raise Exception('Can not make keyboard hook to system')
        if self.mouseTap:
            self.mouseSource = CFMachPortCreateRunLoopSource( kCFAllocatorDefault, self.mouseTap,0)
            CFRunLoopAddSource( CFRunLoopGetCurrent(), self.mouseSource, kCFRunLoopCommonModes);
        else:
            log.log('Can not make mouse hook to system')
            raise Exception('Can not make mouse hook to system')

        self.timer = None
        self.hook()
        pass

    def hook(self):
        if self.keyboardTap:
            CGEventTapEnable(self.keyboardTap,True)
        if self.mouseTap:
            CGEventTapEnable(self.mouseTap,True)
        if self.timer:  self.timer.Stop()
        self.timer = WxCallLater( 5, self.hook )

    def exit(self):
        if self.keyboardTap:
            CFRelease(self.keyboardTap)
            CFRelease(self.keyboardSource)
        if self.mouseTap:
            CFRelease(self.mouseTap)
            CFRelease(self.mouseSource)
            pass
        #self.pool.release()
        pass

    pass


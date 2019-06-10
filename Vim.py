#!/usr/bin/env python
# -*- coding: utf-8 -*-
from res import *

class VimStateIndicator(wx.Frame):
    def __init__(self,parent,mainFrame,vim):
        self.geekey = mainFrame
        self.vim = vim
        self.size = (0,0)
        self.timer = None

        wx.Frame.__init__(self,None,wx.NewId(),"Indicator",
        #wx.Frame.__init__(self,parent,wx.NewId(),"Indicator",
                          size = self.size, style=wx.STAY_ON_TOP )
        self.Move((-200,-200) )

        ### by osx api to set always on top
        self.frameobj = objc_object( self.GetHandle() )
        self.window = self.frameobj.window()
        # movetoactive  #ignore cycle #
        bh = 1 << 1 | 1<<6 |1<<8 
        newBehavior = self.window.collectionBehavior()|bh
        #print(self.frameobj, self.window, self.window.level(),newBehavior )
        self.window.setCollectionBehavior_(newBehavior )
        #print(self.frameobj, self.window, self.window.level() )
        
        ###
        font = wx.Font(12, wx.ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT,)

        self.text = wx.StaticText(self, pos=(0,0), style = wx.ALIGN_LEFT)
        self.text.SetFont(font)
        self.text.SetForegroundColour( GetColorMap('vim text') ) ####

        self.text_input = wx.TextCtrl(self, pos=(0,0),style = wx.NO_BORDER,)
        self.text_input.SetFont(font)
        self.text_input.SetForegroundColour( GetColorMap('vim text') ) ####
        self.text_input.Bind(wx.EVT_TEXT, self.OnChange )

        self.text_hide = wx.StaticText(self, pos=(-5000,-5000), style = wx.ALIGN_LEFT)
        self.text_hide.SetFont(font)

        ###
        self.text.SetLabel( lt("--vim enabled--")),

        self.last_pos = (0,0)

        self.last_app = None
        pass

    def GetText(self):
        return self.text_input.GetValue()

    def ConfSize(self):
        self.label_size = self.text.GetSize()
        self.text_hide.SetLabel( self.text.GetLabel() +self.GetText() )
        self.size = self.text_hide.GetSize()
        self.size = (self.size[0]+20,self.size[1] )
        self.text_input.SetPosition( (self.label_size[0],0) )
        self.text_input.SetSize( (self.size[0] - self.label_size[0],self.label_size[1]) )

        self.SetSize( self.size )
        pass

    def OnChange(self,evt):
        self.ConfSize()

    def GetPosition(self):
        if self.vim.commanding and self.last_pos: return self.last_pos
        if self.FindFocus() == self.text_input and self.last_pos: return self.last_pos
        if INFO['PID'] == geeWindow.getActiveAppPID() and self.last_pos:
            return self.last_pos

        self.last_app = geeWindow.getActiveWindow()
        INFO['CAPP'] = self.last_app[1].bundleIdentifier()
        rect = self.last_app[0]
        #print('rect = ',rect)
        if not rect:
            pos = self.last_pos
        else:
            pos  = ( int(rect[0]+3*rect[2]/4), rect[1] )
            self.last_pos = pos
            pass
        #print('get position ',pos)
        return pos
 
    def DeactiveSelf(self):
        #self.last_app[1].NSApplicationActivateIgnoringOtherApp(True)
        # ignore other Apps 1<<1  activate all windows 1<<0 
        if self.last_app: self.last_app[1].activateWithOptions_( 1<<1 )
        pass

    def RaiseSelf(self):
        self.geekey.Show(False)
        self.Raise()
        INFO['NSAPP'].activateIgnoringOtherApps_(True)
        self.text_input.SetFocus()
        pass

    def __set(self,label,text,color_name = None):
        #print('indicator set',label,text,color_name)
        self.text.SetLabel( "  "+label+"  ")
        self.text_input.ChangeValue( text )
        self.ConfSize()

        if color_name:
            color = GetColorMap(color_name)
            self.geekey.key_buttons['v'].SetBackgroundColour( color )
            self.geekey.key_buttons['v'].Refresh()

            self.text.SetBackgroundColour( color )
            self.text_input.SetBackgroundColour( color )
            self.text.Refresh()
            self.text_input.Refresh()
            pass
        self.Hide()
        self.Show()
        pass

    def ResetPosition(self):
        self.Move( self.GetPosition() )
        pass
    def StateReset(self,label='', text="", label_extra=''):
        #if INFO['PID'] == geeWindow.getActiveAppPID(): self.DeactiveSelf()
        if self.geekey.state_is_over: return 
        WxCallLater(0.001,self._StateReset,label,text,label_extra)
        #print('StateReset finished' )
        pass
        
    def _StateReset(self,label,text,label_extra):
        if self.vim.vim_on:
            mode = ""
            if self.vim.visual_mode:  mode = 'visual'
            elif self.vim.insert_mode: mode = 'insert'
            else: mode = 'normal'

            if label == "" or label == 'disable':
                label = '--' + lt(mode) + '--'
                if self.vim.number: label = label + self.vim.number + "--"
                if self.vim.record: label = label + lt("recording ")+self.vim.record+"--"
                if self.vim.register: label = label + "\""+self.vim.register+"--"
                if label_extra: label = label + label_extra+"--"
                if self.vim.commanding:
                    if self.vim.expression: label = '='
                    else: label = ':'
                pass

            self.__set( label ,text, 'vim '+mode )

            self.Move( self.GetPosition() )
            self.Show( True )
        else:
            if label == 'disable':
                if self.timer: self.timer.Stop()
                self.Show(False )
                return
            if label or text:
                self.__set( label,text, 'vim insert' )
            else :
                self.__set( "--"+lt('vim disabled')+"--","",'vim disable' )
                pass
            self.Move( self.GetPosition() )
            self.Show( True )
            if not self.geekey.state_is_recording:
                if self.timer: self.timer.Stop()
                self.timer = WxCallLater(5,self.Show,False)
            pass
    pass


class Vim:
    def __init__(self,parent, mainFrame):
        self.geekey = mainFrame
        self.vim_on = False
        self.visual_mode = False
        self.insert_mode = False
        self.visual_move = 0
        self.unprocessed_char = ""
        self.unprocessed_other_key = False
        self.number = ""
        self.registering = False
        self.register = ""
        self.esc_time = 0
        self.line_cut = False
        self.big_cut = False
        self.commanding = False
        self.command = ''
        self.expression = False
        self.recording = False
        self.record = ''
        self.executing = False
        self.execute = ''
        self.commands = ['']
        self.expressions = ['']
        self.command_index = 0 
        self.expression_index = 0

        #self.caret = VimCaret(parent, self.geekey, self)
        self.indicator = VimStateIndicator(parent, self.geekey, self)

        pass

    def Destroy(self):
        #if self.caret: self.caret.Destroy()
        if self.indicator: self.indicator.Destroy()
        pass

    pass

    def quit_visual_mode_state(self):
        #KeyRelease('left shift')
        self.visual_mode = False
        INFO['EVCF'] = 0x0

    def quit_visual_mode_move(self):
        if self.visual_move < 0: 
            KeyStroke('left')
        else:
            KeyStroke('right')
            pass
        self.visual_move = 0

    def quit_visual_mode(self,force=False):
        if force or self.visual_mode :
            #log.log('quit visual mode', self.visual_move)
            self.quit_visual_mode_state()
            self.quit_visual_mode_move()
            pass
        pass

    def quit_insert_mode(self):
        self.insert_mode = False
        pass

    def mini_state_reset(self):
        pass

    def state_reset(self):
        self.quit_visual_mode()
        self.quit_insert_mode()
        self.unprocessed_char = ''
        self.unprocessed_other_key = False
        self.number = ''
        #self.vim_on = True
        self.registering = False
        self.register = ''
        self.commanding = False
        self.command = ''
        self.expression = False
        # self.recording = False
        # self.record = ''
        self.play_ratio = 0
        self.indicator.StateReset()
        #self.caret.StateReset()
        pass

    def state_switch(self,state=None):
        #state = None, 'on', 'off'
        self.geekey.number_string = ''
        self.insert_mode = False
        self.quit_visual_mode()
        self.state_reset()

        if state == 'on' or state == 'True':
            self.vim_on = True
        elif state == 'off' or state == 'False':
            self.vim_on = False 
        else:
            self.vim_on = not self.vim_on

        if self.vim_on:
            ### to make shift cover and recover work properly
            #geeKeyboard.coverKey('shift')
            #geeKeyboard.recoverKey('shift')
            ###
            pass
        else:
            self.recording = False
            self.record = ''

        self.geekey.Log(lt('enable vim mode') if self.vim_on else lt('exit vim mode') )

        self.indicator.StateReset()

        return False

    # big cut should be '0' '1' '0' for big copy '1' for big delete
    def _setRegister(self,bigcut,linecut):
        #print('setRegister')
        txt = getCbText()
        #print('txt get is',txt)
        if linecut: txt = '^' + txt
        if not self.register:
            if bigcut == '0':
                self.register = '0'
            elif bigcut == '1':
                self.register = '1'
                # move 
                for i in range(9,1,-1):
                    SetRegister(str(i), GetRegister(str(i-1) ) )
                    pass
                pass
            else:
                self.register = '-'
                pass
            pass
        SetRegister(self.register, txt )
        self.line_cut = linecut
        self.register = ''
        self.indicator.StateReset()

    def setRegister(self,bigcut,linecut):
        WxCallLater(0.05, self._setRegister, bigcut, linecut )

    def getRegister(self):
        if not self.register: return True #do nothing
        if self.register != '"': 
            res = GetRegister(self.register) 
            #print('get register {0}:{1}'.format(self.register,res) )
            if not res:
                self.indicator.StateReset( lt('nothing in register {0}',self.register)  ) 
                return False
            if res[0] == '^':
                setCbText( res[1:] )
                self.line_cut = True
            else:
                setCbText( res )
                self.line_cut = False
                pass
            pass
        self.register = ''
        self.indicator.StateReset()
        return True

    def registeringGet(self,Key):
        if self.geekey.state_on_shift:Key = 'shift_' + Key 
        self.register = Key
        self.registering = False
        if Key == '=':
            self.commanding = True
            self.expression = True
            self.indicator.StateReset("=")
            if self.expressions[0]: self.expressions = [''] + self.expressions
            pass
        else:
            self.indicator.StateReset()
            pass
        return False
            
    def recordingGet(self,Key):
        if self.geekey.state_on_shift:Key = 'shift_'+Key
        self.record = Key
        self.recording = False #state to get register key for store recording
        self.indicator.StateReset()

        self.geekey.startRecording()

        return False

    def executingDo(self,Key):
        if self.geekey.state_on_shift:Key = 'shift_'+Key
        self.execute = Key
        self.executing = False
        self.indicator.StateReset(lt('executing {0}',Key) )
        cont = GetRegister(Key) 
        #print('cont =',cont)
        if not cont: return False
        mapvalue = cont.split(':') # :0:_x~0.1:x~0.2
        if len(mapvalue)>=3:
            try:
                ratio = toFloat(mapvalue[1],-1)
                if ratio < 0: return False
                mapvalue = map(lambda v: v.split('~'), mapvalue[2:] )  
                oper_number = lambda : 1 if self.number  == '' else int(self.number)
                sequence =  list(mapvalue) * oper_number()
                self.number = ''
                self.geekey.Replay(ratio, sequence)
            except Exception as e:
                self.geekey.Log("try execute register {0} failed for: {1}".format(Key,e) )
                self.indicator.StateReset( lt('executing {0} failed',Key) )
                DE()
        return False

                
    def ProcessKey(self,Key,EvtType):
        #print('processkey',Key,EvtType,'CF:',hex(INFO['CF']),'RawCF:',hex(INFO['RCF']),'shift:',hex(INFO['RCF']&M_S),'cshift:',hex(INFO['CF']&M_S),self.state_on_shift)
        #print('processkey',Key,EvtType,'shift:',hex(INFO['RCF']&M_S),'cshift:',hex(INFO['CF']&M_S),self.geekey.state_on_shift,INFO['EVCF'] )
        #print('processkey',Key,EvtType,)
        # esc not included
        if ( Key in MenuKeys_1 ): 
            self.quit_visual_mode()
            self.indicator.StateReset()
            return True

        if self.commanding:
            self.indicator.RaiseSelf()
            if self.visual_mode:
                #self.quit_visual_mode_state()
                #KeyRelease('left shift')
                pass
            if Key in ('delete','backspace',):
                if EvtType == 'key up': return True
                if self.indicator.GetText() == '':
                    self.command = ""
                    self.commanding = False
                    self.expression = False
                    self.indicator.StateReset()
                    self.indicator.DeactiveSelf()
                    return False
                return True
            if Key in ('up','down','page up','page down'):
                if EvtType == 'key up': return False
                if self.expression:
                    if Key in ('up','page up'):
                        if self.expression_index<len(self.expressions)-1:self.expression_index+=1 
                    else:
                        if self.expression_index>0: self.expression_index -=1 
                        pass
                    self.command = self.expressions[self.expression_index]
                    self.indicator.text_input.SetValue(self.command)
                    return False
                else:
                    if Key in ('up','page up'):
                        if self.command_index<len(self.commands)-1:self.command_index+=1 
                    else:
                        if self.command_index>0: self.command_index -=1 
                        pass
                    self.command = self.commands[self.command_index]
                    self.indicator.text_input.SetValue(self.command)
                    return False

            elif Key == 'return': #single in ('xxxx') will lead to var in 'xxx'
                if EvtType == 'key up': return False
                #print('the final return ')
                if self.visual_mode:
                    #KeyPress('left shift')
                    pass
                if self.indicator.FindFocus() == self.indicator.text_input:
                    self.indicator.DeactiveSelf()
                if self.expression:
                    try:
                        self.expressions[0] = self.indicator.GetText()
                        self.command = self.expressions[0]
                        res = str( eval( self.command) )
                        # save result to "=
                        SetRegister('=',res)
                    except Exception as e:
                        res = lt('evaluation failed for: {0}',e) 
                        #self.registering = False
                        #self.register = ''
                        pass
                    self.commanding = False
                    self.command = ''
                    self.expression = False
                    self.registering = False
                    self.register = ''
                    #print('try set res=',res)
                    self.indicator.StateReset('',res)
                    pass
                else:
                    self.commands[0] = self.indicator.GetText()
                    self.command = self.commands[0]
                    #print('execute command',self.command)
                    WxCallLater(0.1,self.ProcessCommand, self.command )
                    self.commanding = False
                    self.command = ''
                    self.expression = False
                    pass
                return False
            # append to command
            return True

        #######################################################
        ### always ignore key up for none input keys
        if EvtType == 'key up':
            if self.unprocessed_other_key:
                self.unprocessed_other_key = False
                return True
            return False
        ########################################################
        ckey = Key
        if self.geekey.state_on_shift: ckey = 'shift_' + ckey
        if self.geekey.state_on_ctrl: ckey = 'ctrl_' + ckey
        if self.geekey.state_on_alt: ckey = 'alt_' + ckey
        if self.unprocessed_char:
            ckey = self.unprocessed_char + "__" + ckey 
            self.unprocessed_char = ""
            pass
        oper = GetMap('vim',ckey)
        #print('deal ckey:',ckey,'oper:',oper)

        if not oper and Key in EditKeys: return True
        
        ### record number to do repeat
        if not self.geekey.state_on_shift and not self.geekey.state_on_ctrl and Key in NumberKeys and not (self.number == '' and Key == '0'):
            if self.registering: self.registeringGet(Key)
            elif self.recording: self.recordingGet(Key)
            elif self.executing: self.executingDo(Key)
            else:
                self.number += Key
                self.registering = False
                self.recording = False
                self.indicator.StateReset()
                pass
            return False

        if self.registering: return self.registeringGet(Key) 
        elif self.recording: return self.recordingGet(Key)
        elif self.executing: return self.executingDo(Key)

        char_processed = True
        keep_number = False

        #log.log('Key = {2}, ckey = {0}, oper = {1}'.format(ckey,oper,Key) )
        if self.visual_mode: self.visual_move +=  vim_move_count.get(oper,0)
        ### record first char this turn for double chars cmd like dd, gg, et.al

        # if not self.visual_mode: geeKeyboard.coverKey('shift')
        # geeKeyboard.coverKey('alt')
        # geeKeyboard.coverKey('ctrl')
        # geeKeyboard.coverKey('cmd')

        oper_number = lambda : 1 if self.number  == '' else int(self.number)
        def home(flags=0x0):
            if INFO['CAPP'] == 'com.apple.Terminal': KeyStroke('a',M_C )
            else: KeyStroke('left',M_M|flags )
        def end(flags=0x0):
            if INFO['CAPP'] == 'com.apple.Terminal': KeyStroke('e',M_C )
            else: KeyStroke('right',M_M|flags )

        ###########################################
        ##### vim oper start 
        ###########################################

        if oper in ('left','right','up','down','return','page up','page down'):
            for i in range(oper_number() ): KeyStroke(oper, )
        elif oper in ('home','home block','home line'):
            home()
        elif oper == 'end':
            end()
            #if self.visual_mode: KeyStroke('left shift')
        ############################################################ 
        # instant return oper which keep self.number values
        elif oper == 'register':
            self.registering = True
            self.register = ''
            self.indicator.StateReset(label_extra="\"")
            keep_number = True
        elif oper == 'execute':
            self.execute = ''
            self.executing = True
            self.indicator.StateReset(label_extra="@")
            keep_number = True
        elif oper == 'command':
            self.commanding = True
            if self.commands[0]: self.commands = [''] + self.commands
            self.indicator.StateReset(":")
        elif oper == 'record':
            #print('record command',self.record,self.recording)
            if self.record: # is recording state, try stop recording
                #print('stop recording')
                res = self.geekey.endRecording()
                #print( 'vim recording res =',self.record,res )
                if res:
                    res = ":0{0}".format(res)
                    SetRegister(self.record, res, )   
                    pass
                
                self.indicator.StateReset( lt("recording {0} end",self.record) )
                self.record = ''
            else:
                #print('prepare recording')
                self.recording = True
                self.indicator.StateReset(label_extra="q")
                pass
            pass
        ############################################################ 
        elif oper == 'next word':
            for i in range(oper_number() ): KeyStroke( 'right', M_A )
        elif oper == 'end word':
            for i in range(oper_number() ): KeyStroke( 'right', M_A )
        elif oper == 'prev word':
            for i in range(oper_number() ): KeyStroke( 'left', M_A )
        elif oper == 'prev para':
            for i in range(oper_number() ): KeyStroke( 'up', M_A )
        elif oper == 'next para':
            for i in range(oper_number() ): KeyStroke( 'down', M_A )
        elif oper == 'insert':
            if not self.visual_mode:
                self.insert_mode = True
                self.indicator.StateReset()
            else:
                char_processed = False 
        elif oper == 'insert begin':
            if not self.visual_mode:
                home()
                self.insert_mode = True
                self.indicator.StateReset()
            else:
                char_processed = False 
        elif oper == 'append':
            if not self.visual_mode:
                self.insert_mode = True
                self.indicator.StateReset()
            else:
                char_processed = False 
        elif oper == 'append end':
            if not self.visual_mode:
                end()
                self.insert_mode = True
                self.indicator.StateReset()
            else:
                char_processed = False
        elif oper == 'insert prev line':
            if not self.visual_mode:
                self.insert_mode = True
                KeyStroke('up')
                end()
                KeyStroke('return')
                self.indicator.StateReset()
            else:
                char_processed = False 
            pass
        elif oper == 'insert next line':
            if not self.visual_mode:
                self.insert_mode = True
                end()
                KeyStroke('return')
                self.indicator.StateReset()
            else:
                char_processed = False 
            pass
        elif oper == 'change':
            if self.visual_mode:
                self.quit_visual_mode_state()
                KeyStroke('delete',)
            else:
                for i in range(oper_number() ): KeyStroke('delete')
            self.insert_mode = True
            self.indicator.StateReset()
            pass
        elif oper == 'change word':
            if self.visual_mode:
                self.quit_visual_mode_state()
            else:
                for i in range(oper_number() ): KeyStroke('right',M_S|M_A)
            KeyStroke('delete')
            self.insert_mode = True
            self.indicator.StateReset()
            pass
        elif oper == 'change word back': #visual or not visual 
            if self.visual_mode:
                self.quit_visual_mode_state()
            else:
                for i in range(oper_number() ): KeyStroke('left',M_S|M_A)
            KeyStroke('delete')
            self.insert_mode = True
            self.indicator.StateReset()
            pass
        elif oper == 'change line':
            if not self.visual_mode:
                home()
                end(M_S)
                for i in range(oper_number()-1 ): KeyStroke('down',M_S )
                end(M_S)
            else: self.quit_visual_mode_state()
            KeyStroke('delete')
            self.insert_mode = True
            self.indicator.StateReset()
            pass
        elif oper == 'change begin':
            if not self.visual_mode: home(M_S)
            else: self.quit_visual_mode_state()
            KeyStroke('delete')
            self.insert_mode = True
            self.indicator.StateReset()
            pass
        elif oper == 'change end':
            if not self.visual_mode: end(M_S)
            else: self.quit_visual_mode_state()
            KeyStroke('delete')
            self.insert_mode = True
            self.indicator.StateReset()

            pass
        elif oper in ('visual mode','line visual mode'):
            #log.log('visual mode')
            if not self.visual_mode:
                if oper == 'line visual mode': home()
                INFO['EVCF'] = M_S
                self.visual_mode = True
                if oper == 'line visual mode': KeyStroke('down')
                #print('into visual mode')
            else:
                self.quit_visual_mode()
                #print('quit visual mode')
                pass
            self.indicator.StateReset()
            return False
        ##########################
        ### copy part
        elif oper == 'copy' :
            if self.visual_mode:
                #print('process copy',hex(INFO['CF']&M_S) )
                self.quit_visual_mode_state()
                KeyStroke('c',M_M)
                self.setRegister('0',False,)
                WxCallLater(0.1,self.quit_visual_mode_move )
            else:
                char_processed = False 
            pass
        elif oper == 'copy word':
            for i in range(oper_number() ): KeyStroke('right',M_S|M_A)
            KeyStroke('c',M_M)
            DelayKeyStroke(0.1,'left')
            self.setRegister(False, False,)
        elif oper == 'copy word back':
            for i in range(oper_number() ): KeyStroke('left',M_S|M_A)
            KeyStroke('c',M_M)
            self.setRegister(False,False,)
            DelayKeyStroke(0.1,'right')
        elif oper == 'copy line' : # no visual mode will be here
            home()
            for i in range( oper_number() ): KeyStroke('down',M_S)
            KeyStroke('c',M_M)
            self.setRegister('0',True)
            DelayKeyStroke(0.1,'left')
        elif oper == 'copy begin':
            home(M_S)
            KeyStroke('c',M_M)
            self.setRegister('0',False)
            DelayKeyStroke(0.1,'right')
        elif oper == 'copy end':
            end(M_S)
            KeyStroke('c',M_M)
            self.setRegister('0',False)
            DelayKeyStroke(0.1,'left')
        elif oper == 'x cut' :
            #log.log('process cut')
            if self.visual_mode:
                ## extra shift will make ctrl-c not working
                self.quit_visual_mode_state() 
                KeyStroke('x',M_M)
                self.setRegister('1',False)
            else:
                for i in range(oper_number() ):
                    KeyStroke('delete')
                #self.setRegister(False,False)
                pass
        elif oper == 'x cut previous' :
            #log.log('process cut')
            if self.visual_mode:
                ## extra shift will make ctrl-c not working
                self.quit_visual_mode_state() 
                KeyStroke('x',M_M)
                self.setRegister('1',False)
            else:
                for i in range(oper_number() ):
                    KeyStroke('backspace')
                #self.setRegister(False,False)
        elif oper == 'cut':
            if self.visual_mode:
                self.quit_visual_mode_state() 
                KeyStroke('x',M_M)
                self.setRegister('1',False)
            else:
                char_processed = False 
        elif oper == 'cut line':  # visual mode will processed by cut
            home()
            for i in range( oper_number() ): KeyStroke('down',M_S)
            KeyStroke('x',M_M)
            self.setRegister('1',True)
        elif oper == 'cut begin': 
            home(M_S)
            KeyStroke('x',M_M)
            self.setRegister('1',False)
        elif oper == 'cut end': 
            end(M_S)
            KeyStroke('x',M_M)
            self.setRegister('1',False)
        elif oper == 'cut word': 
            for i in range( oper_number() ): KeyStroke('right',M_A|M_S)
            KeyStroke('x',M_M)
            self.setRegister(False,False)
        elif oper == 'cut word back':
            for i in range( oper_number() ): KeyStroke('left',M_A|M_S)
            KeyStroke('x',M_M)
            self.setRegister(False,False)
        #######################
        # paste part
        elif oper == 'paste' :
            if self.getRegister():
                if self.line_cut: # paste to a single line
                    for i in range(oper_number() ):
                        end()
                        KeyStroke('v',M_M)
                    pass
                else:
                    for i in range(oper_number() ): KeyStroke('v',M_M)
                pass
        elif oper == 'paste prev':
            if self.getRegister():
                if self.line_cut: # paste to a single line
                    for i in range(oper_number() ):
                        home()
                        KeyStroke('v',M_M)
                else:
                    for i in range(oper_number() ): KeyStroke('v',M_M)
                pass
        elif oper == 'undo' : KeyStroke('z',M_M)
        elif oper == 'redo' : KeyStroke('z',M_M|M_S)
        elif oper == 'merge line':
            KeyStroke('e',M_C)
            KeyStroke('delete')
        elif oper == 'find' :
            if self.visual_mode: # the same as d cut
                self.quit_visual_mode_state() 
                KeyStroke('c',M_M); KeyStroke('f',M_M); KeyStroke('v',M_M)
                self.insert_mode = True
            else:
                KeyStroke('f',M_M)
                self.insert_mode = True
        elif oper == 'find current':
            if self.visual_mode: # the same as d cut
                self.quit_visual_mode_state() 
                KeyStroke('c',M_M); KeyStroke('f',M_M); KeyStroke('v',M_M)
                self.insert_mode = True
            else:
                KeyStroke('right',M_A|M_S)
                KeyStroke('c',M_M); KeyStroke('f',M_M); KeyStroke('v',M_M)
                self.insert_mode = True
            pass
        elif oper in ('jump head','jump tail') :
            if self.number == '': # jump to buffer end
                if oper == 'jump head': KeyStroke('up',M_M)
                else: KeyStroke('down',M_M)
            else:
                KeyStroke('up',M_M)
                for i in range(oper_number()-1 ): KeyStroke('down')
            pass
        elif oper == 'save': KeyStroke('s',M_M)
        elif oper == 'jump bar':
            home()
            for i in range(oper_number()-1 ): KeyStroke('right')
        elif oper == 'roll page down':
            
            pass
        elif oper == 'roll page up':
            pass

        elif oper == 'caret center':
            KeyStroke('l',M_C)
            pass

        ###########################################
        ##### vim oper end
        ###########################################
        else: #others 
            if not self.visual_mode:
                #log.log('try test vim map for',ckey)
                #log.log(mapvalue)
                if oper:
                    mapvalue = oper.split(':')

                    if len(mapvalue)>=3:
                        try:
                            #log.log( lt('cmd "{0}" processed by self-defined macro',ckey) )
                            name = mapvalue[0]
                            oper = name
                            ratio = toFloat(mapvalue[1],1.0 )
                            mapvalue = map(lambda v: v.split('~'), mapvalue[2:] )  
                            sequence =  list(mapvalue) * oper_number()
                            #log.log('macro sequence is',sequence)
                            self.number = ''
                            self.geekey.Replay(ratio, sequence)
                            return False
                        except Exception as e:
                            self.geekey.Log("self-defined command {0} failed for: {1}".format(oper,e) )
                            self.indicator.StateReset( lt('command {0} failed',oper) )
                            DE()
                            pass
                        pass
                    else:
                        self.geekey.Log("Command {0} not processed".format(oper) )
                        self.indicator.StateReset( lt('Command not processed')+": "+oper )
                    pass
                else:
                    char_processed = False 
                    pass
            else:
                #log.log('key {0} oper {1} not processed'.format(ckey, oper) )
                char_processed = False 

        # if not self.visual_mode: geeKeyboard.recoverKey('shift')
        # geeKeyboard.recoverKey('alt')
        # geeKeyboard.recoverKey('ctrl')
        # geeKeyboard.recoverKey('cmd')

        ### record unprocessed Key for 
        if char_processed: # processed
            if not keep_number:
                self.number = ''
                if not self.visual_mode: self.indicator.StateReset()
            return False

        if potentialKeyOfDict(ckey,GlobalMaps['vim'] ):
            self.unprocessed_char = ckey
            return False

        if Key in FunctionKeys or self.geekey.state_on_ctrl or self.geekey.state_on_alt or self.geekey.state_on_cmd:
            ### pass on current keyboard event
            self.unprocessed_char = ''
            self.number = ''
            self.unprocessed_other_key = True
            return True 

        # what left are all unprocessed ckey
        self.indicator.StateReset(lt("command {0} not found.",ckey ),' ')
        log.log( lt('command {0} not found. You can bind your own operation to vim_map_{0}:: item in default.ini',ckey) )
        self.unprocessed_char = ''
        self.number = ''
        self.unprocessed_other_key = True
        return False

    # n == 0: current to end
    # n == -N: current to end - n 
    # n > 0:  current to someplace
    def do_replace(self,pattern,string,flags): #
        ori_txt = getCbText()
        flag = re.M|re.S|re.U
        count = 0
        if not 'g' in flags: count = 1
        if 'i' in flags: flag = flag|re.I
        #print('ori txt =',ori_txt)
        if count:
            strings = ori_txt.split('\n')
            #print('do seperate to',strings)
            new_txt='\n'.join([re.sub(pattern,string,s,count=count,flags=flag)for s in strings])
            pass
        else:
            new_txt = re.sub(pattern,string,ori_txt,count=count,flags=flag)
            pass
        #print('new txt',[new_txt,type(new_txt)] )
        #print('do replace with',pattern,string,flags,[ori_txt,new_txt] )
        #print(ori_txt == new_txt)
        #self.getRegister(new_txt)
        setCbText( str(new_txt) )
        #KeyStroke('left',M_M)
        KeyStroke('v',M_M)
        self.indicator.StateReset( lt('substitution done') )
        return 
        
    def ProcessCommand(self,command):
        command = command.strip()
        if not command: return
        # check if substitute command s/

        items = re.split(r'(?<!\\)#',command)
        if not( len(items) == 4 and items[0][-1] == 's'): items = re.split(r'(?<!\\)/',command)
        if len(items) == 4 and items[0][-1] == 's': # a sub command 'xxs/xx/yy/zz'
            #print('try do substitute')
            try:
                pattern = items[1]
                string = items[2]
                flags = items[3] # only support 'gi' or empty
                if 'c' in flags:  raise Exception(("flag 'c' is not supported"))

                if self.visual_mode:
                    self.quit_visual_mode_state()
                    KeyStroke('x',M_M)
                else:
                    scope = items[0][:-1]
                    if scope == '%':
                        start = [1,0]
                        end = ['$',0] 
                    elif scope == '':
                        start = ['.',0]
                        end = ['.',0]
                    else:
                        ss = scope.split(',')
                        if len(ss) > 2:
                            raise Exception(lt("Invalid search scope {0}",scope))
                        start = vim_search_scope(ss[0] )
                        if not start: raise Exception(("Invalid search scope {0}",scope))
                        if len( ss ) == 1: end = start
                        else: end = vim_search_scope(ss[1] )
                        if not end: raise Exception(("Invalid search scope {0}",scope))
                        #print(start,end)
                        if start[0] == '': start[0] = '.'
                        if end[0] == '': end[0] = '.'
                        pass
                    #print(start,end)

                    # step 1 get range txt
                    #SetKeyDelay( 0 )
                    if type(start[0])  == int and type(end[0]) == int:
                        s = start[0] + start[1]
                        e = end[0] + end[1]
                        if s>e:
                            raise Exception(("Invalid search scope {0}",scope))
                        KeyStroke('up',M_M)
                        for i in range(s-1): KeyStroke('down')
                        KeyStroke('left',M_M)
                        for i in range(e-s+1): KeyStroke('down',M_S)

                        KeyStroke('x',M_M)

                    elif type(start[0])  == int and end[0] == '$':
                        KeyStroke('up',M_M)
                        s = start[0]+start[1]
                        for i in range(s-1): KeyStroke('down')
                        KeyStroke('left',M_M)

                        KeyStroke('down',M_M|M_S)
                        for i in range(-end[1]): KeyStroke('up',M_S)
                        KeyStroke('right',M_M|M_S)
                        KeyStroke('x',M_M)

                    elif type(start[0]) == int and end[0] == '.':
                        #print('top to current')
                        for i in range( -end[1] ): KeyStroke('up')
                        for i in range( end[1] ): KeyStroke('down')
                        KeyStroke('right',M_M)

                        KeyStroke('up',M_M|M_S)
                        s = start[0]+start[1]
                        for i in range(s-1): KeyStroke('down',M_S)
                        KeyStroke('left',M_M|M_S)
                        KeyStroke('x',M_M)

                    elif start[0] == '.' and end[0] == '$':
                        #print('current to tail')
                        for i in range( -start[1] ): KeyStroke('up')
                        for i in range( start[1] ): KeyStroke('down')
                        KeyStroke('left',M_M)

                        KeyStroke('down',M_M|M_S)
                        for i in range(-end[1]): KeyStroke('up',M_S)
                        KeyStroke('right',M_M|M_S)
                        KeyStroke('x',M_M)

                    elif start[0] == '.' and type(end[0]) == int:
                        #print('current to tail')
                        for i in range( -start[1] ): KeyStroke('up')
                        for i in range( start[1] ): KeyStroke('down')
                        KeyStroke('left',M_M)
                        KeyStroke('up',M_M|M_S)

                        e = end[0]+end[1]
                        for i in range(e): KeyStroke('down',M_S)
                        KeyStroke('right',M_M|M_S)
                        KeyStroke('x',M_M)

                    elif start[0] == '.' and end[0] == '.':
                        #print('around to current')
                        if start[1] > end[1]: raise Exception(("Invalid search scope {0}",scope))
                        for i in range( -start[1] ): KeyStroke('up')
                        for i in range( start[1] ): KeyStroke('down')
                        KeyPress('left',M_M)

                        n = end[1] - start[1] + 1
                        for i in range(n): KeyStroke('down',M_S)
                        KeyStroke('right',M_M|M_S)
                        KeyStroke('x',M_M)

                    pass
                WxCallLater(0.1,self.do_replace,pattern,string,flags) 
            except Exception as e:
                self.indicator.StateReset(lt('substitude failed for: {0}',e))
                DE()
                pass
            return False

        cmds = command.split()
        if cmds[0] == 'reg' or cmds[0] == 'register': 
            cont = "--"+lt('Registers')+"--\n\n"
            cont += "\"{0}    {1}\n".format('"',escape(getCbText()[:55] ) )
            for (key,value) in sorted( GlobalMaps['vim_register'].items() ) :
                #print(key,value)
                if key and value:
                    cont += "\"{0}    {1}\n".format(key, escape(value[:55])  )
                    pass
                pass
            self.indicator.StateReset(cont)
            pass
        elif cmds[0] == 'w':
            KeyStroke('s',M_M)
            self.indicator.StateReset(lt('save') )
            pass
        else:
            cont = GetMap('vim_cmd',command )
            if cont: 
                mapvalue = cont.split(':') # :0:_x~0.1:x~0.2
                if len(mapvalue)>=3:
                    try:
                        ratio = toFloat(mapvalue[1],-1)
                        if ratio < 0: return False
                        mapvalue = map(lambda v: v.split('~'), mapvalue[2:] )  
                        oper_number = lambda : 1 if self.number  == '' else int(self.number)
                        sequence =  list(mapvalue) * oper_number()
                        self.number = ''
                        self.geekey.Replay(ratio, sequence)
                        self.indicator.StateReset(lt('{0} done',command ))

                    except Exception as e:
                        self.geekey.Log("command {0} failed for: {1}".format(command ,e ) )
                        self.indicator.StateReset( lt('execute {0} failed',command ))
                        DE()
                        pass
                    pass
                pass
            else:
                self.indicator.StateReset(lt("command {0} not found.",command ) )
                log.log(lt("command {0} not found. You can bind your own operation to vim_cmd_map_{0} item in default.ini",command) )
                pass
            return False

        return False
    pass



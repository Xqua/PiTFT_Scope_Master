from kivy.config import Config
try:
    import RPi.GPIO as GPIO
    Config.set('graphics', 'fullscreen', 1)
    Config.set('graphics', 'borderless', 1)
    Config.set('graphics', 'show_cursor', 0)
    Config.set('graphics', 'resizable', 0)
    GPIO.setmode(GPIO.BOARD)
    lumar = 13
    axio = 15
    pir = 11
    GPIO.setup(pir, GPIO.IN, GPIO.PUD_DOWN)
    GPIO.setup(lumar, GPIO.OUT)
    GPIO.setup(axio, GPIO.OUT)
    PI = True
    print "GPIO READY"
except:
    Config.set('graphics', 'width', '320')
    Config.set('graphics', 'height', '240')
    PI = False
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.uix.dropdown import DropDown
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.base import runTouchApp
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from slacker import Slacker

slack = Slacker('xoxb-16330556231-3F73A8ZxhFBcA20j1p3kN03M')

globalvars = {}

userlist = []
f = open('userlist')
lines = f.readlines()
for l in lines:
    userlist.append(l.strip())
f.close()

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        print "test"
        self.dropdowncreated=False

    def createDropdown(self):
        # print "test"
        if not self.dropdowncreated:
            b = Button()
            print b.events()
            print self.ids
            chooseuser = self.ids.chooseuser
            dropdown = DropDown()
            chooseuser.bind(on_release=dropdown.open)
            for user in userlist:
                btn = Button(text='%s' % user, size_hint_y=None, height=20)
                btn.bind(on_release=lambda btn: dropdown.select(btn.text))
                dropdown.add_widget(btn)
            dropdown.bind(on_select=lambda instance, x: setattr(chooseuser, 'text', x))
            chooseuser.bind(on_press=dropdown.open)
            # chooseuser.unbind(on_press)
            self.dropdowncreated = True

    def reset(self):
        self.ids.chooseuser.text = "Select User"
        globalvars['user'] = ''

    def login(self):
        # print btn
        print "click login"
        print self.ids.chooseuser.text
        if self.ids.chooseuser.text != "Select User":
            self.manager.current = 'select'
            globalvars['user'] = self.ids.chooseuser.text
        else:
            self.ids.messagebar.text = "Select a User first !"

class ScopeScreen(Screen):
    
    def on_enter(self):
        self.ids.messagebar.text = "Logged in as: %s" % globalvars['user']

    def lumar(self):
        globalvars['scope'] = 'Lumar'
        if globalvars.has_key(globalvars['scope']):
            if not globalvars[globalvars['scope']]['state']:
                print "resest"
                globalvars[globalvars['scope']]['dt'] = 3600
                globalvars[globalvars['scope']]['user'] = str(globalvars['user'])
        else:
            globalvars[globalvars['scope']] = {
            'state':False,
            'user':str(globalvars['user']),
            'dt':3600
            }

    def axio(self):
        globalvars['scope'] = 'AxioImager'
        if globalvars.has_key(globalvars['scope']):
            if not globalvars[globalvars['scope']]['state']:
                print "resest"
                print globalvars
                globalvars[globalvars['scope']]['dt'] = 3600
                globalvars[globalvars['scope']]['user'] = str(globalvars['user'])
        else:
            globalvars[globalvars['scope']] = {
            'state':False,
            'user':str(globalvars['user']),
            'dt':3600
            }

class ScopeLoopLumar(Screen):
    
    def start(self):
        self.ids.title.text = 'Lumar'
        self.ids.messagebar.text = "Logged in as: %s\nScope used by %s" % (globalvars['user'], globalvars['Lumar']['user'])
        print globalvars
        self.ON = globalvars['Lumar']['state']
        print globalvars['Lumar']['dt'], self.ON
        self.ALERT = False
        if self.ON:
            self.ids.off.background_color = (1.0, 1.0, 1.0, 1.0)
            self.ids.on.background_color = (0.0, 1.0, 0.0, 1.0)
        else:
            self.ids.on.background_color = (1.0, 1.0, 1.0, 1.0)
            self.ids.off.background_color = (1.0, 0.0, 0.0, 1.0)
        self.ids.timer.text = self.t2str()

    def stop(self):
        globalvars['Lumar']['state'] = self.ON

    def on(self):
        self.ids.on.background_color = (0.0, 1.0, 0.0, 1.0)
        self.ids.off.background_color = (1.0, 1.0, 1.0, 1.0)
        self.ids.timer.color = (1.0, 0.0, 0.0, 1.0)
        self.ON = True
        #DO GPIO STUFF HERE
        if PI:
            print "LUMAR",lumar
            print "LUMAR ON"
            GPIO.output(lumar, GPIO.HIGH)
        Clock.schedule_interval(self.updateTime, 1)
        

    def off(self):
        self.ids.off.background_color = (1.0, 0.0, 0.0, 1.0)
        self.ids.on.background_color = (1.0, 1.0, 1.0, 1.0)
        self.ON = False
        globalvars['Lumar']['dt'] = 3600
        self.ids.timer.text = "01:00:00"
        self.ids.timer.color = (1.0, 1.0, 1.0, 1.0)
        self.ALERT = False
        #DO GPIO STUFF HERE
        if PI:
            print "LUMAR",lumar
            print "LUMAR OFF"
            GPIO.output(lumar, GPIO.LOW)
        Clock.unschedule(self.updateTime)

    def hour(self):
        globalvars['Lumar']['dt'] += 3600
        self.ids.timer.text = self.t2str()

    def minute(self):
        globalvars['Lumar']['dt'] += 900
        self.ids.timer.text = self.t2str()

    def ChkMovement(self):
        if PI:
            state = GPIO.input(pir)
            print "Movement state is:", state
            if not state:
                return False
            else:
                print "MOVEMENT"
                return True
        else:
            return False

    def t2str(self):
        h = globalvars['Lumar']['dt'] / 60 / 60
        mn = (globalvars['Lumar']['dt'] / 60) - (h * 60)
        s = (globalvars['Lumar']['dt'] - (h * 3600) - (mn * 60))
        h  = str(h)
        while len(h) < 2:
            h = '0' + h
        mn  = str(mn)
        while len(mn) < 2:
            mn = '0' + mn
        s  = str(s)
        while len(s) < 2:
            s = '0' + s
        return "%s:%s:%s" % (h, mn, s)

    def updateTime(self, dt):
        print dt, globalvars['Lumar']['dt']
        globalvars['Lumar']['dt'] -= 1
        if globalvars['Lumar']['dt'] < 900 and not self.ALERT:
            self.alert()
        if globalvars['Lumar']['dt'] < 0:
            self.off()
            self.alert2()
        if self.ChkMovement():
            globalvars['Lumar']['dt'] = 3600
        self.ids.timer.text = self.t2str()

    def alert(self):
        self.ALERT = True
        slack.chat.post_message('#testrobots', 'The scope %s used by %s has been left ON and will be turned OFF in 15 min !' % (globalvars['scope'], globalvars['user']), as_user=True)
        print "ALARM"

    def alert2(self):
        slack.chat.post_message('#testrobots', 'The scope %s used by %s has been turned OFF' % (globalvars['scope'], globalvars['user']), as_user=True)
        print "ALARM"

class ScopeLoopAxio(Screen):
    
    def start(self):
        self.ids.title.text = 'AxioImager'
        self.ids.messagebar.text = "Logged in as: %s\nScope used by %s" % (globalvars['user'], globalvars['AxioImager']['user'])
        print globalvars
        self.ON = globalvars['AxioImager']['state']
        print globalvars['AxioImager']['dt'], self.ON
        self.ALERT = False
        if self.ON:
            self.ids.off.background_color = (1.0, 1.0, 1.0, 1.0)
            self.ids.on.background_color = (0.0, 1.0, 0.0, 1.0)
        else:
            self.ids.on.background_color = (1.0, 1.0, 1.0, 1.0)
            self.ids.off.background_color = (1.0, 0.0, 0.0, 1.0)
        self.ids.timer.text = self.t2str()

    def stop(self):
        globalvars['AxioImager']['state'] = self.ON

    def on(self):
        self.ids.on.background_color = (0.0, 1.0, 0.0, 1.0)
        self.ids.off.background_color = (1.0, 1.0, 1.0, 1.0)
        self.ids.timer.color = (1.0, 0.0, 0.0, 1.0)
        self.ON = True
        #DO GPIO STUFF HERE
        if PI:
            print "axio=",axio
            print "AXIO ON"
            GPIO.output(axio, GPIO.HIGH)
        Clock.schedule_interval(self.updateTime, 1)
        

    def off(self):
        self.ids.off.background_color = (1.0, 0.0, 0.0, 1.0)
        self.ids.on.background_color = (1.0, 1.0, 1.0, 1.0)
        self.ON = False
        globalvars['AxioImager']['dt'] = 3600
        self.ids.timer.text = "01:00:00"
        self.ids.timer.color = (1.0, 1.0, 1.0, 1.0)
        self.ALERT = False
        #DO GPIO STUFF HERE
        if PI:
            print "axio=",axio
            print "AXIO OFF"
            GPIO.output(axio, GPIO.LOW)
        Clock.unschedule(self.updateTime)

    def hour(self):
        globalvars['AxioImager']['dt'] += 3600
        self.ids.timer.text = self.t2str()

    def minute(self):
        globalvars['AxioImager']['dt'] += 900
        self.ids.timer.text = self.t2str()

    def ChkMovement(self):
        if PI:
            state = GPIO.input(pir)
            print "Movement state is:", state
            if not state:
                return False
            else:
                print "MOVEMENT"
                return True
        else:
            return False

    def t2str(self):
        h = globalvars['AxioImager']['dt'] / 60 / 60
        mn = (globalvars['AxioImager']['dt'] / 60) - (h * 60)
        s = (globalvars['AxioImager']['dt'] - (h * 3600) - (mn * 60))
        h  = str(h)
        while len(h) < 2:
            h = '0' + h
        mn  = str(mn)
        while len(mn) < 2:
            mn = '0' + mn
        s  = str(s)
        while len(s) < 2:
            s = '0' + s
        return "%s:%s:%s" % (h, mn, s)

    def updateTime(self, dt):
        print dt, globalvars['AxioImager']['dt']
        globalvars['AxioImager']['dt'] -= 1
        if globalvars['AxioImager']['dt'] < 900 and not self.ALERT:
            self.alert()
        if globalvars['AxioImager']['dt'] < 0:
            self.off()
            self.alert2()
        if self.ChkMovement():
            globalvars['AxioImager']['dt'] = 3600
        self.ids.timer.text = self.t2str()

    def alert(self):
        self.ALERT = True
        slack.chat.post_message('#testrobots', 'The scope %s used by %s has been left ON and will be turned OFF in 15 min !' % (globalvars['scope'], globalvars['user']), as_user=True)
        print "ALARM"

    def alert2(self):
        slack.chat.post_message('#testrobots', 'The scope %s used by %s has been turned OFF' % (globalvars['scope'], globalvars['user']), as_user=True)
        print "ALARM"

class MainScreen(ScreenManager):
    pass

root_widget = Builder.load_file('main.kv')


class MainApp(App):

    def build(self):
        return root_widget

if __name__ == '__main__':
    MainApp().run()
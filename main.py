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

    def axio(self):
        globalvars['scope'] = 'AxioImager'


class ScopeLoop(Screen):
    
    def start(self):
        self.ids.title.text = globalvars['scope']
        self.ids.messagebar.text = "Logged in as: %s" % globalvars['user']
        self.time = 3600
        self.ON = False
        self.ALERT = False
        self.ids.on.background_color = (1.0, 1.0, 1.0, 1.0)
        self.ids.off.background_color = (1.0, 0.0, 0.0, 1.0)
        self.ids.timer.text = self.t2str()

    def stop(self):
        Clock.unschedule(self.updateTime)

    def on(self):
        self.ids.on.background_color = (0.0, 1.0, 0.0, 1.0)
        self.ids.off.background_color = (1.0, 1.0, 1.0, 1.0)
        self.ids.timer.color = (1.0, 0.0, 0.0, 1.0)
        self.ON = True
        #DO GPIO STUFF HERE
        if PI:
            if globalvars['scope'] == 'Lumar':
                print "LUMAR",lumar
                print "LUMAR ON"
                GPIO.output(lumar, GPIO.HIGH)
            elif globalvars['scope'] == 'AxioImager':
                print "axio=",axio
                print "AXIO ON"
                GPIO.output(axio, GPIO.HIGH)
        Clock.schedule_interval(self.updateTime, 1)
        

    def off(self):
        self.ids.off.background_color = (1.0, 0.0, 0.0, 1.0)
        self.ids.on.background_color = (1.0, 1.0, 1.0, 1.0)
        self.ids.timer.color = (1.0, 1.0, 1.0, 1.0)
        self.ON = False
        self.time = 3600
        self.ids.timer.text = "01:00:00"
        self.ALERT = False
        #DO GPIO STUFF HERE
        if PI:
            if globalvars['scope'] == 'Lumar':
                print "LUMAR",lumar
                print "LUMAR OFF"
                GPIO.output(lumar, GPIO.LOW)
            elif globalvars['scope'] == 'AxioImager':
                print "axio=",axio
                print "AXIO OFF"
                GPIO.output(axio, GPIO.LOW)
        Clock.unschedule(self.updateTime)

    def hour(self):
        self.time += 3600
        self.ids.timer.text = self.t2str()

    def minute(self):
        self.time += 900
        self.ids.timer.text = self.t2str()

    def ChkMovement(self):
        state = GPIO.input(pir)
        print "Movement state is:", state
        if not state:
            return False
        else:
            print "MOVEMENT"
            return True

    def t2str(self):
        h = self.time / 60 / 60
        mn = (self.time / 60) - (h * 60)
        s = (self.time - (h * 3600) - (mn * 60))
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
        print dt, self.time
        if not self.ON:
            if self.ChkMovement():
                self.time = 3600
                self.ids.timer.text = "01:00:00"
        else:
            self.time -= 1
            if self.time < 900 and not self.ALERT:
                self.alert()
            if self.time < 0:
                self.off()
                self.alert2()
            if self.ChkMovement():
                print "chkMovement", self.chkMovement
                self.time = 3600
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
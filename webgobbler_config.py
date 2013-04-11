#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
'''
webGobbler configuration GUI 1.2.8


Note: this configuration GUI is still kept outside the main webgobbler code
      so that webGobbler core is not polluted with Tkinter/GUI stuff.

'''

# Single-file executable:
# http://homepage.hispeed.ch/py430/python/index.html
# http://starship.python.net/crew/theller/moin.cgi/SingleFileExecutable
# pyco page is dead ?

# Stub for fractint screensaver:
# http://home.online.no/~thbernt/fintscrn.htm

try:
    import Pmw
except ImportError:
    raise ImportError, "The Pmw (Python Megawidgets) module is required for the webGobbler configuration GUI. See http://pmw.sourceforge.net/"

import os, os.path
import hashlib

if os.path.isdir('libtcltk84'):
    os.environ['TCL_LIBRARY'] = 'libtcltk84\\tcl8.4'
    os.environ['TK_LIBRARY'] =  'libtcltk84\\tk8.4'
    
import Tkinter
import tkFont
import tkFileDialog

try:
    import webgobbler   # We import the webGobbler module.
except ImportError:
    raise ImportError, "The webGobbler module is required to run this webGobbler configuration GUI. See http://sebsauvage.net/python/webgobbler/"

try:
    import Image
    import ImageTk
    import tkSimpleDialog
except ImportError:
  raise ImportError, "The PIL (Python Imaging Library) is required to run this program. See http://www.pythonware.com/products/pil/"

import StringIO, base64 


def main():
    root = Tkinter.Tk()             # Initialize Tkinter
    root.withdraw()                 # Hide the main root window
    Pmw.initialise(root)            # Initialize Pmw
    wgconfig = wg_confGUI(root)     # Build the GUI.
    root.wait_window(wgconfig.top)  # Wait for configuration window to close.

# FIXME: allow to choose where to save to/load from ? (combo with .ini file/registry ?)


class wg_confGUI(Tkinter.Toplevel):  # FIXME: Should I derive from Frame so that I can be included ?
    '''
    Example:
        root = Tkinter.Tk()             # Initialize Tkinter
        root.withdraw()                 # Hide the main root window
        Pmw.initialise(root)            # Initialize Pmw
        wgconfig = wg_confGUI(root)     # Build the GUI.
        root.wait_window(wgconfig.top)  # Wait for configuration window to close.

    Example 2:
        import webgobbler_config       
        wgconfig = webgobbler_config.wg_confGUI(None)
        wgconfig.focus_set()        
        self._parent.wait_window(wgconfig.top)  # Wait for window to close.
    '''
    def __init__(self,parent):
        Tkinter.Toplevel.__init__(self, parent)
        self.top = self
        # the following dictionnary will keep a refenrece to all the widgets/variables
        # we need to read/write information from/to.
        self._widgets = {}  # References to tkinter widgets and tkinter variables       
        self._widgets_group = {}  # We group some widgets to enable/disable them by group.
        self.config = None  #  The webGobbler configuration (an wg.applicationConfig object)
        self.configSource = None  # Configuration source ('registry','inifile' or 'default')
        self.configChanged = False   # Tells if the user has changed the configuration

        self._setICONS()
        self._initializeGUI()
        self.loadConfig()   # Automatically load current webGobbler configuration into the GUI.
        if not self.configSource in ('registry','inifile'):
            Pmw.MessageDialog(self.top,title = 'Configuration loaded',message_text="Configuration could not be read from registry or .ini file.\nConfiguration was loaded with default values.",iconpos='w',icon_bitmap='warning')
        
    def _setICONS(self):
        ''' Here are all the icons used by the GUI '''
        # Yeah... I know it's bad to have base64 data in code. Sue me.
        self._ICONS = {'normal': Tkinter.PhotoImage(master=self.top,data="""
R0lGODlhIAAgAIUAAQBygwBzhQJ3iXtygx7DRxzDSxrFVxfIb2SFME+XNwqClACTqimVpQC30hLN
jAzSsQXO0ADe/wHe/gHd/ATd+wLY8wDN7Bfg/zXk/zjlxmCnsX+4wGbqmFLo9nft/7k8Fbg8RrBE
T7FCQcA2E/8AAP8EB/8FCP8cLv80VP9rrv92wKTyWv//APn+Bff9CP//F834Moi9xZnGzaTy/ovv
yv+P6f+c/f+X9v+A0P//rP//m///0f//////++/7983v9CwAAAAAIAAgAAUG/sCIcEgsGiMUinAi
aTaP0CIH1mrBOEmnJHpMRlassBhG0XKNSY547eKYz8Ska71ulZ/w4SRDp2ecZxQYHR6FNC99Ly0s
f3hHGDM+PJOUPTmILC87PD07HYBHF5KUpJM7iDmkPkpRHaWvPDs6rzNcFDOwuZM9PD9nDTK6sD4y
AhZcDQAMGhoxMjIxGxvMGgwMAgAAAQALW0dNydni49vj2gIN3kZOFgoK5eUCAu4KCwsNDRWORW8R
FRYWKkyIc2GCQS0I92kxmCeChAEhIkqcOMAJwzwSQpDYSKIEx40gHKrDqJFEDRsoUZ4gEXIfnIwe
T+JIQXMlCFDrcDoseRIFhwkTHFuOJNJv58aTKmimAOlw4DedDkQcRXmj6kYRTZRUeODggIECBw48
gFCkwIepKEyoBSmhAoQDBQjInRuXgFh9EsyiBeqRhIgHBgjUnUuY7oO8Z01StXHD5wi6gwsTBquX
RAoVmDGvfCy5M92viT+W6MvZs+kCCRCoXs06genXsGPLnj07CAA7
"""),
'emboss':Tkinter.PhotoImage(master=self.top,data="""
R0lGODlhIAAgAIYAAU5wdEx8hFR+hCTqVSTqZGS+dEzObFTHbFzCc1vCfCTwlBLL8wT+/Bb+/DnO
5DTe/Dzc8jze/CzR9Dri9i3w+DzA1FeEilaMlEyntmqqslSYpEy7ylzChU/OkFHKsnzWrEvH2VbP
0krO5EzS5ETS5EzS9EzW90TX+1fT5FTO5GzZ2LF3XLR2fNwzM/wbOuQnJPkoMPwnSPY+SdpJR9xO
V9ZXVulPU+RSbtxCNOR0jpGTYeznFujmNNTiJNjkVMjqaOTmSuzmTOTmXLzefJSUnI6OlImYpJ6n
rJzklJTc5rTP0uSKtOik2eS39e6t7OSa1NzitOTmkdDT0tTe4NHk5uTM++TS/OTm1+Tm5Ozm5Pbs
6fny6vz+/Pz29Nzm3Jy+xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACwA
AAAAIAAgAAYH/oAMgoOEhYaHhRQPEQ8Qi42PjowQEw8qSD8+SCgLCxIPFIIRIiOlpqemKSkoP0A+
QkCuSJ2Mgg+kqLmlKEM8sb8+PyGeD4IQuqcOyg4hO0HPwMGeEg0MD6glpSTKFZ4LHTs8PEG/4kAg
nqKl2abbCyAjKPIfPDvhPrHiPR7p1rkpKpJQmUKloJeDQuzxEHLlChYoG/odQ6VCi5YsWDJqvJIF
ij0oDq8Q7GQrV5ItWy5qxMKxIZQoGjFSUbFA3Sl5Wbpw6YLSos+UPrWg5EIllL8R7EqkyCCFi9On
UHXufEolg9GJp0JgAEBEiZQpGadMkaJEyZezGTSo1VChJCoR/iK2AgBg4YLduxbyWqAboG9bBhNQ
oUgBAoTcuYgR9617QQOGDcWsRZhAmRLlyiRCbNi8uTCIDZ4Li4hgjAKFag1Sq059DG4KdiNMkCKV
DYKgIiyIGCnCu3eGEA0mlMCly4Qp2wxqwMBBo4XzF85nGAmOAlku0gxowLBRpQkTJk2cyJhRpAHW
UsaRIdfOvcmSJ/Br0CASPGmqU7iws+9O44X/FzPQF1gpIJRQggkHJshOZDds190SOSxxA4ACxlbC
CRhiGEGGJ5hgQjEKNGiDFU08UQWJNtAw3QQmnJBNCB50wIEHHoxwAgQYFkPADC6M2IQNLdgApA30
UYCCBxxwopDAkggkkOSMKTjCwAAzxOCjDTD8h4MOFMhYQAJNIhBmmE52YBuVPVpBYnhMAKmDAh0g
wIGYCHxZQJ11gplABwqgaQMTTgQa6A02rKDAnHmOqaeYdx4wwAA4uOBCDJRWKmkNHRyg55125vml
mAY8qsMKpJZqqg6f3rmoonk6OoABCBxQgKYH0BnrAQbgesCuuCagqwEGJADso8QWa+yxyB4bCAA7
"""),
'invert':Tkinter.PhotoImage(master=self.top,data="""
R0lGODlhIAAgAIUAAQAAAAAABA8EBwAALjIQCwAAUgAAZABiAQBoCQBwFgB/L1sNAGU4MXQQNXdC
OgAA5wAA/wUB+QgC9zIHzVoMpACIPgCTUADKqgD//wD7+AD69z/J7ADj0U+7sE69vkfCuEbD6ogS
AKwWCJgUZoBHP55YTcoaAOgeAP8hAP4hAf0hA/ohBPwmC/8yE/kwLsYaOOwycvItTv5ILP9rVPR8
atVpWZt6z7BnyOg2kOE8uOI7s+Q6qIONe/+NfP+Lef2HdSwAAAAAIAAgAAUG/kCUcEgsGlGrlVCV
ajaP0OJoEolMRklnKnpMoiiQsHiy0nKNyZF4LRmZz8SkZL2OlJ/woepFp7+cZysmIiGFDQ99DxEQ
f3hHJgsCAJOUAQWIEA8DAAEDIoBHJ5KUpJMDiAWkAkpRIqWvAAMGrwtcKwuwuZMBAARnMgy6sAIM
Py1cMj01JSUODAwODszMNTU/PT0+PTNbR03J2OHY2tri2T8y3UZOLTQ05eU/P+40MzMyMiyORW8o
LC0tvAxZcUKFQVBc+qHQwhAQjw4QI0rkgXBhQ4YoOmDYiEEDx40fLBK5iFEjhgQHUqbkgCHkPpJm
OnhEqcCCTZYfQDUcCcgkg8oLGDJwzIln55CYG1HatAkSIcajTmB4SKoSAYKmT1jEgIFjhw4cOGK4
YKgDBNULGtJu9JBixVYdOeLKlRt2hQoUZc96HBpjx9y/f3XEwGsWAwKVKYFuAMx47te8GGzWrFCB
5eLGjHVozlH448fLmBvruGGjtOnTN0Jjhqu6tevXrYMAADs="""),
'mirror':Tkinter.PhotoImage(master=self.top,data="""
R0lGODlhIAAgAIUAAQBygwBzhQJ3iXtygx7DRxzDSxrFVxfIb2SFME+XNwqClACTqimVpQC30hLN
jAzSsQXO0ADe/wHe/gHd/ATd+wLY8wDN7Bfg/zXk/zjlxmCnsX+4wGbqmFLo9nft/7k8Fbg8RrBE
T7FCQcA2E/8AAP8EB/8FCP8cLv80VP9rrv92wKTyWv//APn+Bff9CP//F834Moi9xZnGzaTy/ovv
yv+P6f+c/f+X9v+A0P//rP//m///0f//////++/7983v9CwAAAAAIAAgAAUG/sCIcCikUIjIpDLJ
gbVcMM7wuKwOYaysdlUxWq0crZjF8X6XY7GLGpG4JedIJi3ODN/wc/j1Sr9oHjMeHRhvXxMdOz09
O30sLjk8kj6SPD4zGF8XPouLOSwvO5WjlT4XVjM8nYs6i6SvHUtuP6qrna+jM2xIEhYCMpy2PbiS
Mg1VEgsAywIKDAwa0RsbMTIyMdEMAMdVDQHLzODi4wENu0oVDQvrC80CAuQCCxBxbkL2RBUVFhVx
93iGvgDMQ2QgvioDQihcyHBAG4NfQJCYWGKiRRIhHg6MSOKEjY8fa0zMaJDgEoknUqjEYUMkRo0A
OVo0gaLlSJhuJkxIclAicwmVKVTYfAkQggMHBwwYOODgQQWCPmuAHCrCQc4HBgho3cr1AAQjIiaa
GFuzRsUPBSJg5cqWrYEHPsWWnYj2QNu7bEeQQHHjBsgbdAtkxUv4Q0cVKlLgUEmiBFrCkPVenPwY
Mt4ECDJr3pyggOXPoEOHDgIAOw=="""),
'norotation':Tkinter.PhotoImage(master=self.top,data="""
R0lGODlhIAAgAIYAAQAAAABaAABfGgBkAAB0RQBgbx9kb18AX0JCAFhYAG9vbwAA/yoq1Ts74wB8
jxZojyF6rwBL/0BAv0B4v1Z513JyygCGAAChAACrLwC7b1iWSH/rfgCKnx+AtByIuxqPwACR/wCs
/zitxyi7/zC0/wDDjwDHpADSzwDD/wXO8gXP8wDX5ADY6gfX/wLY+gLY+wDe/w/Q8CLi/zDk/0OH
r0SHr0ift2nBlbg9R8gvN/8AAP8NDf8WANB/Lv9AAP9YANJWXMxzev9ISI8Aj7kAudgh//8A/6io
V7y8TajxVbftTtfAF8D2P/XIP//AP///AOPjO4Gan6qtrq+vr6qvsKqwsYeHwIC8xYS6w5Xx/7j1
/8nJydD4/////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACwA
AAAAIAAgAAYH/oAwgoOEhYaHhx8di4yNHSmIkYIeEJWWlxCQkoiUmJY0UlRVo6SkV5GdnhA1U62u
r1NYqKqVrLCwspy0q65WFb/AFRQgxCiFqZ62Uw0Lzc7PCyDHu8rM0NDShC/b3BtJ30pQ4khH5QzX
0ZtMT+zt7k8S6NkwI0X290VN7/vx1/MkRgIKNOJk37t+2AYBHBiwoMF2CJ/9Y9jwYbsJETJqjBBC
IUWCFtndEEGypIgYHo0QOcDywJKQT3zomElTh42UQwDoBIAggc+fGnr8GMqjJs2bghbm3Ml0ZwEc
RqMihdFixIgHTbM+jWp06iAHWZtu5Xp0kAkMGASEZTqWrM1BcCUuXAiwdqeBIELy6tW7462guHPr
6lTQpbDhw0ByiIAr18KAx5AfE+AQZcvhy11mFAIst7PnDDC4YL6smRBnz59Djz5cmjFq1KBFry7c
+u9r2KpnZy7E4oTv38BPrMg9u/YmQlm0KF/OXIuM49A3BQIAOw=="""),
'resuperpose':Tkinter.PhotoImage(master=self.top,data="""
R0lGODlhIAAgAIYAAX85QVpaaFhoeFhgb39vfz9xglh2iXXdPEXXazKxlie7mwCowQCpwgCvyg22
zzKzyxLQnw/Qow7Qog7QpQ3RqxDQoQ/TtS/UoyrUhwjVxgXY2gDM6gDe/wPe/wDa+gDW9gPa6DrI
3STi/1yNiliHnFiQpFiMoX+AtkrXo1/ao1LakkTN4UzR5Vbo/n/u/3/u/YpASI1wc6tqcK1lWcB3
P/9/AP9/Cs5uc/9/f/h+d/J7cZZ3gY69O4vgJbHCGIHGQYbnXt+aCdudIP+BCf+RHf+YLtueef+C
afy0Wf+6YP/MfP/HdIiMxZuXzqac04Xfo4vhpYnkvYbn0YLr7Nueo/+JkP+aq/+xnv+42/+z0/+9
5P/OjP/K2v/H9P/O//bC7wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACwA
AAAAIAAgAAYH/oARgoOEhYUTExEVhoyNjAgHPT0HCI6WgxUQEQc+nZ48CaEKl4aZCEE1qao1NDEG
I6SFFRU9qERJuLhIMQQjExaxihUYtTVESshKW0syvRMcGhSMmRcXKNcqQEKrNUXLMzG+HBwfGsCD
FylQ61BRU+9UNqk2R1ZeXDKvz+PjIBkZFtpFkSLlhUGDVHTYUILFi8MuOXaUyMCvIgcRU1xkdHEQ
IY4cV7Jk0eKlC44bJSxW7NDChcuXB6ngmDnTnkkdKVXy28DipcuYOKpgGUryyw0YJHTuZOAgRIgV
LFisCLFjhgwnTbI2MQAAgAClSxeIHbsgQNezaAEYALuzQYOx/gwWGAgwYIAAAQbyGjDxoANbix4+
CO7QwUNgwfwIF/5AmIOHcYUDE5asuDHYDg9M6L1bd0CAAmQXuN3g97IBGGnRBoDLoPWCDWw7nIZh
gAmTJk6cyJix42nUqQ8cvL5MAsaNL160DMVSBQeVgz5dsICttEMJHTm6eLFCc+Zzg9FdtCit0voN
HNq1iLySwzn08CKUZtCc3eG9JTZ0fH/BkWCUdRb8A4JFFYxggAxcbKfDEEPUYIMRBk3x3zoppHCB
MBFYoMFjHEwwQgwzLLFFEdwIAYQK11xzQQUSSBDBBIsoMoEGHY6wgwwiJqMEiUH0gIEwFcAYY5CJ
CPJLgQbESIBELrgQUUOPmsAoZIxCJoIIIiMQQAAN3KQSRCUywkjKBAqEkgAPnnjyA5VEktKiIC1C
IgklsxASpJsSTNBii1UKEqORfzoSCAA7"""),
'rotation':Tkinter.PhotoImage(master=self.top,data="""
R0lGODlhIAAgAIYAAQQCBAwKBAoQCiQmBAQ0BARWBAR0BAZXZGACYEx2PAQC/AwO/A0U9QQr/Cwq
6Bx+tCR6rCR+rCZ4tAR4/EhmvHxohFxI2GwqlAScBASOBASiBASiDASmHASuMASyTAS6ZGymdByK
uhicqByYxA+r2Ai88DKo3ATEjwTKsAnSzgTI+gTe/ATa/AjW+AfL6Dbl/CTY8FSWrGmo3ETmvFHI
2Vbp/HTs/F7G1LQCTNAuMPwCBPQKDPAYGOYZJPxiZIxmdJxY/MQ6hNwC3PwC/PQG/OwO/NIe8sYs
vpSSBJzqZMy6NPz+BPT5COz4GODYGM7NZNTCVJqYtqyurKystKeysKSnnoy6xJTy/Lb2/PygoNb6
/Pz+/Pz6/PT+/Oz+/PTS0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACwA
AAAAIAAgAAYH/oArgoOCLiQshIksLDCJjokkEg8liI8tN1M0j48kDw8QDy6PNFRTU1Qtm4MsI58Q
oCEqhDBWUlNRpTepmyohrxASrxIhgjA3UshRCxZTUo2PLp7AoBHCI5jIUlEMCgoOUlaLkMHTn5IQ
IVXNUNrc3d6ZlYIkvq6urxEjT01LS08O7945uAHpFzlXIJLw67dEScCADWStImHw1QMQDDMucbDg
YbeIg1q0CPEgmISTR5ho7Feho0cFIAWpIEIOmJEhUFYucfLy3YISg4DQlEBByJAhQXQuCdETpsQV
JoYYsUDk6BAiKjUySTLhZcxBN61azaKzCYuuARk8HSRDrNWk/iuZzGhxIWCFRyqKXCVCBIEAAE50
PumxA4cCBoRjyAsq5AgCAJABINHpRIdlHD0s7yCRyMWByKAHZF3SRAkPy6hT5xA1SATo14GRJMiR
urblHiYIeRAQ4DXkAX8DfMly2raO1YRQaCjg23cVLly++OCxA/UPRx02ZGge+QAV6Fy2iM/iQ0cM
R8o3aCDgW8CBEjW6dIEuXjyXLldeJFKPQYMB0AQY0N8JWtRn4BbgcUHICRo02KAAAhSQgYMYpHCg
geBhkcgJHDg4oQb9NeiBDRfWB14Nj5ygnoMspmBDgSVC54UqLnzAIogfDPLCFRfed4UqgqTggQbq
bbALITVgH9GFfV3oB6QgKHSgwQmqwHCFFlxo8eSGR6rygpOEBAIAOw=="""),
'debug':Tkinter.PhotoImage(master=self.top,data="""
R0lGODlhIAAgAIIAAf8A/wAAAOAgAIAAAOBgwP///0BAQGBgQCH5BAEAAAAALAAAAAAgACAAAgOn
CLrc7uHJCaml8bY8uWbeVmkhCJbY46FWGHBvF1fva2SsAkOBQBQFgWBGcgkLBOHgkFOtfEllU1Kr
Ca+CQbMG8gEJhgF2oO3oql6CWqnUslav9JhAJueM6ig7W+VihHp7fDwdWFdih29UhlmGZR8APY6O
bpCSh4xlRC1jmY+bhYKHjwtTl4hjdiJ/jaN2oKZhWXVuEZtTOjd9G7g8W5DAvcCRwxegFAkAOw==
"""),
'frequency':Tkinter.PhotoImage(master=self.top,data="""
R0lGODlhIAAgAIIAAf////8A/wAAAMDAwICAgAAAgP8AAAD//yH5BAEAAAEALAAAAAAgACAAAgPV
GLq88q/JSQWwmOp6h/Bb2HwDKDLRCK2ClKIA0SoPYd/3KxAXTIC1knA4sEU+vFlg5/HYBoCodAoo
ypoy1IdJrRag1OJWifp1z1NxxXxBUwtRtYvdnlrcpjJYeo/2z3IOJV19f1QHMWRcZ3eGXYGLjHVn
iJB0gB9uVVk0ZnCPEHtTcJZQn2GhZ6ScS5dUBkKapWgGmlGVrJFTtbZSgUuDu723iSOXvMObZDTB
p5qnrHrJYdHS08obTKJe29ghOz/dviXVGjXhROQyyyLnODnsJzQsECIJADs="""),
'imagesize':Tkinter.PhotoImage(master=self.top,data="""
R0lGODlhIAAgAMZAAPIACf8AAAB1h9YiDPsTI8U0E8ktNqFPHf8iOZ1UPASQpZhaZ2p/LwCet/8x
UVqNL/83XEOiOm59jwHFUDKyQQ/ESFaRpkKmblCWq/9IegDNhR3HXhDLfP9RhSG41ADJ6ADTs/9b
kRnPm/9emQDYygDb2gDZ9P9pqXKxu/9ssRDe/f94xkXnsv+M4f+Q6m/skv+c/pPwaK/T2qn1UH3t
/pPw/bD1/v//Aebw7eP6yv//ZNT5/+D68f7/kO/7/f7//P//////////////////////////////
////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////yH5
BAEKADYALAAAAAAgACAAAAf+gDaCg4SFhjYqiYovMSUqh5CHioksNzczj5GIk5yTOz48Oj05mZGd
pyoyOKs4Mh+am6iTHgq1DQ2vmrIqJRYLv7vBiTQ7Pz8+CykdBMK7NcbQCcoEJSAcGiAmzZM+0D8H
HcsV4+MT24kmCigy7BQR7+Tk54kfAvb3+Aq5zqgmH/8ftE0SdIpGtx8fJChcaCEYwU4Hf3gIQACC
RQAGHMaaRAPaxAwwUqQgkHHXQ04fUHT76MKBgwAlZZ2clM7ehQAgV6yAmYiEhg0TNnAAkWgmJwUC
IuBsEaCpAREb4pGbAMJoJ6UgYcBwMECqV6ucIgAYS7aAV6kEB5BdCwDD2bd38QgCCABhhN0RBAJY
EMG3r9+/hlTMPQFD5woEes8FHgwjb9PE2wyZYOyi8tyGNEuUEDiw0AbGIcI1xexzQrwJHEgoMjSB
sePRUOFW2KCaNeMWuF8ykB2Pg6EKcx2EC5d3N29yvwsMWM58+YPjyAtBh/57Om9DgQAAOw==
"""),
'storage':Tkinter.PhotoImage(master=self.top,data="""
R0lGODlhIAAgAKL/AAAAAACAAMDAwICAgAD/AMDAwP///wAAACH5BAEAAAIALAAAAAAgACAAAANs
KLrc/jDKSau9OOvNu39DKI5kSTZDoa5s67IDsKRvbYeyMBh87/9Anyi3sxkJSNVQUTTWAlAljmlw
WgtLXdXELUlj1EJwDPwSt900LVsku3nm8NU4Zarv2QVgz+/7/34fgoOEhYaHiImKixgJADs=
"""),
'workingdir':Tkinter.PhotoImage(master=self.top,data="""
R0lGODlhIAAgAKL/AP///+++3+vr677v5q50kXSumAAAAMDAwCH5BAEAAAcALAAAAAAgACAAAAPd
eLrM9rDJ6SAh5uJIpc1BGDwBdj2dYoUGC7ZjmRldtonig8kWNtm44IhEGp1oDqELgmsxTUhVcUpg
VYe6nQYJHO6aVeDro7qKYazQxWrcHmbpXO6am+lKm7XwToTYXnhZMEUbfmYaclhMPIdsXi2FRydg
jn86fpA+cHNLl4hWgm95K1l5VYggJwuWhawuW6VRbzaSJrCYirJSmLu0eBpHKQ20rLfCHjMnRwYF
usermAXS0s7Pq9MDA83V1tDZHN0pDwLk3OGr5OXn4gDq6xQGAO3m6/Hz7/Dy9O8oDAkAOw==
"""),
'variante0':Tkinter.PhotoImage(master=self.top,data="""
R0lGODlhIAAgAPf/AP///zExMf/n5+/W1s6trcalpXtjY2tCQpRaWntKSlIxMTkQEJwQEAgAABgA
ACkAAOdCOecQAL1aUve1rWspIVIQCFIIAIRCOcZaSrVCMUoYEP9KMec5IVIpIZxCMYwxIcZKMZwp
EFoQAHMxIaVSOXspEKUxEGsYAKWMhKVzY1I5Md5CEIwpCK1rUpxaQv+Ua+9jMTkQAM45AGtCMc5r
QqVCGIx7c1o5KcZ7WudaGLU5AIRSOYRaQrV7Ws5rMcZjKb1aIXMpAMZKALWcjHNaSvecY/+UUpRS
Ke9zIaVKEHMxCCkQAO9aAJyEc72chGNKOVpCMZxrSnNCIeeEQq1jMVIhAIw5AGtKMf+cUv+UQoxK
GL1SAP+cSv+tYykYCIxCAP97ANbGtf+tWpRjMe+cSq1jGLVaAMZjAGtjWv+9c9ala3tSIVoxAHNa
OVI5GHtKAIRSAP/GY3tzYykhEP/Wc//OUnNSAP/ehFpCAJx7EFpKEP/vnIRzGHtrCP/3lP//7ykp
If//zv//tf//pSEhEP//e///Y2NjAEJKAHuEQjE5AHuEUmt7Mc7/Od7/jDlCIYycaxAYAEJjAKXn
OUp7CFp7MXO1ITFSCDFaAEpSQlJrOSlSADljEFpjUqXvYzFrAEJjKSFCCDlaISlrAHOcWpzWe0p7
MTF7CNb3xhhKAFKMOUJ7KTlzIVJ7QqX3hCFjCCFzAEJzMUJrOQhjADmlMbW9taW1pYSUhFqEWmPO
YwAYAAApAABCAABSACFzKQBrEEqlWnPOhCFrMQhSGDmESpzntQg5GDlSQlqMcyFCMRBSMQBzOQBr
OUJrWozOtSFrUgBKMUqMe0pjY4TW1ilKSkqlrUKMlDF7hClKUhAxOTF7lCFCUhBaezGt7yGUzhB7
tTGEtQApQgBCawBalEJaawAYKQAhOQgxUgAxWlpja0pSWgAhShApWgAQOQAIIXNzhCkpMTk5Sikp
QgAAEP/3/5yUnFpSWlJCUtbGzjEQITEAEFo5QkIhKf+cpechKQAAACwAAAAAIAAgAAAI/wB74MBB
6dWpg6colQrkihUgW7fktHFz40aTMAaGGKjH48qRMUe0rBk1axasUZ9gwSqFStOjTrWI6OmgYcSI
ISiioCDSAoSHNVXY4OlVUmXKWacWFbDBDw0aIlIojLjAI4yTMNIkbIBAQkkSNopKlsQ0CtamGwTw
JehApMkON1AuXGgyoBa5Axw2YPAABNEuXryY9cIkCdODCggGHLDQRk6KEh0OSEmQTpqBDytASMDw
RpdnXsuYzUIUw4EDDQoeVPlChIeLDjdmXLj3boK/CBkkUAm1q3cvZqHd/Rs+vAEhK0eeXFHAz57c
dwAEQGBwIQqxXoB7/YJ2zt26de3Kuf9r4MXKFitBgmiYYS+Bunf0APT7kAgYsFm8tIf7jm4dOnHi
oBOADjLowMIJVSxwDjfinKMOPgDQI0owuVgCmC7thJNNOOicc8532Vihg4EiPPCPOwAGuI8Lf2Az
jSeT9BLJP+GYsyE88AACSDnlVKGEFVaIsIQXhJwD4DrxnGAGON040ggiD+hijjnhANKBO+7kk88D
FgBpBhx2sMFGNgGeE88NX1jjjTOGHDLcPPPw80E+WM5TAxJb5LnFl2xUwU+Z8OwjTzTWVFNMIsQ1
UMEC+mjQQT4aGFEHGEycYcYXbyhBwQH3yANPPOzggss11VQTiQMWiCBCBSKcYIIYauz/cAYYQlj6
RRBs3HDAARdQsE88zZCCjDbeiFJFECeEkAMXYmQRRyAA/FEIrZeywU8AClAg1QEJPIMMJNx8I0tQ
NcDQhR+BBDLIHwAIEkgWTHzBRgzlwJOtTRQkoAw00mAzzjF2vOEDFnesC8DBgsRxhx8/VKBBA//A
ww8/UlFwwTDlhHMMN9TAUYYPXdwhCLsH/5FuIFOcYIEDkRCygAbajjADLTxugw02b5SRRciDGHww
AO9msYUIMczhBWw3xKyKL9Csg00nUpQwRch7uEvyHkjowIQJbiANhQoKdNDBB5ysIgyVmVzRQQsv
pLHwIO4CQMYJViTBAgsfQHHD1yrw/9MBBZykwooy5iSTCSAG9DCFEWLQ4cfIWShxQxAsmODBBQoo
sI8KjzwiReCvrGKMLticY08KNNBA8CB+ZJHDGh1QvvcIH9ygQgePuDEDJ5tswkoshJRDjjpEEHwH
HYVwwQIQFHTAQgj7uFGCFR980PwJMxS2SSyqaDLHE+mos0bIXXCRxQ9AQFbCBwq44QYFSpQwghJB
lHAJJtvLksgTR+gtBQ9FyAISfEAGLTSPdrBhQ/zih54RXGIToRCFLCrRiick4Q1SOIAWkpCEI/hg
DB1QwQhCQAHpsaAE8UuPAzeRilDIohWVWMMGjyCFL8ABDnpwQwo6EQAKmKAEJQgBEHtFYIEqVKED
oEgFYGQhC1PwAYNakIId+tCHHD7BBpkowQ+fNwKVPWAJoUhGK1JBRlCAYhWMkIIeQKGHKVZRBSp4
AgVCsMUSnKBEDQBEAOLRCVBc4hKg0EQrWpGJTFSCD3zIQx+ksI97QOEDR/jACFB4Ag0AIh7JOMYx
AgIAOw=="""),
'variante1':Tkinter.PhotoImage(master=self.top,data="""
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
VAADGBTJBgOwBy+ssYuAAAA7"""),
'connected':Tkinter.PhotoImage(master=self.top,data="""
R0lGODlhIQCxANX/AP/////PL8DAwODg4N/f39DQ0M/Pz8DAwL+/v6+vr5+foJCQz5CQkICAgICA
AIAAAHBwcGCQkGBgz2BgkGBgYF9fX1dXVy//YC+QkC+QLy9gYC8vkC8vLwD/AACQkACAAAB/fwAA
/wAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAAIALAAAAAAhALEAAAb/QIFw
SByGQo1DshEqOp/Ej7SRPACugINIBO1+Gh/lEoy9arldIjVkVR6kUsAHEDKj09RH4wr+HKV1VyEi
B1p4X21iX35HbHVHhHdFYFR8VHCUYUdWIoOGk1+XhXCkc5uCg1uSAg5Tl3Adb4CNbIWpX2pSrWAd
YbK+tI1ag2B3VK1Svb2js8EHkA0iuELIB70f18lfwbSdW9FCIV/KYVOY3NwilFwh1eXlVc+b6Opw
7GAOhfpwbFjywd6msBNnpdSiI/7oKflyLwmANdiaJeyWqt7AOf/6CDND7xuVe3OyODpoRSTAit8u
mtGEBJCtjoVUoTmVheUldINQnjFCUxgS/25VUp2JZOSZr5LyXh6hMlSVEkmONiGd50idTKerpM5r
0+3ZVavgiuQk1EgQISrRtpxZB0WtPEJZ9BVa4jFs20i1EmUZw9RuF3X6yswVo9Zvmm9uBqO9muaJ
KrSQZTZu/HXL5MtDAFjAzFmI5s6cP4O+LHp049Kmu6BO/WQ16yKuX2feLLs17dqwb+OevTt3byKx
aweXPfx1cdbHUyc3vXx0c9DPO0cPrbv3dMzXSVffnX1y99PbcX9PM151eOHniac3vh55e+Xvmcd3
Ph96fen3qf/mvV9AeSj/2daff/lhV6B2AwbohIK+9ccgcAd6FyF4CU5InoXmVaihgxgC2P+hgBxu
uN+D/I344YInNmiiiL+R6FmKELJoHYwltkjjizJydyOBOYq3o4s8hijkikPa2CN6R6qXJHtLutck
fE/KFyV9U9pXJX5XFkHAllwSUMCXXxog5pgIGNDAZF16CaaYCLSJQAJwJqAABRBAkAYBBjCg5558
9smAnBRQUIGdUOCpgQeIIgrCoow2CqigFXRhKKIVbGDppZZWwOijFURaqAGHelDBAqSWSqqmi3Lq
6ROTNjDBq7C+2gCqIKgqKageNCDBrrzuOiujCjAQaKe3HtpAmlsi8OuiwQ67qhOtEhBAAQhMG4Cy
tDYLabG5EqCAAQrAqQC2wAq77afGcgn/ZpvLgqAtseh2uyWY1Lb77p24QqZvA43ey22ijQbMrLnP
QmuAnApEEAEGDGMgsLvmNobnmBSz2aa4CmjbWJwcdxwnAx1kHDFnBFzsp54iU3AZlwgEW2egMEPa
6cx1QlCwAF3K2UDNL8c886B1zuzEAG8m4ObRIjOAFs8y30x0Ahdk4DHHR7f5M7xEPJ2B1B7riVa4
cF7tdNFTJ0DFzApQkYDYRYybp5gNTF1xxmtfPUTGXzbwrd7Kwk22xz8PofeXZu+tAAGD611yA2Yy
0HcDHBQMgd5jdpm4AtSO24DjDORJAQdd1Kz3txQvXoDeZpv5OWc8U176lsKCzhrPk2ccBGgXQQAA
Ow=="""),
'localonly':Tkinter.PhotoImage(master=self.top,data="""
R0lGODlhIQCxANX/AP/////PL8DAwP8AAODg4N/f39DQ0M/Pz8DAwL+/v6+vr6EAAJ+foJCQz5CQ
kICAgICAAIAAAHBwcGCQkGBgz2BgkGBgYF9fX1dXVy//YC+QkC+QLy9gYC8vkC8vLwD/AACQkACA
AAB/fwAA/wAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAAIALAAAAAAhALEAAAb/QIFw
SByORg9E8jEqOp/EkPSRRACuAASJBO2GHiHlEoy9arldInVkVSKkUkAIMDKj09TI4woOHaV1VyMk
CFp4X21iX35HbHVHhHdFYFR8VHCUYUdWJIOGk1+XhXCkc5uCg1uSAhBTl3Afb4CNbIWpX2pSrWAf
YbK+tI1ag2B3VK1Svb2js8EIkA8kuELICL0h18lfwbSdW9FCI1/KYVOY3NwklFwj1eXlVc+b6Opw
7GAQhfpwbFjywd6msBNnpdSiI/7oKflyLwmANdiaJeyWqt7AOf/6CDND7xuVe3OyODpoRSTAit8u
mtGEBJCtjoVUoTmVheUldINQnjFCUxgS/25VUp2JZOSZr5LyXh6hMlSVEkmONiGd50idTKerpM5r
0+3ZVavgiuQk1EgQISrRtpxZB0WtPEJZ9BVa4jFs20i1EmUZw9RuF3X6yswVo9Zvmm9uBqO9muaJ
KrSQZTZu/HXL5MtDAGDAzFmI5s6cP4O+LHp049Kmu6BO/WQ16yKuX2feLLs17dqwb+OevTt3byKx
aweXPfx1cdbHUyc3vXx0c9DPO0cPrbv3dMzXSVffnX1y99PbcX9PM151eOHniac3vh55e+Xvmcd3
Ph96fen3qf/m/XqA7SL+cTbAgE6gNmCAkx1IIHC3KYhgGg4+KFqEmFHo2WYRLoDZAhZqlv/hAhpO
BiKFAHwI4oYcRuggiCdyNqKKA7IYYmcvmjgjaDUeKGN/KraYGowL/ghkkKB9aGFnNh55mY05Egnh
iixq1uSDXUB54mdNVhgjixcKUeONaXC4Y5deiuljmGOSWSaXl7HJ3xButlngdmDKt5+av5UHhZ7/
3cnnnHcK8KdvfuaHnaHaBToog4oi6p2j4DUqaaGT7rfom3lCSp6m5lWaqafWcbqnqH1aSiqglKZq
KqjcnUroqqp+GmuorBVg660FGKCrrgf06msCBzwwGa657tprAsgmoMCyCjBggQQSpFHAAQ5Ua+21
2DrQrAUWXBAtFNNyAMK444pg7rnobtv/7QVdhDvuBR3EK2+8F5yr7gXsgnuAuCBc0MC/AP9br7n3
5vuEuw9UoPDCCj8wsAgFt7svCA9QYPHFFjt8LgMOcIuvxOI+QKytCWhsLsceG+wEwgUEYEACLgdQ
8sMorwsyxQUwcAADyzIw88Yd26xvyLfuiqzJItT88dA427rry0grLe3EkFX9ALpS30wuulyfHLTK
Kx/QLAMTTKDB2Rp0nXTQjU3r69vHItszAzU3xuzdeDPrwAd0s81ZAXJnW23fFlx2awIcQ8vt4uvi
6zi0EoAtAK7NPgC54ow77i20jjtBgLIKJCt63w6gdXnjkn+uQAYb5H236MhqvjQRqm/QeHre1aLF
87Kypw666wpQ4TgDVCjQexE+U9vrA67DTbfxsg9Bt64P6Fx9ycv/nrfmQ1Sva/DWM1CA99UD/kCw
DmD/gAdgS1C9r7iSz8DLPj+QvgPUWuBBF5BXr/Pb5jNA9YIXLP1x5nLvA6CtOrY/1lzOfXTjVheC
AAA7"""),
'proxy':Tkinter.PhotoImage(master=self.top,data="""
R0lGODlhIQCxAPf/AP/////PL8DAwODg4N/f397f3tDQ0M/Pz87Pzs3PzcrOysnOycfNx8bNxsXN
xcLMwsDMwMDAwL+/v76/vri+uLe+t7DJsK+vr67Jrq6vrqrIqqqvqqmvqaGuoZ+foJ6fn52fnZyu
nJufnJqumpqfm5ifmZefmJaulpafl5WglpCQz5CQkImRiYiRiIeRh4aShoGSgYCAgICAAIAAAHuT
e3eUd3WUdXKVcnBwcGCQkGBgz2BgkGBgYF9fX1dXV1WjVUmjSS//YC+QkC+QLy9gYC8vkC8vLyyc
QyB3QRmCMheELxacQxWdQhWdPxWHLBWHKxOKKBKMJRCOIQ6RHQ2TGwqlDgimCwemCwemCgelBwam
CQamCASmBASkBAOnAwOmAwKnAgKmAgGnAQGmAgGmAQD/AACnAgCnAQCnAACmCACmBgCmBQCmAgCm
AQCkCgCiIgCiHgChJwChFACgLgCgFwCgFgCgFQCfMACfGgCfGQCdHgCcIQCbJwCaKgCZLQCZLACY
MQCYMACXMgCWNQCQkACPTgCOTwCNUQCDcwCAAAB/fwAA/wAAgAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAAIALAAAAAAhALEA
AAj/AAUIHEhw4KJFMSIkjLGooMOHBBNJjJEwAoCLACIwYgSxY6IYiRQuBInxokaOHQlSXGRRYQSJ
EgEkArDIJMqUFGfEuAgy0UGJNS8uYhRBI86PLUV+9HmQZc2DRG8WBEmRJ0WYVEMetMhoqNGpH68W
hUl25lahQzdKFSBj4lWYZV4CbcqyaNqPKiW2BVkmpFy/dJtqHAryJsW2Evv2HTs3cASoMRjhFYg4
Qt9ElxN/DEy368bIAhd9VBxyIlbOnBlR5biocunSFR9vRa0aJmuQMorqhskSo+zAnieyFm2x7NKD
vmkr/Hg7IYCVmBsn75y29vCZv3sKNkn7M8XbMzM6/z1uUTzw6p+vm9SKEKjd7kXVojybkf1V1EPR
nzRIXzBCzhWldVJUBj3mV3myvXcQRQOqpZBUTm2F4GxOqSafg2tJOFtLnT12oYWgFZQfUU0JRRRF
kW100moQqSgbURnpVtRC3oXYYlR1JZXRSAza2JFqupU0o0gq+pjSZy4NieKFKT2kFopQytdkkx9u
NOWVAwHgA5ZcCqRll1x+CeaVYo7ZZJlmdoRmmg+tyWZBbr6Z5ZZytklnnXDeieece+bZJ0Fx1hmo
nIO+WSibh6aZqJmLjtkomI92GWmYevY5KZaXklnpnplO2emZm+L5aUqjqhmqoKcSmqqhqyLaqqKv
Mv8aq6OzPkTArbgSYMCuux7g668SHBDDlLgWUACvBvgqwQTMZuDsBR7wgAMOKRGAAAs0wPCCC9y6
8AIMNtwgbg0tZBAtDz1QCxEBCiABxxtxzHFHH33woQcdddhhBx6HcHBuDz10RIADUpxxBhpjJDxG
G2i00QYZB+sRwgc8oBvwug1EYcYZZGxhxRVbaIFFFVd0wQYacoxAscUCM6BEGl+gwXEYZNQ8Rhho
5ExHB/9ebCsEUKzBRc45G5yzGETTkcIKFQPcUQEYULEGzkQTLQbSOdeBAtMsQ1SABlKDUTXRXlSd
hwlcO+21BVOoETMaWFtN9B4lpO2zQwQ8AAUaXMT/PXbRf5Bgt8ALPIEG1VWD4bcfgjdd7QJOoJGF
GGBwwcUXSCte9CAipF2tAkn8LbobhoDgucAInPADEEccscQSTDQByB+BCCJIIYh8wHWTBByQgAIL
BC/8AhRUUAEHG4jwgQe7p3TB89BHL/0KZXjAfMVdEiCBBBes4P333lvP9JW4SsD8tBWnbzHA7E+L
w90C5QptDO6jrz776U7LvkMDcH/B9gDcnvhWgKL6rQ9+AujfBYIwBOlJL4Dbw5/aCKLAITTQgd5D
kQegJ0EEKtCB0KMI+zxAkQt0sCAeCNYKfBUDEP7KV9YzoQQHYr1dxcADwkphDFjoPxDibyA33NUF
/26YQwIE8Yba22EMViABJRoBfjggoq9ydUQPGMB8TWTiCplmhI6474Y4fGESDXDDIQqLB13EUv2k
+CtccfFN9Yui9bCHqj/xyY4CKBVE9GgnPOaxVpICJKX8yEeHFNJPeDwkoASJKUZqipCO9FQkQQXJ
SiZykqTCpKksaUdF3rGTmtxjKPt4SU7+yZNeGqUhVYlIUJrSUqxc5Cs5Nclc4QpZyXrhAYI1LN7l
ClnKAmD0ojWtah0AfMhM5gqg1TR12eoARCCENKWpiGpa85rM7Nozo0mIHhThm+D8Zg+smc0J4g2a
0uyBCtbJznWOs5rlROBAehfNGOzgnvi8Zwzeqf+IeAoMnTHQgUAHKtB9WvN62jxnPW15qybyE6Hm
LAg9CREDAgTgihcNgEMPOrh1AZQAONwgtDZaTYjKM34fvRWvtmfQknZ0mxS95UpbqgiIGrOeUMrp
NW36T25S85pArenpPAotD+QgB0JIqhCCKlQ6/lOXLxRmURHaJBBalXricyr5ttc9ZWaVfA09Hw7U
17QOug+B8iNhHMmKv7NGNIH+g6AAmUdAihjwhwVRIAOt+jy5njCv3LMgCDNIEZHKEK8U7CEIRQgw
ErbwrzRUIQtd+MIYQraGZMThDZvIQ74iNogGGKJmPWBEKyKRs0tE7RMLIsc24qqKV9ShFo+JRi8b
TguMuhxjGZVYWzV+MYyuJcAb2RRHMGq1IAEBADs="""),
'proxyauth':Tkinter.PhotoImage(master=self.top,data="""
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
59EOpNRL3vIyWoDssWd7yitmIQIBADs="""),
'sebsauvage.net':Tkinter.PhotoImage(master=self.top,data="""
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
FxAAOw==""")

}
        

    def quit(self, event=None):
        pass
   
    def loadConfig(self,appConfig=None):
        ''' Read webGobbler configuration from registry or .INI file.
            If the registry is not available, the .ini file will be read.
            If the .ini file is not available, the default configuration will be used.
        '''
        if appConfig != None:
            raise NotImplementedError
        self.config = webgobbler.applicationConfig()  # Get a new applicationConfig object.
        self.configSource = None
        # First, we try to read configuration from registry.
        try:
            self.config.loadFromRegistryCurrentUser()
            self.configSource = "registry"
        except ImportError:
            pass
        except WindowsError:
            pass
        
        if self.configSource == None:
            # We are probably not under Windows, or the registry could not be read.
            # We try to read the .ini file in user's home directory:
            try:
                self.config.loadFromFileInUserHomedir()
                self.configSource = "inifile"
            except:
                self.configSource = 'default'
        
        # Then we push the configuration to the GUI so that the user can change it.
        self.configToGUI(self.config)

    def saveConfig(self):
        ''' Save configuration from the GUI to registry or .ini file.'''
        # Get all data from the GUI back into the applicationConfig object:
        self.GUItoConfig(self.config)
        
        # We first try to save config from where we got it.
        configSaved = False
        if self.configSource == 'registry':
            try:
                self.config.saveToRegistryCurrentUser()
                configSaved = True
            except ImportError:
                pass
            except WindowsError:
                pass
        elif self.configSource == 'inifile':
            try:
                self.config.saveToFileInUserHomedir()
                configSaved = True
            except IOError:
                pass
        
        # If configuration was not properly saved, try to save by another mean:
        if not configSaved:
            self.configSource == 'default'
            try:  # Try registry first.
                self.config.saveToRegistryCurrentUser()
                configSaved = True
                self.configSource = "registry"
            except ImportError:
                pass
            except WindowsError:
                pass        
        if not configSaved:  # If save into registry failed, try to .ini file.
            self.configSource = 'default'
            try:
                self.config.saveToFileInUserHomedir()
                configSaved = True
                self.configSource = "inifile"
            except ImportError:
                pass
            except WindowsError:
                pass        
                
        if not configSaved:
            self.configSource = 'default'
        else:
            self.configChanged = True
    
    def defaultValues(self):
        ''' Set configuration back to the default values.
            Note that this does not alter configuration saved in registry
            or .ini file until you press the 'Save' button.
        '''
        # Get the default values for webGobbler configuration:
        self.config = webgobbler.applicationConfig()
        self.configSource = None
        # Then we push the configuration to the GUI so that the user can change it.
        self.configToGUI(self.config)    
               
    def _initializeGUI(self):
        ''' This method creates all the GUI widgets. '''
        # GUI programming sucks.
        
     
        
        boldFont = tkFont.Font(weight='bold',size=-11)  # A simple bold font.
        smallFont = tkFont.Font(size=-9)  # A smaller font (for blacklists)
        
        defaultPadding = 5   # Padding around some widgets.
        
        # FIXME: All expand and sticky have to be set for proper GUI resizing.
        
        # FIXME: correct tab order.
        
        # FIXME: Put Icons on every option.

        # ----------------------------------------------------------------------
        # Main frame:
        # row 0 - Note book (tabs)
        # row 1 - Help area
        # row 2 - Buttons (Save/Default/Cancel)
        
        # row 0 - Note book (tabs)
        nbook = Pmw.NoteBook(self.top)
        self._widgets['main_notebook'] = nbook
        nbook.grid(column=0,row=0,sticky='NSWE')
        for name in ("Image generation","Storage","Network","Blacklists","About"):
            nbook.add(name)
            
        # row 1 - Help area
        #helpFrame = Tkinter.Frame(self.top)
        #helpFrame.grid(column=0,row=1,sticky='NSWE')
        
        # row 2 - Buttons (Save/Default/Cancel)
        buttonsframe = Tkinter.Frame(self.top,borderwidth=5 )
        buttonsframe.grid(column=0,row=2,sticky='NSWE')

        
        # ----------------------------------------------------------------------
        # Help area:
#        helpArea = Pmw.Group(helpFrame, tag_text='Help',tag_font=boldFont)
#        helpArea.pack(expand=1,fill='both')
#        message = 'This area will contain the help text which describes the control which is in focus.'
#        helpText = Tkinter.Text(helpArea.interior(), bg='#d4d0c8', height=4, relief='flat', wrap='word', takefocus=0, exportselection=0)
#        helpText.pack(expand=1,fill='both')
#        helpText.insert('0.0',message)  # Insert text in area.
#        helpText.config(state='disabled')  # Make area read-only.
        
        # ----------------------------------------------------------------------
        # Buttons (Save/Default/Cancel):
        # FIXME: Use Pmw.ButtonBox() instead ?
        Tkinter.Button(buttonsframe,text="Save configuration",command=self.saveClick).grid(column=0,row=0)
        Tkinter.Button(buttonsframe,text="Load configuration",command=self.loadClick).grid(column=1,row=0)
        Tkinter.Button(buttonsframe,text="Get default values",command=self.defaultClick).grid(column=2,row=0)
        Tkinter.Button(buttonsframe,text="Close",command=self.exitClick).grid(column=3,row=0)
        
        # ======================================================================
        # Note book tab "Image generation"
        # Cells:
        #     00000      "If you're unsure of the options to change, you can leave the default values."
        #     11111      Image resolution
        #     22222      Frequency
        #     33333      Keyword image search
        #     44 55      44=Output options,  55=Variante
        #     44 66      66=Debug
        
        # Cell 0 - "If you're unsure of the options to change, you can leave the default values."
        Tkinter.Label(nbook.page(0),text="If you're unsure of the options to change, you can leave the default values.",
                font=boldFont).grid(column=0,row=0,columnspan=2)
        
        # Cell 1 - Image resolution
        resolutionFrame = Pmw.Group(nbook.page(0), tag_text='Image resolution')
        resolutionFrame.grid(column=0,row=1,columnspan=2,sticky='NSEW',padx=defaultPadding,pady=defaultPadding,ipadx=defaultPadding,ipady=defaultPadding)
        
        # Cell 2 - Frequency
        timeFrame = Pmw.Group(nbook.page(0), tag_text='Frequency')
        timeFrame.grid(column=0,row=2,columnspan=2,sticky='NSEW',padx=defaultPadding,pady=defaultPadding,ipadx=defaultPadding,ipady=defaultPadding)
        
        # Cell 3 - Keyword image search
        keywordFrame = Pmw.Group(nbook.page(0), tag_text='Keyword image search')
        keywordFrame.grid(column=0,row=3,columnspan=2,sticky='NSEW',padx=defaultPadding,pady=defaultPadding,ipadx=defaultPadding,ipady=defaultPadding)
        
        # Cell 4 - Output options
        optionsGroup = Pmw.Group(nbook.page(0), tag_text='Output options')
        optionsGroup.grid(column=0,row=4,rowspan=2,sticky='NSEW',padx=defaultPadding,pady=defaultPadding,ipadx=defaultPadding,ipady=defaultPadding)
        
        # Cell 5 - Variante
        varianteGroup = Pmw.Group(nbook.page(0), tag_text='Variante')
        varianteGroup.grid(column=1,row=4,sticky='NSEW',padx=defaultPadding,pady=defaultPadding,ipadx=defaultPadding,ipady=defaultPadding)

        # Cell 6 - Debug
        debugGroup = Pmw.Group(nbook.page(0), tag_text='Debug')
        debugGroup.grid(column=1,row=5,sticky='NSEW',padx=defaultPadding,pady=defaultPadding,ipadx=defaultPadding,ipady=defaultPadding)
         
        # ----------------------------------------------------------------------
        # Cell 1 content: Image resolution:
        #    II  FFFFFFF    FFF = frame containing the cursors
        #    II  LLLLLLL    LLL = "Note: Resolution will be ignored by the Windows screensaver..."
        #                   III = icon
        #                  
        Tkinter.Label(resolutionFrame.interior(),image=self._ICONS['imagesize'],width=80).grid(column=0,row=0,rowspan=2,sticky='w')
        tempFrame = Tkinter.Frame(resolutionFrame.interior())
        tempFrame.grid(column=1,row=0)
        Tkinter.Label(resolutionFrame.interior(),text="Note: Resolution will be ignored by the Windows screensaver.\n(It will automatically detect screen resolution.)",justify='left').grid(column=1,row=1)

        # The frame FFFFFFF containing the cursors:
        self._widgets['assembler.sizex'] = Pmw.Counter(tempFrame,datatype={'counter':'numeric'},entryfield_value='1024',entry_width=6)
        self._widgets['assembler.sizex'].grid(column=0,row=0)
        Tkinter.Label(tempFrame,text=" by ").grid(column=1,row=0)
        self._widgets['assembler.sizey'] = Pmw.Counter(tempFrame,datatype={'counter':'numeric'},entryfield_value='768',entry_width=6)
        self._widgets['assembler.sizey'].grid(column=2,row=0)
        Tkinter.Label(tempFrame,text="Width").grid(column=0,row=1)
        Tkinter.Label(tempFrame,text="Height").grid(column=2,row=1)

        # ----------------------------------------------------------------------        
        # Cell 2 content : Frequency
        Tkinter.Label(timeFrame.interior(),text="Evolve current image every").grid(column=1,row=0,sticky='e')
        # FIXME: How do I right justify this ?  (label_justify does not exist !)
        self._widgets['program.every'] = Pmw.Counter(timeFrame.interior(),datatype={'counter':'numeric'},entryfield_value='60',entry_width=4)
        self._widgets['program.every'].grid(column=2,row=0)
        Tkinter.Label(timeFrame.interior(),text="seconds").grid(column=3,row=0,sticky='w')

        Tkinter.Label(timeFrame.interior(),text="by adding").grid(column=1,row=1,sticky='e')
        self._widgets['assembler.superpose.nbimages'] = Pmw.Counter(timeFrame.interior(),datatype={'counter':'numeric'},entryfield_value='10',entry_width=4)
        self._widgets['assembler.superpose.nbimages'].grid(column=2,row=1)
        Tkinter.Label(timeFrame.interior(),text="random images from the internet").grid(column=3,row=1,sticky='w')
        
        Tkinter.Label(timeFrame.interior(),image=self._ICONS['frequency'],width=80).grid(column=0,row=0,rowspan=3,sticky='w')
        
        # ----------------------------------------------------------------------        
        # Cell 3 content : Keyword image search
        v = Tkinter.IntVar(); self._widgets['collector.keywords.enabled'] = v
        Tkinter.Radiobutton(keywordFrame.interior(),variable=v,value=0,command=self._enablerDisabler,text="Use totally random images (default)").grid(column=0,row=0,sticky='W')
        Tkinter.Radiobutton(keywordFrame.interior(),variable=v,value=1,command=self._enablerDisabler,text="Search images using the following keywords:").grid(column=0,row=1,sticky='W')
        v.set(0)

        s = Tkinter.StringVar(); self._widgets['collector.keywords.keywords'] = s
        widget = Tkinter.Entry(keywordFrame.interior(),width=40,textvariable=s)
        widget.grid(column=1,row=1,sticky='EW')
        self._widgets_group['collector.keywords.keywords'] = [widget]  # Store reference to this widget so that we can enable/disable it later.
        
        # FIXME: empty image pool if keyword search enabled (but not if keyword search disabled)                
        
        # ----------------------------------------------------------------------        
        # Cell 4 content: Output options
        v = Tkinter.IntVar(); self._widgets['assembler.superpose.randomrotation']=v
        self._widgets['RotationCheckbutton'] = Tkinter.Checkbutton(optionsGroup.interior(),variable=v,image=self._ICONS['rotation'],command=self._imageChanger)
        self._widgets['RotationCheckbutton'].grid(column=0,row=0,sticky='W')
        Tkinter.Label(optionsGroup.interior(),text="Random rotation").grid(column=1,row=0,sticky='W')
        
        v = Tkinter.IntVar(); self._widgets['assembler.mirror']=v
        self._widgets['MirrorCheckbutton'] = Tkinter.Checkbutton(optionsGroup.interior(),variable=v,image=self._ICONS['mirror'],command=self._imageChanger)
        self._widgets['MirrorCheckbutton'].grid(column=0,row=1,sticky='W')
        Tkinter.Label(optionsGroup.interior(),text="Mirror (left-right)").grid(column=1,row=1,sticky='W')
        
        v = Tkinter.IntVar(); self._widgets['assembler.invert']=v
        self._widgets['InvertCheckbutton'] = Tkinter.Checkbutton(optionsGroup.interior(),variable=v,image=self._ICONS['invert'],command=self._imageChanger)
        self._widgets['InvertCheckbutton'].grid(column=0,row=2,sticky='W')
        Tkinter.Label(optionsGroup.interior(),text="Invert (negative)").grid(column=1,row=2,sticky='W')
        
        v = Tkinter.IntVar(); self._widgets['assembler.emboss']=v
        self._widgets['EmbossCheckbutton'] = Tkinter.Checkbutton(optionsGroup.interior(),variable=v,image=self._ICONS['emboss'],command=self._imageChanger)
        self._widgets['EmbossCheckbutton'].grid(column=0,row=3,sticky='W')
        Tkinter.Label(optionsGroup.interior(),text="Emboss").grid(column=1,row=3,sticky='W')
        
        v = Tkinter.IntVar(); self._widgets['assembler.resuperpose']=v
        self._widgets['ResuperposeCheckbutton'] = Tkinter.Checkbutton(optionsGroup.interior(),variable=v,image=self._ICONS['resuperpose'],command=self._imageChanger)
        self._widgets['ResuperposeCheckbutton'].grid(column=0,row=4,sticky='W')
        Tkinter.Label(optionsGroup.interior(),text="Re-superpose").grid(column=1,row=4,sticky='W')
        
        self._widgets['assembler.superpose.bordersmooth'] = Pmw.Counter(optionsGroup.interior(),datatype={'counter':'numeric'},entry_width=4,entryfield_value=30)
        self._widgets['assembler.superpose.bordersmooth'].grid(column=0,row=5,sticky='W')
        Tkinter.Label(optionsGroup.interior(),text="pixels border smooth\n(0=no smooth)",anchor='w').grid(column=1,row=5,sticky='NW')
        
        Tkinter.Label(optionsGroup.interior(),text="scale before superposing\n(1=no scale)",anchor='w').grid(column=1,row=6,sticky='NW')        
        s = Tkinter.StringVar(); self._widgets['assembler.superpose.scale'] = s
        Tkinter.Entry(optionsGroup.interior(),width=6,textvariable=s).grid(column=0,row=6,sticky='EW')
        
        # ----------------------------------------------------------------------        
        # Cell 5 content: Variante
        v = Tkinter.IntVar(); self._widgets['assembler.superpose.variante'] = v
        Tkinter.Radiobutton(varianteGroup.interior(),variable=v,value=0,command=self._enablerDisabler,image=self._ICONS['variante0']).grid(column=0,row=0,sticky='W')
        Tkinter.Radiobutton(varianteGroup.interior(),variable=v,value=1,command=self._enablerDisabler,image=self._ICONS['variante1']).grid(column=0,row=1,sticky='W')
        v.set(0)
        Tkinter.Label(varianteGroup.interior(),text="0 (Superpose+Equalize)   [Recommended]").grid(column=1,row=0,sticky='w')
        Tkinter.Label(varianteGroup.interior(),text="1 (Darken+Superpose+Autocontrast)").grid(column=1,row=1,sticky='w')
        
        # ----------------------------------------------------------------------        
        # Cell 6 content: Debug
        tempFrame= Tkinter.Frame(debugGroup.interior())
        tempFrame.grid(column=0,row=0,sticky='W')
        v = Tkinter.IntVar(); self._widgets['debug']=v
        Tkinter.Checkbutton(tempFrame,image=self._ICONS['debug'],variable=v).grid(column=0,row=0,sticky='W')
        Tkinter.Label(tempFrame,text="Debug mode").grid(column=1,row=0,sticky='W')
        Tkinter.Label(debugGroup.interior(),text="(Debug mode will create webGobbler.log in the installation directory.)").grid(column=0,row=1,columnspan=2,sticky='w')
        

        # ======================================================================
        # Note book tab "Storage"        
        # row 0 - Downloaded images
        # row 1 - Working directory
        downloadedImagesGroup = Pmw.Group(nbook.page(1), tag_text='Downloaded images')
        downloadedImagesGroup.grid(column=0,row=0,sticky='NSEW',padx=defaultPadding,pady=defaultPadding,ipadx=defaultPadding,ipady=defaultPadding)
        workingDirGroup = Pmw.Group(nbook.page(1), tag_text='Working directory')
        workingDirGroup.grid(column=0,row=1,sticky='NSEW',padx=defaultPadding,pady=defaultPadding,ipadx=defaultPadding,ipady=defaultPadding)
        
        # ----------------------------------------------------------------------        
        # row 0 content: Downloaded images
        Tkinter.Label(downloadedImagesGroup.interior(),image=self._ICONS['storage'],width=80).grid(column=0,row=0,rowspan=2,sticky='w')
        
        Tkinter.Label(downloadedImagesGroup.interior(),text="Store downloaded images in :").grid(column=1,row=0,columnspan=2,sticky='W')
        s = Tkinter.StringVar(); self._widgets['pool.imagepooldirectory'] = s
        Tkinter.Entry(downloadedImagesGroup.interior(),width=50,textvariable=s).grid(column=1,row=1,sticky='W')
        Tkinter.Button(downloadedImagesGroup.interior(),text="Browse...",command=self.chooseImagepoolDirClick).grid(column=2,row=1,sticky='W')
        Tkinter.Label(downloadedImagesGroup.interior(),text="(Directory will be created if it does not exist.)\n").grid(column=1,row=2,columnspan=2,sticky='W')
        tempFrame = Tkinter.Frame(downloadedImagesGroup.interior())
        tempFrame.grid(column=1,row=3,columnspan=2,sticky='W')       
        Tkinter.Label(tempFrame,text="Keep").grid(column=0,row=0)
        
        self._widgets['pool.nbimages'] = Pmw.Counter(tempFrame,datatype={'counter':'numeric'},entry_width=4,entryfield_value=50)
        self._widgets['pool.nbimages'].grid(column=1,row=0)
        Tkinter.Label(tempFrame,text="images in this directory.  (Recommended: 50)").grid(column=2,row=0)
        
        
        # ----------------------------------------------------------------------        
        # row 1 content: Working directory
        Tkinter.Label(workingDirGroup.interior(),image=self._ICONS['workingdir'],width=80).grid(column=0,row=0,rowspan=2,sticky='nw')
        
        Tkinter.Label(workingDirGroup.interior(),text="Store working files in :").grid(column=1,row=0,columnspan=2,sticky='W')
        s = Tkinter.StringVar() ; self._widgets['persistencedirectory'] = s
        Tkinter.Entry(workingDirGroup.interior(),width=50,textvariable=s).grid(column=1,row=1,sticky='W')
        Tkinter.Button(workingDirGroup.interior(),text="Browse...",command=self.chooseWorkingDirClick).grid(column=2,row=1,sticky='W')
        
        
        
        # ======================================================================
        # Note book tab "Network":
        # in the connectionGroup:
        #       ii  00000
        #       ii  11111
        #       ii  22222
        # row 0 - radiobutton "Do not connect to internet"
        # row 1 - radiobutton "Use the internet"
        # row 2 - group "Internet connexion parameters"       
        # iii - image.
        
        connectionGroup = Pmw.Group(nbook.page(2), tag_text='Connection')
        connectionGroup.grid(column=0,row=0,sticky='NSEW',padx=defaultPadding,pady=defaultPadding)
        
        self._widgets['ConnectionImage'] = Tkinter.Label(connectionGroup.interior(),image=self._ICONS['connected'])
        self._widgets['ConnectionImage'].grid(column=0,row=0,rowspan=5,sticky='n')

        # ----------------------------------------------------------------------        
        # row 0 content: radiobutton "Do not connect to internet"
        v = Tkinter.IntVar() ; self._widgets['collector.localonly'] = v
        Tkinter.Radiobutton(connectionGroup.interior(),variable=v,value=1,command=self._enablerDisabler,text="Do not connect to internet: use images found on local disk").grid(column=1,row=0,columnspan=2,sticky='W')
        # Choose directory
        
        s = Tkinter.StringVar() ; self._widgets['collector.localonly.startdir'] = s
        localStartDirEntry = Tkinter.Entry(connectionGroup.interior(),width=30,textvariable=s)
        localStartDirEntry.grid(column=2,row=1,sticky='EW')
        chooseLocalStartDirButton = Tkinter.Button(connectionGroup.interior(),text="Choose diretory...",command=self.chooseLocalStartDirectory)
        chooseLocalStartDirButton.grid(column=3,row=1,sticky='W')
        
        # ----------------------------------------------------------------------        
        # row 1 content: radiobutton "Use the internet"
        Tkinter.Radiobutton(connectionGroup.interior(),variable=v,value=0,command=self._enablerDisabler,text="Use the internet :").grid(column=1,row=2,columnspan=3,sticky='W')
        v.set(0)
        # ----------------------------------------------------------------------        
        # row 2 content: group "Internet connexion parameters"   
        #     SSSS GGGG     SSSS = a space (Canvas)
        #                   GGGG = the "Internet connexion parameter" group.
        
        Tkinter.Canvas(connectionGroup.interior(),width=20,height=10).grid(column=1,row=4)  # Just a spacer
        connectionParamGroup = Pmw.Group(connectionGroup.interior(), tag_text='Internet connection parameters')
        connectionParamGroup.grid(column=2,row=4,columnspan=3,sticky='W',padx=defaultPadding,pady=defaultPadding)
        
        # "Internet connexion parameter" group content:
        v = Tkinter.IntVar(); self._widgets['network.http.proxy.enabled'] = v
        rbDirectConnection = Tkinter.Radiobutton(connectionParamGroup.interior(),variable=v,value=0,text="Direction connection",command=self._enablerDisabler)
        rbDirectConnection.grid(column=0,row=0,sticky='W')
        rbUseProxy = Tkinter.Radiobutton(connectionParamGroup.interior(),variable=v,value=1,text="Use HTTP Proxy :",command=self._enablerDisabler)
        rbUseProxy.grid(column=0,row=1,sticky='NW')        
        v.set(0)
        proxyParamsFrame = Tkinter.Frame(connectionParamGroup.interior())
        proxyParamsFrame.grid(column=1,row=1)
        self._widgets['proxyParamsFrame'] = proxyParamsFrame
        
        # Proxy parameters:
        Tkinter.Label(proxyParamsFrame,text="Proxy address").grid(column=0,row=0,sticky='W')
        Tkinter.Label(proxyParamsFrame,text="Port").grid(column=1,row=0,sticky='W')
        
        s = Tkinter.StringVar(); self._widgets['network.http.proxy.address'] = s
        proxyAddressEntry = Tkinter.Entry(proxyParamsFrame,width=30,textvariable=s)
        proxyAddressEntry.grid(column=0,row=1,sticky='EW')
        
        s = Tkinter.StringVar(); self._widgets['network.http.proxy.port'] = s
        proxyPortEntry = Tkinter.Entry(proxyParamsFrame,width=6,textvariable=s)
        proxyPortEntry.grid(column=1,row=1,sticky='EW')
        
        v = Tkinter.IntVar(); self._widgets['network.http.proxy.auth.enabled'] = v
        proxyUseAuthCheckbox = Tkinter.Checkbutton(proxyParamsFrame,text="Proxy requires authentication",variable=v,command=self._enablerDisabler)
        proxyUseAuthCheckbox.grid(column=0,row=2,columnspan=2,sticky='W')
        
        proxyAuthFrame = Tkinter.Frame(proxyParamsFrame,width=50)
        self._widgets['proxyAuthFrame'] = proxyAuthFrame
        #proxyAuthFrame.grid_propagate(0)
        proxyAuthFrame.grid(column=0,row=3,columnspan=2,stick='E')
        
        # Proxy authentication frame:
        Tkinter.Canvas(proxyAuthFrame,width=20,height=10).grid(column=0,row=0,rowspan=3)  # Just a spacer
        Tkinter.Label(proxyAuthFrame,text="Login :").grid(column=1,row=1,sticky='W')
        s = Tkinter.StringVar(); self._widgets['network.http.proxy.auth.login'] = s
        loginEntry = Tkinter.Entry(proxyAuthFrame,width=15,textvariable=s)
        loginEntry.grid(column=2,row=1,sticky='EW')
        Tkinter.Label(proxyAuthFrame,text="Password :").grid(column=1,row=2,sticky='W')
        s = Tkinter.StringVar(); self._widgets['network.http.proxy.auth.password'] = s
        passwordEntry = Tkinter.Entry(proxyAuthFrame,width=15,textvariable=s,show='*')
        passwordEntry.grid(column=2,row=2,sticky='EW')
        Tkinter.Label(proxyAuthFrame,text="(WARNING: Password is stored in registry)").grid(column=2,row=3)

        # List of widgets to disable according to selected options:
        self._widgets_group['network.http.proxy.auth.enabled'] = ( loginEntry,passwordEntry )
        self._widgets_group['network.http.proxy.enabled']      = ( loginEntry,passwordEntry,proxyUseAuthCheckbox,proxyAddressEntry,proxyPortEntry)
        self._widgets_group['collector.localonly']             = ( loginEntry,passwordEntry,proxyUseAuthCheckbox,proxyAddressEntry,proxyPortEntry,rbDirectConnection,rbUseProxy)
        self._widgets_group['NOT collector.localonly']         = ( localStartDirEntry, chooseLocalStartDirButton)
        
        # ======================================================================
        # Note book tab "Blacklists"  
        # column 0 - "Blacklisted images"
        # column 1 - "Blacklisted URLs"
        blacklistedImagesGroup = Pmw.Group(nbook.page(3), tag_text='Blacklisted images')
        blacklistedImagesGroup.grid(column=0,row=0,sticky='NS')
        blacklistedURLsGroup = Pmw.Group(nbook.page(3), tag_text='Blacklisted URLs')
        blacklistedURLsGroup.grid(column=1,row=0,sticky='NS')
        
        # Blacklisted images:
        self._widgets['blacklist.imagesha1'] = Pmw.ScrolledText(blacklistedImagesGroup.interior(),text_width=42,text_height=30,text_wrap='none',vscrollmode='static',text_font=smallFont)
        self._widgets['blacklist.imagesha1'].grid(column=0,row=0)
        Tkinter.Button(blacklistedImagesGroup.interior(),text="Add image...",command=self.addImageBlacklist).grid(column=0,row=1)
        
        # Blacklisted URLs
        self._widgets['blacklist.url'] = Pmw.ScrolledText(blacklistedURLsGroup.interior(),text_width=42,text_height=30,text_wrap='none',vscrollmode='static',text_font=smallFont)
        self._widgets['blacklist.url'].grid(column=0,row=0)
        

        # ======================================================================
        # Note book tab "About"  
        aboutNbook = Pmw.NoteBook(nbook.page(4))
        self._widgets['about_notebook'] = aboutNbook
        aboutNbook.grid(column=0,row=0)
        for name in ("About","License","Disclaimer"):
            aboutNbook.add(name)

        # "About" tab content:
        aboutMessage = '''
        
%s

webGobbler wanders the web, downloads random images and mixes them.

Authors :
        - Sébastien SAUVAGE (http://sebsauvage.net)
        - Kilian (http://thesermon.free.fr/)
        
Website : http://sebsauvage.net/webgobbler



webGobbler was developped in Python (http://python.org)
and uses the following libraries and programs:
    - PIL (Python Imaging Library) : http://www.pythonware.com/products/pil/
    - ctypes : http://starship.python.net/crew/theller/ctypes/
    - Psyco : http://psyco.sourceforge.net/
    - Pmw (Python MegaWidgets) : http://pmw.sourceforge.net/
    - cxFreeze : http://starship.python.net/crew/atuining/cx_Freeze/
    - AutoIt : http://www.autoitscript.com/autoit3/
    - InnoSetup : http://www.jrsoftware.org/isinfo.php
''' % webgobbler.VERSION
        aboutText = Pmw.ScrolledText(aboutNbook.page(0),text_width=70,text_height=30,text_bg='#d4d0c8', text_relief='flat', text_takefocus=0, text_exportselection=0 )
        aboutText.grid(column=0,row=0)
        aboutText.insert('0.0',aboutMessage)
        aboutText.image_create('0.0', image=self._ICONS['sebsauvage.net'])
        aboutText.configure(text_state='disabled')  # Text in read-only


        # "License" tab content:
        licenseText = Pmw.ScrolledText(aboutNbook.page(1),text_width=70,text_height=30,text_bg='#d4d0c8', text_relief='flat', text_takefocus=0, text_exportselection=0 )
        licenseText.grid(column=0,row=0)
        licenseText.insert('0.0',webgobbler.LICENSE)
        licenseText.configure(text_state='disabled')  # Text in read-only
        
        # "Disclaimer" tab content:
        disclaimerText = Pmw.ScrolledText(aboutNbook.page(2),text_width=70,text_height=30,vscrollmode='static',text_bg='#d4d0c8', text_relief='flat', text_takefocus=0, text_exportselection=0 )
        disclaimerText.grid(column=0,row=0)
        disclaimerText.insert('0.0',webgobbler.DISCLAIMER)
        disclaimerText.configure(text_state='disabled')  # Text in read-only
        
        aboutNbook.setnaturalsize()
        
        nbook.setnaturalsize()  # Auto-size the notebook to fit all its pages size.

        # FIXME: force types in widgets (numeric, etc.)

    def configToGUI(self,c):
        ''' Reads an applicationConfig object of webGobbler and pushes all the value to the GUI. '''
        # For the "Image generation" tab:
        self._widgets['assembler.sizex'].setentry( c['assembler.sizex'] )
        self._widgets['assembler.sizey'].setentry( c['assembler.sizey'] )
        self._widgets['program.every'].setentry( c['program.every'] )
        self._widgets['assembler.superpose.nbimages'].setentry( c['assembler.superpose.nbimages'] )
        if c['assembler.superpose.randomrotation']: self._widgets['assembler.superpose.randomrotation'].set(1)
        else:                                       self._widgets['assembler.superpose.randomrotation'].set(0)
        if c['assembler.mirror']: self._widgets['assembler.mirror'].set(1)
        else:                     self._widgets['assembler.mirror'].set(0)
        if c['assembler.invert']: self._widgets['assembler.invert'].set(1)
        else:                     self._widgets['assembler.invert'].set(0)
        if c['assembler.emboss']: self._widgets['assembler.emboss'].set(1)
        else:                     self._widgets['assembler.emboss'].set(0)
        if c['assembler.resuperpose']: self._widgets['assembler.resuperpose'].set(1)
        else:                          self._widgets['assembler.resuperpose'].set(0)
        
        self._widgets['assembler.superpose.bordersmooth'].setentry( c['assembler.superpose.bordersmooth'] )
        self._widgets['assembler.superpose.scale'].set( c['assembler.superpose.scale'] )
        
        self._widgets['assembler.superpose.variante'].set(c['assembler.superpose.variante'])
        if c['debug']: self._widgets['debug'].set(1)
        else:          self._widgets['debug'].set(0)
 
        self._widgets['collector.keywords.enabled'].set( c['collector.keywords.enabled'] )
        self._widgets['collector.keywords.keywords'].set( c['collector.keywords.keywords'] )

        # For the "Storage" tab:
        self._widgets['pool.imagepooldirectory'].set( c['pool.imagepooldirectory'] )
        self._widgets['persistencedirectory'].set( c['persistencedirectory'] )
        self._widgets['pool.nbimages'].setentry(c['pool.nbimages'])  # Why the hell the Pmw.Counter().setentry() method is not documented ?
        
        
        # For the "Network" tab:
        if c['collector.localonly']: self._widgets['collector.localonly'].set(1)
        else:                        self._widgets['collector.localonly'].set(0)
        
        self._widgets['collector.localonly.startdir'].set( c['collector.localonly.startdir'] )
        
        if c['network.http.proxy.enabled']: self._widgets['network.http.proxy.enabled'].set(1)
        else:                        self._widgets['network.http.proxy.enabled'].set(0)
        self._widgets['network.http.proxy.address'].set(c['network.http.proxy.address'])
        self._widgets['network.http.proxy.port'].set(c['network.http.proxy.port'])
        if c['network.http.proxy.auth.enabled']: self._widgets['network.http.proxy.auth.enabled'].set(1)
        else:                                     self._widgets['network.http.proxy.auth.enabled'].set(0)
        self._widgets['network.http.proxy.auth.login'].set(c['network.http.proxy.auth.login'])
        self._widgets['network.http.proxy.auth.password'].set(c['network.http.proxy.auth.password'])
                
        # For the "Blacklists" tab
        self._widgets['blacklist.imagesha1'].delete('1.0', 'end')
        self._widgets['blacklist.imagesha1'].insert('0.0','\n'.join(c['blacklist.imagesha1'].keys()))

        self._widgets['blacklist.url'].delete('1.0', 'end')
        self._widgets['blacklist.url'].insert('0.0','\n'.join(c['blacklist.url']))
        
        self._enablerDisabler()  # Enabled/disable widgets according to values.
        self._imageChanger()     # Display proper icons


    def GUItoConfig(self,c):
        ''' Commit all GUI parameters to the config object (c must be an webgobbler.applicationConfig object)
            c is modified in-place.
        '''
        # From the "Image generation" tab:        
        c['assembler.sizex'] = int(self._widgets['assembler.sizex'].get())
        c['assembler.sizey'] = int(self._widgets['assembler.sizey'].get())
        c['program.every'] = int(self._widgets['program.every'].get())
        c['assembler.superpose.nbimages'] = int(self._widgets['assembler.superpose.nbimages'].get())
        if self._widgets['assembler.superpose.randomrotation'].get()==0: c['assembler.superpose.randomrotation']=False
        else:                                                            c['assembler.superpose.randomrotation']=True
        if self._widgets['assembler.mirror'].get()==0: c['assembler.mirror']=False
        else:                                          c['assembler.mirror']=True
        if self._widgets['assembler.invert'].get()==0: c['assembler.invert']=False
        else:                                          c['assembler.invert']=True
        if self._widgets['assembler.emboss'].get()==0: c['assembler.emboss']=False
        else:                                          c['assembler.emboss']=True
        c['assembler.superpose.variante'] = int(self._widgets['assembler.superpose.variante'].get())
        if self._widgets['assembler.resuperpose'].get()==0: c['assembler.resuperpose']=False
        else:                                               c['assembler.resuperpose']=True

        c['assembler.superpose.bordersmooth'] = int(self._widgets['assembler.superpose.bordersmooth'].get())       
        c['assembler.superpose.scale'] = float(self._widgets['assembler.superpose.scale'].get())
        
        if self._widgets['collector.keywords.enabled'].get()==0: c['collector.keywords.enabled']=False
        else:                                                    c['collector.keywords.enabled']=True
        c['collector.keywords.keywords'] = str(self._widgets['collector.keywords.keywords'].get())               
        
        if self._widgets['debug'].get()==0: c['debug']=False
        else:                               c['debug']=True

        # From the "Storage" tab:
        c['pool.imagepooldirectory'] = str(self._widgets['pool.imagepooldirectory'].get())
        c['persistencedirectory'] = str(self._widgets['persistencedirectory'].get())
        c['pool.nbimages'] = int(self._widgets['pool.nbimages'].get() )

        # For the "Network" tab:
        if self._widgets['collector.localonly'].get()==0: c['collector.localonly']=False
        else:                                             c['collector.localonly']=True
        c['collector.localonly.startdir'] = self._widgets['collector.localonly.startdir'].get()
 
        if self._widgets['network.http.proxy.enabled'].get()==0: c['network.http.proxy.enabled']=False
        else:                                                    c['network.http.proxy.enabled']=True
        c['network.http.proxy.address'] = str(self._widgets['network.http.proxy.address'].get())        
        c['network.http.proxy.port'] = int(self._widgets['network.http.proxy.port'].get())
        if self._widgets['network.http.proxy.auth.enabled'].get()==0: c['network.http.proxy.auth.enabled']=False
        else:                                                         c['network.http.proxy.auth.enabled']=True
        c['network.http.proxy.auth.login'] = str(self._widgets['network.http.proxy.auth.login'].get())
        c['network.http.proxy.auth.password'] = str(self._widgets['network.http.proxy.auth.password'].get())

        # For the "Blacklists" tab
        c['blacklist.imagesha1'] = dict([ (i.strip(),0) for i in self._widgets['blacklist.imagesha1'].getvalue().strip().split('\n') if len(i.strip())!=0])
        c['blacklist.url'] = [i.strip() for i in self._widgets['blacklist.url'].getvalue().strip().split('\n') if len(i.strip())!=0]


    # ##########################################################################
    # GUI elements events handlers:
    
    def _enablerDisabler(self):
        ''' This handler will enable/disable widgets according to the value of
            some of these widgets.
        '''    
        # First enable all widgets, then de-activate them according to selected options.
        for group in self._widgets_group.values():
            for widget in group:
                widget.configure(state='normal')
        
        # Enable/disable according to "Use HTTP proxy:" radiobutton.
        if self._widgets['collector.localonly'].get()!=0:
            for widget in self._widgets_group['collector.localonly']:
                widget.configure(state='disabled')
        else:
            for widget in self._widgets_group['NOT collector.localonly']:
                widget.configure(state='disabled')        

        # Enable/disable according to "Use HTTP proxy:" radiobutton.
        if self._widgets['network.http.proxy.enabled'].get()==0:
            for widget in self._widgets_group['network.http.proxy.enabled']:
                widget.configure(state='disabled')

        # Enable/disable according to "Proxy requires authentication:" checkbox
        if self._widgets['network.http.proxy.auth.enabled'].get()==0:
            for widget in self._widgets_group['network.http.proxy.auth.enabled']:
                widget.configure(state='disabled')
                
        if self._widgets['collector.localonly'].get()==0:
            if self._widgets['network.http.proxy.enabled'].get()==0:
                self._widgets['ConnectionImage'].configure(image=self._ICONS['connected'])
            else:
                if self._widgets['network.http.proxy.auth.enabled'].get()==0:
                    self._widgets['ConnectionImage'].configure(image=self._ICONS['proxy'])
                else:
                    self._widgets['ConnectionImage'].configure(image=self._ICONS['proxyauth'])
        else:
            self._widgets['ConnectionImage'].configure(image=self._ICONS['localonly'])
        
        
        # Enable/disable keyword search text area:
        if self._widgets['collector.keywords.enabled'].get()==0:
            self._widgets_group['collector.keywords.keywords'][0].configure(state='disabled')
        else:
            self._widgets_group['collector.keywords.keywords'][0].configure(state='normal')
            
            
            
    def _imageChanger(self):
        ''' This event handler changes the image according to checked options. '''
        if self._widgets['assembler.superpose.randomrotation'].get()==0:
            self._widgets['RotationCheckbutton'].configure(image=self._ICONS['norotation'])
        else:
            self._widgets['RotationCheckbutton'].configure(image=self._ICONS['rotation'])
            
        if self._widgets['assembler.mirror'].get()==0:
            self._widgets['MirrorCheckbutton'].configure(image=self._ICONS['normal'])
        else:
            self._widgets['MirrorCheckbutton'].configure(image=self._ICONS['mirror'])

        if self._widgets['assembler.invert'].get()==0:
            self._widgets['InvertCheckbutton'].configure(image=self._ICONS['normal'])
        else:
            self._widgets['InvertCheckbutton'].configure(image=self._ICONS['invert'])

        if self._widgets['assembler.emboss'].get()==0:
            self._widgets['EmbossCheckbutton'].configure(image=self._ICONS['normal'])
        else:
            self._widgets['EmbossCheckbutton'].configure(image=self._ICONS['emboss'])

        if self._widgets['assembler.resuperpose'].get()==0:
            self._widgets['ResuperposeCheckbutton'].configure(image=self._ICONS['normal'])
        else:
            self._widgets['ResuperposeCheckbutton'].configure(image=self._ICONS['resuperpose'])
            

    def saveClick(self):
        self.saveConfig()
        if self.configSource in ('registry','inifile'):
            sourceName = "registry"
            if self.configSource == 'inifile':
                sourceName = self.config.configFilename()
            # Pre-defined Tk bitmaps: ('error', 'gray25', 'gray50', 'hourglass','info', 'questhead', 'question', 'warning')
            Pmw.MessageDialog(self.top,title = 'Configuration saved',message_text="Configuration saved to %s." % sourceName,iconpos='w',icon_bitmap='info')
        else:
            Pmw.MessageDialog(self.top,title = 'Error while saving configuration',message_text="Could not save configuration to registry or .ini file !",iconpos='w',icon_bitmap='error')

    def loadClick(self):
        self.loadConfig()        
        if self.configSource in ('registry','inifile'):
            sourceName = "registry"
            if self.configSource == 'inifile':
                sourceName = self.config.configFilename()
            Pmw.MessageDialog(self.top,title = 'Configuration loaded',message_text="Configuration loaded from from %s." % sourceName,iconpos='w',icon_bitmap='info')
        else:
            Pmw.MessageDialog(self.top,title = 'Configuration loaded',message_text="Configuration could not be read from registry or .ini file.\nConfiguration was loaded with default values.",iconpos='w',icon_bitmap='warning')
    
    def defaultClick(self):
        self.defaultValues()
        
    def exitClick(self):
        self.top.destroy()

    def chooseImagepoolDirClick(self):
        initialDir = self._widgets['pool.imagepooldirectory'].get()
        newDir = tkFileDialog.askdirectory(parent=self,initialdir=initialDir,title='Select a directory where to store downloaded images...').strip()
        if len(newDir) > 0:
            self._widgets['pool.imagepooldirectory'].set( newDir )

    def chooseWorkingDirClick(self):
        initialDir = self._widgets['persistencedirectory'].get()
        newDir = tkFileDialog.askdirectory(parent=self,initialdir=initialDir,title='Select a directory where to store working files...').strip()
        if len(newDir) > 0:
            self._widgets['persistencedirectory'].set( newDir )
    
    def addImageBlacklist(self):
        file = tkFileDialog.askopenfile(parent=self,mode='rb',title='Select a file to add to the blacklist...')
        if file == None:
            return
        data = file.read(10000000)  # Read at most 10 Mb
        file.close()
        self._widgets['blacklist.imagesha1'].insert('end',"\n"+hashlib.sha1(data).hexdigest())

    def chooseLocalStartDirectory(self):
        initialDir = self._widgets['collector.localonly.startdir'].get()
        newDir = tkFileDialog.askdirectory(parent=self,initialdir=initialDir,title='Select a directory where to get images from...').strip()
        if len(newDir) > 0:
            self._widgets['collector.localonly.startdir'].set( newDir )
    
    def showAbout(self):
        ''' Displays the about dialog. '''
        self._widgets['main_notebook'].selectpage(4)
        self._widgets['about_notebook'].selectpage(0)
        
if __name__ == "__main__":
    main()


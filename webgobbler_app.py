#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
'''
webGobbler application 1.2.8
'''


try:
    import Pmw
except ImportError, exc:
    raise ImportError, "The Pmw (Python Megawidgets) module is required for the webGobbler application. See http://pmw.sourceforge.net/\nCould not import module because: %s" % exc

import sys,os,os.path

if os.path.isdir('libtcltk84'):
    os.environ['TCL_LIBRARY'] = 'libtcltk84\\tcl8.4'
    os.environ['TK_LIBRARY'] =  'libtcltk84\\tk8.4'

import time
import Tkinter
import tkFileDialog
import tkFont
import threading,Queue

try:
    import webgobbler   # We import the webGobbler module.
except ImportError, exc:
    raise ImportError, "The webGobbler module is required to run this webGobbler configuration GUI. See http://sebsauvage.net/python/webgobbler/\nCould not import module because: %s" % exc

try:
  import ImageTk
except ImportError, exc:
  raise ImportError, "The PIL (Python Imaging Library) is required to run this program. See http://www.pythonware.com/products/pil/\nUnder Linux, install the packages pythonX.X-imaging and pythonX.X-imaging-tk.\nCould not import module because: %s" % exc 

CTYPES_AVAILABLE = True
try:
    import ctypes
except ImportError:
    CTYPES_AVAILABLE = False


SAVE_FORMATS = (
    ('Windows Bitmap','*.bmp'),
    ('Portable Network Graphics','*.png'),
    ('JPEG / JFIF','*.jpg'),
    ('CompuServer GIF','*.gif'),
    ('Adobe Portable Document Format','*.pdf'),
    ('TIFF','*.tif'),
    ('ZSoft Paintbrush','*.pcx'),
    ('Portable Pixmap','*.ppm'),
    ('X11 Bitmap','*.xbm'),
    ('Encapsulated Postscript','*.eps')
    )

def main():
    return
#    root = Tkinter.Tk()                       # Initialize Tkinter
#    Pmw.initialise(root)                      # Initialize Pmw
#    root.title('webGobbler')    # Set window title.    
#    wgconfig = wg_application(root)               # Build the GUI.
#    root.mainloop()                           # Display it and let is operate...

class wg_application:
    '''
    Example:
            root = Tkinter.Tk()                       # Initialize Tkinter
            root.title('webGobbler configuration')
            Pmw.initialise(root)                      # Initialize Pmw            
            wgconfig = wg_confGUI(root)   # Build the GUI.
            root.mainloop()   # Display it and let is operate...
    '''
    def __init__(self,parent,config):
        ''' Input:
               parent : tkinter parent widget
               config : applicationConfig object (the webGobbler configuration)
        '''
        self._parent = parent
        self.imageLabel = None          # The widget which displays the image.
        self.config = config            # The main webGobbler configuration
        self.assembler = webgobbler.assembler_superpose(pool=webgobbler.imagePool(config=config),config=config) # The assembler (which creates images)
        self.assembler.start()  # Start the assembler. (The assembler and collectors will work in background.)
        self._parent.protocol("WM_DELETE_WINDOW", self.handlerExit)  # Catch the "close window" event sent by the window manager.
        self.lastImageDate = None       # Date when last image was generated.
        self.lastImage = None           # Last generated image (PIL Image object.)
        self.closing = False            # If True, the application is currently closing (probably waiting for network connections to close.)
        self.currentlyAssembling = False # Is the assemble currently assembling ?
        self._widgets= {}               # List of stateful widgets
    

        self._initializeGUI()  # Create the GUI
        self.setStatus("webGobbler running.")
        self.timerCollectorsStatus = self._parent.after(250, self._updateCollectorStatus) 
        
        self._updateImage()   # Regularly update the image from the assembler. 
        self.handlerGenerateNow()  # Generate a new image right now.
   
    def _setCollectorStatus(self,collectorName,status,information):
        ''' Sets the collector status and info.
            Input : 
                collectorName (string) : the name of the collector (eg."collector_googleimages")
                status (string) : Status to display (eg."Downloading")
                information (string) : information to display (eg."http://...")
                
                If collectorName does not exist, does nothing.
        '''
        widgets = (None, None)
        if collectorName == "collector_googleimages"      : widgets = (self.googleStatus,self.googleInfo)
        elif collectorName == "collector_yahooimagesearch": widgets = (self.yahooStatus,self.yahooInfo)
        elif collectorName == "collector_flickr"          : widgets = (self.flickrStatus,self.flickrInfo)
        elif collectorName == "collector_deviantart"      : widgets = (self.deviantArtStatus,self.deviantArtInfo)
        elif collectorName == "collector_local"           : widgets = (self.localdiskStatus,self.localdiskInfo)

        # If there is such widget, display its status:
        if widgets != (None,None):
            widgets[0].configure(text=status)       
            widgets[1].configure(text=information)      
   
    def _updateCollectorStatus(self):
        ''' Update the collectors status on screen. 
            This method is called every 0.5 seconds.
        '''
        # We poll each collector status every second.
        
        # The known collectors:
        visitedCollectors = { "collector_googleimages": False,
                               "collector_yahooimagesearch": False,
                               "collector_flickr": False,
                               "collector_deviantart": False,
                               "collector_local": False
                             }

        # Get the status of all collectors present in the assembler's pool:                     
        for collector in self.assembler.pool.collectors:
            # Get the status of this collector:
            (status,information) = collector.getCurrentStatus()   # .getCurrentStatus() is thread safe.
            # Set this information in the GUI:
            self._setCollectorStatus(collector.name,status,information)
            # Now mark this collector as "visited".
            visitedCollectors[collector.name] = 1
        
        # Now put status "Stop" in all collectors we could not get status from.
        # (If they are not present in the assembler's pool, it means they
        # are de-activated)
        for (collectorName,visited) in visitedCollectors.items():
            if not visited:
                self._setCollectorStatus(collectorName,'Off','')
        
        self.poolSize.configure(text = "%d on %d" % ( self.assembler.pool.getPoolSize(),self.config['pool.nbimages']))
        

        # Superpose a new image if delay is elapsed:
        if time.time() > (self.lastImageDate + self.config["program.every"]) and not self.currentlyAssembling:
            self._superpose()
        # Update also the state of the assembler:       
        assemblerText = self.assembler.state
        if not self.currentlyAssembling and not self.closing:
             assemblerText += "  (Next image in %d seconds)" % (int(self.lastImageDate + self.config["program.every"]- time.time()+1) )
        self.assemblerState.configure(text=assemblerText)

        self.timerCollectorsStatus = self._parent.after(250, self._updateCollectorStatus)  # 0.25 seconds
        
        
   
    def _updateImage(self):
        ''' Update the image in window from the assembler.
            This method will be automatically call every second by the Tkinter main loop timer.
        '''
        # We pool the assembler every second to see if it has generated a new
        # image.
        # If it has, we try to get the image and display it. 
        if self.lastImageDate != self.assembler.finalImageCompletionDate and not self.closing:
            # Get the new image:
            image = self.assembler.getImage()
            if image != None:
                self.lastImage = image  # Keep a reference of the PIL Image object.
                # Display the image:
                photo = ImageTk.PhotoImage(image)
                self.imageLabel.configure(image=photo)
                self.imageLabel.photo = photo  # Keep a reference, otherwise the widget will not display the image.
                self.lastImageDate = self.assembler.finalImageCompletionDate
                self._setWallpaper()
                self.currentlyAssembling = False
                self._widgets['updateimage.button'].configure(state='normal')  # Enable the "Update image" button
                
                # If the "Auto-save" checkbox is checked, save the image.
                if self._widgets['autosave.value'].get()!=0:
                   filename = time.strftime("%Y%m%d_%H%M%S")+".bmp"
                   self.setStatus("Saving image as %s..." % filename)
                   self.lastImage.save(filename)
                self.setStatus("webGobbler running.")
                
        # If the application is closing and the assembler has died, we can destroy the window.
        if self.closing and not self.assembler.isAlive():            
            self.assembler.join()
            self._parent.destroy()
        
        self.timerUpdateimage = self._parent.after(1000, self._updateImage)  # Re-arm the timer.

    # FIXME: display errors ?  (network errors, etc. ?)
    # FIXME: redirect webGobbler stdout/stderr to a text widget ?

    def _setWallpaper(self):
        # FIXME: Ctypes does not mean we are under windows !
        if CTYPES_AVAILABLE and self.setAsWallpaper.get() != 0:
            # Set this image as wallpaper:
            if sys.platform == "win32":
                filepath = os.path.join(self.config['persistencedirectory'],'wallpaper.bmp')
                self.lastImage.save(filepath)
                SPI_SETDESKWALLPAPER = 20 # According to http://support.microsoft.com/default.aspx?scid=97142
                ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, filepath , 0)                       
            # FIXME: Implement for Gnome and KDE.

    def _superpose(self):
        ''' Ask the assembler to superpose new images regularly.
            This method will be automatically call by the Tkinter main loop timer.        
        '''
        if self.closing: return
        if self.currentlyAssembling: return
        self.currentlyAssembling = True
        self._widgets['updateimage.button'].configure(state='disabled')  # Disable the "Update image" button
        self.setStatus('Updating current image (%d x %d).' % (self.config['assembler.sizex'],self.config['assembler.sizey']))
        self.assembler.superpose()  # (This is a non-blocking call.)
        
    def loadConfig(self,appConfig=None):
        ''' Read webGobbler configuration from registry or .INI file.
            If the registry is not available, the .ini file will be read.
            If the .ini file is not available, the default configuration will be used.
        '''
        self.setStatus("Loading configuration.")
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
                #self.handlerConfigure()  # Display configuration screen right now.
        
    def _initializeGUI(self):
        ''' This method creates all the GUI widgets. '''

        smallFont = tkFont.Font(size=-11) 
        smallFontBold = tkFont.Font(size=-11,weight='bold') 
                
        # ======================================================================
        # Create the menu        
        mainmenu = Tkinter.Menu(self._parent)
        self._parent.config(menu=mainmenu)        
        filemenu = Tkinter.Menu(mainmenu)
        mainmenu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Start new image from scratch",command=self.handlerStartNewImage)
        filemenu.add_command(label="Update current image now",command=self.handlerGenerateNow)
        filemenu.add_separator()
        filemenu.add_command(label="Save as...",command=self.handlerSaveAs)
        filemenu.add_separator()
        filemenu.add_command(label="Exit",command=self.handlerExit)
        
        optionsMenu = Tkinter.Menu(mainmenu)
        mainmenu.add_cascade(label="Options", menu=optionsMenu)
        optionsMenu.add_command(label="Configure...", command=self.handlerConfigure)
        
        v = Tkinter.IntVar()
        self.setAsWallpaper = v
        
        if sys.platform=="win32" and CTYPES_AVAILABLE:
            # (If ctypes is not available, we won't be able to set the Windows wallpaper,
            # so let's disable the option.)
            cb = optionsMenu.add_checkbutton(label='Set as wallpaper',variable=v,command=self.handlerSetAsWallpaper)
        # FIXME: Implement this option for Gnome and KDE.
                
        helpmenu = Tkinter.Menu(mainmenu)
        mainmenu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About...", command=self.handlerAbout)
        
        
        # ======================================================================
        # The buttons area (Save, Update now, etc.)
        self.buttonsArea = Tkinter.Frame(self._parent)
        self.buttonsArea.grid(column=1,row=0,sticky='ewn',padx=3)
        
        self.saveButton = Tkinter.Button(self.buttonsArea,text="Save\nimage",command=self.handlerSaveAsForButton)
        self.saveButton.grid(column=0,row=0,sticky='EW',padx=3)
        
        v = Tkinter.IntVar(); self._widgets['autosave.value'] = v
        self._widgets['autosave.checkbox'] = Tkinter.Checkbutton(self.buttonsArea,variable=v,text="Auto-save")
        self._widgets['autosave.checkbox'].grid(column=0,row=1,sticky='W',padx=3)       
        
        self._widgets['updateimage.button'] = Tkinter.Button(self.buttonsArea,text="Update\nimage",command=self.handlerGenerateNow)
        self._widgets['updateimage.button'].grid(column=0,row=2,sticky='EWS',padx=3,pady=20)
        
        # ======================================================================
        # The status bar
        self.statusFrame = Tkinter.Frame(self._parent)
        #self.statusFrame.pack(side='top',fill='x',expand=1)      
        self.statusFrame.grid(column=0,row=0,sticky='ew')
        
        # The Google status:
        Tkinter.Label(self.statusFrame,text='Google',anchor='w',bd=1,relief='sunken',font=smallFontBold).grid(column=0,row=0,sticky='ew')
        self.googleStatus = Tkinter.Label(self.statusFrame,text="Off",anchor='w',bd=1,relief='sunken',font=smallFont);  self.googleStatus.grid(column=1,row=0,sticky='ew')
        self.googleInfo = Tkinter.Label(self.statusFrame,text="",anchor='w',bd=1,relief='sunken',font=smallFont); self.googleInfo.grid(column=2,row=0,sticky='ew')
        
        # The Yahoo status:
        Tkinter.Label(self.statusFrame,text='Yahoo',anchor='w',bd=1,relief='sunken',font=smallFontBold).grid(column=0,row=1,sticky='ew')
        self.yahooStatus = Tkinter.Label(self.statusFrame,text="Off",anchor='w',bd=1,relief='sunken',font=smallFont); self.yahooStatus.grid(column=1,row=1,sticky='ew')
        self.yahooInfo = Tkinter.Label(self.statusFrame,text="",anchor='w',bd=1,relief='sunken',font=smallFont); self.yahooInfo.grid(column=2,row=1,sticky='ew')

        # The Flickr status:
        Tkinter.Label(self.statusFrame,text='Flickr',anchor='w',bd=1,relief='sunken',font=smallFontBold).grid(column=0,row=3,sticky='ew')
        self.flickrStatus = Tkinter.Label(self.statusFrame,text="Off",anchor='w',bd=1,relief='sunken',font=smallFont); self.flickrStatus.grid(column=1,row=3,sticky='ew')
        self.flickrInfo = Tkinter.Label(self.statusFrame,text="",anchor='w',bd=1,relief='sunken',font=smallFont); self.flickrInfo.grid(column=2,row=3,sticky='ew')
        
        # The DeviantArt status:
        Tkinter.Label(self.statusFrame,text='DeviantArt',anchor='w',bd=1,relief='sunken',font=smallFontBold).grid(column=0,row=4,sticky='ew')
        self.deviantArtStatus = Tkinter.Label(self.statusFrame,text="Off",anchor='w',bd=1,relief='sunken',font=smallFont); self.deviantArtStatus.grid(column=1,row=4,sticky='ew')
        self.deviantArtInfo = Tkinter.Label(self.statusFrame,text="",anchor='w',bd=1,relief='sunken',font=smallFont); self.deviantArtInfo.grid(column=2,row=4,sticky='ew')

        # The local disk status:
        Tkinter.Label(self.statusFrame,text='Local disk',anchor='w',bd=1,relief='sunken',font=smallFontBold).grid(column=0,row=5,sticky='ew')
        self.localdiskStatus = Tkinter.Label(self.statusFrame,text="Off",anchor='w',bd=1,relief='sunken',font=smallFont); self.localdiskStatus.grid(column=1,row=5,sticky='ew')
        self.localdiskInfo = Tkinter.Label(self.statusFrame,text="",anchor='w',bd=1,relief='sunken',font=smallFont); self.localdiskInfo.grid(column=2,row=5,sticky='ew')
        
        # The pool state:
        Tkinter.Label(self.statusFrame,text='Number of images in pool:',anchor='w',bd=1,relief='sunken',font=smallFontBold).grid(column=0,row=6,sticky='ew',columnspan=2)
        self.poolSize = Tkinter.Label(self.statusFrame,text="",anchor='w',bd=1,relief='sunken',font=smallFont); self.poolSize.grid(column=2,row=6,sticky='ew')

        # The image assembler state:
        Tkinter.Label(self.statusFrame,text='Image assembler:',anchor='w',bd=1,relief='sunken',font=smallFontBold).grid(column=0,row=7,sticky='ew',columnspan=2)
        self.assemblerState = Tkinter.Label(self.statusFrame,text="Waiting",anchor='w',bd=1,relief='sunken',font=smallFont); self.assemblerState.grid(column=2,row=7,sticky='ew')
        
        
        # Allow the information columns to expand
        self.statusFrame.columnconfigure(1,minsize=95)
        self.statusFrame.columnconfigure(2,weight=1,minsize=200)

        
        # ======================================================================
        # The scrollable frame which contains the image:
        sf = Pmw.ScrolledFrame(self._parent)
        sf.grid(column=0,row=1,stick='news',columnspan=2)
        self.imageLabel = Tkinter.Label(sf.interior())  # This widget will hold the image.
        self.imageLabel.pack(fill='both', expand=1)
        
        # ======================================================================
        # The status bar.
        statusFrame = Tkinter.Frame(self._parent,bd=1,relief='sunken')
        statusFrame.grid(column=0,row=2,sticky='ew',columnspan=2)
        self.statusLabel = Tkinter.Label(statusFrame,text="",anchor='w',font=smallFont)
        self.statusLabel.grid(column=0,row=0,sticky='w')
        statusFrame.grid_columnconfigure(0,weight=1)
        
        # Configure auto-resize of widgets:
        self._parent.rowconfigure(1,weight=1,minsize=0)
        self._parent.columnconfigure(0,weight=1,minsize=200)

        # Prevent the Window to resize if a long URL is displayed:
        self._parent.propagate(False)
        
        # Default window geometry is 1x1+0+0, which is "autosize".
        # When this geometry is used, the window automatically resizes
        # despite the self._parent.propagate(False)
        # So we force the Window geometry:
        self._parent.geometry('500x400')
        

    def setStatus(self,text):
        ''' Set the status bar text. '''
        self.statusLabel.configure(text=text)
     
    def handlerExit(self):
        # Note about the line below:
        # When I issue a self.assembler.shutdown() command, all threads
        # finish their download first before dying.
        # That's why the main webGobbler window does not close immediately
        # when you choose "Exit". This is confusing for some users.
        # Workaround: I hide the main window immediately (self._parent.withdraw())
        # The threads will finish their job in the background.
        # It would be better if I could kill each thread immediately,
        # but I found no way to do this in Python.
        self._parent.withdraw()  # Hide the root window immediately.
        if self.config['collector.localonly']:
            self.setStatus("Closing - Please wait...")
        else:
            self.setStatus("Finishing current downloads - Please wait...")
        self.assembler.shutdown()
        self.closing = True
    
    def handlerAbout(self):
        import webgobbler_config       
        wgconfig = webgobbler_config.wg_confGUI(None)  # Display webGobbler configuration screen.
        wgconfig.focus_set()        
        wgconfig.showAbout()
        self._parent.wait_window(wgconfig.top)  # Wait for window to close.
    
    def handlerConfigure(self):
        import webgobbler_config       
        # FIXME: grey out menues so that user does not call the config Windows several times at once.
        wgconfig = webgobbler_config.wg_confGUI(None)  # Display webGobbler configuration screen.
        # webGobbler configuration windows will read configuration from registry or .ini file.
        wgconfig.focus_set()        
        self._parent.wait_window(wgconfig.top)  # Wait for window to close.
        if wgconfig.configChanged:
            # Configuration was changed. 
            self.config = wgconfig.config   # Get the new configuration
            # Kill the old assembler:
            self.assembler.shutdown()   
            #self.assembler.join()
            
            # Set the new proxy address (if any)
            self.config = webgobbler.setUrllibProxy(log=None,CONFIG=self.config)
            
            # Start a new assembler with this new configuration:
            self.assembler = webgobbler.assembler_superpose(pool=webgobbler.imagePool(config=self.config),config=self.config)
            self.assembler.start()
     
    def handlerGenerateNow(self):
        if self.currentlyAssembling: return
        self.currentlyAssembling = True
        self._widgets['updateimage.button'].configure(state='disabled') # Disable the "Update image" button
        self.setStatus('Updating current image (%d x %d).' % (self.config['assembler.sizex'],self.config['assembler.sizey']))
        self.assembler.superpose()  # (This is a non-blocking call.)

    def handlerSaveAs(self):
        # Praise tkFileDialog !   This couldn't be easier.   :-)
        saveAsName = tkFileDialog.asksaveasfilename(parent=self._parent,defaultextension='png',initialfile=time.strftime("%Y%m%d_%H%M%S"),filetypes=SAVE_FORMATS,title='Save image as...')
        if len(saveAsName) > 0:
            self.setStatus("Saving image - Please wait...")
            self.lastImage.save(saveAsName)
            self.setStatus("Image saved.")

    def handlerSaveAsForButton(self):
        saveAsName = tkFileDialog.asksaveasfilename(parent=self._parent,defaultextension='bmp',initialfile=time.strftime("%Y%m%d_%H%M%S"),filetypes=SAVE_FORMATS,title='Save image as...')
        if len(saveAsName) > 0:
            self.setStatus("Saving image - Please wait...")
            self.lastImage.save(saveAsName)
            self.setStatus("Image saved.")

    def handlerStartNewImage(self):
        dialog = Pmw.MessageDialog(self._parent,  title = 'Confirmation',
                 message_text = 'Do you really want to discard current image and start a new one ?',
                 buttons = ('Yes,\nstart new image', 'NO,\nkeep current image'),
                 defaultbutton = 'NO,\keep current image')
        result = dialog.activate()     
        dialog.withdraw()
        if result == 'Yes,\nstart new image':
            self.assembler.shutdown()     # Stop current assembler.
            #self.assembler.join()
            # Start a new assembler with this new configuration:
            self.assembler = webgobbler.assembler_superpose(pool=webgobbler.imagePool(config=self.config),config=self.config,ignorePreviousImage=True)
            self.assembler.start()
            self.handlerGenerateNow()  # Generate a new image right now.
            
    
    def handlerSetAsWallpaper(self):
        self._setWallpaper()



if __name__ == "__main__":
    main()



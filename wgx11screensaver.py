# -*- coding: iso-8859-1 -*-

# This module, his ideas and his code is hugely inspired from any documentation and examples which can be found on these url:
# http://www.essi.fr/~buffa/cours/X11_Motif/cours/XlibWindows.html
# http://tronche.com/gui/x/xlib/function-index.html
# http://xander.ncl.ac.uk/game/index1.php
# PIL documentation: http://www.pythonware.com/library/pil/handbook/introduction.htm
# http://users.actcom.co.il/~choo/lupg/tutorials/xlib-programming/xlib-programming-2.html
# Code from wgwin32screensaver's module written by SebSauvage
# [...]
# Thanks a lot!! :-)

# 12 April 2006
# _ Minor corrections.
# _ Hide the cursor when the screensaver is running

import time, threading, os, logging
try:
    import ctypes
except ImportError:
    raise ImportError, "The ctypes module is required for module wgx11screensaver. See http://starship.python.net/crew/theller/ctypes/"

# XSetWindowAttributes Structure defined in X11/Xlib.h. It contains the attributes of a X window.
# We need it to change the override_redirect field to get a full screen window
class XSetWindowAttributes(ctypes.Structure):
    _fields_ = [("background_pixmap",ctypes.c_ulong),
            ("background_pixel",ctypes.c_ulong),
            ("border_pixmap",ctypes.c_ulong),
            ("border_pixel",ctypes.c_ulong),
            ("bit_gravity",ctypes.c_int),
            ("win_gravity",ctypes.c_int),
            ("backing_store",ctypes.c_int),
            ("backing_planes",ctypes.c_ulong),
            ("backing_pixel",ctypes.c_ulong),
            ("save_under",ctypes.c_byte),#Bool type
            ("event_mask",ctypes.c_long),
            ("do_not_propagate_mask",ctypes.c_long),
            ("override_redirect",ctypes.c_int),#Bool type
            ("colormap",ctypes.c_ulong),#Colormap type
            ("cursor",ctypes.c_ulong)]
    
# XGCValues Structure defined in X11/Xlib.h. You can see there the graphical context values
# We need the foreground field to set the color of the pixels from an image to a window
class XGCValues(ctypes.Structure):
    _fields_ = [("function",ctypes.c_int),
            ("plane_mask",ctypes.c_ulong),
            ("foreground",ctypes.c_ulong),
            ("background",ctypes.c_ulong),
            ("line_width",ctypes.c_int),
            ("line_style",ctypes.c_int),
            ("cap_style",ctypes.c_int),
            ("join_style",ctypes.c_int),
            ("fill_style",ctypes.c_int),
            ("fill_rule",ctypes.c_int),
            ("arc_mode",ctypes.c_int),
            ("tile",ctypes.c_ulong), #Pixmap type
            ("stipple",ctypes.c_ulong), #Pixmap type
            ("ts_x_origin",ctypes.c_int),
            ("ts_y_origin",ctypes.c_int),
            ("font",ctypes.c_ulong),#Font type
            ("subwindow_mode",ctypes.c_int),
            ("graphics_exposures",ctypes.c_int),#Bool type
            ("clip_x_origin",ctypes.c_int),
            ("clip_y_origin",ctypes.c_int),
            ("clip_mask",ctypes.c_ulong),#Pixmap type
            ("dash_offset",ctypes.c_int),
            ("dashes",ctypes.c_byte)]

# XEvent Structure defined in X11/Xlib.h. It contains the datas about an Event queued in a Window.
# It's like a MSG in Microsoft Windows API
class XEvent(ctypes.Structure):
    # We only need the "type" field.
    # The whole Structure is 96 bytes long (given by sizeof C operator, sum of all fields is lesser). "type" is 4 octets. 
    # We don't need to describe other fields which are complex Structure types.
    # It would be too hard to define them. We only need to define their size so we summarize them in a tab of 92 bytes
    _fields_ =[("type",ctypes.c_int),
        ("all_other",ctypes.c_byte * 92)] 

# XColor Structure defined in X11/Xlib.h. It contains a color's properties
class XColor(ctypes.Structure):
    _fields_ = [("pixel",ctypes.c_ulong),
        ("rgb",ctypes.c_ushort * 3), # It is usually three distinct shorts: short r,g,b;
        ("flags",ctypes.c_byte),
        ("pad",ctypes.c_byte)]

# Xlib constants defined in X11/X.h
class X11_con:
    GCForeground=1L<<2
    CWOverrideRedirect=1L<<9
    CWCursor=1L<<14
    KeyPressMask=1L<<0
    RevertToParent=2
    CurrentTime=0L
    KeyPress= 2
    

class x11screensaver(threading.Thread):
    '''The ScreenSaver Class which deals with X11 API. It works in a single Thread.
    Operations related to X11 have to be in the same thread unless you want to get X11 request errors.
    Unlike Microsoft Windows's WNDPROC Callback function, the window events can be processed outside the main Thread, 
    but have to be in the same thread than other x11 operations'''

    def __init__(self, config):
        threading.Thread.__init__(self)
        # Find your xlib path
        xlib_path=get_unix_lib('libX11.so')
        if not xlib_path:
            no_xlib()
        self.xlib=ctypes.CDLL(xlib_path)
        self.width=config['assembler.sizex']
        self.height=config['assembler.sizey']
        self.quit=False # When True => this thread has to stop itself
        self.img=None   # The image pixels given by the assembler and PIL
        
        # Connection to the X-server
        self.display=self.xlib.XOpenDisplay(0)
        if self.display == 0:
            raise OSError, "I can't connect to your X server. Did you launch it?"
        # Default Screen
        self.screen=self.xlib.XDefaultScreen(self.display)
        # The window parent
        self.rootwin=ctypes.c_ulong(self.xlib.XRootWindow(self.display, self.screen) )
        # This pixmap is stored in memory. We will use it like a temporary buffer to store the image's pixels and to display them easily
        self.pixmap=self.xlib.XCreatePixmap(self.display,self.rootwin,self.width,self.height,self.xlib.XDefaultDepth(self.display,self.screen) )
        # Our window
        self.window=self.xlib.XCreateSimpleWindow(self.display, self.rootwin, 0, 0, self.width, self.height, 0, 0x000000, 0x000000);
                
        # Create a black one-pixel pixmap to attribute it on our cursor. It will almost hide the cursor...
        # Inspired by XYZ library http://www.koders.com/c/fid4756155F1F6C96F218F55D5A29D7AF1F5FEAE246.aspx (see yzHideCursor() function ).
        cursor_pix=self.xlib.XCreatePixmap(self.display, self.rootwin, 1, 1, 1)
        cursor_color=XColor()
        cursor_color.rgb=(0, 0, 0)
        
        # Change any attributes of our window       
        self.win_attributes=XSetWindowAttributes()
        # Set the one-pixel cursor on our window
        self.win_attributes.cursor=self.xlib.XCreatePixmapCursor(self.display, cursor_pix, 0, ctypes.byref(cursor_color), ctypes.byref(cursor_color), 0, 0)
        # Override Redirect
        self.win_attributes.override_redirect=1 # Set with TRUE, this value will let us get a full screen Window
        # Apply
        self.xlib.XChangeWindowAttributes(self.display, self.window, X11_con.CWOverrideRedirect | X11_con.CWCursor, ctypes.byref(self.win_attributes ) )

        # Get a Graphical Context on our Pixmap with a default black colored foreground "pencil"
        self.gc_values=XGCValues()
        self.gc_values.foreground=0x000000
        self.gc=self.xlib.XCreateGC(self.display, self.pixmap, X11_con.GCForeground, ctypes.byref(self.gc_values) )
        # Display this window
        self.xlib.XMapWindow(self.display, self.window) 
        # We only want to receive the "KeyPress" Events (but we will process the mouse-move events too)
        self.xlib.XSelectInput(self.display, self.window, X11_con.KeyPressMask)
        # Focus on our Window
        self.xlib.XSetInputFocus(self.display,self.window, X11_con.RevertToParent, X11_con.CurrentTime) 
        self.xlib.XFlush(self.display)

        # Get the mouse position
        mouse_pos=self.get_mouse_pos()
        self.mouse_x=mouse_pos[0]
        self.mouse_y=mouse_pos[1]

    def set_image(self,img):
        '''Let the assembler send us an Image. Only a list of Pixel 
        values is accepted. Each Pixel should be a tuple of three (R/G/B) values'''
        # Wait if the previous image is still processing
        while self.img:
            if self.quit: return # If this thread is leaving, we don't need to wait with this new image
            time.sleep(0.05)
        self.img=img
    
    def paint_image(self):
        '''Paint the image stored in self.img to the screen.
        FIXME: This method is really slow (almost 12 sec on an Athlon XP 2000) because all pixels have to be merged and set one by one
        on a Pixmap buffer. And the GC foreground s'color have to be changed for each pixel'''

        if not self.img: # No image queued at this time
            time.sleep(0.05) # CPU....
            return
        k=0 # the current pixel in our image
        # Set all the pixels
        for i in range(self.height):
            if i%3: self.msgproc() # All three lines of pixels processed, we launch the Event Process to check KeyPress and Mouse Moves.
            if self.quit:return
            for j in range(self.width):
                # Merge the (R/G/B) values of this pixel
                self.gc_values.foreground=(self.img[k][0] << 16) | (self.img[k][1] << 8) | self.img[k][2]
                k+=1
                # Draw this point in pixmap buffer
                self.xlib.XChangeGC(self.display, self.gc, X11_con.GCForeground, ctypes.byref(self.gc_values) )
                self.xlib.XDrawPoint(self.display, self.pixmap, self.gc, j, i)
        # Copy this Pixmap in our window
        self.xlib.XCopyArea(self.display, self.pixmap, self.window, self.gc, 0, 0, self.width, self.height, 0, 0)
        self.xlib.XFlush(self.display)
        self.img=None # Erase this old image

    def shutdown(self):
        '''Launch it everywhere to stop this thread'''
        # Close this window
        self.xlib.XDestroyWindow(self.display, self.window)
        self.xlib.XCloseDisplay(self.display)
        self.msgproc=lambda:None # Do not check events from a no more existent display to avoid segmentation fault
        self.quit=True

    def run(self):
        '''Main Loop of this thread'''
        while not self.quit:
            self.paint_image()
            self.msgproc() # We just processed an image or we have no one. So we process the Window Events

    def get_mouse_pos(self):
        '''Get the mouse position on our window'''
        mask=ctypes.c_uint()
        child=ctypes.c_ulong()
        root_x=ctypes.c_int()
        root_y=ctypes.c_int()
        current_x=ctypes.c_int()
        current_y=ctypes.c_int()

        self.xlib.XQueryPointer(self.display, self.window, ctypes.byref(self.rootwin), ctypes.byref(child), ctypes.byref(root_x), ctypes.byref(root_y), ctypes.byref(current_x), ctypes.byref(current_y), ctypes.byref(mask))
        return tuple( (current_x.value, current_y.value) )
        
    def msgproc(self):
        '''Window Event processing. It not a traditionnal one because we don't check the mouse movements toward the Window Events'''
        mouse_pos=self.get_mouse_pos()
        current_x=mouse_pos[0]
        current_y=mouse_pos[1]
        # FIXME: It compare mouse position with the initial one. Can I do this with the events?
        if abs(self.mouse_x - current_x)>=10  or abs(self.mouse_y - current_y)>=10: #If mouse moved in 10 pixel: shutdown
            self.shutdown()
            return

        # Check the events
        event=XEvent()
        num_events=self.xlib.XPending(self.display)
        while(num_events):
            self.xlib.XNextEvent(self.display, ctypes.byref(event) )
            # If you pressed any key. I will close this window
            if event.type == X11_con.KeyPress:
                self.shutdown()
                return
            num_events-=1

def no_xlib():
    '''Raise an error if we can't find your xlib'''

    raise OSError, '''I can't find your X11 protocol client shared library. 
    You should verify that "Xlib" package is installed on your machine.
    For example this package is called "libx11-6" on a Debian Gnu/Linux system.
    If you suspect a bug or need help, please send me an email at chantecode@gmail.com
    I would appreciate to get the result of these three commands in your machine in attachment of this email:
    ls -lR /usr/X11R6
    ls -lR /usr/lib
    ls -lR /lib
    Please write the name and the version of your Unix/Linux distribution.
    Thanks'''           
            
def get_unix_lib():
    '''Same as get_unix_lib in webgobbler.py (will be defined on it)'''
    pass
    

def getScreenResolution():
    '''Find the resolution of the screen in a x environment'''

    xlib_path=get_unix_lib('libX11.so')
    if not xlib_path:
        no_xlib()
    xlib=ctypes.CDLL(xlib_path)
    # Connect to the x server...
    display=xlib.XOpenDisplay(0)    
    if display == 0:
        raise OSError, "I can't connect to your X server. Did you launch it?"
    screen=xlib.XDefaultScreen(display)
    # Get the height and width and return it in a tuple: (x, y)
    height=xlib.XDisplayHeight(display, screen)
    width=xlib.XDisplayWidth(display, screen)
    xlib.XCloseDisplay(display)
    return (width, height)
    

def generateNewImage(assembler_sup,config,wsaver):
    '''Almost the same function than in wgwin32screensaver module'''

    log = logging.getLogger('XWindowScreensaver')    
    log.info("Generating a new image now with %d new images" % config["assembler.superpose.nbimages"])
    log.info("XWindowScreensaver: (Next image in %d seconds.)" % config["program.every"])
    assembler_sup.superposeB()   # Generate new image
    image = assembler_sup.getImage()
    if image != None:
        wsaver.set_image(image.getdata())  # Send the image to the screensaver.



def Loop(assembler_sup, config):
    ''' Create the screensaver window thread and query images to the assembler (inspired by wgwin32screensaver.messageLoop)'''
    
    # Launch x11screensaver thread
    wsaver = x11screensaver(config)
    wsaver.start()
    wsaver.set_image(assembler_sup.getImage().getdata() )
    
    log = logging.getLogger('XWindowScreensaver')
    log.info("Next image in %d seconds." % config["program.every"])

    # Start to generate a new images right now.    
    generateImageThread = threading.Thread(target=generateNewImage, args=(assembler_sup,config,wsaver))
    generateImageThread.start()
    start_time = time.time()

    while wsaver.isAlive():  # While the display thread has not died, send him images
        # Is delay elapsed ?  If yes, generate a new image.
        if (time.time()-start_time > config["program.every"]) or (time.time()<start_time):
            if (generateImageThread==None or (not generateImageThread.isAlive())):  # If we have no thread or the thread has completed:
                    # We start image generation in a new thread so that the screensaver windows
                    # is more responsive and close as soon as mouse is moved.
                    # (Even if the image generation and collector threads are still running.)
                    generateImageThread = threading.Thread(target=generateNewImage, args=(assembler_sup,config,wsaver))
                    generateImageThread.start()
                    start_time = time.time()
            
        time.sleep(0.05)  # Ben gentle on CPU usage.

    # Close threads
    assembler_sup.shutdown()
    if generateImageThread.isAlive():
        generateImageThread.join()



#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
import threading
import Queue
import time
import logging

try:
    import ctypes
except ImportError:
    raise ImportError, "The ctypes module is required for module wgwin32screensaver. See http://starship.python.net/crew/theller/ctypes/"
    
try:
    import ImageWin
except ImportError:
    raise ImportError, "The ImageWin module of the library PIL (Python Imaging Library) is required for module wgwin32screensaver. See http://www.pythonware.com/products/pil/"

class win32con:
    ''' Win32 API constants (required for the screensaver) '''
    BLACK_BRUSH = 4
    CS_HREDRAW = 2
    CS_VREDRAW = 1
    PM_NOREMOVE = 0
    SM_CXSCREEN = 0
    SM_CYSCREEN = 1    
    SW_SHOW = 5
    SW_SHOWNORMAL = 1
    SWP_NOMOVE = 2
    SWP_NOSIZE = 1
    WM_CLOSE = 16
    WM_DESTROY = 2
    WM_KEYDOWN = 256
    WM_LBUTTONDOWN = 513
    WM_MBUTTONDOWN = 519
    WM_MOUSEMOVE = 512
    WM_PAINT = 15
    WM_QUIT = 18
    WM_RBUTTONDOWN = 516
    WS_EX_TOPMOST = 8
    WS_POPUP = 0x80000000L
    WS_VISIBLE = 0x10000000


# Structures used to communicate with Windows API and callbacks:

# Note: A large part of code in this module is heavily inspired from
#       http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/208699

WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, ctypes.c_uint, ctypes.c_int, ctypes.c_int)
class WNDCLASS(ctypes.Structure):
    _fields_ = [('style', ctypes.c_uint),
                ('lpfnWndProc', WNDPROC),
                ('cbClsExtra', ctypes.c_int),
                ('cbWndExtra', ctypes.c_int),
                ('hInstance', ctypes.c_int),
                ('hIcon', ctypes.c_int),
                ('hCursor', ctypes.c_int),
                ('hbrBackground', ctypes.c_int),
                ('lpszMenuName', ctypes.c_char_p),
                ('lpszClassName', ctypes.c_char_p)]

class RECT(ctypes.Structure):
    _fields_ = [('left', ctypes.c_long),
                ('top', ctypes.c_long),
                ('right', ctypes.c_long),
                ('bottom', ctypes.c_long)]

class PAINTSTRUCT(ctypes.Structure):
    _fields_ = [('hdc', ctypes.c_int),
                ('fErase', ctypes.c_int),
                ('rcPaint', RECT),
                ('fRestore', ctypes.c_int),
                ('fIncUpdate', ctypes.c_int),
                ('rgbReserved', ctypes.c_char * 32)]
                
class POINT(ctypes.Structure):
    _fields_ = [('x', ctypes.c_long),
                ('y', ctypes.c_long)]
                
class MSG(ctypes.Structure):
    _fields_ = [('hwnd', ctypes.c_int),
                ('message', ctypes.c_uint),
                ('wParam', ctypes.c_int),
                ('lParam', ctypes.c_int),
                ('time', ctypes.c_int),
                ('pt', POINT)]
        
class wgwin32screensaver(threading.Thread):
    ''' A screensaver class based entirely on ctypes.
        Requires the call to handle the GetMessageA/TranslateMessage/DispatchMessageA loop itself.
    '''
    
    def __init__(self,imagedib=None):
        ''' Starts the screensaver.
            imagedib is an optionnal PIL ImageWin.Dib object
        '''
        threading.Thread.__init__(self)
        self.inputqueue = Queue.Queue()  # Put new images to display here (PIL ImageWin.Dib objects)
        self.mousmove_count = 0   # Count how many times Windows has sent use the WM_MOUSEMOVE message.
        
        #open("\messages.log","a").write(str(id(self))+ " - " + str(time.time())+" : START ---------------------------------------\n")        
        
        # Get current screen resolution:
        self.screen_resolution = ( ctypes.windll.user32.GetSystemMetrics(win32con.SM_CXSCREEN), ctypes.windll.user32.GetSystemMetrics(win32con.SM_CYSCREEN) )
        
        self.currentImage = imagedib  # the current image to display (a PIL ImageWin.Dib object)
        self.closing = False;  # We are not closing.
        
        # Prepare the parameters of the window we are about to create.
        # See: http://msdn.microsoft.com/library/en-us/winui/winui/windowsuserinterface/windowing/windowclasses/windowclassreference/windowclassstructures/wndclassex.asp
        self.windowInfo = WNDCLASS()
        self.windowInfo.lpszClassName = "WebGobblerScreenSaver"
        #self.windowInfo.hbrBackground = ctypes.windll.gdi32.GetStockObject(win32con.BLACK_BRUSH)  # Not really necessary.
        self.windowInfo.hInstance = ctypes.windll.kernel32.GetModuleHandleA(None)
        self.windowInfo.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        self.windowInfo.lpfnWndProc = WNDPROC(self.WndProc) # WndProc will be our window callback
        self.windowInfo.cbClsExtra = self.windowInfo.cbWndExtra = 0
        self.windowInfo.lpszMenuName = None
    
        # Pass our window parameters to Windows API
        if not ctypes.windll.user32.RegisterClassA(ctypes.byref(self.windowInfo)):
            raise WinError()    
            
        # And create the window (borderless, fullscreen, always on top)
        self.hwnd_screensaver = ctypes.windll.user32.CreateWindowExA(win32con.WS_EX_TOPMOST,
                                    "WebGobblerScreenSaver",
                                    "WebGobbler Screensaver",
                                    win32con.WS_POPUP | win32con.WS_VISIBLE,
                                    0, 0,
                                    #50, 50,  # for debug
                                    #800,600,  # for debug, too. The real line is below:
                                    self.screen_resolution[0],self.screen_resolution[1],
                                    None,
                                    None,
                                    self.windowInfo.hInstance,
                                    None) 
                                    
        if self.hwnd_screensaver == None:
            raise WindowsError, "Could not create the screensaver Window (CreateWindowExA() returned None)."
        
        # Show the Window (in case it's not yet visible.):
        ctypes.windll.user32.ShowWindow(self.hwnd_screensaver, win32con.SW_SHOW)         
        # And force redraw:
        ctypes.windll.user32.UpdateWindow(self.hwnd_screensaver)

        ctypes.windll.user32.ShowCursor(False) # Mask the mouse cursor.
        
    def run(self):
        self.startTime = time.time() + 2  # Ignore mouse moves for 2 seconds after starting.
        while not self.closing:
            # Is there an image in the input Queue ?
            # If yes, store it for later usage (in WM_PAINT handling in WndProc())
            try:
                image = self.inputqueue.get_nowait()
                if image:
                    self.currentImage = image
                    ctypes.windll.user32.InvalidateRect(ctypes.c_int(self.hwnd_screensaver), None, False) # Force Window repaint
            except Queue.Empty:
                pass
            time.sleep(0.1)   # Be gentle on CPU usage.
            
        ctypes.windll.user32.ShowCursor(True)  # Show cursor before exiting.
        #open("\messages.log","a").write(str(id(self))+ " - " + str(time.time())+" : END ---------------------------------------\n")


    def setImage(self, imagedib):
        ''' Set the image to display in the screensaver. 
            imagedib must be a PIL ImageWin.Dib object.
        '''
        self.inputqueue.put(imagedib,True)  # Give the new image to the thread.

    def WndProc(self, hwnd, message, wParam, lParam):
        ''' Callback used by Windows to pass messages to our screensaver window. '''
        if self.closing:  # If we are closing, ignore all other Window messsages.
            return 0;
        
        #open("\messages.log","a").write(str(id(self))+ " - " + str(time.time())+" : "+repr(message)+"\n")
            
        # Now we react to the different messages Windows sends us:
        if message == win32con.WM_PAINT:  # Windows asks our window to repaint.
            ps = PAINTSTRUCT()
            rect = RECT()
            hdc = ctypes.windll.user32.BeginPaint(ctypes.c_int(hwnd), ctypes.byref(ps))
            ctypes.windll.user32.GetClientRect(ctypes.c_int(hwnd), ctypes.byref(rect))
            if self.currentImage:  # If an image is available, display it.
                #print "WM_PAINT: image"
                self.currentImage.expose(hdc)
            #else:
                #print "WM_PAINT: NO IMAGE"
            ctypes.windll.user32.EndPaint(ctypes.c_int(hwnd), ctypes.byref(ps))
            return 0
        elif message == win32con.WM_MOUSEMOVE:  # Mouse was moved in our Window
            if (time.time()<self.startTime):  # Ignore the first mouse moved just after the screensaver activates.
                return 0
            # FIXME: only exit if mouse moved more than n pixels in s seconds
            self.mousmove_count += 1
            # Only exist if Windows sent us 3 mouse move event (to prevent spurious events)
            if self.mousmove_count > 3:
               ctypes.windll.user32.PostMessageA(hwnd, win32con.WM_CLOSE, 0, 0);  # Close the screensaver Window.
            #ctypes.windll.user32.PostMessageA(hwnd, win32con.WM_CLOSE, 0, 0);  # Close the screensaver Window.
            return 0
        elif message in (win32con.WM_KEYDOWN,win32con.WM_LBUTTONDOWN,win32con.WM_RBUTTONDOWN,win32con.WM_MBUTTONDOWN):
            if (time.time()<self.startTime):  # Ignore the first mouse moved just after the screensaver activates.
                return 0
            ctypes.windll.user32.PostMessageA(hwnd, win32con.WM_CLOSE, 0, 0);  # Close the screensaver Window.        
            return 0
        elif message == win32con.WM_CLOSE:   # Windows gently asks us to close.
            ctypes.windll.user32.DestroyWindow(self.hwnd_screensaver) # This sends a WM_DESTROY message
            return 0
        elif message == win32con.WM_DESTROY: # Windows tells us that we should close now.
            ctypes.windll.user32.PostQuitMessage(0)  # This sends a WM_QUIT message.
            self.closing = True
            return 0
        elif message == win32con.WM_QUIT:    # Now it's time to quit. Right now.
            self.closing = True
            return

            
        # FIXME: other messages to handle ?

        return ctypes.windll.user32.DefWindowProcA(ctypes.c_int(hwnd), ctypes.c_int(message), ctypes.c_int(wParam), ctypes.c_int(lParam))
      
def getScreenResolution():
    ''' Returns the current screen resolution.
        Output: a tuple (x,y)  where x and y are integers.
    '''
    return ( ctypes.windll.user32.GetSystemMetrics(win32con.SM_CXSCREEN), ctypes.windll.user32.GetSystemMetrics(win32con.SM_CYSCREEN) )


def generateNewImage(assembler_sup,config,wsaver):
    log = logging.getLogger('windowsScreensaver')    
    log.info("Generating a new image now with %d new images" % config["assembler.superpose.nbimages"])
    log.info("windowsScreensaver: (Next image in %d seconds.)" % config["program.every"])
    assembler_sup.superposeB()   # Generate new image
    image = assembler_sup.getImage()
    if image != None:
        wsaver.setImage(ImageWin.Dib(image))  # Display the image.
    #print "generateNewImage:Done"




def messageLoop(assembler_sup, config):
    ''' Create the screensaver window thread and start the event loop.
        Input:
            assembler_sup is a started assembler_superpose object which provides the images.
            config is the config dictionnary of webGobbler.
    '''
    # Message loop dispatching is here because it has to be in the main thread.
    # (Only the main thread receives messages from the OS)
    
    log = logging.getLogger('windowsScreensaver')
    
    wsaver = wgwin32screensaver(ImageWin.Dib(assembler_sup.getImage()))
    wsaver.start()
    
    msg = MSG()
    pMsg = ctypes.pointer(msg)
    NULL = ctypes.c_int(0)
    
    # Note: here, we are in the main thread.
    # The message loop dispatching needs to be here because Windows will
    # send the window message only to the main thread.
    # We will dispatch the messages to other threads with DispatchMessageA() below:
    start_time = time.time()
    log.info("Next image in %d seconds." % config["program.every"])

    # Start to generate a new images right now.    
    generateImageThread = threading.Thread(target=generateNewImage, args=(assembler_sup,config,wsaver))
    generateImageThread.start()
    start_time = time.time()

    while wsaver.isAlive():  # While the display thread has not died, dispatch him the windows messsages
    
        # Are there Windows messages waiting ?
        if ctypes.windll.user32.PeekMessageA( pMsg, NULL, 0, 0, win32con.PM_NOREMOVE) !=0:
            # Yes !  Let's handle the message.
            ctypes.windll.user32.GetMessageA( pMsg, NULL, 0, 0)
            # The following 2 lines will automatically call the WndProc of the wsaver object:
            ctypes.windll.user32.TranslateMessage(pMsg)
            ctypes.windll.user32.DispatchMessageA(pMsg)
            
        # Is delay elapsed ?  If yes, generate a new image.
        if (time.time()-start_time > config["program.every"]) or (time.time()<start_time):
            # Has the image generation thread completed ?
            if (generateImageThread==None or (not generateImageThread.isAlive())):  # If we have no thread or the thread has completed:
                # We start image generation in a new thread so that the screensaver windows
                # is more responsive and close as soon as mouse is moved.
                # (Even if the image generation and collector threads are still running.)
                generateImageThread = threading.Thread(target=generateNewImage, args=(assembler_sup,config,wsaver))
                generateImageThread.start()
                start_time = time.time()
            
        time.sleep(0.05)  # Ben gentle on CPU usage.

    
    assembler_sup.shutdown()
    # Make sure generateImageThread is dead.
    if generateImageThread.isAlive():
        generateImageThread.join()
    wsaver.join()


import PIL.Image
import PIL.ImageTk
import PIL.ImageEnhance

from Tkinter import *
import Tkinter

import time

from pp_utils import StopWatch
from pp_utils import Monitor


class ImagePlayer:
    """ Displays an image on a canvas for a period of time. Image display can be interrupted
          Implements animation of transitions but Pi is too slow without GPU aceleration."""

    # slide state constants
    NO_SLIDE = 0
    SLIDE_IN = 1
    SLIDE_DWELL= 2
    SLIDE_OUT= 3

# *******************
# external commands
# *******************

    def __init__(self,canvas,cd,track_params):
        """
                canvas - the canvas onto which the image is to be drawn
                cd - configuration dictionary
        """
        self.s = StopWatch()
        self.s.off()
        self.s.start()
        
        self.mon=Monitor()
        self.mon.on()

        self.canvas=canvas
        self.cd=cd
        self.track_params=track_params

        # get config from medialist if there.
        if 'duration' in self.track_params and self.track_params['duration']<>"":
            self.duration= int(self.track_params['duration'])
        else:
            self.duration= int(self.cd['duration'])
            
        if 'transition' in self.track_params and self.track_params['transition']<>"":
            self.transition= self.track_params['transition']
        else:
            self.transition= self.cd['transition']
  
        # keep dwell and porch as an integer multiple of tick          
        self.porch = 1000 #length of pre and post porches for an image (milliseconds)
        self.tick = 100 # tick time for image display (milliseconds)
        self.dwell = (1000*self.duration)- (2*self.porch)
        if self.dwell<0: self.dwell=0

        self.centre_x = int(self.canvas['width'])/2
        self.centre_y = int(self.canvas['height'])/2

        self.s.split('init')


    def play(self,
                    track,
                    end_callback,
                    ready_callback,
                    enable_menu=False,
                    starting_callback=None,
                    playing_callback=None,
                    ending_callback=None):
                        
        self.s.start()
        # instantiate arguments
        self.track=track
        self.enable_menu=enable_menu
        self.ready_callback=ready_callback
        self.end_callback=end_callback

        #init state and signals
        self.state=ImagePlayer.NO_SLIDE
        self.quit_signal=False
        self._tick_timer=None
        self.drawn=None

        self.pil_image=PIL.Image.open(self.track)
        self.s.split("open gif file - sarename")
        # adjust brightness and rotate (experimental)
        # pil_image_enhancer=PIL.ImageEnhance.Brightness(pil_image)
        # pil_image=pil_image_enhancer.enhance(0.1)
        # pil_image=pil_image.rotate(45)
        # tk_image = PIL.ImageTk.PhotoImage(pil_image)

        # and start image rendering
        self._start_front_porch()


    def key_pressed(self,key_name):
        if key_name=='':
            return
        elif key_name in ('p'):
            return
        elif key_name=='escape':
            self._stop()
            return

    def button_pressed(self,button,edge):
        if button =='pause':
            return
        elif button=='stop':
            self._stop()
            return

    def kill(self):
        if self._tick_timer<>None:
            self.canvas.after_cancel(self._tick_timer)
            self._tick_timer=None


    
# *******************
# internal functions
# *******************


    def _stop(self):
        self.quit_signal=True
  
     #called when back porch has completed or quit signal is received
    def _end(self):
        self.quit_signal=False
        self.canvas.delete(ALL)
        self.canvas.update_idletasks( )
        self.state=self.NO_SLIDE
        self.end_callback("ImagePlayer ended")
        self=None


    def _start_front_porch(self):
        self.state=ImagePlayer.SLIDE_IN
        self.porch_counter=0
        if self.ready_callback<>None: self.ready_callback()

        if self.transition=="cut":
            self.s.start()
            #just display the slide full brightness. No need for porch but used for symmetry
            self.tk_img=PIL.ImageTk.PhotoImage(self.pil_image)
            self.s.split("process PIL image to Tk image")
            self.drawn = self.canvas.create_image(self.centre_x, self.centre_y,
                                                  image=self.tk_img, anchor=CENTER)
            self.s.stop("create image on the canvas")
  

        elif self.transition=="fade":
            #experimental start black and increase brightness (controlled by porch_counter).
            self._display_image()

        elif self.transition == "slide":
            #experimental, start in middle and move to right (controlled by porch_counter)
            self.tk_img=PIL.ImageTk.PhotoImage(self.pil_image)
            self.drawn = self.canvas.create_image(self.centre_x, self.centre_y,
                                                  image=self.tk_img, anchor=CENTER)
            
        elif self.transition=="crop":
            #experimental, start in middle and crop from right (controlled by porch_counter)
            self.tk_img=PIL.ImageTk.PhotoImage(self.pil_image)
            self.drawn = self.canvas.create_image(self.centre_x, self.centre_y,
                                                  image=self.tk_img, anchor=CENTER)

        self._tick_timer=self.canvas.after(self.tick, self._do_front_porch)
        
            
    def _do_front_porch(self):
        if self.quit_signal == True:
            self._end()
        else:
            self.porch_counter=self.porch_counter+1
            # print "doing slide front porch " +str(self.porch_counter)
            self._display_image()
            if self.porch_counter==self.porch/self.tick:
                self._start_dwell()
            else:
                self._tick_timer=self.canvas.after(self.tick,self._do_front_porch)


    def _start_dwell(self):
        self.state=ImagePlayer.SLIDE_DWELL
        self.dwell_counter=0
        self._tick_timer=self.canvas.after(self.tick, self._do_dwell)

        
    def _do_dwell(self):
        if self.quit_signal == True:
            self.mon.log(self,"quit received")
            self._end()
        else:
            self.dwell_counter=self.dwell_counter+1
            # print"doing slide dwell " + str(self.dwell_counter)
            if self.dwell_counter==self.dwell/self.tick:
                self._start_back_porch()
            else:
                self._tick_timer=self.canvas.after(self.tick, self._do_dwell)

    def _start_back_porch(self):
        self.state=ImagePlayer.SLIDE_OUT
        self.porch_counter=self.porch/self.tick
        
        if self.transition=="cut":
             # just keep displaying the slide full brightness.
            # No need for porch but used for symmetry
             pass
        elif self.transition=="fade":
            #experimental start full and decrease brightness (controlled by porch_counter).
            self._display_image()

        elif self.transition== "slide":
            #experimental, start in middle and move to right (controlled by porch_counter)
            self.tk_img=PIL.ImageTk.PhotoImage(self.pil_image)
            self.drawn = self.canvas.create_image(self.centre_x, self.centre_y,
                                                  image=self.tk_img, anchor=CENTER)
            
        elif self.transition =="crop":
            #experimental, start in middle and crop from right (controlled by porch_counter)
            self.tk_img=PIL.ImageTk.PhotoImage(self.pil_image)
            self.drawn = self.canvas.create_image(self.centre_x, self.centre_y,
                                                  image=self.tk_img, anchor=CENTER)

        self._tick_timer=self.canvas.after(self.tick, self._do_back_porch)

            
    def _do_back_porch(self):
        if self.quit_signal == True:
            self._end()
        else:
            self.porch_counter=self.porch_counter-1
            # print "doing slide front porch " +str(self.porch_counter)
            self._display_image()
            if self.porch_counter==0:
                self._end()
            else:
                self._tick_timer=self.canvas.after(self.tick,self._do_back_porch)

    



    def _display_image(self):
        if self.transition=="cut":
            pass
        
        # all the methods below have incorrect code !!!
        elif self.transition=="fade":
            self.s.start()
            self.enh=PIL.ImageEnhance.Brightness(self.pil_image)
            prop=float(self.porch_counter)/float(20)  #????????
            # print"proportion" + str(prop)
            self.pil_img=self.enh.enhance(prop)
            self.s.split("calculate fade")
            self.tk_img=PIL.ImageTk.PhotoImage(self.pil_img)
            self.s.split("convert PIL to Tk") 
            self.drawn = self.canvas.create_image(self.centre_x, self.centre_y,
                                                  image=self.tk_img, anchor=CENTER)
            self.s.split("render")
            self.s.stop("do nothing")

        elif self.transition=="slide":
            self.canvas.move(self.drawn,5,0)
            
        elif self.transition=="crop":
            self.crop= 10*self.porch_counter
            self.pil_img=self.pil_image.crop((0,0,1000-self.crop,1080))
            self.tk_img=PIL.ImageTk.PhotoImage(self.pil_img)           
            self.drawn = self.canvas.create_image(self.centre_x, self.centre_y,
                                                  image=self.tk_img, anchor=CENTER)
            
        # display instructions if enabled
        if self.enable_menu== True:
            self.canvas.create_text(self.centre_x, int(self.canvas['height']) - int(self.cd['hint-y']),
                                                  text=self.cd['hint-text'],
                                                  fill=self.cd['hint-colour'],
                                                  font=self.cd['hint-font'])
            self.canvas.update_idletasks( )


# *****************
#Test harness follows
# *****************

def on_end(message):
        print ("end")
        ip=ImagePlayer(canvas,cd,)
        ip.play(track,enable_menu,on_end)

def stop_image(event):
    ip.stop()

if __name__ == '__main__':
  
    s=StopWatch()

    s.on()
    s.start()
    
        # create and instance of a Tkinter top level window and refer to it as 'my_window'
    my_window= Tkinter.Tk()
    my_window.title("ImagePlayer Test Harness")
    
    # change the look of the window
    my_window.configure(background='grey')

    # get size of the screen and calculate canvas dimensions
    screen_width = my_window.winfo_screenwidth()
    screen_height = my_window.winfo_screenheight()

    # allow 2 pixels for the taskbar
    #self.window_width=self.screen_width-2 !!!!!!
    window_width=screen_width-200
    window_height=screen_height

    canvas_height=window_height
    canvas_width=window_width
    
    my_window.geometry("%dx%d+0+0" %(window_width,window_height))

    my_window.bind("<Key>", stop_image)

    #setup a canvas onto which will be drawn the images or text
    canvas = Canvas(my_window, bg='black')
    canvas.config(height=canvas_height, width=canvas_width)
    canvas.grid(row=1,columnspan=2)
    
    # make sure focus is set on canvas.
    canvas.focus_set()

    s.split("create windows")

    cd={'hint-text' : 'the cat sat',
            'hint-font' : 'Helvetica 30 bold',
            'hint-colour' : 'white',
            'transition' : 'cut',
            'hint-y' : 100,
            'duration':10}
    
    ip=ImagePlayer(canvas,cd,)
    
    enable_menu=True
    track="/home/pi/pipresents/images/islands.jpg"

    ip.play(track,enable_menu,on_end)
    my_window.mainloop()


                                            




   

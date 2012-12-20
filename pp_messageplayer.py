
from Tkinter import *
import Tkinter

import time
from pp_utils import Monitor


class MessagePlayer:
    """ Displays lines of text in the centre of a black screen"""
    

# *******************
# external commands
# *******************

    def __init__(self,canvas,cd,track_params):
        """
                canvas - the canvas onto which the image is to be drawn
                cd - configuration dictionary for the show from which player was called
        """

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

        # keep dwell and porch as an integer multiple of tick          
        self.tick = 100 # tick time for image display (milliseconds)
        self.dwell = (1000*self.duration)

        self.centre_x = int(self.canvas['width'])/2
        self.centre_y = int(self.canvas['height'])/2


    def play(self,
                    text,
                    end_callback,
                    ready_callback,
                    enable_menu=False,
                    starting_callback=None,
                    playing_callback=None,
                    ending_callback=None):
                        
        # instantiate arguments
        self.text=text
        self.enable_menu=enable_menu
        self.ready_callback=ready_callback
        self.end_callback=end_callback
        #init state and signals
        self.quit_signal=False
        self._tick_timer=None
        self.drawn=None

        # and start text display
        self._start_dwell()


    def key_pressed(self,key_name):
        self.mon.log(self,"key received: "+key_name)
        if key_name=='':
            return
        elif key_name in ('p'):
            return
        elif key_name=='escape':
            self._stop()
            return

    def button_pressed(self,button,edge):
        self.mon.log(self,"button received: "+button)
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
  
     #called when dwell has completed or quit signal is received
    def _end(self):
        self.quit_signal=False
        self.canvas.delete(ALL)
        self.canvas.update_idletasks( )
        self.end_callback("MessagePlayer ended")
        self=None


    def _start_dwell(self):
        self.dwell_counter=0
        if self.ready_callback<>None:
            self.ready_callback()
        # display text
        self.canvas.create_text(self.centre_x, self.centre_y,
                                                text=self.text,
                                                fill=self.track_params['message-colour'],
                                                font=self.track_params['message-font'])     
        
        # display instructions (hint)
        if self.enable_menu==True:
            self.canvas.create_text(int(self.canvas['width'])/2,
                                    int(self.canvas['height']) - int(self.cd['hint-y']),
                                    text=self.cd['hint-text'],
                                    fill=self.cd['hint-colour'],
                                    font=self.cd['hint-font'])
        
        self.canvas.update_idletasks( )
        self._tick_timer=self.canvas.after(self.tick, self._do_dwell)

        
    def _do_dwell(self):
        if self.quit_signal == True:
            self.mon.log(self,"quit received")
            self._end()
        else:
            if self.dwell<>0:
                self.dwell_counter=self.dwell_counter+1
                if self.dwell_counter==self.dwell/self.tick:
                    self._end()
            self._tick_timer=self.canvas.after(self.tick, self._do_dwell)


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

    cd={'hint-text' : 'Welcome to Pi Presents\nSecond line',
            'hint-font' : 'Helvetica 30 bold',
            'hint-colour' : 'white',
            'duration':20}
    
    ip=MessagePlayer(canvas,cd,None)
    
    ip.play("",on_end)
    my_window.mainloop()


                                            




   

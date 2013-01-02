import RPi.GPIO as GPIO
import time


class Buttons:



    # Button defintion constants index the _buttons array
    SHUTDOWN=0
    DOWN=1
    UP=2
    PLAY=3
    PAUSE=4
    STOP=5
    PIR=6

    # locations of the _buttons array
    PIN=0                # pin on RPi board GPIO connector e.g. P1-11
    NAME=1             # name for callback
    THRESHOLD=2    #threshold of debounce count for on state change to be considered
    COUNT=3           # variable - count of the number of times the input has been 0 (limited to threshold)
    PRESSED=4        # variable - debounced state 
    LAST = 5              # varible - last state - used to detect edge
    FRONT_EDGE=6      #True if calback required on front edge
    BACK_EDGE=7      #True if callback required on backedge

    def reset_buttons(self):
        for but in self._buttons:
            but[Buttons.COUNT]=0
            but[Buttons.PRESSED]==False
            but[Buttons.LAST]==False

        
    def __init__(self,widget,tick,callback=None):
        self.widget=widget
        self.tick=tick
        self.callback=callback
        self.tick_timer=None
        GPIO.setwarnings(False)
        self._buttons = [
                                 [12,"shutdown",8,0,False,False,True,False],
                                 [15,"down",2,0,False,False,True,False],
                                 [16,"up",2,0,False,False,True,False],
                                 [18,"play",2,0,False,False,True,False],
                                 [22,"pause",2,0,False,False,True,False],
                                 [7,"stop",2,0,False,False,True,False],
                                 [11,"PIR",2,0,False,False,True,False]]


        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(12,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(15,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(16,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(18,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(22,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(7,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        GPIO.setup(11,GPIO.IN,pull_up_down=GPIO.PUD_UP)


    def kill(self):
        if self.tick_timer<>None:
            self.widget.after_cancel(self.tick_timer)
        GPIO.cleanup()


    def is_pressed(self,button):
        return self._buttons[button][Buttons.PRESSED]


    def poll(self):
        for index, but in enumerate(self._buttons):
            # debounce
            if GPIO.input(but[Buttons.PIN])==0:
                if but[Buttons.COUNT]<but[Buttons.THRESHOLD]:
                    but[Buttons.COUNT]+=1
                    if but[Buttons.COUNT]==but[Buttons.THRESHOLD]:
                        but[Buttons.PRESSED]=True
            else: # input us 1
                if but[Buttons.COUNT]>0:
                    but[Buttons.COUNT]-=1
                    if but[Buttons.COUNT]==0:
                         but[Buttons.PRESSED]=False
 
            #detect edges
            if but[Buttons.PRESSED]==True and but[Buttons.LAST]==False:
                but[Buttons.LAST]=but[Buttons.PRESSED]
                if  but[Buttons.FRONT_EDGE]==True and self.callback <> None:
                    self.callback(index, but[Buttons.NAME],"front")
   
            if but[Buttons.PRESSED]==False and but[Buttons.LAST]==True:
                but[Buttons.LAST]=but[Buttons.PRESSED]     
                if  but[Buttons.BACK_EDGE]==True and self.callback <> None:
                     self.callback(index, but[Buttons.NAME],"back")         
          
        #loop
        self.tick_timer=self.widget.after(self.tick,self.poll)


if __name__ == '__main__':

    # may not work as poll is now tkintered !!!!!!
    buttons= Buttons()
    print "runnning"

    def callback(index,name,edge):
        print name, " ", edge," ",buttons.is_pressed(index)
    
    while True:
        buttons.poll(callback)
        time.sleep (0.02)
        

    


        

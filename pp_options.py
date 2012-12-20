import argparse

def command_options():
    """ reads the command line options and returns a dictionary of them"""
    parser = argparse.ArgumentParser(description = 'Pi presents presentation package')
    parser.add_argument( '-b','--noblank', 
                                          action='store_false',
                                          help='Disable screen blanking.')
    parser.add_argument( '-f','--fullscreen', 
                                          action='store_true',
                                          help='Full screen operation')
    parser.add_argument( '-g','--gpio', 
                                          action='store_true',
                                          help='Use GPIO')
    parser.add_argument( '-d','--debug', 
                                          action='store_true',
                                          help='Debug output to terminal window')
    parser.add_argument( '-u','--usbstick', nargs='?', default='', const='',
                                          help='USB Stick home path')
    parser.add_argument( '-s','--sdcard', nargs='?', default='', const='',
                                          help='SD card home path')
    parser.add_argument( '-p','--profile', nargs='?', default='', const='',
                                          help='Profile path')
    args=parser.parse_args()
    return  vars(args)



PI PRESENTS
===========

Pi Presents is a presentation application intended for Museums and Visitor Centres. I am involved with a couple of charity organisations that are museums or have visitor centres and have wanted a cheap way to provide audio interpretation and slide/videoshow displays. Until the Raspberry Pi arrived buying or constructing even sound players was expensive. The Pi with its combination of Linux, GPIO and a powerful GPU is ideal for black box multi-media applications; all it needs is a program to harness its power in a way that could be used by non-programmers.

This initial issue of Pi Presents offers some basic features but under the bonnet it is, I hope, a flexible modular application with simple to use editing facilities to configure it to your exact display requirements. The initial features include:

*	Animation or interpretation of exhibits by triggering a sound, video, or slideshow from a PIR or button.

*	A repeating media show for a visitor centre. Images, videos, audio tracks, and messages can be displayed.

*	Allow media shows to be interrupted by the visitor and a menu of videos to be presented.

*	Showing 'Powerpoint' like presentations where progress is controlled by buttons or keyboard. The presentation may include images, text, audio tracks and videos.

I have immediate plans to develop an audio player based on pulseaudio which should replace omxplayer for audio tracks and allow use of the 3.5mm jack without popping. Also the ability to asynchronously trigger a number of tracks from GPIO pins. Other ideas are animation of exhibits using GPIO outputs, synthetic speech, and display of animations using OpenGLES.

There are potentially many applications of Pi Presents and your input on real world experiences would be invaluable to me, both minor tweaks to the existing functionality and major improvements.

Licence
=======

See the licence.txt file. Pi Presents is giftware to help support a small museum of which I am a Trustee and who are busy building a larger premises https://www.facebook.com/MuseumOfTechnologyTheGreatWarWw11. Particularly if you are using Pi Presents in a profit making situation a small donation would be appreciated.

Installation
============

The full manual is in the file manual.pdf. To download Pi Presents including the manual and get going follow the instructions below.

*   Install required applications (PIL and X Server utils) as described in the install_instructions.txt file.

*   Download and install p-expect as specified here http://www.noah.org/wiki/pexpect#Download_and_Installation  and in the install_instructions.txt file.

*   Download Pi Presents from the pipresents github repository as described in the install_instructions.txt file.

*   Now run Pi Presents  to check the installation is successful. From a terminal window opened in the pipresents directory type:

          python pipresents.py

    You will see a welcome message followed by an error message which is because you have no profiles. Exit Pi Presents using CTRL-BREAK or close the window.

*   Now download and try some examples as described in the manual.


Reading the Manual
==================

The manual is issued as a PDF because it was too large and unwieldy to be a text file. Raspbian has a pdf reader; however there are a couple of issues with this:

*	The currently installed pdf reader mupdf is somewhat limited. Install xpdf using

         sudo apt-get install xpdf

*   You cannot cut and paste from xpdf. I have therefore provided a text file install_instructions.txt with the necessary information..


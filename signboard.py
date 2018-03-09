#!/usr/bin/env python3

"""
A simple controller script to communicate with signboard via serial.
"""

import serial  # pySerial lib
import time

"""
class
- connect via serial
- craft a signboard message w/ options
- send a crafted message
- send a regular message l1 vs l2
- clear the display

Create a new instance with the Signboard Port 
 - sb = Signboard("/dev/ttyUSB0")
"""

# To do,  
# Define Defaults, validate defaults against user settings
#

#DRYRUN = True
DRYRUN = False
class Signboard:


	def __init__(self, port, charlimit=20, linelimit=2, messagelimit=256):
		"""
		Basic instance initizliation
		required inputs:
		 - port: OS serial port (/dev/ttyUSB0, or COM1)

		 optional inputs:
		 - charlimit: # of characters display can handle
		 - linelimit: # of lines the display can handle
		 - messagelimit: Max # of ascii characters in a single message (including controlcodes)
		"""

		self.port = port
		self.baud = 9600
		# possibly add parity/stopbits/control (8N1 defaults) for now the pyserial defaults work perfectly.

		self.charlimit = charlimit
		self.linelimit = linelimit
		self.messagelimit = messagelimit

		#default attributes
		self.blinkrate = 128
		self.blink = "-"
		self.inverseblink = "-"
		self.hue_foreground = "0"
		self.hue_background = "0"
		self.font = "1"
		self.ESC="\x1b"
		self.scroll_rate = 2
		self.scroll_repeat = 0
		# possible font options:


	def set_scroll_rate(self, i):
		"""
		This argument specifies the scroll rate. Where 1 is the slowest setting and 
		3 is the fastest setting. A value of zero or no number selects the previous 
		rate, or, if no previous rate is available, selects the default rate of 2 
		(medium). 
		"""
		if i > 3:
			print("Error: invalid scroll rate: %s" % (i))
		else:
			self.scroll_rate = i

	def set_scroll_repeat(self, i):
		"""
		This argument specifies the number of times the scrolling text should 
		repeat. Acceptable values are from 1 through 3, and represent the actual 
		number of repeats. A value of zero or no number will cause the text to 
		scroll continuously until it is explicitly cleared or a new 
		message is received by the display (also called an infinite scroll). 
		"""
		if i > 3:
			print("Error: invalid scroll repeat: %s" % (i))
		else:
			self.scroll_repeat = i

	def set_hue(self,f=0,b=0):
		"""
		f - forground
		b - background
		1 Selects dimmest. 
		2 Selects medium brightness. 
		3 Selects brightest (power up setting). 
		4 Selects sparkle. 
		"""
		if  f > 4 or b > 4:
			print("Error: invalid hue option f=%s, b=%s" % (f,b))
			return False
		else:
			self.hue_foreground = f
			self.hue_background = b

			self._write("%s%s;%sH" % (self.ESC, self.hue_foreground, self.hue_background))
			return True

	def set_font(self, f):
		"""
		Set the font for the next message
		1 -  8x6 pixels  2 lines of 20 characters.  
		2 -  8x8 pixels  2 lines of 15 characters.  
		3 -  16x12 pixels 1 lines of 10 characters.  
		4 -  16x15 pixels  1 lines of 8 characters.  
		5 -  16x8 pixels  1 lines of 15 characters.  
		6 -  16x10 pixels  1 lines of 12 characters.  
		7 -  8x6 pixels  2 lines of 20 characters.  * JIS8 / Katakana
		8 -  8x6 pixels  2 lines of 20 characters.  * Slavic
		9 -  8x6 pixels  2 lines of 20 characters.  * Cyrillic 
		"""
		if int(f) > 9:
			print("Error: invalid font selection: %s" % (f))
			return False
		else:
			self._write("%s%sf" %(self.ESC, f))
			return True

	def connect(self):
		"""
		creates the connection to the serial device.
		"""
		self.serialport = serial.Serial(self.port)
		self._write("\x1b 24A")
		#self.name = serialport.name
		return True

	def close(self):
		"""
		closes the connection to the serial device.
		"""
		self.serialport.close()
		return True

	def _write(self, s):
		"""
		Internal function for sending data across the port, this should only be called by other methods
		that have setup thier data first.  This handles the ascii/binary encoding requires to communicate
		with the signboard.

		input: str
		"""

		if len(s) <= self.messagelimit:
			if DRYRUN:
				print("%s" % (s))
			else:
				self.serialport.write(b'%s' % (s.encode('ascii')))
				return True
		else:
			print("Error: Message exceed char limit of %s" % (self.messagelimit))
			return False

	def print_msg(self, s, l, type="static"):
		"""
		Displays message: s on line: l
		You can pre-setup some options, using the following methods, they all have defaults
		set_hue
		set_scroll_rate
		set_scroll_repeat
		set_font


		Optional arguments:
		type = "static" - display a static 20character message
		type = "scroll" - scrolls a larger message (up to 256 characters including control codes)
		"""

		# check to see if we're requesting something outside the line bounds.
		if l > self.linelimit:
			print("Error: max line limit is %s" % (self.linelimit))
			return False

		# check to see if we're requesting something outside the char limit PER line.
		if len(s) > self.charlimit and type == static:
			print("Error: message exceeds the character limit of %s" % (self.charlimit))
			return False

		if type == "static":
			message = "\x1b%s;1C%s\r" % (l,s)

		if type == "scroll":
			message = "\x1b%s \x1bS %s \r" % (l,s)

		# figure out formatting/font settings and pre-pend them to the message.
		self._write(message)
		return True


	def clear(self):
		"""
		clears the display 
		"""
		#self._write("\x1b2i\r".encode('ascii')) # fuck this didnt work

		#okay this should be simplier, we can derive the spaces from the maxlengths.
		self.print_msg("                    ",1,"static")
		self.print_msg("                    ",2,"static")
		return True

# testing class functions
sb = Signboard("/dev/ttyUSB0")
sb.connect()
sb.clear()
sb.set_font(5)
sb.print_msg('Vorne signboard.',1,type="static")
sb.print_msg('python test.',2,type="scroll")


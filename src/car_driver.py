#! /usr/bin/env python

import rospy, math
import sys, termios, tty, select , os
from std_msgs.msg import String
from BLConnector import BLConnector

class CarDriver(object):

	# pair of user/aurdino(car) commands
	cmd = {'w':'d',
		   's':'e',
		   'd':'g',
		   'a':'h',
		   'f':'f',
		   'j':'j',
		   'k':'k',
		   'l':'l',
		   'm':'m',
		   'r':'s',
		   'v':'a',
		   'b':'b',
		   'z':'z'

		}


	def init(self):
	    # Save terminal settings
	    self.settings = termios.tcgetattr(sys.stdin)
	    # Initial values
	    self.update_rate = 10   # Hz
	    self.alive = True
	    # command to be sent to the car
	    self.command = ''
	    # Setup publisher for debegging purpose
	    self.pub_cmd = rospy.Publisher('driving_cmd', String,queue_size=10)
	    # initialize bluetooth connector object
	    self.connector = BLConnector()
	    self.connector.init()
	    # distance from the car to obstacle
	    self.CLOSE = 20
	    self.VCLOSE = 10
	    
	# loop indefinatly until quit command is passed
	def run(self):
	    try:
	      self.init()
	      self.print_usage()
	      r = rospy.Rate(self.update_rate) # Hz
	      while not rospy.is_shutdown():
	        ch = self.get_key()
	        self.process_key(ch)
	        self.update()
	        r.sleep()
	    except rospy.exceptions.ROSInterruptException:
	      pass
	    finally:
	      self.finilize()

	# For processing user input to a command
	def process_key(self, ch):
	    if ch == 'h':
	      self.command = 'h'
	    elif ch in self.cmd.keys():
	      self.command = self.cmd[ch]
	    elif ch == 'q':
	      self.loginfo('Quitting')
	      # Stop the car
	      self.command = 'r'
	      rospy.signal_shutdown('Shutdown')
	    else:
	      # z - does nothing (the car have no z command)
	      self.command = 'z'


     # Get input from the terminal
	def get_key(self):
	    tty.setraw(sys.stdin.fileno())
	    select.select([sys.stdin], [], [], 0)
	    key = sys.stdin.read(1)
	    return key.lower()

	def update(self):
	    if rospy.is_shutdown():
	      return
	    
	    self.check_safty()
	    
	    if(self.command == 'h'):
	    	self.print_usage()
	    else:
	    	self.send_data(self.command)

	    self.pub_cmd.publish(self.command)
	    #rospy.loginfo('cmd: %s is published.' % self.command)

	def print_usage(self):
	    msg = """
	    Keyboard Teleop that Publish to /driving_cmd (driving_car/string)
	    And send the command to the car connected using serial port
	    Copyright (C) 2016
	    --------------------------------------------------
	    h:       Print this menu
	    Moving around:
	          W   
	      A   S   D
	    light front-on/front-off	j/k
	    	  back-on/back-off		l/m

	    stop : r

	    anything else : ignored

	    q :   Quit
	    --------------------------------------------------
	    """
	    self.loginfo(msg)

	# Used to print items to screen, while terminal is in funky mode
	def loginfo(self, str):
	    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
	    tty.setraw(sys.stdin.fileno())

	def finilize(self):
	    # Restore terminal settings
	    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)

	# send the command to the car using bluetooth
	def send_data(self,command):
		self.connector.send_data(command)

	# check if there is obstacle in closer range
	def check_safty(self):
		if(self.command == 'w'):
			self.check_front()
			distance = self.connector.readline()
			if(distance > self.CLOSE):
				pass
			elif(distance <= self.CLOSE and distance >= VCLOSE):
				self.command = 'r'
			elif(distance < self.VCLOSE):
				self.command = 's'
		elif(self.command == 's'):
			self.check_back()
			distance = self.connector.readline()
			if(distance > self.CLOSE):
				pass
			elif(distance <= self.CLOSE and distance >= VCLOSE):
				self.command = 'r'
			elif(distance < self.VCLOS):
				self.command = 'w'
		else:
			pass

	# returns the distance from the car to obstacle forward 
	def check_front(self):
		self.connector.send_data('v')

	# returns the distance from the car to obstacle backward
	def check_back(self):
		self.connector.send_data('b')

		
		

if __name__ == '__main__':
  rospy.init_node('driver_node')
  driver = CarDriver()
  driver.run()
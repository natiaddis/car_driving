#! /usr/bin/env python
import serial

class BLConnector(object):

	def init(self):
		self.serial_port = '/dev/rfcomm0'
		try:
			self.ser = serial.Serial(self.serial_port,9600,timeout=1)
		except:
			print("There is no Bluetooth connection\nSet a connection first and try again.")
		
	def send_data(self,data):
		try:
			if(self.ser.isOpen()):
				self.ser.write(data)
			else:
				self.ser.open()
				print("can't send the data.\nconnection is not open.")
		except:
			print("can't send the data.\nserial port error.")

			

		
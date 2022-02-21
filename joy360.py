#!/bin/env python

# Only really useful for VRChat joycon with Driver4VR

import time
import collections
import itertools


import openvr

from pyjoycon import JoyCon, get_R_id, get_L_id, ButtonEventJoyCon
import logging

import threading

import time
import pprint

import vgamepad as vg

gamepad = vg.VX360Gamepad()


	
class VibrationReceiver(object):
	
	def __init__(self):
		pass
	
	def poll(self,cons):
		new_event = openvr.VREvent_t()
		while openvr.VRSystem().pollNextEvent(new_event):
			self.checkHaptics(new_event,cons)

	def checkHaptics(self, event, cons):
		if event.eventType == openvr.VREvent_HapticVibration_t:
			print("VREvent_HapticVibration_t????")
			return
		if event.eventType != openvr.VREvent_Input_HapticVibration:
			return
		role = openvr.VRSystem().getControllerRoleForTrackedDeviceIndex(event.data.hapticVibration.containerHandle)
		fDurationSeconds = event.data.hapticVibration.fDurationSeconds
		con=False
		if role == openvr.TrackedControllerRole_RightHand:
			print("  right controller trigger")
			con=cons[1]
		elif role == openvr.TrackedControllerRole_LeftHand:
			print("  left controller trigger ")
			con=cons[0]
		else:
			print("getControllerRoleForTrackedDeviceIndex=",role,"???")
		if con:
			con[2].rumble_simple()
			con[4]=time.time()+max(min(fDurationSeconds,3),0)

class VibeStatus():
	pass #TODO Send vibrate cmd every 0.5 seconds

def handleVibe(con):
	if not con[4]:
		return
	if time.time()<con[4]:
		return
	con[4]=False
	con[2].rumble_stop()
	
def handle(name,event_type,status):
	if name == "l":
		if event_type=="l":
			if status:
				gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
			else:
				gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
		elif event_type=="left_sl":
			if status:
				gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
			else:
				gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)

	elif name == "r":
		if event_type=="r":
			if status:
				gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
			else:
				gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
		elif event_type=="right_sr":
			if status:
				gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
			else:
				gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
	
if __name__ == '__main__':
	while True:
		joycon_id_r = get_R_id()
		joycon_id_l = get_L_id()
		if joycon_id_r and joycon_id_r[0] and joycon_id_l and joycon_id_l[0]:
			break
		print("All joycons yet not found, retrying")
		time.sleep(0.1)
	print("found ids",joycon_id_r,joycon_id_l)
	cons=[
		[joycon_id_l,1,False,"l",False],
		[joycon_id_r,2,False,"r",False]
	]
	for con in cons:
		print("init",con)
		j = ButtonEventJoyCon(*con[0])
		time.sleep(0.3)
		j.set_player_lamp_on(1)  # required to keep knockoff joycons from shutting down it seems (you can set it off afterwards)
		time.sleep(0.3)
		j.set_player_lamp_on(con[1])
		time.sleep(0.3)
		j.rumble_simple()
		con[2]=j
		time.sleep(0.3)
		print("checking connected")
		assert j.connected()
		print("connected joycon",con)


	openvr.init(openvr.VRApplication_Utility)
	r = VibrationReceiver()
	
	print("Starting loop")
	while True:
		r.poll(cons)
		handled=False
		for con in cons:
			joycon=con[2]
			name=con[3]
			handleVibe(con)
			time.sleep(1/240)
			for event_type, status in joycon.events():
				handled=True
				print(name,event_type, status and "PRESS" or "RELEASE")
				handle(name,event_type,status)
		if handled:
			gamepad.update()
			assert j.connected()
			
	print("\nSpawning interactive shell for debugging:\n")
	import code
	code.interact(local=locals())





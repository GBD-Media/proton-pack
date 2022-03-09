#!/usr/bin/python

import argparse
import pygame
import RPi.GPIO as GPIO
import threading
import time
from time import sleep
from transitions import Machine
from transitions.extensions.states import add_state_features, Timeout

@add_state_features(Timeout)
class CustomStateMachine(Machine):
	pass

# State machine for power_cell
class power_cell(object):
	# leds = [29, 31, 33, 37, 32, 36, 38]
	states = [
		{'name': 'off'},
		{'name': 'running', 'timeout': 0.2, 'on_timeout': 'run_timeout'}
	]
	dataPin = 32
	latchPin = 36
	clockPin = 38
	numLEDs = 7


	def __init__(self, cyclotron):
		# for led in self.leds:
		# 	GPIO.setup(led, GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup((self.dataPin, self.latchPin, self.clockPin),GPIO.OUT)

		self.leds_lit = 0
		self.cyclotron = cyclotron
		self.machine = CustomStateMachine(model=self, states=power_cell.states, initial='off')

		self.machine.add_transition('switch_on', 'off', 'running')
		self.machine.add_transition('increment', 'running', 'running')
		self.machine.add_transition('switch_off', '*', 'off')

	def on_exit_off(self):
		self.dim_all_led()

	def on_enter_running(self):
		self.advance_led()
		# print("power_pack %d leds lit" % self.leds_lit)

	def on_enter_off(self):
		self.dim_all_led()

	def dim_all_led(self):
		# print("power_pack is off")
		self.leds_lit = 0
		# for led in self.leds:
			# GPIO.output(led, 0)
		self.shift_update("00000000")
		

	def run_timeout(self):
		self.increment()

	def shift_update(self, input):
		#put latch down to start data sending
		GPIO.output(self.clockPin,0)
		GPIO.output(self.latchPin,0)
		GPIO.output(self.clockPin,1)

		#load data in reverse order
		for i in range(7, -1, -1):
			GPIO.output(self.clockPin,0)
			GPIO.output(self.dataPin, int(input[i]))
			GPIO.output(self.clockPin,1)

		#put latch up to store data on register
		GPIO.output(self.clockPin,0)
		GPIO.output(self.latchPin,1)
		GPIO.output(self.clockPin,1)

	def advance_led(self):
		if self.leds_lit == self.numLEDs - 1:
			# Increment cyclotron
			self.cyclotron.increment()

		self.leds_lit = (self.leds_lit + 1) % (self.numLEDs + 1)
		# print('leds_lit %d' % self.leds_lit)
		# if self.leds_lit == 0:
		# 	print("power_pack is dim")
		# else:
		# 	print("power_pack %s" % " ".join(str(x) for x in self.leds[0:self.leds_lit]))

		# for led in self.leds:
		# 	GPIO.output(led, 0)
		output = ""
		for l in range(0, self.leds_lit, 1):
			# GPIO.output(led, 1)
			output += "1"
		for p in range(0, 8 - self.leds_lit, 1):
			output += "0"
		# print(output)
		self.shift_update(output)

# State machine for gun_bg (gun bar graph LEDs)
class gun_bg(object):
	leds = [19, 21, 22, 23, 24]
	states = [
		{'name': 'off'},
		{'name': 'running', 'timeout': 0.075, 'on_timeout': 'run_timeout'}
	]

	def __init__(self):
		for led in self.leds:
			GPIO.setup(led, GPIO.OUT, initial=GPIO.LOW)

		self.leds_lit = 0
		self.machine = CustomStateMachine(model=self, states=gun_bg.states, initial='off')

		self.machine.add_transition('switch_on', 'off', 'running')
		self.machine.add_transition('increment', 'running', 'running')
		self.machine.add_transition('switch_off', '*', 'off')

	def on_exit_off(self):
		self.dim_all_led()

	def on_enter_running(self):
		self.advance_led()
		# print("gun_bg %d leds lit" % self.leds_lit)

	def on_enter_off(self):
		self.dim_all_led()

	def dim_all_led(self):
		# print("gun_bg is off")
		self.leds_lit = 0
		for led in self.leds:
			GPIO.output(led, 0)

	def run_timeout(self):
		self.increment()

	def advance_led(self):
		self.leds_lit = (self.leds_lit + 1) % (len(self.leds) + 1)
		# if self.leds_lit == 0:
		# 	print("gun_bg is dim")
		# else:
		# 	print("gun_bg %s" % " ".join(str(x) for x in self.leds[0:self.leds_lit]))

		for led in self.leds:
			GPIO.output(led, 0)
		for led in self.leds[0:self.leds_lit]:
			GPIO.output(led, 1)

# State machine for gun_blast (gun firing LEDs)
class gun_blast(object):
	leds = [26, 18]
	states = [
		{'name': 'off'},
		{'name': 'running', 'timeout': 0.05, 'on_timeout': 'run_timeout'}
	]

	def __init__(self):
		for led in self.leds:
			#print('setting %d' % led)
			GPIO.setup(led, GPIO.OUT, initial=GPIO.LOW)

		self.leds_lit = 0
		self.machine = CustomStateMachine(model=self, states=gun_blast.states, initial='off')

		self.machine.add_transition('switch_on', 'off', 'running')
		self.machine.add_transition('increment', 'running', 'running')
		self.machine.add_transition('switch_off', '*', 'off')

	def on_exit_off(self):
		self.dim_all_led()

	def on_enter_running(self):
		self.advance_led()
		# print("gun_blast %d leds lit" % self.leds_lit)

	def on_enter_off(self):
		self.dim_all_led()

	def dim_all_led(self):
		# print("gun_blast is off")
		self.leds_lit = 0
		for led in self.leds:
			GPIO.output(led, 0)

	def run_timeout(self):
		self.increment()

	def advance_led(self):
		self.leds_lit = (self.leds_lit + 1) % (len(self.leds) + 1)
		# if self.leds_lit == 0:
		# 	print("gun_blast is dim")
		# else:
		# 	print("gun_blast %s" % " ".join(str(x) for x in self.leds[0:self.leds_lit]))

		for led in self.leds:
			GPIO.output(led, 0)
		for led in self.leds[0:self.leds_lit]:
			GPIO.output(led, 1)


# State machine for cyclotron
class cyclotron(object):
	leds = [11, 7, 5, 3]
	states = [
		{'name': 'off'},
		{'name': 'running'}
	]

	def __init__(self):
		for led in self.leds:
			GPIO.setup(led, GPIO.OUT, initial=GPIO.LOW)

		self.led_lit = 0
		self.machine = CustomStateMachine(model=self, states=cyclotron.states, initial='off')

		self.machine.add_transition('switch_on', 'off', 'running')
		self.machine.add_transition('increment', 'running', 'running')
		self.machine.add_transition('switch_off', '*', 'off')

	def on_exit_off(self):
		self.dim_all_led()

	def on_enter_running(self):
		self.advance_led()

	def on_enter_off(self):
		self.dim_all_led()

	def on_timeout(self):
		self.advance_led()

	# Illuminate only leds[num]
	def illuminate_led(self, num):
		for led in self.leds:
			GPIO.output(led, 0)
			# print("Turning off %s" % led)
		GPIO.output(self.leds[num], 1)
		# print("Turning on %s" % self.leds[num])

	def advance_led(self):
		self.led_lit = (self.led_lit + 1) % len(self.leds)
		self.illuminate_led(self.led_lit)
		# print("cyclotron led %s" % self.leds[self.led_lit])

	# Turn them all off
	def dim_all_led(self):
		print("cyclotron is off")
		self.led_lit = 0
		for led in self.leds:
			GPIO.output(led, 0)
			# print("Turning off %s" % led)

# State machine for sound
#  - Power up
#  - Firing
#  - Power down
#  - Theme song
class sound_generator(object):
	states = [
		{'name': 'off'},
		{'name': 'on'},
		{'name': 'firing'},
		{'name': 'theme'}
	]

	def __init__(self):
		self.machine = CustomStateMachine(model=self, states=sound_generator.states, initial='off')

		pygame.mixer.init()
		self.power_up = pygame.mixer.Sound('/home/pi/proton-pack/power-up.wav')
		self.power_down = pygame.mixer.Sound('/home/pi/proton-pack/power-down.wav')
		self.firing = pygame.mixer.Sound('/home/pi/proton-pack/firing-loop.wav')
		self.firing_release = pygame.mixer.Sound('/home/pi/proton-pack/firing-shutdown.wav')

		self.machine.add_transition('switch_on', 'off', 'on')
		self.machine.add_transition('fire_press', 'on', 'firing')
		self.machine.add_transition('fire_release', 'firing', 'on')
		self.machine.add_transition('theme_press', 'on', 'theme')
		self.machine.add_transition('theme_release', 'theme', 'on')
		self.machine.add_transition('switch_off', '*', 'off')

	def on_exit_off(self):
		# Play power-up sound
		self.power_up.play()

	def on_enter_off(self):
		# Play power-down sound
		self.power_down.play()

	def on_enter_firing(self):
		# Start looping firing sound
		self.firing.play(-1)

	def on_exit_firing(self):
		# Stop looping firing sound
		self.firing.stop()
		self.firing_release.play()

	def on_enter_theme(self):
		# Start looping theme
		pygame.mixer.music.load('theme.wav')
		pygame.mixer.music.play()

	def on_exit_theme(self):
		# Stop looping theme
		pygame.mixer.music.stop()


# General handler for debouncing
class ButtonHandler(threading.Thread):
	def __init__(self, pin, handler, edge='both', bouncetime=200):
		#super(ButtonHandler, self).__init__(daemon=True)
		super(ButtonHandler, self).__init__()
		self.daemon = True

		self.edge = edge
		self.handler = handler
		self.pin = pin
		self.bouncetime = float(bouncetime)/1000

		self.lastpinval = GPIO.input(self.pin)
		self.lock = threading.Lock()

	def __call__(self, *args):
		#if not self.lock.acquire(blocking=False):
		if not self.lock.acquire(False):
			return

		t = threading.Timer(self.bouncetime, self.read, args=args)
		t.start()

	def read(self, *args):
		pinval = GPIO.input(self.pin)

		if ((pinval == 0 and self.lastpinval == 1) and
			(self.edge in ['falling', 'both'])):
			self.handler.falling(*args)

		elif ((pinval == 1 and self.lastpinval == 0) and
			  (self.edge in ['rising', 'both'])):
			self.handler.rising(*args)

		self.lastpinval = pinval
		self.lock.release()

class switch(object):
	def __init__(self, pin, c, p, s, g, b):
		self.pin = pin
		self.c = c
		self.p = p
		self.s = s
		self.g = g
		self.b = b
		# self.led_lit = 0
		# self.led_pin = 18

		
		# GPIO.setup(self.led_pin, GPIO.OUT, initial=GPIO.LOW) #LED

		GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		self.handler = ButtonHandler(pin, self, edge='both', bouncetime=200)
		self.handler.start()
		GPIO.add_event_detect(pin, GPIO.BOTH, self.handler)

	def rising(self, args):
		print("Switch off")
		# GPIO.output(self.led_pin, 0)
		self.c.switch_off()
		self.p.switch_off()
		self.s.switch_off()
		self.g.switch_off()
		self.b.switch_off()

	def falling(self, args):
		print("Switch on")
		# GPIO.output(self.led_pin, 1)
		self.c.switch_on()
		self.p.switch_on()
		self.s.switch_on()
		self.g.switch_on()


class theme(object):
	def __init__(self, pin, c, p, s, g, b):
		self.pin = pin
		self.c = c
		self.p = p
		self.s = s
		self.g = g
		self.b = b

		GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		self.handler = ButtonHandler(pin, self, edge='both', bouncetime=200)
		self.handler.start()
		GPIO.add_event_detect(pin, GPIO.BOTH, self.handler)

	def rising(self, args):
		print("Theme released")
		self.s.theme_release()

	def falling(self, args):
		print("Theme pressed")
		self.s.theme_press()


class fire(object):
	def __init__(self, pin, c, p, s, g, b):
		self.pin = pin
		self.c = c
		self.p = p
		self.s = s
		self.g = g
		self.b = b

		GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		self.handler = ButtonHandler(pin, self, edge='both', bouncetime=200)
		self.handler.start()
		GPIO.add_event_detect(pin, GPIO.BOTH, self.handler)

	def rising(self, args):
		print("Fire released")
		self.b.switch_off()
		self.s.fire_release()

	def falling(self, args):
		print("Fire pressed")
		self.b.switch_on()
		self.s.fire_press()

# This software will
#  - Enable the lighting state machine while switch "on"
#  - Play the nutrona wand sounds while switch "on" and fire "held"
#  - Play the theme music while switch "on" and theme "held"
#
# It will transmit the switch press events, affecting each state machine
#
def run_logic(args):
	try:
		GPIO.setmode(GPIO.BOARD)

		c = cyclotron()
		p = power_cell(c)
		s = sound_generator()
		g = gun_bg()
		b = gun_blast()

		sw = switch(16, c, p, s, g, b)
		f = fire(13, c, p, s, g, b)
		t = theme(15, c, p, s, g, b)

		while True:
			time.sleep(5)
	
	except KeyboardInterrupt:
		print("Exiting Proton Pack")
	finally:
		GPIO.cleanup()


def main():
	parser = argparse.ArgumentParser(
		description='Run control logic for Ghostbusters proton pack'
	)

	parser.set_defaults(func=run_logic)

	args = parser.parse_args()
	args.func(args)

if __name__ == '__main__':
	main()


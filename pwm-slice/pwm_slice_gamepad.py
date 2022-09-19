# Simple 2 Channel R/C Receiver for Raspberry Pi Pico

from machine import Pin
import time
from time import ticks_us, ticks_diff
from PWMCounter import PWMCounter
import _thread
import gamepad

# Steering pin connects channel 1 on the Traxxas receiver to GP15 on the Pico (pin 20)
# Throttle pin connects channel 3 on the Traxxas receiver to GP13 on the Pico (pin 17)

# For R/C servos, pulse width time in µS 
MIN_PW = 1000
MID_PW = 1500
MAX_PW = 2000

# These are the global variables to keep track of the pulse width 
throttle_pulse = MID_PW
steering_pulse = MID_PW

def range_map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min)

'''
bound_and_range
Bound the value to a R/C signal (1000 - 2000) pulsewidth
and convert to -127 to 127 for gamepad
'''

def bound_and_range(x):
    # return int(max(min(127, (x - MIN_PW) * (127 - -127) // (MAX_PW - MIN_PW) + -127), -127))
    return int(max(min(127, (x - MIN_PW) * 254 // 1000 - 127), -127))

throttle_lock = _thread.allocate_lock()
steering_lock = _thread.allocate_lock()

steering_counter = 0
throttle_counter = 0

def init_pwm_counters():
    global steering_counter
    global throttle_counter
    # Configure counter to count rising edges on GP15
    # Start counting when the pin goes high
    steering_counter = PWMCounter(15, PWMCounter.LEVEL_HIGH)
    # Set divisor to 16 (helps avoid counter overflow)
    steering_counter.set_div(16)
    # Start counter
    steering_counter.start()

    # Configure counter to count rising edges on GP13
    throttle_counter = PWMCounter(13, PWMCounter.LEVEL_HIGH)
    # Set divisor to 16 (helps avoid counter overflow)
    throttle_counter.set_div(16)
    # Start counter
    throttle_counter.start()

def steering_interrupt(pin):
    global steering_pulse
    global steering_counter
    
    steering_lock.acquire()
    raw_pulse = steering_counter.read_and_reset()
    if raw_pulse == 0:
        print("rp == 0")
    steering_pulse = ( raw_pulse * 16) // 125
    steering_lock.release()
    
def throttle_interrupt(pin):
    global throttle_pulse
    global throttle_counter
    
    raw_pulse = throttle_counter.read_and_reset()
    throttle_lock.acquire()
    throttle_pulse = ( raw_pulse * 16) // 125
    throttle_lock.release()
        

# Is the global program running
running = True

def read_pwm_pins_to_gamepad():
        
    global throttle_pulse
    global steering_pulse
    global running
   
    # We'll use counter pin for triggering, so set it up.
    steering_pin = Pin(15, Pin.IN, Pin.PULL_DOWN) # GP15, Pin 20 - Channel 1 on Traxxas Receiver
    throttle_pin = Pin(13, Pin.IN, Pin.PULL_DOWN) # GP13, Pin 17 - Channel 3 on Traxxas Receiver

    init_pwm_counters()
    steering_pin.irq(steering_interrupt, Pin.IRQ_FALLING)
    throttle_pin.irq(throttle_interrupt, Pin.IRQ_FALLING)
    game_pad = gamepad.GamePad()
    
    while running:
        throttle_lock.acquire()
        throttle_pw = throttle_pulse
        throttle_lock.release()
        throttle_ranged = bound_and_range(throttle_pw)


        steering_lock.acquire()
        steering_pw = steering_pulse
        steering_lock.release()
        steering_ranged = bound_and_range(steering_pw)
        # print("S: ",steering_pw, "T: ", throttle_pw)
        
        game_pad.set_linear(0,throttle_ranged,0)
        game_pad.set_rotation(steering_ranged,0,0)
        game_pad.send()
 
        time.sleep(0.020)


  
   
if __name__ == "__main__":
    
    read_pwm_pins_to_gamepad()
    
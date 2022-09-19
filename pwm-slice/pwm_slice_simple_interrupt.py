# Simple 2 Channel R/C Receiver for Raspberry Pi Pico

from machine import Pin
import time
from time import ticks_us, ticks_diff
from PWMCounter import PWMCounter
import _thread
import micropython

# Steering pin connects channel 1 on the Traxxas receiver to GP15 on the Pico (pin 20)
# Throttle pin connects channel 3 on the Traxxas receiver to GP13 on the Pico (pin 17)


# For R/C servos, pulse width time in µS 
MIN_PW = 1000
MID_PW = 1500
MAX_PW = 2000

# These are the global variables to keep track of the pulse width 
throttle_pulse = MID_PW
steering_pulse = MID_PW

# Is the global program running
running = True

throttle_lock = _thread.allocate_lock()
steering_lock = _thread.allocate_lock()

steering_counter = 0
throttle_counter = 0

def init_pwm_counters():
    global steering_counter
    global throttle_counter
    # Configure counter to count rising edges on GP15
    steering_counter = PWMCounter(15, PWMCounter.LEVEL_HIGH)
    # Set divisor to 16 (helps avoid counter overflow)
    steering_counter.set_div(16)
    # Start counter
    steering_counter.start()

    # Configure counter to count rising edges on GP15
    throttle_counter = PWMCounter(13, PWMCounter.LEVEL_HIGH)
    # Set divisor to 16 (helps avoid counter overflow)
    throttle_counter.set_div(16)
    # Start counter
    throttle_counter.start()

def steering_interrupt(pin):
    global steering_pulse
    
    raw_pulse = steering_counter.read_and_reset()
    steering_lock.acquire()
    steering_pulse = ( raw_pulse * 16) // 125
    steering_lock.release()
    
def throttle_interrupt(pin):
    global throttle_pulse
    
    raw_pulse = throttle_counter.read_and_reset()
    throttle_lock.acquire()
    throttle_pulse = ( raw_pulse * 16) // 125
    throttle_lock.release()
        

def read_pwm_pins():
    global throttle_pulse
    global steering_pulse
    global running
   
    # We'll use counter pin for triggering, so set it up.
    steering_pin = Pin(15, Pin.IN, Pin.PULL_DOWN) # GP15, Pin 20 - Channel 1 on Traxxas Receiver
    throttle_pin = Pin(13, Pin.IN, Pin.PULL_DOWN) # GP13, Pin 17 - Channel 3 on Traxxas Receiver

    init_pwm_counters()
    throttle_pin.irq(throttle_interrupt, Pin.IRQ_FALLING)
    steering_pin.irq(steering_interrupt, Pin.IRQ_FALLING)
    
    while running:
        # print("Loop time: ", ticks_diff(loop_start,loop_end))
        # print(micropython.mem_info())

        # time.sleep_us(10)
        throttle_lock.acquire()
        steering_lock.acquire()
        print("S: ",steering_pulse, "T: ",throttle_pulse)
        steering_lock.release()
        throttle_lock.release()
 
        time.sleep(0.05)

if __name__ == "__main__":
    
    read_pwm_pins()
    

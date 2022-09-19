# Simple 2 Channel R/C Receiver for Raspberry Pi Pico

from machine import Pin
import time
from time import ticks_us, ticks_diff
from PWMCounter import PWMCounter
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

def read_pwm_pins():
    global throttle_pulse
    global steering_pulse
    global running
   
    # We'll use counter pin for triggering, so set it up.
    steering_pin = Pin(15, Pin.IN) # GP15, Pin 20 - Channel 1 on Traxxas Receiver
    throttle_pin = Pin(13, Pin.IN) # GP13, Pin 17 - Channel 3 on Traxxas Receiver

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

    last_state_steering = 0
    last_state_throttle = 0
    
    while running:
        
        loop_start = ticks_us()
        steering_value = steering_pin.value()
        throttle_value = throttle_pin.value()
        
        if ~(x := steering_value) & last_state_steering:
            steering_pulse = (steering_counter.read_and_reset() * 16) // 125
            # Print pulse width in µS
            print("S: ", steering_pulse)
        last_state_steering = x

        
        if ~(x := throttle_value) & last_state_throttle:
            throttle_pulse = (throttle_counter.read_and_reset() * 16) // 125
            # Print pulse width in µS 
            print("T: ",throttle_pulse)
        last_state_throttle = x
        loop_end = ticks_us()
        # print("Loop time: ", ticks_diff(loop_start,loop_end))
        # print(micropython.mem_info())

        # time.sleep_us(10)

if __name__ == "__main__":
    
    read_pwm_pins()
    
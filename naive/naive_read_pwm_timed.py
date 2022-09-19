from machine import Pin, PWM
from time import ticks_us, ticks_diff
import time

# Steering pin connects channel 1 on the Traxxas receiver to GP15 on the Pico (pin 20)
# Throttle pin connects channel 3 on the Traxxas receiver to GP13 on the Pico (pin 17)


# For R/C servos, pulse width time in µS
# PWM period is 50 µS
# Input should be bound to these values
MIN_CYCLE = 1000
MID_CYCLE = 1500
MAX_CYCLE = 2000

steering_pin = Pin(15, Pin.IN) # GP15, Pin 20 - Channel 1 on Traxxas Receiver
throttle_pin = Pin(13, Pin.IN) # GP13, Pin 17 - Channel 3 on Traxxas Receiver

last_state_steering = 0
last_state_throttle = 0
last_update = ticks_us()

steering_value = 0
def read_pwm_pins():
    global last_state_steering
    global last_state_throttle

    while True:
        # Read the pins
        # value() with no parameter means "get"
        loop_start = ticks_us()
        steering_value = steering_pin.value()
        throttle_value = throttle_pin.value()
        
        # Steering first
        if (steering_value == True) & (last_state_steering == False):
            # Pin went from low to high; Start timing
            steering_start = ticks_us()
            last_state_steering = True
        else:
            if (steering_value == False) & (last_state_steering == True):
                # Pin went from low to high; Stop timing
                steering_stop = ticks_us()
                steering_us = ticks_diff(steering_start, steering_stop)
                last_state_steering = False
                print("Steering: ",steering_us)

        loop_end = ticks_us()
        print("Loop time: ", ticks_diff(loop_start,loop_end))
                
        time.sleep_us(10)

if __name__ == "__main__":
        
    read_pwm_pins()
        

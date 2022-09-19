from machine import Pin
from time import ticks_us, ticks_diff
import _thread
import time

# Steering pin connects channel 1 on the Traxxas receiver to GP15 on the Pico (pin 20)
# Throttle pin connects channel 3 on the Traxxas receiver to GP13 on the Pico (pin 17)

throttle_value = 0
start_throttle = 0

throttle_lock = _thread.allocate_lock()

def throttle_interrupt(pin):
    global throttle_value
    global start_throttle
    
    throttle_lock.acquire()
    if (pin.value()) :
        start_throttle = ticks_us()
    else:
        # On falling edge
        end_throttle = ticks_us()
        throttle_value = ticks_diff(start_throttle, end_throttle)
    throttle_lock.release()
    
    
throttle_pin = Pin(13, Pin.IN, Pin.PULL_DOWN)
throttle_pin.irq(throttle_interrupt, Pin.IRQ_RISING | Pin.IRQ_FALLING)

while True:
    
    throttle_lock.acquire()
    print("T: ",throttle_value)
    throttle_lock.release()
    
    time.sleep(0.05)


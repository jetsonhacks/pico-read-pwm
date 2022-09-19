# Example PIO to measure servo pulse width.
import time
from machine import Pin
import rp2
import _thread

# Steering pin connects channel 1 on the Traxxas receiver to GP15 on the Pico (pin 20)
# Throttle pin connects channel 3 on the Traxxas receiver to GP13 on the Pico (pin 17)

@rp2.asm_pio()
def pulsewidth():
    wrap_target()        # Creates Loop
    set(x, 0)                             # 0  Reset counter
    wait(1, pin, 0)                       # 1  Wait for pin to go high - leading edge
# :label1
    label("1")
    jmp(x_dec, "2")                       # 2  Decrement X register
# :label2
    label("2")
    jmp(pin, "1")                         # 3  If pin is still high, keep counting
    mov(isr, x)                           # 4  
    push(isr, block)                      # 5  
    irq( 0)                               # 6  Should match index in PIO block [0-3] PIO Block 0, 1
    wrap()              # Ends loop

@rp2.asm_pio()
def pulsewidth1():
    wrap_target()        # Creates Loop
    set(x, 0)                             # 0  Reset counter
    wait(1, pin, 0)                       # 1  Wait for pin to go high - leading edge
# :label1
    label("1")
    jmp(x_dec, "2")                       # 2  Decrement X register
# :label2
    label("2")
    jmp(pin, "1")                         # 3  If pin is still high, keep counting
    mov(isr, x)                           # 4  
    push(isr, block)                      # 5  
    irq( 1)                               # 6  Should match index in PIO block [0-3] PIO Block 0, 1
    wrap()              # Ends loop

steering_result = 0
throttle_result = 0

steering_lock = _thread.allocate_lock()
throttle_lock = _thread.allocate_lock()

def steering_handler(sm):
    global steering_result
    # x-reg counts down
    value = 0x100000000 - sm.get()  # count is negative, subtract from 32 bit max
    steering_lock.acquire()
    steering_result = value  
    steering_lock.release()
    
def throttle_handler(sm):
    global throttle_result
    # x-reg counts down
    throttle_value = 0x100000000 - sm.get()  # count is negative, subtract from 32 bit max
    throttle_lock.acquire()
    throttle_result = throttle_value
    throttle_lock.release()

    
pin15 = Pin(15, Pin.IN, Pin.PULL_DOWN)
sm0 = rp2.StateMachine(0, pulsewidth, freq=2_000_000, in_base=pin15, jmp_pin=pin15)
sm0.irq(steering_handler)


pin13 = Pin(13, Pin.IN, Pin.PULL_DOWN)
sm1 = rp2.StateMachine(1, pulsewidth1, freq=2_000_000, in_base=pin13, jmp_pin=pin13)
sm1.irq(throttle_handler)


sm0.active(1)
sm1.active(1)


while True:
    steering = 0
    throttle = 0
    
    steering_lock.acquire()
    steering = steering_result
    steering_lock.release()

    throttle_lock.acquire()
    throttle = throttle_result
    throttle_lock.release()
    print("S: ", steering, "T: ", throttle)

    time.sleep(0.05)

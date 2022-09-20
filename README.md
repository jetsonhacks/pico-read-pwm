# readPWM
Read PWM signals from the Raspberry Pi Pico

Some simple software sketches exploring how to read R/C Receiver PWM pulses on a Raspberry Pi Pico.

The folder named pio has a Pico PIO implementation
The folder named pwm_slice uses a Pico PWM Slice implementation.

The pwm_slice_gamepad.py example outputs a USB-HID stream through the USB port. Requires MicroPython be built with USB-HID support: https://github.com/jetsonhacks/micropython/tree/usb-hid

Software was built against a Traxxas 6553B 5 channel R/C Receiver.

from razmetka import *

pin = r'e:\rks\razmetka_source\kanopu_full_ms'
pout = r'e:\rks\razmetka_test\kanopus_full_ms'

input = NeuroMasking()
input.InputFromPairs(pin)
input.SetRazmetka(pout)
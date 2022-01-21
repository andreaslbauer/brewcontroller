from gpiozero import LED


relais = [LED(24), LED(23), LED(14), LED(15), LED(18)]

def relaisOn(idx):
    relais[idx - 1].on()

def relaisOff(idx):
    relais[idx - 1].off()
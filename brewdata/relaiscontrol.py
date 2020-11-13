from gpiozero import LED


relais = [LED(14), LED(15), LED(18), LED(23)]

def relaisOn(idx):
    relais[idx].off()

def relaisOff(idx):
    relais[idx].on()
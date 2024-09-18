from machine import I2C, Pin, PWM
import struct
import time
import random
import neopixel
from MSA311 import Acceleration
import uasyncio as asyncio
import network
from mqtt import MQTTClient


difference = False
big_button = False

enable = False

def wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('Tufts_Robot', '')
    
    while wlan.ifconfig()[0] == '0.0.0.0':
        print('.', end=' ')
        time.sleep(1)
    
    print(wlan.ifconfig())

def callback_2(topic, msg):
    global enable
    command = msg.decode()
    print("in callback")
    print((topic.decode(), msg.decode()))
    if command == 'start':
        enable = True
    if command == 'stop':
        enable = False

async def mqtt():

    print("in mqtt")
    mqtt_broker = 'broker.hivemq.com' 
    port = 1883
    topic_sub = 'ME35-24/MedhanRex'
    
    client = MQTTClient('ME35_Claire', mqtt_broker , port, keepalive=60)
    client.connect()
    client.set_callback(callback_2)
    client.subscribe(topic_sub.encode())
    
    while True:
        client.check_msg()
        await asyncio.sleep(1)

async def neo():

    neo = neopixel.NeoPixel(Pin(28),1)
    
    while True:

        if enable:

            if difference:
    
                #print("tapped")
    
                #print(difference)
    
                
                
                color_1 = random.randint(0,30)
                color_2 = random.randint(0,30)
                color_3 = random.randint(0,30)
                
            
                state = (color_1,color_2,color_3)  # RGB
                
                neo[0] = state
                neo.write()
        else:

            state = (0,0,0) 
            neo[0] = state
            neo.write()
            
    
        await asyncio.sleep(0.1)

            



async def led():

    f = Pin('GPIO7', Pin.OUT)

    while True:

        if enable:

            if difference:
    
                #print(difference)
    
                #print("tapped")
    
                if f.value() == 1:
                    # print("Pin is HIGH")
                    f.off()
                    
                else:
                    # print("Pin is LOW")
                    f.on()
        else:
            f.off()
            
                
        await asyncio.sleep(0.1)

        


async def board_led():

    led = machine.PWM(machine.Pin('GPIO3', machine.Pin.OUT))
    led.freq(50)
    
    while True:

        if enable:
    
            # Increase duty cycle from 0 to 65535
            for i in range(0, 65535, 500):
                led.duty_u16(i)
                await asyncio.sleep(0.01)
         
            # Decrease duty cycle from 65535 to 0
            for i in range(65535, 0, -500):
                led.duty_u16(i)
                await asyncio.sleep(0.01)

        else:
            led.duty_u16(0)
            



async def motion_accel(): 

    scl = Pin('GPIO27', Pin.OUT)
    sda = Pin('GPIO26', Pin.OUT)
    
    t = Acceleration(scl, sda)
    
    x,y,z = t.read_accel()

    print(x)
    print(y)
    print(z)
    print("")

    sensitivity = 500

    while True:
    
        x1, y1, z1 = t.read_accel()
    
        # print("X")
        # print(x1)
        # print(x)
        # print(x1-x)
        # print("")

        # print("Y")
        # print(y1)
        # print(y)
        # print("")
        
        
        
    
    
        if abs(x1-x) > sensitivity:
    
            print("X changed")
    
    
            global difference
            difference = True
    
        elif abs(y1-y) > sensitivity:
    
            print("Y changed")
            
    
            
            global difference
            difference = True
    

        else:
            global difference
            difference = False

        
        x = x1
        y = y1
        z = z1

        await asyncio.sleep(0.1)


async def play_song():

    # Define the buzzer pin
    buzzer = PWM(Pin('GPIO18', Pin.OUT))
    
    # Define the NeoPixel pin and number of pixels
    np_pin = Pin(28)  # Change to your NeoPixel GPIO pin
    num_pixels = 1    # Change to the number of NeoPixels you have
    np = neopixel.NeoPixel(np_pin, num_pixels)
    
    # Define frequencies for notes
    notes = {
        'E': 329,
        'D#': 311,
        'B': 493,
        'C#': 277,
        'A': 440,
        'C': 261,
        'E2': 659
    }
    
    # Define the song (note, duration)
    song = [
        ('E', 0.5),
        ('D#', 0.5),
        ('E', 0.5),
        ('D#', 0.5),
        ('E', 0.5),
        ('B', 0.5),
        ('C', 0.5),
        ('A', 0.5),
        ('E2', 0.5),
        ('E', 0.5),
        ('D#', 0.5),
        ('E', 0.5),
        ('D#', 0.5),
        ('E', 0.5),
        ('B', 0.5),
        ('C', 0.5),
        ('A', 0.5),
        ('E2', 0.5)
    ]
    
    # Define the colors
    colors = [
        (0, 0, 255),  # Blue
        (128, 0, 128),  # Purple
        (255, 255, 0),  # Yellow
        (255, 0, 0)     # Red
    ]
    
    
    while True:
    
        if big_button:
            
            for i, (note, duration) in enumerate(song):
                if enable:
                    if note in notes:
                        buzzer.freq(notes[note])
                        buzzer.duty_u16(32767)  # Set volume (0-65535)
                        color = colors[i % len(colors)]  # Cycle through colors
                        np[0] = color
                        np.write()                # Update NeoPixel
                        time.sleep(duration)
                        buzzer.duty_u16(0)      # Turn off buzzer
                        np[0] = (0, 0, 0)        # Turn off NeoPixel
                        np.write()                # Update NeoPixel
                        await asyncio.sleep(0.1)        # Short pause between notes
    
                else:
                    buzzer.duty_u16(0)
            
            
           
        await asyncio.sleep(0.1)
        


last_time = 0
debounce_time = 0.2  # Debounce time in seconds

def callback(g):

    global last_time
    current_time = time.time()
    
    if current_time - last_time > debounce_time:
    
        global big_button
        if big_button == False:
            big_button = True
    
        else:
            big_button = False

        last_time = current_time
        

# Setup GPIO pin
g = Pin('GPIO8', Pin.IN, Pin.PULL_UP)
g.irq(trigger=Pin.IRQ_FALLING, handler=callback)   




async def main():

    wifi()

    asyncio.create_task(mqtt())
    
    # Run all tasks concurrently
    await asyncio.gather(
        neo(),
        led(),
        board_led(),
        motion_accel(),
        play_song(),
    )
        

# Start the event loop and run the tasks

asyncio.run(main())

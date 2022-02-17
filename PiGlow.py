from PyGlow import PyGlow


b = input("Maximum brightness: ")
s = input("Speed in milliseconds (try 1000 as a default): ")

pyglow = PyGlow(brightness=int(b), speed=int(s), pulse=True)

pyglow.all(0)

print("Pulsing 1 Light")
pyglow.led(1)

print("Pulsing Arms")
pyglow.arm(1)
pyglow.arm(2)
pyglow.arm(3)

print("Pulsing All")
pyglow.all()
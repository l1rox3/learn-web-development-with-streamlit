import os

print(os.access(".", os.W_OK))  # sollte True zurückgeben

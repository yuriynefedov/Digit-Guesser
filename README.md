# Digit-Guesser

Digit Guesser is a Python GUI that guesses user's handwritten digits using a neural network.

![screenshot of the GUI](screenshots/2.png)

## The Interface

The GUI is made using PyQt5. After the user draws a digit in an integrated graphic field and clicks "Process", the neural network processes the drawing and the GUI displays its guess in a separate field. Each new drawing is used to train the neural network starting from the next script launch. If the guess was incorrect, the GUI also allows the user to chose what they meant to draw.

![screenshot of the GUI](screenshots/1.png)

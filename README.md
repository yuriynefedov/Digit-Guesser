# Digit-Guesser

Digit Guesser is a Python GUI that guesses user's handwritten digits using a neural network.

## Interface

The GUI is made using PyQt5. After the user draws a digit in an integrated graphic field and clicks "Process", the neural network processes the drawing and the GUI displays its guess in a separate field. Each new drawing is used to train the neural network starting from the next script launch. If the guess was incorrect, the GUI also allows the user to chose what they meant to draw.

![screenshot of the GUI](screenshots/2.png)

## Neural network

The neural network created for this project was inspired by Make Your Own Neural Network by Tariq Rashid. It initially used MNIST training set, further replaced by my own [knowledgex.csv](knowledgex.csv) dataset for setup. The script updates the dataset with new examples each time the interface is used.

![screenshot of the GUI](screenshots/1.png)

## DigitalLearning.py

Neural network requires a lot of examples to work properly. To make the teaching process even easier for the user, I developed a supplementary GUI called [DigitalLearning.py](DigitalLearning.py) that asks the user to draw digits it requires for more accurate recognition.

![screenshot of the supplementary GUI](screenshots/3.png)

## Text-to-speech functionality

I also implemented functionality that gives the neural network its own voice. Each time the recognition happens, the program speaks out it's guess, i.e. "I think you drew 4". This is done using the Pyttsx3 module. To enable this, uncomment lines 435-437 of [DigitalRecognition.py](DigitalRecognition.py).


## Further development

1. Since text-to-speech is already implemented, it now makes sense to allow the user to also speak to the GUI, i.e. when answering which number they meant to draw.

2. To make the recognition even more precise, the dataset needs more examples of different people's handwriting.

## License

[MIT](LICENSE)

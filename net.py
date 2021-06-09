import datetime, scipy.special, numpy

class MachineLearning:
    def __init__(self, inputs, hidden, outputs, lrate):
        self.n_in = inputs
        self.n_hidden = hidden
        self.n_out = outputs
        self.lrate = lrate

        self.in_hidden_weights = numpy.random.normal(0.0, pow(self.n_in, -0.5),
                                               (self.n_hidden, self.n_in))
        self.hidden_out_weights = numpy.random.normal(0.0, pow(self.n_hidden, -0.5),
                                                (self.n_out, self.n_hidden))

        self.activate = lambda x: scipy.special.expit(x)


    def query(self, inlist):
        inputs = numpy.array(inlist, ndmin = 2).T
        
        hidden_in = numpy.dot(self.in_hidden_weights, inputs)
        hidden_out = self.activate(hidden_in)

        final_in = numpy.dot(self.hidden_out_weights, hidden_out)
        final_out = self.activate(final_in)

        return final_out

    
    def train(self, inlist, targets):
        inputs = numpy.array(inlist, ndmin = 2).T
        targets = numpy.array(targets, ndmin = 2).T

        hidden_in = numpy.dot(self.in_hidden_weights, inputs)
        hidden_out = self.activate(hidden_in)

        final_in = numpy.dot(self.hidden_out_weights, hidden_out)
        final_out = self.activate(final_in)

        final_errors = targets - final_out
        
        hidden_errors = numpy.dot(self.hidden_out_weights.T, final_errors)

        self.hidden_out_weights += self.lrate * numpy.dot(final_errors * final_out * (1 - final_out),  numpy.transpose(hidden_out))
        self.in_hidden_weights += self.lrate * numpy.dot(hidden_errors * hidden_out * (1 - hidden_out),  numpy.transpose(inputs))
        
if __name__ == '__main__':
    
    datafile = open('X:/Miscellaneous/MNIST/mnist_test.csv', 'r')
    lines = datafile.readlines()
    datafile.close()
    
    ins = 784
    hiddens = 100
    outs = 10
    lrate = 0.3
    
    nn = MachineLearning(ins, hiddens, outs, lrate)
    t1 = datetime.datetime.now()
    for numline in lines:
        all_values = numline.split(',')
        answer = int(all_values[0])
        inputs = numpy.asfarray(all_values[1:]) / 255.0 * 0.99 + 0.01
        targets = numpy.zeros(outs) + 0.01         #OUTS = 10
        targets[answer] = 0.99
        nn.train(inputs, targets)
    
    print(datetime.datetime.now() - t1)

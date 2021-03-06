import tensorflow as tf

class RecurrentNeuralNetwork(object):
    def __init__(self, device, random_seed, hidden_size, input_size, sequence_length, cell_type, batch_size, learning_rate, optimizer):
        self.sess = tf.Session()

        with tf.device(device):
            # Set random seed
            tf.set_random_seed(random_seed)

            # Input with shape [?, sequence_length * input_size]. 
            # sequence_length * input_size must be equal to 784
            with tf.name_scope('input') as scope:
                self.x = tf.placeholder(tf.float32, shape=[None, sequence_length * input_size], name='x-input')
                with tf.name_scope('input-preprocess'):

                    # Get x input in correct format
                    x_squared = tf.reshape(self.x, [-1, sequence_length, input_size])
                    x_transposed = tf.transpose(x_squared, [1,0,2])
                    x_reshaped = tf.reshape(x_transposed, [-1, input_size])
                    x_split = tf.split(x_reshaped, num_or_size_splits=sequence_length, axis=0)
                
                # Target input with shape [?, 10]
                with tf.name_scope('target_input') as scope:
                    self.y_ = tf.placeholder(tf.float32, shape=[None, 10], name='target-output')
            
            if cell_type == 'rnn':
                cell = tf.contrib.rnn.BasicRNNCell(hidden_size)
                with tf.name_scope('initial_state') as scope:
                    state = cell.zero_state(batch_size, dtype=tf.float32)
                    #state = tf.placeholder(tf.float32, [batch_size, hidden_size])
            else: #LSTM
                cell = tf.contrib.rnn.BasicLSTMCell(hidden_size, forget_bias=1.0, state_is_tuple=True)
                with tf.name_scope('initial_state') as scope:
                    state = cell.zero_state(batch_size, dtype=tf.float32)

            outputs, state = tf.contrib.rnn.static_rnn(cell, x_split, state)
            
            # Output with shape [?, 10]
            with tf.name_scope('output') as scope:
                W = tf.Variable(tf.truncated_normal([hidden_size, 10]), name='weights-1')
                b = tf.Variable(tf.zeros([10]), name='bias-1')
                self.y = tf.matmul(outputs[-1], W) + b
            
            with tf.name_scope('optimizer') as scope:

                with tf.name_scope('loss') as scope:
                    # Objective function - Cross Entropy
                    self.loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=self.y, labels=self.y_))
                
                if optimizer.lower() == 'adam':
                    # Adam Optimizer
                    self.train_step = tf.train.AdamOptimizer(learning_rate).minimize(self.loss)
                elif optimizer.lower() == 'rmsprop':
                    # RMSProp
                    self.train_step = tf.train.RMSPropOptimizer(learning_rate).minimize(self.loss)
                else: 
                    # Gradient Descent
                    self.train_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(self.loss)

            # Specify how accuracy is measured
            with tf.name_scope('accuracy') as scope:
                correct_prediction = tf.equal(tf.argmax(self.y, 1), tf.argmax(self.y_, 1))
                self.accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

            init = tf.global_variables_initializer()
            self.sess.run(init)

    '''
    Utilizes the optimizer and objectie function to train the network based on the input and target output.
    '''
    def train(self, x_input, target_output):
        _, loss = self.sess.run([self.train_step, self.loss],
                    feed_dict={self.x: x_input,
                            self.y_: target_output})
        return loss

    '''
    Feeds a value through the network and produces an output.
    '''
    def predict(self, x_input):
        predicted_output = self.sess.run(self.y, feed_dict={self.x: x_input})
        return predicted_output

    '''
    Measures the accuracy of the network based on the specified accuracy measure, the input and the target output.
    '''
    def get_accuracy(self, x_input, target_output):
        acc = self.sess.run(self.accuracy, feed_dict={self.x: x_input, 
                                                    self.y_: target_output})
        return acc

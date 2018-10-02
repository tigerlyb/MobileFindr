import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import frida

print(frida.__version__)

data_dir = "./"

def load_data(data_dir, train_row):
    train = pd.read_csv(data_dir + "train.csv")
    print(train.shape)

    X_train = train.values[0:train_row,1:]
    y_train = train.values[0:train_row,0]
    
    Pred_test = pd.read_csv(data_dir + "test.csv").values

    return X_train, y_train, Pred_test

train_row = 5000
Origin_X_train, Origin_y_train, Origin_X_test = load_data(data_dir, train_row)

print(Origin_X_train.shape, Origin_y_train.shape, Origin_X_test.shape)
print(Origin_X_train)

row = 3
print (Origin_y_train[row])
plt.imshow(Origin_X_train[row].reshape((28, 28)))
plt.show()
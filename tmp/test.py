import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
import time
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.neighbors import KNeighborsClassifier

def load_data(data_dir, train_row):
    train = pd.read_csv(data_dir + "train.csv").values
    if train_row > 0:
        x_train = train[0:train_row, 1:]
        y_train = train[0:train_row, 0]
    else:
        x_train = train[0:, 1:]
        y_train = train[0:, 0]
    
    pred_test = pd.read_csv(data_dir + "test.csv").values
    
    return x_train, y_train, pred_test
    
data_dir = "./"
train_row = -1 # -1 means train all data, otherwise train specific number of rows
k_range = range(1, 21)
scores = []

origin_x_train, origin_y_train, origin_x_test = load_data(data_dir, train_row)

x_train, x_valid, y_train, y_valid = train_test_split(origin_x_train, origin_y_train, test_size = 0.2, random_state = 0)

print("train data: x = %s, y = %s validation data: x = %s, y = %s\n" % (x_train.shape, y_train.shape, x_valid.shape, y_valid.shape))


for k in k_range:
    print("k = %s begin: " % str(k))
    start = time.time()
    knn = KNeighborsClassifier(n_neighbors = k)
    knn.fit(x_train, y_train)
    
    y_train_pred = knn.predict(x_valid)
    
    accuracy = accuracy_score(y_valid, y_train_pred)
    scores.append(accuracy)
    end = time.time()
    
    #print(classification_report(y_valid, y_pred))
    #print(confusion_matrix(y_valid, y_pred))
    print("accuracy = %s" % str(accuracy))
    print("training time: %s second(s)\n" % str(end - start))

score_max = max(scores)    
k_highest = scores.index(score_max) + 1
print("total accuracy scores: %s" % scores)
print("highest accuracy: k = %s, accuracy = %s\n" % (k_highest, score_max))

"""
plt.plot(k_range, scores)
plt.xlabel("Value of K")
plt.ylabel("Accuracy")
plt.show()
"""

start = time.time()
knn = KNeighborsClassifier(n_neighbors = k_highest)
knn.fit(origin_x_train, origin_y_train)
y_test_pred = knn.predict(origin_x_test)
end = time.time()

print("number of recognized images: " + str(len(y_test_pred)))
print("complete time: %s second(s)\n" % str(end - start))

pd.DataFrame({"ImageId": list(range(1,len(y_test_pred)+1)),"Label": y_test_pred}).to_csv('Digit_Recogniser_Result.csv', index=False,header=True)
print("Digit_Recogniser_Result.csv is generated.")
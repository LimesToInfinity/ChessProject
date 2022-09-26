import torch
import torch.nn as nn
import torch.optim as optim
from collections import OrderedDict
import time
import math

#The neural net
def NeuralNet(depth=2):
    layers = []
    layers.append((f"linear1", torch.nn.Linear(386,500)))
    layers.append((f"activation1", torch.nn.Tanh()))
    l = 1
    while l < depth - 1:
        layers.append((f"linear{l+1}", torch.nn.Linear(500,500)))
        layers.append((f"activation{l+1}", torch.nn.Tanh()))
        l += 1
    
    layers.append((f"linear{depth}", torch.nn.Linear(500,1)))
    layers.append((f"activation{depth}", torch.nn.Tanh()))
    Network = torch.nn.Sequential(OrderedDict(layers))
    
    #Optimizer
    optimizer = optim.SGD(Network.parameters(), lr=0.1)
    
    #The loss function
    loss_fn = nn.MSELoss()
    
    return Network, optimizer, loss_fn



#Load the training data in tensor a and the labels in b
a = torch.load("train.pt")
b = torch.load("label.pt")

#Split a and b in train and test data (train=80% and test=20%)
a_train = a[0:math.ceil(len(a)*0.8)]
b_train = b[0:math.ceil(len(b)*0.8)]
a_test = a[math.ceil(len(a)*0.8):len(a)]
b_test = b[math.ceil(len(b)*0.8):len(b)]

#The training loop
def training_loop(n_epochs, model, loss_fn, optimizer):
    for k in range(1,n_epochs + 1):
        timer = time.time()
        print("Epoch: ", k)
        loss = 0
        for i in range(0, math.ceil(len(a_train)/1000)):
            train_min = min((i+1)*1000, len(a_train))
            output_min =  min((i+1)*1000, len(b_train))
            train_data = a_train[i*1000 :train_min]
            true_output = b_train[i*1000 :output_min]
            prediction = model(train_data)
            train_loss = loss_fn(prediction, true_output)

            with torch.no_grad():
                loss += train_loss

            optimizer.zero_grad()
            train_loss.backward()
            optimizer.step()
        
        with torch.no_grad():
            loss1 = 0
            for i in range(0, math.ceil(len(a_test)/1000)):
                    test_min = min((i+1)*1000, len(a_test))
                    output_min =  min((i+1)*1000, len(b_test))
                    test_data = a_test[i*1000:test_min]
                    true_output = b_test[i*1000:output_min]
                    prediction = model(test_data)
                    test_loss = loss_fn(prediction, true_output)
                    loss1 += test_loss
                    
        print("train loss:", format(float(loss),'.5f'), "|", "test loss:", format(float(loss1), '.5f'), "|", "time:", format((time.time() - timer)//60, '.0f'), "min:", format((time.time() - timer)%60, '.3f'), "sec") 

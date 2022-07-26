# -*- coding: UTF-8 -*-
from datetime import time
from time import time as randomTime
import os
from random import random
import torch
import torch.nn as nn
from torch.autograd import Variable
import my_dataset
from cnn_model import CNN
from test import validation
from tqdm import tqdm
import setting

num_epochs = 50
batch_size = 2
learning_rate = 0.0005
saveModelName = 'model.pkl'


# Note: 处理文件夹
# Time: 2021/12/10 9:06 上午
# Author: HengYi
def handleDir():
    dirs = os.path.join(setting.CURRENT_PATH, 'result')
    if not os.path.exists(dirs):
        os.makedirs(dirs)
        print('[*] Make ./result dir done.')


# Note: 计算正确率
# Time: 2021/12/10 9:11 上午
# Author: HengYi
def getCorrect(modelPath):
    print('[*] Start to get correctRate.')
    cnn = CNN()
    cnn.eval()
    if not torch.cuda.is_available():
        cnn.load_state_dict(torch.load(modelPath, map_location='cpu'))
    else:
        cnn.load_state_dict(torch.load(modelPath))
    test_dataloader = my_dataset.get_test_data_loader()
    correctNum, totalNum = validation(cnn, test_dataloader)
    return round(100 * correctNum / totalNum , 3)


# Note: 作图
# Time: 2021/12/10 9:22 上午
# Author: HengYi
def makeRateImage(epochArray, correctRateArray):
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    plt.style.use('ggplot')
    import matplotlib
    matplotlib.rcParams['axes.unicode_minus'] = False
    df = pd.DataFrame({'epoch': epochArray, 'correctRate': correctRateArray})  # 字典创建
    sns.lineplot(x="epoch", y="correctRate", markers="o", data=df)
    plt.savefig("./result/rate.png")


def main():
    if not torch.cuda.is_available():
        cnn = CNN()
        print('[*] CPU In Use!')
    else:
        cnn = CNN().cuda()
        print('[*] GPU In Use!')
    cnn.train()
    print("[*] Start to init CnnNet!")
    criterion = nn.MultiLabelSoftMarginLoss()
    optimizer = torch.optim.Adam(cnn.parameters(), lr=learning_rate)
    handleDir()
    savePath = os.path.join(setting.CURRENT_PATH, 'result',saveModelName)

    # 开始训练
    train_dataloader = my_dataset.get_train_data_loader(batch_size)
    correctRateArray = [0]
    epochArray = [0]
    for epoch in range(num_epochs):
        epoch += 1
        loss = ''
        print(f'[*] Start Num.{str(epoch)} epoch.')
        for i, (images, labels) in tqdm(enumerate(train_dataloader)):
            if not torch.cuda.is_available():  # 处理CPU与GPU
                images = Variable(images)
                labels = Variable(labels.float())
            else:
                images = Variable(images).cuda()
                labels = Variable(labels.float()).cuda()

            predict_labels = cnn(images)
            loss = criterion(predict_labels, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        timePath = os.path.join(setting.CURRENT_PATH, 'result',str(int(randomTime())) + '-model.pkl')
        torch.save(cnn.state_dict(), timePath)  # 每个epoch都保存一次
        correctRate = getCorrect(timePath)  # 计算正确率
        print("[*] epoch:", epoch, "loss:", loss.item(), "correctRate:", str(correctRate) + '%')
        epochArray.append(epoch)
        correctRateArray.append(correctRate)
        if correctRate >= max(correctRateArray):
            if os.path.exists(os.path.join(setting.CURRENT_PATH, 'result',saveModelName)):
                os.remove(os.path.join(setting.CURRENT_PATH, 'result',saveModelName))
            os.rename(timePath,os.path.join(setting.CURRENT_PATH, 'result',saveModelName))
        else:
            os.remove(timePath)
    makeRateImage(epochArray, correctRateArray)
    print("[*] Save Last Model and Png in ./result")


if __name__ == '__main__':
    main()

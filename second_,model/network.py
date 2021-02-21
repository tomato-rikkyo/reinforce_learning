import numpy as np

import torch
import torch.backends.cudnn as cudnn
import torch.nn as nn
import torch.nn.functional as F
import math

class Conv_Block(nn.Module):
    def __init__(self, channel, kernel):
        super().__init__()
        self.conv = nn.Conv2d(channel, channel, kernel_size=kernel, padding=1)
        self.bn = nn.BatchNorm2d(num_features=channel)

    def forward(self, x):
        out = F.relu(self.bn(self.conv(x)))
        return out + x


class Policy_Net(nn.Module):
    def __init__(self, channel=192, kernel_first=5, kernel_other=3, n_blocks=2):
        super().__init__()
        self.conv1 = nn.Conv2d(2, channel, kernel_size=kernel_first, padding=2)
        self.bn1 = nn.BatchNorm2d(num_features=channel)
        self.conv_block = nn.Sequential(
            *(n_blocks * [Conv_Block(channel, kernel_other)])
        )
        self.conv_last = nn.Conv2d(channel, 1, kernel_size=1)
        
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()

    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.conv_block(x)
        x = self.conv_last(x)
        out = x.view(x.size(0), -1)
        return out

class Value_Net(nn.Module):
    def __init__(self, channel=192, kernel_first=5, kernel_other=3, n_blocks=10):
        super().__init__()
        self.conv1 = nn.Conv2d(2, channel, kernel_size=kernel_first, padding=2)
        self.bn1 = nn.BatchNorm2d(num_features=channel)
        self.conv_block = nn.Sequential(
            *(n_blocks+1 * [Conv_Block(channel, kernel_other)])
        )
        self.conv_last = nn.Conv2d(channel, 1, kernel_size=1)
        self.fc1 = nn.Linear(15*15, 128)
        self.fc2 = nn.Linear(128, 1)
        
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / n))
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()

    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.conv_block(x)
        x = self.conv_last(x)
        x = x.view(x.size(0), -1)
        out = F.tanh(self.fc2(F.relu(self.fc1(x))))
        return out
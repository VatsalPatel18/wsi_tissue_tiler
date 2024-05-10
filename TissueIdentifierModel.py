import torch
import torch.nn as nn
import torch.nn.functional as F

class TissueIdentifierModel(nn.Module):
    def __init__(self):
        super(TissueIdentifierModel, self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3,stride=1,padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)  )
        
        self.conv2 = nn.Sequential(
            nn.Conv2d(16, 32, kernel_size=3,stride=1,padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2))
        
        self.conv3 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, stride=1,padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2))
        
        self.classifier = nn.Sequential(
            # nn.Flatten(),
            nn.Linear(64 * 28 * 28, 1),

            nn.Sigmoid())
    
    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x
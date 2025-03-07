import os
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

import torch
from torch.utils.data import Dataset
from torchvision import transforms
from torchvision import utils

data_dir_options = {
    'EyePACS': '/home/hong/hc701/preprocessed/eyepacs',
    'APTOS': '/home/hong/hc701/preprocessed/aptos',
}

class Eye_APTOS(Dataset):
    def __init__(self, data_dir, transform=None, mode='train',train_val_split=0.25):
        self.data_dir = data_dir
        self.transform = transform
        self.transform = transforms.ToTensor() if transform is None else transform
        self.mode = mode
        self.train_val_split = train_val_split

        self.data = []
        self.labels = []

        if self.mode == 'train' or self.mode == 'val':
            self.data_path = os.path.join(self.data_dir, 'train')
            for i in os.listdir(self.data_path):
                    data = np.load(os.path.join(self.data_path, i), allow_pickle=True).item()
                    # Image to 0-1
                    image_data = data['image']
                    self.data.append(image_data)
                    self.labels.append(data['label'])
            self.data, self.val_data, self.labels, self.val_labels = train_test_split(self.data, self.labels, test_size=self.train_val_split, random_state=42)
        elif self.mode == 'test':
            self.data_path = os.path.join(self.data_dir, 'test')
            for i in os.listdir(self.data_path):
                data = np.load(os.path.join(self.data_path, i), allow_pickle=True).item()
                # Image to 0-1
                image_data = data['image']
                self.data.append(image_data)
        else:
            raise ValueError('mode should be train, val or test')


    def __len__(self):
        if self.mode == 'train':
            return len(self.data)
        elif self.mode == 'val':
            return len(self.val_data)
        elif self.mode == 'test':
            return len(self.data)
        else:
            raise ValueError('mode should be train, val or test')
    
    def __getitem__(self, idx):
        if self.mode == 'train':
            return self.transform(self.data[idx]), self.labels[idx]
        elif self.mode == 'val':
            return self.transform(self.val_data[idx]), self.val_labels[idx]
        else:
            return self.transform(self.data[idx]), 0
        
    def calculate_weights(self):
        if self.mode == 'train':
            labels = self.labels
        elif self.mode == 'val':
            labels = self.val_labels
        else:
            raise ValueError('mode should be train or val')
        class_weights = compute_class_weight(
            class_weight='balanced',
            classes=list(set(labels)),
            y=labels,
        )
        return torch.FloatTensor(class_weights)


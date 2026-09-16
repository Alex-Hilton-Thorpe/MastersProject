import torch #PyTorch Library
import torch.nn as nn #PyTorch Neural Network Module (Toolbox for building neural networks)
import torch.optim as optim #Optimization algorithms (tools for updating the model's weights during learning)
from torchvision import transforms, datasets #transforms = tools for preparing/manipulating images before the model sees them
from torch.utils.data import DataLoader 


"""Configuration"""
BATCH_SIZE = 32
LEARNING_RATE = 0.001
EPOCHS = 10

DEVICE = torch.device("cpu")

transform = transforms.Compose([transforms.Resize((128, 128)), transforms.ToTensor()])

train_dataset = datasets.ImageFolder(
    root='data/learningObjectDetection/african_plums_dataset/split_datasets/train', 
    transform=transform
)

train_loader = DataLoader(
    train_dataset, 
    batch_size = BATCH_SIZE, 
    shuffle=True
)



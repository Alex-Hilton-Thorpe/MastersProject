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

class CNN(nn.Module):

    def __init__(self):
        super().__init__()

        self.conv1 = nn.Conv2d(
            in_channels=3,
            out_channels=16,
            kernel_size=3,
        )

        self.relu = nn.ReLU()

        self.pool = nn.MaxPool2d(kernel_size=2)

        self.flatten = nn.Flatten()

        self.fc1 = nn.Linear((16 * 63 * 63), 6) 
        # This is a linear layer that takes the flattened output of the convolutional layers and maps it to 6 output classes 
        # Basically 16 = out_channels, 63 = (128 - 3 + 1) / 2 = 63 (after convolution (-3+1) and pooling (/2))

    def forward(self, x):
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pool(x)
        x = self.flatten(x)
        x = self.fc1(x)
        return x

"""These all get called before loop to initialize the model, optimizer, and loss function."""
model = CNN()

optimizer = optim.Adam(
    model.parameters(),
    lr = LEARNING_RATE
)

criterion = nn.CrossEntropyLoss()
# CrossEntropyLoss is commonly used for multi-class classification.
# It compares the model's logits with the correct class labels
# and produces a single loss value. 

for epoch in range(EPOCHS):
    epoch_loss = 0.0
    
    for images, labels in train_loader:
        optimizer.zero_grad() # Clears previous gradient else the gradients would accumulate across multiple backward passes
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward() # Backpropagation: computes the gradient of the loss with respect to the model's parameters
        optimizer.step()
        epoch_loss += loss.item()

    print(f"Epoch {epoch + 1} Loss: {epoch_loss/len(train_loader)}")


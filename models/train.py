import torch #PyTorch Library
import torch.nn as nn #PyTorch Neural Network Module (Toolbox for building neural networks)
import torch.optim as optim #Optimization algorithms (tools for updating the model's weights during learning)
from torchvision import transforms, datasets #transforms = tools for preparing/manipulating images before the model sees them
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay


"""Configuration"""
BATCH_SIZE = 32
LEARNING_RATE = 0.001
EPOCHS = 30

DEVICE = torch.device("cpu")

train_transform = transforms.Compose(
    [transforms.Resize((128, 128)),
    #transforms.RandomHorizontalFlip(),
    #transforms.RandomRotation(10),
    #transforms.RandomResizedCrop((128, 128)),
    #transforms.RandomAffine(),
    #transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor()])

validation_transform = transforms.Compose(
    [transforms.Resize((128, 128)),
    transforms.ToTensor()])

train_dataset = datasets.ImageFolder(
    root='data/learningObjectDetection/african_plums_dataset/split_datasets/binary/train',
    transform=train_transform
)

train_loader = DataLoader(
    train_dataset, 
    batch_size = BATCH_SIZE, 
    shuffle=True
)

validation_dataset = datasets.ImageFolder(
    root='data/learningObjectDetection/african_plums_dataset/split_datasets/binary/validation',
    transform=validation_transform
)

validation_loader = DataLoader(
    validation_dataset,
    batch_size = BATCH_SIZE,
    shuffle=False
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

        self.fc = nn.Linear((16 * 63 * 63), 2) 
        # This is a linear layer that takes the flattened output of the convolutional layers and maps it to 6 output classes 
        # Basically 16 = out_channels, 63 = (128 - 3) / 2 (rounded down) = 63 (after convolution (-3+1) and pooling (/2))

        self.conv2 = nn.Conv2d(
            in_channels=16,
            out_channels=32,
            kernel_size=3,
        )

        #self.fc = nn.Linear((32 * 30 * 30), 2)
        # Linear layer
        # 63 -> Conv3: 63 - 3 + 1 = 61
        # 61 -> Pool2: floor(61 / 2) = 30

        self.dropout = nn.Dropout(p=0.5)  # Dropout layer with a probability of 0.5

    def forward(self, x):
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pool(x)
        #x = self.conv2(x)
        #x = self.relu(x)
        #x = self.pool(x)
        x = self.flatten(x)
        x = self.dropout(x)
        x = self.fc(x)
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
    val_loss = 0.0
    correct_predictions_val = 0
    total_predictions_val = 0
    correct_predictions_train = 0
    total_predictions_train = 0
    
    for images, labels in train_loader:
        optimizer.zero_grad() # Clears previous gradient else the gradients would accumulate across multiple backward passes
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward() # Backpropagation: computes the gradient of the loss with respect to the model's parameters
        optimizer.step()
        epoch_loss += loss.item()

        correct_predictions_train += (torch.argmax(outputs, dim=1) == labels).sum().item()
        total_predictions_train += labels.size(0)

    model.eval()  # Set the model to evaluation mode (disables dropout, batch norm, etc.)

    with torch.no_grad():  # Disable gradient calculation for validation (saves memory and computations)
        for images, labels in validation_loader:
            outputs = model(images)
            total_predictions_val += labels.size(0)  # Get the number of samples in the batch
            predictions = torch.argmax(outputs, dim=1) 
            # dim = 1 means we are taking the argmax across the class dimension (the second dimension of the output tensor)
            correct_predictions_val += (predictions == labels).sum().item()
            # Count the number of correct predictions in the batch

            loss = criterion(outputs, labels)
            val_loss += loss.item()

    model.train()  # Set the model back to training mode for the next epoch

    accuracy_val = correct_predictions_val / total_predictions_val * 100
    accuracy_train = correct_predictions_train / total_predictions_train * 100  
    print(f"Epoch {epoch + 1} Loss: {epoch_loss/len(train_loader):.2f} Training Accuracy: {accuracy_train:.2f}% Validation Loss: {val_loss/len(validation_loader):.2f} Validation Accuracy: {accuracy_val:.2f}%")

model.eval()

all_labels = []
all_predictions = []

with torch.no_grad():
    for images, labels in validation_loader:
        outputs = model(images)
        predictions = torch.argmax(outputs, dim=1)

        all_labels.extend(labels.tolist())
        all_predictions.extend(predictions.tolist())

cm = confusion_matrix(all_labels, all_predictions)

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=validation_dataset.classes
)

disp.plot()
plt.show()

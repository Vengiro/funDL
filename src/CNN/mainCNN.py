import matplotlib.pyplot as plt
import numpy as np

from MyCNN import *
from FCNN import *
from ResNet18 import *
from utilsCNN import *
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

def main(epochs=1):

    train_images = datasets.CIFAR100(root='data', train=True, download=True, transform=transforms.ToTensor())
    test_images = datasets.CIFAR100(root='data', train=False, download=True, transform=transforms.ToTensor())
    classes = train_images.classes
    img_dim = train_images[0][0].shape
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")

    train_loader = DataLoader(train_images, batch_size=2000, shuffle=True)
    test_loader = DataLoader(test_images, batch_size=2000, shuffle=False)

    model = FCNN(in_dim=img_dim[0]*img_dim[1]*img_dim[2], out_dim=100)
    trainNplot(train_loader, test_loader, epochs, model, 'Loss FCNN')

    visualize(model, test_loader, classes)
   
    model = CNN(3, 100)
    loss = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    X_epoch = np.arange(epochs) + 1
    loss_train, loss_test = train(train_loader, test_loader, epochs, model, loss, optimizer)
    trainNplot(train_loader, test_loader, epochs, model, 'Loss CNN')

    visualize(model, test_loader, classes)

    model = ResNet18().to(device)
    trainNplot(train_loader, test_loader, epochs, model, 'Loss ResNet18', device, classes, 10)
def trainNplot(train_loader, test_loader, epoch, model, title, device, classes, nbVis=100):
    loss = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    X_epoch = np.arange(epoch) + 1
    loss_train, loss_test = train(train_loader, test_loader, epoch, model, loss, optimizer, device)

    plt.title(title)
    plt.plot(X_epoch, loss_train, label='Train Loss')
    plt.plot(X_epoch, loss_test, label='Test Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()
    visualize(model, test_loader, classes, device, nbVis)


def train(train_loader, test_loader, epoch, model, loss, optimizer, device):
    loss_train_list = []
    loss_test_list = []
    for i in range(epoch):
        model.train()
        loss_tr = 0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            out = model(x)
            l = loss(out, y)
            loss_tr += l.item()
            l.backward()
            optimizer.step()
            print(f"Epoch: {i} Loss training: {l.item()}")
        loss_train_list.append(loss_tr/len(train_loader))
        print(f"Epoch: {i} Loss training: {loss_tr/len(train_loader)}")
        loss_tr = 0

        model.eval()
        correct = 0
        total = 0
        l_pred = 0
        for x, y in test_loader:
            x, y = x.to(device), y.to(device)
            predicted = model(x)
            l_pred += loss(predicted, y).item()
            predicted = torch.argmax(predicted, dim=1)
            total += y.size(0)
            correct += (predicted == y).sum().item()
            print(f"Epoch: {i} Loss test: {l_pred/len(test_loader)}")
            print(f"Epoch: {i} Accuracy: {correct/total}")
        loss_test_list.append(l_pred/len(test_loader))
        print(f"Epoch: {i} Loss test: {l_pred/len(test_loader)}")
        print(f"Epoch: {i} Accuracy: {correct/total}")
        l_pred = 0

    return loss_train_list, loss_test_list

def visualize(model, test_loader, classes, device, n=100):
    model.eval()
    label_set = set()
    label_list = []
    img = []
    iterator = iter(test_loader)
    while len(label_set) < n:
        try:
            x, y = next(iterator)
        except StopIteration:
            iterator = iter(test_loader)
            x, y = next(iterator)
        for i in range(len(y)):
            old_len = len(label_set)
            label_set.add(y[i].item())
            if len(label_set) > old_len:
                label_list.append(y[i].item())
                img.append(x[i])

    label_pred = model.predict(torch.stack(img).to(device))


    figure, ax = plt.subplots(n//5, 5, figsize=(20, 80))
    for i in range(n):
        ax[i//5, i%5].imshow(img[i].permute(1, 2, 0))
        ax[i//5, i%5].set_title(f"True: {classes[label_list[i]]}{label_list[i]} Pred: {classes[label_pred[i]]}{label_pred[i]}", fontsize=12, color='green' if label_list[i] == label_pred[i] else 'red')
        ax[i//5, i%5].axis('off')
    plt.show()

if __name__ == '__main__':
    main()
import torch.utils.data as data
from PIL import Image
import os
import os.path
import numpy as np

IMG_EXTENSIONS = [
    '.jpg', '.JPG', '.jpeg', '.JPEG',
    '.png', '.PNG', '.ppm', '.PPM', '.bmp', '.BMP',
]


def find_classes(dir):
    classes = [d for d in os.listdir(dir) if os.path.isdir(os.path.join(dir, d))]
    classes.sort()
    class_to_idx = {classes[i]: i for i in range(len(classes))}
    return classes, class_to_idx


def is_image_file(filename):
    return any(filename.endswith(extension) for extension in IMG_EXTENSIONS)


def make_dataset(dir, class_to_idx):
    images = []
    dir = os.path.expanduser(dir)
    for target in os.listdir(dir):
        d = os.path.join(dir, target)
        if not os.path.isdir(d):
            continue

        for root, _, fnames in sorted(os.walk(d)):
            for fname in fnames:
                if is_image_file(fname):
                    path = os.path.join(root, fname)
                    item = (path, class_to_idx[target])
                    images.append(item)

    return images


def default_flist_reader(flist):
    """
    flist format: impath label\nimpath label\n ...(same to caffe's filelist)
    """
    imlist = []
    with open(flist, 'r') as rf:
        for line in rf.readlines():
            impath, imlabel = line.strip().split()
            imlist.append((impath, int(imlabel)))

    return imlist


def default_loader(path):
    return Image.open(path).convert('RGB')


def make_dataset_nolist(image_list):
    with open(image_list) as f:
        image_index = [x.split(' ')[0] for x in f.readlines()]
        # print(len(image_index))
        # print(image_index[:5])
    with open(image_list) as f:
        label_list = []
        selected_list = []
        for ind, x in enumerate(f.readlines()):
            label = x.split(' ')[1].strip()
            label_list.append(int(label))
            selected_list.append(ind)
        image_index = np.array(image_index)
        label_list = np.array(label_list)
    # print(image_index.shape)
    # print(image_index[:5])
    image_index = image_index[selected_list]
    # print(image_index.shape)
    # print(image_index[:5])
    # print(label_list[:5])
    # print(selected_list[:5])
    return image_index, label_list


class ImageFolder(data.Dataset):
    """A generic data loader where the images are arranged in this way: ::
        root/dog/xxx.png
        root/dog/xxy.png
        root/dog/xxz.png
        root/cat/123.png
        root/cat/nsdf3.png
        root/cat/asd932_.png
    Args:
        root (string): Root directory path.
        transform (callable, optional): A function/transform that  takes in an PIL image
            and returns a transformed version. E.g, ``transforms.RandomCrop``
        target_transform (callable, optional): A function/transform that takes in the
            target and transforms it.
        loader (callable, optional): A function to load an image given its path.
     Attributes:
        classes (list): List of the class names.
        class_to_idx (dict): Dict with items (class_name, class_index).
        imgs (list): List of (image path, class_index) tuples
    """

    def __init__(self, image_list, transform=None, target_transform=None, return_paths=False,
                 loader=default_loader,train=False, return_id=False):
        imgs, labels = make_dataset_nolist(image_list)
        self.imgs = imgs
        self.labels= labels
        self.transform = transform
        self.target_transform = target_transform
        self.loader = loader
        self.return_paths = return_paths
        self.return_id = return_id
        self.train = train

    def __getitem__(self, index):
        """
        Args:
            index (int): Index
        Returns:
            tuple: (image, target) where target is class_index of the target class.
        """

        path = self.imgs[index]
        target = self.labels[index]
        img = self.loader(path)
        img = self.transform(img)

        if self.target_transform is not None:
            target = self.target_transform(target)
        if self.return_paths:
            return img, target, path
        elif self.return_id:
            return img, target ,index
        else:
            return img, target

    def __len__(self):
        return len(self.imgs)


class ImageFolder_fix(data.Dataset):
    """A generic data loader where the images are arranged in this way: ::
        root/dog/xxx.png
        root/dog/xxy.png
        root/dog/xxz.png
        root/cat/123.png
        root/cat/nsdf3.png
        root/cat/asd932_.png
    Args:
        root (string): Root directory path.
        transform (callable, optional): A function/transform that  takes in an PIL image
            and returns a transformed version. E.g, ``transforms.RandomCrop``
        target_transform (callable, optional): A function/transform that takes in the
            target and transforms it.
        loader (callable, optional): A function to load an image given its path.
     Attributes:
        classes (list): List of the class names.
        class_to_idx (dict): Dict with items (class_name, class_index).
        imgs (list): List of (image path, class_index) tuples
    """

    def __init__(self, image_list, indexes=None, transform=None, target_transform=None, return_paths=False,
                 loader=default_loader,train=False, return_id=False, name=None):
        imgs, labels = make_dataset_nolist(image_list)
        self.imgs = imgs
        self.labels= labels
        self.transform = transform
        self.target_transform = target_transform
        self.loader = loader
        self.return_paths = return_paths
        self.return_id = return_id
        self.train = train
        if indexes is not None:
            self.imgs = self.imgs[indexes]
            self.labels = self.labels[indexes]
        self.set_index()
        if name is not None:
            f = open(os.path.join('/home/admin2/jn/OOD_SSL/OP_Match-main_for_fixmatch/new-result/tiny-28-50-1-1', name+'.txt'), 'w')
            for i, img in enumerate(self.imgs_index):
                if self.targets_index[i] > 6:
                    self.targets_index[i] -= 1
                f.write(img+' '+ str(self.targets_index[i]))
                f.write('\n')
            f.close()

    def set_index(self, indexes=None):
        if indexes is not None:
            self.imgs_index = self.imgs[indexes]
            self.targets_index = self.labels[indexes]
        else:
            self.imgs_index = self.imgs
            self.targets_index = self.labels

    def init_index(self):
        self.imgs_index = self.imgs
        self.targets_index = self.labels

    def __getitem__(self, index):
        """
        Args:
            index (int): Index
        Returns:
            tuple: (image, target) where target is class_index of the target class.
        """

        path = self.imgs_index[index]
        target = self.targets_index[index]
        img = self.loader(path)
        img = self.transform(img)

        if self.target_transform is not None:
            target = self.target_transform(target)
        if self.return_paths:
            return img, target, path
        elif self.return_id:
            return img, target ,index
        else:
            return img, target

    def __len__(self):
        return len(self.imgs_index)


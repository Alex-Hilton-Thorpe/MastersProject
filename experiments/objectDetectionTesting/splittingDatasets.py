import random
from pathlib import Path
import shutil

random.seed(0)

train = 0.7
validation = 0.15

dataset_path = Path("data/learningObjectDetection/african_plums_dataset/african_plums")
output_train_path = Path("data/learningObjectDetection/african_plums_dataset/split_datasets/train")
output_val_path = Path("data/learningObjectDetection/african_plums_dataset/split_datasets/validation")
output_test_path = Path("data/learningObjectDetection/african_plums_dataset/split_datasets/test")
output_train_path.mkdir(parents=True, exist_ok=True)
output_val_path.mkdir(parents=True, exist_ok=True)
output_test_path.mkdir(parents=True, exist_ok=True)

image_extensions = {".jpg", ".jpeg", ".png"}

for file in dataset_path.iterdir():
    if file.is_dir():

        train_path = output_train_path / file.name
        val_path = output_val_path / file.name
        test_path = output_test_path / file.name

        train_path.mkdir(parents=True, exist_ok=True)
        val_path.mkdir(parents=True, exist_ok=True)
        test_path.mkdir(parents=True, exist_ok=True)

        images = [image for image in file.iterdir() if image.suffix.lower() in image_extensions]
        random.shuffle(images)

        total_number_images = len(images)
        train_size = int(total_number_images * train)
        val_size = int(total_number_images * validation)

        train_images = images[:train_size]

        for image in train_images:
            shutil.copy(image, train_path)

        val_images = images[train_size: train_size + val_size]

        for image in val_images:
            shutil.copy(image, val_path)

        test_images = images[train_size + val_size:]

        for image in test_images:
            shutil.copy(image, test_path)

        print(f"{file.name}: {total_number_images}")
        print(f"Train: {len(train_images)}")
        print(f"Validation: {len(val_images)}")
        print(f"Test: {len(test_images)}")
        print("\n")




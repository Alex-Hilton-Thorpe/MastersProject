from pathlib import Path
import shutil

dataset_path = Path("data/learningObjectDetection/african_plums_dataset/split_datasets/six_classes")
output_train_path = Path("data/learningObjectDetection/african_plums_dataset/split_datasets/binary/train")
output_val_path = Path("data/learningObjectDetection/african_plums_dataset/split_datasets/binary/validation")
output_test_path = Path("data/learningObjectDetection/african_plums_dataset/split_datasets/binary/test")
output_train_path.mkdir(parents=True, exist_ok=True)
output_val_path.mkdir(parents=True, exist_ok=True)
output_test_path.mkdir(parents=True, exist_ok=True)

image_extensions = {".jpg", ".jpeg", ".png"}

for file in dataset_path.iterdir():
    if file.is_dir():

        for file2 in file.iterdir():
            if file2.is_dir():

                if file2.name == "unaffected":
                    train_path = output_train_path / "unaffected"
                    val_path = output_val_path / "unaffected"
                    test_path = output_test_path / "unaffected"
                else:
                    train_path = output_train_path / "affected"
                    val_path = output_val_path / "affected"
                    test_path = output_test_path / "affected"

                train_path.mkdir(parents=True, exist_ok=True)
                val_path.mkdir(parents=True, exist_ok=True)
                test_path.mkdir(parents=True, exist_ok=True)

                images = [image for image in file2.iterdir() if image.suffix.lower() in image_extensions]
                for image in images:
                    if file.name == "test":
                        shutil.copy(image, test_path)
                    elif file.name == "train":
                        shutil.copy(image, train_path)
                    elif file.name == "validation":
                        shutil.copy(image, val_path)

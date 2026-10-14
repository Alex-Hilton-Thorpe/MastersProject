from pathlib import Path

dataset_Path = Path("data/learningObjectDetection/african_plums_dataset/split_datasets")

for file in dataset_Path.iterdir():
    print(f"{file.name}:")

    for subfile in file.iterdir():
            images = 0
            if subfile.is_dir():
                images += len(list(subfile.iterdir()))

            print(f"{subfile.name}: {images}")

    print("\n")


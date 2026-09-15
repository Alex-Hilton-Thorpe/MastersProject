from pathlib import Path

dataset_Path = Path("data/learningObjectDetection/african_plums_dataset/african_plums")

for file in dataset_Path.iterdir():
    if file.is_dir():
        images = list(file.iterdir())
        print(f"{file.name}: {len(images)}")


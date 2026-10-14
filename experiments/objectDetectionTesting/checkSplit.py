from pathlib import Path

binary_path = Path("data/learningObjectDetection/african_plums_dataset/split_datasets/binary")

for split in ["train", "validation", "test"]:
    print(f"\n{split}:")
    
    for class_name in ["affected", "unaffected"]:
        path = binary_path / split / class_name
        images = list(path.iterdir())
        print(f"{class_name}: {len(images)}")
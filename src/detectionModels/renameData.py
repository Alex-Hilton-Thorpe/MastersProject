from pathlib import Path

folder = Path("C:/Masters/MastersProject/data/captured_data/left_Frames")

old_files = sorted(
    folder.glob("frame_*.*"),
    key=lambda p: int(p.stem.split("_")[1])
)

for n, path in enumerate(old_files, start=1):
    new_name = folder / f"capture_{n}{path.suffix}"
    path.rename(new_name)
    print(f"{path.name} -> {new_name.name}")
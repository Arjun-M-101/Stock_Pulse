import os, shutil

layers = ["lake/parquet", "chk/parquet", "chk/postgres"]

for layer in layers:
    if os.path.exists(layer):
        for item in os.listdir(layer):
            item_path = os.path.join(layer, item)
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        open(os.path.join(layer, ".gitkeep"), "a").close()
        print(f"🧹 Emptied {layer}/ and restored .gitkeep")
    else:
        os.makedirs(layer)
        open(os.path.join(layer, ".gitkeep"), "a").close()
        print(f"📂 Created missing folder: {layer}/ with .gitkeep")
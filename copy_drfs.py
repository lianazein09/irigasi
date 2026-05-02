import os
import shutil

src = r'C:\Users\ASUS\AppData\Local\Programs\Python\Python312\Lib\site-packages\rest_framework'
dst = r'd:\Irigasi\backend\venv\Lib\site-packages\rest_framework'

# Create destination directory if it doesn't exist
os.makedirs(dst, exist_ok=True)

# Copy all items from source to destination
for item in os.listdir(src):f
    src_item = os.path.join(src, item)
    dst_item = os.path.join(dst, item)
    
    if os.path.exists(dst_item):
        continue
        
    if os.path.isdir(src_item):
        shutil.copytree(src_item, dst_item)
    else:
        shutil.copy2(src_item, dst_item)

print("Copy completed!")
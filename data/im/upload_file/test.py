import os


dst = 1024*1024*1024    # 1GB
base_dir = './'
file_size = {}
for file_name in os.listdir(base_dir):
    file_path = os.path.join(base_dir, file_name)
    if os.path.isfile(file_path):
        size = os.path.getsize(file_path)
        if size <= 1024*1024*10:
            file_size[file_path] = size

size_to_file = {v: k for k, v in file_size.items()}


dp = {}
count = {k:0 for k in file_size}
price = sorted([k for k in size_to_file])

while dst > 0 and len(price) > 0:
    _p = price[-1]
    if dst >= _p:
        
        count[size_to_file[_p]] += (dst // _p)
        dst = dst % _p
        print(111)
    price.pop()



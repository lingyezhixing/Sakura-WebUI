import json
import os

def main():
    path = input("请输入术语表文件路径：")
    if os.path.exists(path) == False:
        if os.path.exists(path[1:-1]):
            path = path[1:-1]
        else:
            print("文件不存在")
            return
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    new_data = [{'src': key, 'dst': value} for key, value in data.items()]
    with open('new_terms.json', 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)
    print("转换完成，新文件名为new_terms.json")

if __name__ == '__main__':
    while True:
        main()
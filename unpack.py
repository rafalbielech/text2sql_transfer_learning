import os
import zipfile

# One big hack!

def unpack_glove():
    glove_dir = os.path.join('models', 'sqlnet', 'glove')
    unziped_path = os.path.join(glove_dir, 'glove.6B.50d.txt')
    zip_path = os.path.join(glove_dir, 'glove6b50dtxt.zip')
    if os.path.exists(unziped_path):
        print('Already unzipped glove!')
    else:
        print('Unzipping glove...', end='')
        with zipfile.ZipFile(zip_path) as f:
            f.extractall(path=glove_dir)
        print('Done!')

def unpack_spider_dataset():
    unziped_path = os.path.join('spider_dataset')
    zip_path = os.path.join('spider_dataset.txt')
    double_zip_path = os.path.join('spider_dataset.zip.zip')
    if os.path.exists(unziped_path):
        print('Already unzipped spider dataset!')
    else:
        print('Unzipping spider dataset...', end='')
        with zipfile.ZipFile(double_zip_path) as f:
            f.extractall()
            with zipfile.ZipFile(zip_path) as g:
                g.extractall()
            os.remove(zip_path)
        print('Done!')


if __name__ == "__main__":
    unpack_glove()
    unpack_spider_dataset()

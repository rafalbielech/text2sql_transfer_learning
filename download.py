import os
import zipfile

def unpack_glove():
    unziped_path = os.path.join('models', 'sqlnet', 'glove', 'glove.6B.50d.txt')
    zip_path = os.path.join('models', 'sqlnet', 'glove', 'glove6b50dtxt.zip')
    if os.path.exists(unziped_path):
        print('Already unzipped glove!')
    else:
        print('Unzipping glove...', end='')
        with zipfile.ZipFile(zip_path) as f:
            f.extractall()
        print('Done!')

if __name__ == "__main__":
    unpack_glove()

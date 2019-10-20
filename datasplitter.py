import os
import sys
import glob

class Datasplitter():
    def __init__(self, path_to_original_dataset):
        # path to the original spider_dataset
        self.path = path_to_original_dataset
        # check if the path exists, if it does not, raise error
        if (not os.path.exists(self.path)):
            raise ValueError("There is an issue with the path you specified, try again")

    def return_path(self):
        return self.path

    def list_available_datasets(self, list_full_path=False):
        # list the full path for each of the datasets
        path = os.path(self.path, database)
        try:
            avail_dataset = [item for item in os.listdir(path) if not item.startswith(".")]
            for counter, db in enumerate(avail_dataset):
                if list_full_path:
                    print("{}. - {} - {}".format(counter, db, os.path.join(path, db)))
                else:
                    print("{}. - {}".format(counter, db))
        except Exception as e:
            print("Error with the specified path {}\nError: {}".format(path, e))

    def create_new_data(self):
        try:
            os.symlink(src, dst)
        except Exception as e:
            print("Error occured while creating symbolic link\nError: {}".format(e))

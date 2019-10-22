import os
import sys
import json
import shutil

class DataSplitter():
    def __init__(self, path_to_original_dataset):
        self.new_dataset = "" # path to the new dataset that we will be creating
        self.path = path_to_original_dataset # path to the original spider_dataset
        self.split = 0.7
        # check if the path exists, if it does not, raise error
        if (not os.path.exists(self.path)):
            raise ValueError("There is an issue with the path you specified, try again")

    def return_path(self):
        # just return path
        return self.path

    def return_directory(self):
        # return the directory of the object's spider specified path
        return os.path.dirname(self.path)

    def create_dataset_folder(self, name_of_new_dir):
        # create a new directory in the same directory as the object's specified spider dataset
        curr_dir = self.return_directory()
        curr_dir = os.path.join(curr_dir, name_of_new_dir)
        if not os.path.exists(curr_dir):
            try:
                os.mkdir(curr_dir)
                print("Directory " , name_of_new_dir ,  " created at " + curr_dir)
                self.new_dataset = curr_dir
            except Exception as e:
                print("Error creating a directory {}\nError: {}".format(name_of_new_dir, e))
        else:
            print("Directory " , name_of_new_dir ,  " already exists, operation terminated")

    def delete_dataset_folder(self):
        if os.path.exists(self.new_dataset):
            try:
                shutil.rmtree(os.path.abspath(self.new_dataset))
                print("Successfully removed {}".format(self.new_dataset))
                self.new_dataset = ""
            except Exception as e:
                print("Error deleting a directory {}\nError: {}".format(self.new_dataset, e))
        else:
            print("Nothing to delete, the path does not exist or self.new_dataset is empty")

    def merge_data_files(self, file_names=["train", "train_others", "dev"]):
        # file names contains all of our examples across three different json files
        # we will be merging all of the three files together to then create our data
        def filter_out_duplicates(list_of_elements):
            # Use set to filter out duplicates SQL examples from the merged files
            print("Before, length of list was {}".format(len(list_of_elements)))
            seen = set()
            new_list = []
            for d in list_of_elements:
                # each query is a concatenration of table, query, and respective question
                rep_string = d['db_id'] + "!@#" + d['query'] + "!@#" + d['question']
                # if we haven't seen the entry yet, add it to the new list and also add it to the set
                if rep_string not in seen:
                    seen.add(rep_string)
                    new_list.append(d)
            print("After, length of list was {}".format(len(new_list)))
            return new_list
        # only proceed if there is a new dataset folder already created
        if (self.new_dataset != ""):
            combined_file = []
            for file in file_names:
                file = os.path.join(self.path, file + ".json")
                with open(file, "rb") as in_file:
                    for entry in json.load(in_file):
                        combined_file.append(entry)
            try:
                combined_file = filter_out_duplicates(combined_file)
                temp_file_path = os.path.join(self.new_dataset, "train.json")
                json.dump(combined_file, open(temp_file_path , "w"))
            except Exception as e:
                print("Error merging file and saving to new directory\nError: {}".format(e))
        else:
            print("Create a new dataset folder first")

    def read_in_json_file_db(self, file, unique=False):
        file = os.path.join(self.path, file)
        items = [item['db_id'] for item in json.load(open(file))]
        print("Len of list is {}".format(len(items)))
        if unique:
            temp = list(set(items))
            print("There are {} unique dbs".format(len(temp)))
            print(temp)

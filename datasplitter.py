import os
import sys
import json
import shutil

class DataSplitter():
    def __init__(self, path_to_original_dataset):
        self.new_dataset = "" # path to the new dataset that we will be creating
        self.path = path_to_original_dataset # path to the original spider_dataset
        self.split = 0.6
        # check if the path exists, if it does not, raise error
        if (not os.path.exists(self.path)):
            raise ValueError("There is an issue with the path you specified, try again")

    def return_path(self):
        return self.path # just return path

    def return_directory(self):
        return os.path.dirname(self.path) # return the directory of the object's spider specified path

    def create_dataset_folder(self, name_of_new_dir):
        # create a new directory in the same directory as the object's specified spider dataset
        curr_dir = os.path.join(self.return_directory(), name_of_new_dir)
        # check if the directory already exists, if not, then print message
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
        # first check if the path exists or if self.new_dataset is set, if not, then only print to screen
        if os.path.exists(self.new_dataset):
            try:
                shutil.rmtree(os.path.abspath(self.new_dataset))
                print("Successfully removed {}".format(self.new_dataset))
                self.new_dataset = ""
            except Exception as e:
                print("Error deleting a directory {}\nError: {}".format(self.new_dataset, e))
        else:
            print("Nothing to delete, the path does not exist or self.new_dataset is empty")

    def merge_data_files(self, database, file_names=["train", "train_others", "dev"]):
        ######### filenames ###########################
        # file names contains all of our examples across three different json files
        # we will be merging all of the three files together to then create our data
        ######### database ###########################
        # the name of the database that we want to split out list of data on
        ##############################################
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

        def move_file_to_new_dir(file):
            try:
                file = os.path.join(self.path, file + ".json")
                shutil.copy(file, self.new_dataset)
            except Exception as e:
                print("Error moving file {}\nError: {}".format(file, e))

        def split_based_on_database(designated_database, combined_list):
            def write_to_json(file_name, list):
                temp_file_path = os.path.join(self.new_dataset, file_name + ".json")
                try:
                    json.dump(list, open(temp_file_path , "w"))
                except Exception as e:
                    print("Error writing {}\nError: {}".format(temp_file_path, e))


            def split_test_val(list_to_split):
                test = list_to_split[:int(len(list_to_split) * self.split)]
                val = list_to_split[int(len(list_to_split) * self.split):]
                return test, val
                # databases contains the list of databases that are in our combined list of unique entries
            databases = [item['db_id'] for item in combined_list]

            if designated_database in databases:
                print("{} is in the list".format(designated_database))
                all_except_designated = [item for item in combined_list if item['db_id'] != designated_database]
                designated = [item for item in combined_list if item['db_id'] == designated_database]
                write_to_json("train", all_except_designated)
                write_to_json("dev", designated)
                test, val = split_test_val(designated)
                write_to_json("test", test)
                write_to_json("validate", val)
            else:
                print("{} is in not the list".format(designated_database))
                write_to_json("all_train", combined_list)

        # only proceed if there is a new dataset folder already created
        if (self.new_dataset != ""):
            combined_file = []
            for file in file_names:
                file = os.path.join(self.path, file + ".json")
                with open(file, "rb") as in_file:
                    for entry in json.load(in_file):
                        combined_file.append(entry)
            try:
                # model expects a tables.json file
                move_file_to_new_dir("tables")
                # remove duplicates
                combined_file = filter_out_duplicates(combined_file)
                # check if the designed database exists in the combined file list, if it does, then
                split_based_on_database(database, combined_file)
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

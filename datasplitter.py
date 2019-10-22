import os
import sys
import json
import shutil

class DataSplitter():
    def __init__(self, path_to_original_dataset):
        self.new_dataset = "" # path to the new dataset that we will be creating
        self.combined_data = []
        self.unique_combined_data = []
        self.path = path_to_original_dataset # path to the original spider_dataset
        self.split = 0.6
        if (not os.path.exists(self.path)): # check if the path exists, if it does not, raise error
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
                sys.exit()
        else:
            print("Directory " , name_of_new_dir ,  " already exists, operation terminated")
            sys.exit()

    def move_file_to_new_dir(self, file):
        try:
            file = os.path.join(self.path, file + ".json")
            shutil.copy(file, self.new_dataset)
        except Exception as e:
            print("Error moving file {}\nError: {}".format(file, e))
            sys.exit()

    def split_based_on_database(self, designated_database, combined_list):
        def write_to_json(file_name, list):
            temp_file_path = os.path.join(self.new_dataset, file_name + ".json")
            try:
                json.dump(list, open(temp_file_path , "w"))
            except Exception as e:
                print("Error writing {}\nError: {}".format(temp_file_path, e))
                sys.exit()

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

    def delete_dataset_folder(self):
        # first check if the path exists or if self.new_dataset is set, if not, then only print to screen
        if os.path.exists(self.new_dataset):
            try:
                shutil.rmtree(os.path.abspath(self.new_dataset))
                print("Successfully removed {}".format(self.new_dataset))
                self.new_dataset = ""
                self.combined_data = []
                self.unique_combined_data = []
            except Exception as e:
                print("Error deleting a directory {}\nError: {}".format(self.new_dataset, e))
        else:
            print("Nothing to delete, the path does not exist or self.new_dataset is empty")

    def merge_data_files(self, file_names=["train", "train_others", "dev"]):
        ######### filenames ###########################
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
                # model expects a tables.json file
                self.move_file_to_new_dir("tables")
                # remove duplicates
                combined_file = filter_out_duplicates(combined_file)
                self.combined_data = combined_file
                self.unique_combined_data = list(set([item['db_id'] for item in self.combined_data]))
            except Exception as e:
                print("Error merging file and saving to new directory\nError: {}".format(e))
        else:
            print("Create a new dataset folder first")

    def show_list_of_available_db(self):
        items = [item['db_id'] for item in self.combined_data]
        print("Len of list is {}".format(len(items)))
        unique_items = list(set(items))
        print("There are {} unique dbs".format(len(unique_items)))
        for counter,db in enumerate(unique_items):
            print("{} - {}".format(counter,db))


if __name__ == "__main__":
    original_directory_name = str(input("Where is the original spider dataset located?:\n"))
    ds = DataSplitter(original_directory_name)
    new_directory_name = str(input("What is the name of directory you would like to create?:\n"))
    ds.create_dataset_folder(new_directory_name)
    ds.merge_data_files()
    ds.show_list_of_available_db()

    db_list = int(input("What database # would you like to split on?\n"))
    db_indicator = None

    while (db_list >= len(ds.unique_combined_data)):
        db_list = int(input("What database # would you like to split on?\n"))

    selected_database = ds.unique_combined_data[db_list]
    print("You selected to split on {}".format(selected_database))

    ds.split_based_on_database(selected_database, ds.combined_data)

import os
import sys
import json
import shutil
import argparse

class DataSplitter():
    def __init__(self, path_to_original_dataset):
        self.new_dataset = "" # path to the new dataset that we will be creating
        self.combined_data = [] # contains all of the merged data from multiple data files
        self.unique_combined_data = [] # contains only unique database names from the combined data list
        self.path = path_to_original_dataset # path to the original spider_dataset
        self.split = 0.6
        if (not os.path.exists(self.path)): # check if the path exists, if it does not, raise error
            raise ValueError("There is an issue with the path you specified, try again")

    def create_dataset_folder(self, name_of_new_dir):
        '''
        This function creates a new directory with the same name as name_of_new_dir parameter
        '''
        curr_dir = os.path.join(os.path.dirname(self.path), name_of_new_dir)
        # check if the directory already exists, if not, then print message
        if not os.path.exists(curr_dir):
            try:
                # try to create a new directory, if successful, then set self.new_dataset path
                os.mkdir(curr_dir)
                self.new_dataset = curr_dir
                print("Directory " , name_of_new_dir ,  " created at location: " + curr_dir)
            except Exception as e:
                print("Error creating directory {}\nError: {}".format(name_of_new_dir, e))
                sys.exit()
        else:
            print("Directory " , name_of_new_dir ,  " already exists, operation terminated")
            sys.exit()

    def delete_dataset_folder(self):
        '''
        This function deletes a directory that is set under self.new_dataset
        '''
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
                sys.exit()
        else:
            print("Nothing to delete, the path does not exist or self.new_dataset is empty")
            sys.exit()

    def split_based_on_database(self, designated_database, combined_list):
        '''
        This function splits the combined list of examples into training/test/validation files
        The split is done based on the designated_database variable, examples where the db_id matches designated_database
        are split into test/validation files, all other examples are sent to training
        '''
        def write_to_json(file_name, list):
            # write a list object to file
            temp_file_path = os.path.join(self.new_dataset, file_name + ".json")
            try:
                json.dump(list, open(temp_file_path , "w"))
            except Exception as e:
                print("Error writing {}\nError: {}".format(temp_file_path, e))
                sys.exit()

        def split_test_val(list_to_split):
            # split list of items into testing and validation sets based on self.split
            test = list_to_split[:int(len(list_to_split) * self.split)]
            val = list_to_split[int(len(list_to_split) * self.split):]
            return test, val
            # databases contains the list of databases that are in our combined list of unique entries

        databases = [item['db_id'] for item in combined_list]

        if designated_database in databases:
            print("{} is in the list".format(designated_database))
            all_except_designated = [item for item in combined_list if item['db_id'] != designated_database]
            designated = [item for item in combined_list if item['db_id'] == designated_database]
            # write to both dev and train files, because current model config expects these values
            write_to_json("train", all_except_designated)
            write_to_json("dev", designated)
            # further split the dev into testing and validation file
            test, val = split_test_val(designated)
            write_to_json("test", test)
            write_to_json("validate", val)
        else:
            print("{} is in not the list".format(designated_database))
            write_to_json("all_train", combined_list)



    def merge_data_files(self, file_names=["train", "train_others", "dev"]):
        '''
        File names contains all of our examples across three different json files
        we will be merging all of the three files together to then create our data
        '''
        def move_file_to_new_dir(file):
            try:
                file = os.path.join(self.path, file + ".json")
                shutil.copy(file, self.new_dataset)
            except Exception as e:
                print("Error moving file {}\nError: {}".format(file, e))
                sys.exit()

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
        # combine data from all of the data files
        if (self.new_dataset != ""):
            combined_file = []
            for file in file_names:
                file = os.path.join(self.path, file + ".json")
                with open(file, "rb") as in_file:
                    for entry in json.load(in_file):
                        combined_file.append(entry)
            try:
                # model expects a tables.json file, so copy the existing tables file to new directory
                move_file_to_new_dir("tables")
                # remove duplicates from combined list
                combined_file = filter_out_duplicates(combined_file)

                self.combined_data = combined_file
                self.unique_combined_data = sorted(list(set([item['db_id'] for item in self.combined_data])))
            except Exception as e:
                print("Error merging file and saving to new directory\nError: {}".format(e))
                sys.exit()
        else:
            print("Create a new dataset folder first")

    def show_list_of_available_db(self):
        items = [item['db_id'] for item in self.combined_data]
        print("Len of list is {}".format(len(items)))
        unique_items = self.unique_combined_data
        print("There are {} unique dbs".format(len(unique_items)))
        for counter,db in enumerate(unique_items):
            print("{} - {}".format(counter,db))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--orig_dataset', type=str,
        help='the location of the original spider dataset')
    parser.add_argument('--new_dataset_dir', type=str,
        help='the directory where the new dataset will be placed')
    parser.add_argument('--database_num', type=int,
        help='the number of the database to split on')
    parser.add_argument('--print_db_nums', action='store_true',
        help='print the database numbers')
    args = parser.parse_args()

    original_directory_name = args.orig_dataset
    ds = DataSplitter(original_directory_name)

    new_directory_name = args.new_dataset_dir
    ds.create_dataset_folder(new_directory_name)

    ds.merge_data_files()

    if args.print_db_nums:
        ds.show_list_of_available_db()

    db_chosen_num = args.database_num
    assert 0 <= db_chosen_num < len(ds.unique_combined_data), 'Database number out of bounds'
    selected_database = ds.unique_combined_data[db_chosen_num]

    ds.split_based_on_database(selected_database, ds.combined_data)

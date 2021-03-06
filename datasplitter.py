import os
import sys
import json
import shutil
import argparse
import random as r
from collections import Counter

class DataSplitter():
    def __init__(self, path_to_original_dataset, train_split=0.6, retrain_split=0.6):
        self.new_dataset = "" # path to the new dataset that we will be creating
        self.path = path_to_original_dataset # path to the original spider_dataset
        self.combined_data = [] # contains all of the merged data from multiple data files
        self.unique_combined_data = [] # contains only unique database names from the combined data list
        self.train_split = train_split # split used to separate training data into train and val
        self.retrain_split = retrain_split # split used to separate retrain data into train and other, other is then split equally to test and val
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

    def split_based_on_database_v2(self, designated_database, combined_list):
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

        def split_training_data(list_to_split, split_param):
            # split list of items into train and validation sets based on self.train_split
            # first, shuffle the list to make random splits
            r.shuffle(list_to_split)
            # shuffle the list before splitting
            if split_param < 1.0:
                # then, we are splitting by percentage
                train_train = list_to_split[:int(len(list_to_split) * split_param)]
                train_val = list_to_split[int(len(list_to_split) * split_param):]
            else:
                train_train = list_to_split[:int(split_param)]
                train_val = list_to_split[int(split_param):]
            return train_train, train_val

        def split_retrain_set(list_to_split, split_param):
            def split_equally(list, n_groups):
                k, m = divmod(len(list), n_groups)
                return [list[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n_groups)]
            # this method splits the retrain data into three categories, train, val, and test
            r.shuffle(list_to_split)
            if split_param < 1.0:
                retrain_train = list_to_split[:int(len(list_to_split) * split_param)]
                val_and_test_equal_split = split_equally(list_to_split[int(len(list_to_split) * split_param):], 2)
            else:
                retrain_train = list_to_split[:int(split_param)]
                val_and_test_equal_split = split_equally(list_to_split[int(split_param):], 2)
            # return 
            return retrain_train, val_and_test_equal_split[0], val_and_test_equal_split[1]
            

        # databases contains the list of databases that are in our combined list of unique entries
        databases = [item['db_id'] for item in combined_list]
        if designated_database in databases:
            #print("{} is in the list".format(designated_database))
            all_except_designated = [item for item in combined_list if item['db_id'] != designated_database]
            designated = [item for item in combined_list if item['db_id'] == designated_database]
            print("| Database {} | train ex #: {} | test ex #: {} |".format(designated_database, len(all_except_designated), len(designated)))
            
            train_train, train_val = split_training_data(all_except_designated, self.train_split)
            write_to_json("train_train", train_train)
            write_to_json("train_val", train_val)
            assert len(all_except_designated) == len(train_train) + len(train_val), "Mismatch in the values for in the train counts" + designated_database

            retrain_train, retrain_val, retrain_test = split_retrain_set(designated, self.retrain_split)
            write_to_json("retrain_train", retrain_train)
            write_to_json("retrain_val", retrain_val)
            write_to_json("retrain_test", retrain_test)
            assert len(designated) == len(retrain_train) + len(retrain_val) + len(retrain_test), "Mismatch in the values for in the retrain counts" + designated_database
        else:
            print("{} is in not the list".format(designated_database))
            write_to_json("all_train", combined_list)

    def split_based_on_database_v1(self, designated_database, combined_list):
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

        def split_test_val(list_to_split, split_param):
            # split list of items into testing and validation sets based on self.split
            if split_param < 1.0:
                # then, we are splitting by percentage
                val = list_to_split[:int(len(list_to_split) * split_param)]
                test = list_to_split[int(len(list_to_split) * split_param):]
            else:
                val = list_to_split[:int(split_param)]
                test = list_to_split[int(split_param):]
            return test, val
            # databases contains the list of databases that are in our combined list of unique entries
        databases = [item['db_id'] for item in combined_list]
        if designated_database in databases:
            #print("{} is in the list".format(designated_database))
            all_except_designated = [item for item in combined_list if item['db_id'] != designated_database]
            designated = [item for item in combined_list if item['db_id'] == designated_database]
            print("| Database {} | train ex #: {} | test ex #: {} |".format(designated_database, len(all_except_designated), len(designated)))
            # write to both dev and train files, because current model config expects these values
            write_to_json("train", all_except_designated)
            write_to_json("dev", designated)

            # further split the dev into testing and validation file
            test, val = split_test_val(designated, self.train_split)
            write_to_json("test", test)
            write_to_json("validate", val)
            assert len(designated) == len(test) + len(val), "Mismatch in the values for in the retrain counts" + designated_database

        else:
            print("{} is in not the list".format(designated_database))
            write_to_json("all_train", combined_list)
    
    
    def get_dataset_statistics(self):
        # used to find the number of different word tokens 
        def get_word_types(list_of_sentences):
            cnt = Counter()
            for sentence in list_of_sentences:
                for token in sentence:
                    cnt[token] += 1
            return len(cnt), cnt.most_common(10)
        
        def get_average_length(list_of_sentences):
            length_list = []
            for sentence in list_of_sentences: 
                length_list.append(len(sentence))
            return sum(length_list)/(len(length_list))

        sentence_list = [item['question_toks'] for item in self.combined_data]
        query_list = [item['query_toks'] for item in self.combined_data]
        print("Number of word types {} and most common tokens: {}".format(get_word_types(sentence_list)[0],get_word_types(sentence_list)[1]))
        print("Average query length {}".format(get_average_length(query_list)))
        print("Average sentence length {}".format(get_average_length(sentence_list)))
                

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

    def produce_example_questions(self):
        data = {}
        for db  in self.unique_combined_data:
            data[db] = []
            while len(data[db]) < 5:
                for item in self.combined_data:
                    if item['db_id'] == db:
                        data[db].append(item['question'])
        json.dump(data, open('example_questions.json', 'w'))



    def show_list_of_available_db(self):
        items = [item['db_id'] for item in self.combined_data]
        print("Len of list is {}".format(len(items)))
        unique_items = self.unique_combined_data
        print("There are {} unique dbs".format(len(unique_items)))
        for counter,db in enumerate(unique_items):
            print("{} - {}".format(counter,db))

    def avail_db_to_json(self):
        data = {}
        unique_items = self.unique_combined_data
        for counter,db in enumerate(unique_items):
            data[counter] = db
            data[db] = str(counter)
        with open('data.json', 'w') as outfile:
            json.dump(data, outfile)


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
    parser.add_argument('--train_split', type=float, 
        help='training data split, either < 1 as decimal for percentage or integer for number of examples in retrain file', default=0.6)
    parser.add_argument('--retrain_split', type=float, 
        help='retrain data split, either < 1 as decimal for percentage or integer for number of examples in retrain file', default=0.6)
    parser.add_argument('--version', type=int, 
        help='version 1 produces train val test splits, version 2 furthers splits each into sub train retrain splits', default=2)
    
    args = parser.parse_args()

    original_directory_name = args.orig_dataset
    ds = DataSplitter(original_directory_name, args.train_split, args.retrain_split)

    new_directory_name = args.new_dataset_dir
    ds.create_dataset_folder(new_directory_name)

    ds.merge_data_files()

    if args.print_db_nums:
        ds.show_list_of_available_db()

    db_chosen_num = args.database_num
    assert 0 <= db_chosen_num < len(ds.unique_combined_data), 'Database number out of bounds'
    selected_database = ds.unique_combined_data[db_chosen_num]

    if args.version == 1:
        print('splitting using version 1')
        ds.split_based_on_database_v1(selected_database, ds.combined_data)
    else:
        print('splitting using version 2')
        ds.split_based_on_database_v2(selected_database, ds.combined_data)

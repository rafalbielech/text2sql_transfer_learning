import subprocess
import argparse
import json
#To generate command line arguments
def process_arguments(arguments, i):
    kwargs=[]
    for key in arguments:
            if key in ["new_dataset_dir", "dataset", "save_to_path", "base_model_path", "output"]:
                kwargs.append("--"+key+"="+arguments[key]+str(i))
            elif key in ["database_num"]:
                kwargs.append("--"+key+"="+str(i))
            elif type(arguments[key])==bool:
                if arguments[key]:
                    kwargs.append("--"+key) 
            else:
                kwargs.append("--"+key+"="+str(arguments[key]))

    return kwargs


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int, default=1,
            help='Starting range for databases to train, retrain')
    parser.add_argument('--end', type=int, default=5,
            help='Ending range for databases to train, retrain')
    args = parser.parse_args()

    #unpack
    with open('config.json') as json_data_file:
        config = json.load(json_data_file)
    subprocess.call(config["unpack"]["execCommand"])

    for i in range(args.start, args.end+1):
        print('Starting datasplitting for', i)
        f = open("output_retrain_"+str(i)+".txt", "w")
        kwargs=process_arguments(config["datasplitter"]["arguments"], i)
        subprocess.call(config["datasplitter"]["execCommand"]+kwargs, stdout=f)
    
        print('Calling train for', i) 
        kwargs_train = process_arguments(config["train"]["arguments"], i)
        subprocess.call(config["train"]["execCommand"]+kwargs_train, stdout=f)
        
        print('Calling retrain for', i)
        kwargs_retrain = process_arguments(config["retrain"]["arguments"], i)
        subprocess.call(config["retrain"]["execCommand"]+kwargs_retrain, stdout=f)

        print('Calling test for', i)
        kwargs_retrain = process_arguments(config["test"]["arguments"], i)
        subprocess.call(config["test"]["execCommand"]+kwargs_retrain, stdout=f)
        f.close()

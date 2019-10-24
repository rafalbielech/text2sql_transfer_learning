#!/bin/bash

parse_yaml() {
   local prefix=$2
   local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
   sed -ne "s|^\($s\)\($w\)$s:$s\"\(.*\)\"$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p"  $1 |
   awk -F$fs '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
      }
   }'
}

eval $(parse_yaml config.yml "config_")
#call unpack
python unpack.py

#Call Data Splitter
python datasplitter.py --orig_dataset=$config_datasplitter_orig_dataset --new_dataset=$config_datasplitter_new_dataset_dir --database_num=$config_datasplitter_database_num


#python datasplitter.py \
# --orig_dataset=spider_dataset \
#--new_dataset_dir=my_new_dataset_for_db_42 \
#--database_num=42 
#--print_db_nums
#call train.py

#call retrain.py

#call eval/test

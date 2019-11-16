import json
import torch
import datetime
import argparse
import numpy as np
from scripts.utils import *
from scripts.model.sqlnet import SQLNet
import os


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--toy', action='store_true',
            help='If set, use small data; used for fast debugging.')
    parser.add_argument('--dataset', type=str, default='',
            help='to dataset directory where includes train, test and table json file.')
    parser.add_argument('--base_model_path', type=str,
            help='path to the saved trained models')
    parser.add_argument('--save_to_path', type=str,
            help='path to save the retrained models')
    parser.add_argument('--train_emb', action='store_true',
            help='Train word embedding.')
    parser.add_argument('--no_gpu', action='store_true',
            help='If set, dont use the GPU')
    parser.add_argument('--epochs', type=int, default=100,
            help='the number of epochs to retrain on')
    parser.add_argument('--learning_rate', type=float, default=1e-3,
            help='learning rate based on Adam update')
    parser.add_argument('--weight_decay', type=float, default=0,
            help='decay rate of weights for Adam update')
    # TODO: Add arguement to accept number of layers to retrain on.
    # Leads to additional guesswork.
    # TODO: Find out shapes and types of layers in the model
    # Might only need to focus on the FC layer. 
    # Sizes of the smallest and largest dataset in SPIDER: 4, 569


    args = parser.parse_args()

    N_word=50
    B_word=6
    GPU = not args.no_gpu
    if args.toy:
        USE_SMALL=True
        BATCH_SIZE=20
    else:
        USE_SMALL=False
        BATCH_SIZE=64
    TRAIN_ENTRY=(True, True, True)  # (AGG, SEL, COND)
    TRAIN_AGG, TRAIN_SEL, TRAIN_COND = TRAIN_ENTRY
    learning_rate = args.learning_rate

    sql_data, table_data, val_sql_data, val_table_data, \
            test_sql_data, test_table_data, schemas,\
            TRAIN_DB, DEV_DB, TEST_DB = load_dataset(args.dataset, train_mode="retrain", use_small=USE_SMALL)


    word_emb = load_word_emb('./models/sqlnet/glove/glove.%dB.%dd.txt'%(B_word,N_word), \
            load_used=args.train_emb, use_small=USE_SMALL)

    #Check if directory exists. Else create one!
    if not os.path.isdir(args.save_to_path):
        os.mkdir(args.save_to_path)
    model = SQLNet(word_emb, N_word=N_word, gpu=GPU, trainable_emb=args.train_emb)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay = 0)
    
    print("Loading from sel model...")
    model.sel_pred.load_state_dict(torch.load(os.path.join(args.base_model_path, "/sel_models.dump")))
    print("Loading from sel model...")
    model.cond_pred.load_state_dict(torch.load(os.path.join(args.base_model_path, "/cond_models.dump")))
    print("Loading from sel model...")
    model.group_pred.load_state_dict(torch.load(os.path.join(args.base_model_path, "/group_models.dump")))
    print("Loading from sel model...")
    model.order_pred.load_state_dict(torch.load(os.path.join(args.base_model_path, "/order_models.dump")))
    #initial accuracy
    init_acc = epoch_acc(model, BATCH_SIZE, val_sql_data, val_table_data, schemas, TRAIN_ENTRY)
    print('Initial acc', init_acc)
    best_sel_acc = init_acc[1][0]
    best_cond_acc = init_acc[1][1]
    best_group_acc = init_acc[1][2]
    best_order_acc = init_acc[1][3]
    best_tot_acc = 0.0
    #Check if directory exists. Else create one!
    if not os.path.isdir(args.save_to_path):
        os.mkdir(args.save_to_path)
        
    for i in range(args.epochs):
        print('Epoch %d @ %s'%(i+1, datetime.datetime.now()))
        print(' Loss = %s'%epoch_train(model, optimizer, BATCH_SIZE, val_sql_data, val_table_data, schemas, TRAIN_ENTRY))
        train_tot_acc, train_bkd_acc = epoch_acc(model, BATCH_SIZE, val_sql_data, val_table_data, schemas, TRAIN_ENTRY, train_flag = True)
        print(' Train acc_qm: %s' % train_tot_acc)
        print(' Breakdown results: sel: %s, cond: %s, group: %s, order: %s'\
            % (train_bkd_acc[0], train_bkd_acc[1], train_bkd_acc[2], train_bkd_acc[3]))

        val_tot_acc, val_bkd_acc = epoch_acc(model, BATCH_SIZE, val_sql_data, val_table_data, schemas, TRAIN_ENTRY, error_print = False, train_flag = False) #for detailed error analysis, pass True to error_print
        print(' Dev acc_qm: %s' % val_tot_acc)
        print(' Breakdown results: sel: %s, cond: %s, group: %s, order: %s'\
            % (val_bkd_acc[0], val_bkd_acc[1], val_bkd_acc[2], val_bkd_acc[3]))
        
        #save models
        if val_bkd_acc[0] > best_sel_acc:
            best_sel_acc = train_bkd_acc[0]
            print("Saving sel model...")
            torch.save(model.sel_pred.state_dict(), os.path.join(args.save_to_path, "/sel_models.dump"))
        if val_bkd_acc[1] > best_cond_acc:
            best_cond_acc = train_bkd_acc[1]
            print("Saving cond model...")
            torch.save(model.cond_pred.state_dict(), os.path.join(args.save_to_path, "/cond_models.dump"))
        if val_bkd_acc[2] > best_group_acc:
            best_group_acc = train_bkd_acc[2]
            print("Saving group model...")
            torch.save(model.group_pred.state_dict(), os.path.join(args.save_to_path, "/group_models.dump"))
        if train_bkd_acc[3] > best_order_acc:
            best_order_acc = train_bkd_acc[3]
            print("Saving order model...")
            torch.save(model.order_pred.state_dict(), os.path.join(args.save_to_path, "/order_models.dump"))
        if val_tot_acc > best_tot_acc:
            best_tot_acc = val_tot_acc


print(' Best val sel = %s, cond = %s, group = %s, order = %s, tot = %s'%(best_sel_acc, best_cond_acc, best_group_acc, best_order_acc, best_tot_acc))

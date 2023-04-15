# ------------------------------------------------------------------------------
# Modified based on https://github.com/HRNet/HRNet-Semantic-Segmentation
# ------------------------------------------------------------------------------

import argparse
import os
import pprint

import logging
import timeit


import numpy as np

import torch
import torch.nn as nn
import torch.backends.cudnn as cudnn

import _init_paths
import models
import datasets
from configs import config
from configs import update_config
from utils.function import testval, test
from utils.utils import create_logger

def parse_args():
    parser = argparse.ArgumentParser(description='Train segmentation network')
    
    parser.add_argument('--cfg',
                        help='experiment configure file name',
                        default="/root/PIDNet-yoon/configs/tooth/pidnet_pico_tooth_w_target_230410.yaml",
                        type=str)
    parser.add_argument('--model',
                        help='model file name',
                        default="/root/PIDNet-yoon/scripted_pidnet_model.pt",
                        type=str)
    parser.add_argument('opts',
                        help="Modify config options using the command-line",
                        default=None,
                        nargs=argparse.REMAINDER)

    args = parser.parse_args()
    update_config(config, args)

    return args

def main():
    args = parse_args()

    logger, final_output_dir, _ = create_logger(
        config, args.cfg, 'test')

    logger.info(pprint.pformat(args))
    logger.info(pprint.pformat(config))

    # cudnn related setting
    cudnn.benchmark = config.CUDNN.BENCHMARK
    cudnn.deterministic = config.CUDNN.DETERMINISTIC
    cudnn.enabled = config.CUDNN.ENABLED

    # build model
    model = torch.jit.load(args.model)
    ##model = torch.load(args.model)

    model = model.cuda()

    # prepare data
    test_size = (config.TEST.IMAGE_SIZE[1], config.TEST.IMAGE_SIZE[0])
    test_dataset = eval('datasets.'+config.DATASET.DATASET)(
                        root=config.DATASET.ROOT,
                        list_path=config.DATASET.TEST_SET,
                        num_classes=config.DATASET.NUM_CLASSES,
                        multi_scale=False,
                        flip=False,
                        ignore_label=config.TRAIN.IGNORE_LABEL,
                        base_size=config.TEST.BASE_SIZE,
                        crop_size=test_size)

    testloader = torch.utils.data.DataLoader(
        test_dataset,
        batch_size=1,
        shuffle=False,
        num_workers=0,
        pin_memory=True)
    
    start = timeit.default_timer()

    
    
    if ('test' in config.DATASET.TEST_SET) and ('city' in config.DATASET.DATASET):
        test(config,
             test_dataset, 
             testloader, 
             model,
             sv_dir=final_output_dir)

    elif ('test' in config.DATASET.TEST_SET) and ('tooth' in config.DATASET.DATASET):
        print("testing tooth")
        test(config,
             test_dataset,
             testloader,
             model,
             sv_dir=final_output_dir)

    else:
        mean_IoU, IoU_array, pixel_acc, mean_acc = testval(config,
                                                           test_dataset, 
                                                           testloader, 
                                                           model)
    
        msg = 'MeanIU: {: 4.4f}, Pixel_Acc: {: 4.4f}, \
            Mean_Acc: {: 4.4f}, Class IoU: '.format(mean_IoU, 
            pixel_acc, mean_acc)
        logging.info(msg)
        logging.info(IoU_array)


    end = timeit.default_timer()
    logger.info('Mins: %d' % np.int32((end-start)/60))
    logger.info('Done')


if __name__ == '__main__':
    main()

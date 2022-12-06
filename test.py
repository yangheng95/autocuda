# -*- coding: utf-8 -*-
# file: test.py
# time: 2021/8/6
# author: yangheng <yangheng@m.scnu.edu.cn>
# github: https://github.com/yangheng95
# Copyright (C) 2021. All Rights Reserved.
import os

from autocuda import auto_cuda_info, auto_cuda_index, auto_cuda, auto_cuda_name

for env in ['', '0', '1', '0,1', '1,2', '0,3', '0,1,2,3']:
    os.environ['CUDA_VISIBLE_DEVICES'] = env
    # os.environ['CUDA_VISIBLE_DEVICES'] = '0'

    cuda_info_dict = auto_cuda_info()

    cuda_device_index = auto_cuda_index()  # return cuda index having largest free memory. return 'cpu' if not cuda
    # os.environ['CUDA_VISIBLE_DEVICES'] = [str(cuda_device_index)]

    cuda_device = auto_cuda()
    # model.to(cuda_device) # assume you have inited your pytorch model

    cuda_device_name = auto_cuda_name()
    print(cuda_device)
    print('Choosing cuda device: {}'.format(cuda_device_name))

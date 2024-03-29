# -*- coding: utf-8 -*-

from functools import lru_cache
import os
import torch

"""
Created on Tue Aug 22 19:41:55 2017

@author: Quantum Liu
"""
'''
Example:
gm=GPUManager()
with torch.cuda.device(gm.auto_choice()):
    blabla

Or:
gm=GPUManager()
torch.cuda.set_device(gm.auto_choice())
'''


def check_gpus():
    '''
    GPU available check
    http://pytorch-cn.readthedocs.io/zh/latest/package_references/torch-cuda/
    '''
    with os.popen('nvidia-smi -h') as f:
        info = f.read()
    if not torch.cuda.is_available():
        # print('This script could only be used to manage NVIDIA GPUs,but no GPU found in your device')
        print('No CUDA GPU found in your device')
        return False
    elif not 'NVIDIA System Management' in info:
        print("'nvidia-smi' tool not found.")
        return False
    return True


if check_gpus():
    def parse(line, qargs):
        '''
        line:
            a line of text
        qargs:
            query arguments
        return:
            a dict of gpu infos
        Pasing a line of csv format text returned by nvidia-smi
        解析一行nvidia-smi返回的csv格式文本
        '''
        numberic_args = ['memory.free', 'memory.total', 'power.draw', 'power.limit']  # 可计数的参数
        power_manage_enable = lambda v: (not 'NOT SUPPORT' in v.upper()) and (
            not 'N/A' in v.upper())  # lambda表达式，显卡是否滋瓷power management（笔记本可能不滋瓷）
        to_numberic = lambda v: float(v.upper().strip().replace('MIB', '').replace('W', ''))  # 带单位字符串去掉单位
        process = lambda k, v: (
            (int(to_numberic(v)) if power_manage_enable(v) else 1) if k in numberic_args else v.strip())
        return {k: process(k, v) for k, v in zip(qargs, line.strip().split(','))}


    def query_gpu(qargs=[]):
        '''
        qargs:
            query arguments
        return:
            a list of dict
        Querying GPUs infos
        查询GPU信息
        '''
        qargs = ['index', 'gpu_name', 'memory.free', 'memory.total', 'power.draw', 'power.limit'] + qargs
        cmd = 'nvidia-smi --query-gpu={} --format=csv,noheader'.format(','.join(qargs))
        with os.popen(cmd) as f:
            results = f.readlines()
        return [parse(line, qargs) for line in results]


    def by_power(d):
        '''
        helper function fo sorting gpus by power
        '''
        power_infos = (d['power.draw'], d['power.limit'])
        if any(v == 1 for v in power_infos):
            print('Power management unable for GPU {}'.format(d['index']))
            return 1
        return float(d['power.draw']) / d['power.limit']


    class GPUManager(object):
        """
        qargs:
            query arguments
        A manager which can list all available GPU devices
        and sort them and choice the most free one.Unspecified
        ones pref.
        GPU设备管理器，考虑列举出所有可用GPU设备，并加以排序，自动选出
        最空闲的设备。在一个GPUManager对象内会记录每个GPU是否已被指定，
        优先选择未指定的GPU。
        """

        def __init__(self, qargs=[]):
            '''
            '''
            available_gpus = os.getenv('CUDA_VISIBLE_DEVICES').split(',') if os.getenv(
                'CUDA_VISIBLE_DEVICES') else [str(idx) for idx in
                                              range(torch.cuda.device_count())] if torch.cuda.device_count() > 0 else []
            _available_gpus = available_gpus[:]
            self.qargs = qargs
            self.gpus = query_gpu(qargs)
            for gpu in self.gpus:
                gpu['specified'] = False if gpu['index'] in available_gpus else True
                _available_gpus.pop(_available_gpus.index(gpu['index'])) if gpu['index'] in _available_gpus else None
            if _available_gpus:
                print('WARNING:Some specified GPUs in CUDA_VISIBLE_DEVICES are not available now: {}'.format(
                    ', '.join(_available_gpus)))
            self.gpu_num = len(self.gpus)

        def _sort_by_memory(self, gpus, by_size=False):
            if by_size:
                # print('Sorted by free memory size')
                return sorted(gpus, key=lambda d: d['memory.free'], reverse=True)
            else:
                # print('Sorted by free memory rate')
                return sorted(gpus, key=lambda d: float(d['memory.free']) / d['memory.total'], reverse=True)

        def _sort_by_power(self, gpus):
            return sorted(gpus, key=by_power)

        def _sort_by_custom(self, gpus, key, reverse=False, qargs=[]):
            if isinstance(key, str) and (key in qargs):
                return sorted(gpus, key=lambda d: d[key], reverse=reverse)
            if isinstance(key, type(lambda a: a)):
                return sorted(gpus, key=key, reverse=reverse)
            raise ValueError(
                "The argument 'key' must be a function or a key in query args,please read the documention of nvidia-smi")

        def auto_choice(self, threshold=0, mode=0):
            '''
            mode:
                0:(default)sorted by free memory size
            return:
                a TF device object
            Auto choice the freest GPU device,not specified
            ones
            自动选择最空闲GPU,返回索引
            '''
            for old_infos, new_infos in zip(self.gpus, query_gpu(self.qargs)):
                old_infos.update(new_infos)
            unspecified_gpus = [gpu for gpu in self.gpus if not gpu['specified']]

            if mode == 0:
                # print('Choosing the GPU device has largest free memory...')
                chosen_gpu = self._sort_by_memory(unspecified_gpus, True)[0]
            elif mode == 1:
                # print('Choosing the GPU device has highest free memory rate...')
                chosen_gpu = self._sort_by_power(unspecified_gpus)[0]
            elif mode == 2:
                # print('Choosing the GPU device by power...')
                chosen_gpu = self._sort_by_power(unspecified_gpus)[0]
            else:
                # print('Given an unavailable mode,will be chosen by memory')
                chosen_gpu = self._sort_by_memory(unspecified_gpus)[0]
            chosen_gpu['specified'] = True
            # print('Using GPU {i}:\n{info}'.format(i=index, info='\n'.join(
            #     [str(k) + ':' + str(v) for k, v in chosen_gpu.items()])))
            return chosen_gpu


@lru_cache(maxsize=32)
def auto_cuda_index():
    index = 'cpu'
    if torch.cuda.is_available():
        try:
            chosen_gpu = GPUManager().auto_choice()
            index = chosen_gpu['index']
            return int(index) if index.isdigit() else index
        except Exception as e:
            return index


@lru_cache(maxsize=32)
def auto_cuda():
    index = 'cpu'
    try:
        if torch.cuda.is_available():
            chosen_gpu = GPUManager().auto_choice()
            index = chosen_gpu['index']
        return "cuda:{}".format(index) if index.isdigit() else index
    except Exception as e:
        return index


@lru_cache(maxsize=32)
def auto_cuda_name():
    device_name = ''
    try:
        if torch.cuda.is_available():
            chosen_gpu = GPUManager().auto_choice()
            device_name = chosen_gpu['gpu_name']
        return device_name
    except Exception as e:
        return 'N.A.'


@lru_cache(maxsize=32)
def auto_cuda_info():
    '''
    :return: information dict of the cuda device having largest memory
    '''
    try:
        return GPUManager().auto_choice()
    except:
        return 'N.A.'

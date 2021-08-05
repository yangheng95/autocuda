# autocuda - Auto choose the cuda device having largest free memory in Pytorch

![PyPI - Python Version](https://img.shields.io/badge/python-3.6-blue.svg) 
[![PyPI](https://img.shields.io/pypi/v/autocuda)](https://pypi.org/project/autocuda/)
[![PyPI_downloads](https://img.shields.io/pypi/dm/autocuda)](https://pypi.org/project/autocuda/)
![Repo Size](https://img.shields.io/github/repo-size/yangheng95/autocuda)

This is a package for you to locate your target file(s)/dir(s) easily.

# Usage
## Install
```
pip install autocuda
```

## ready to use


```
from autocuda import auto_cuda_info, auto_device

cuda_info_dict = auto_cuda_info()

cuda_device = auto_deivce()

# model.to(cuda_device) # assume you have inited your pytorch model

```

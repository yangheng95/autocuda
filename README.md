# autocuda - Auto choose the cuda device having largest free memory in Pytorch

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

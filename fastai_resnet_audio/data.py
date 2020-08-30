# AUTOGENERATED! DO NOT EDIT! File to edit: 01_data.ipynb (unless otherwise specified).

__all__ = ['AudioBlock', 'TensorAudio', 'AudioFixLength', 'AudioResample', 'AudioToMono', 'AudioRandomCrop',
           'AudioAddNoise', 'AudioToTensor']

# Cell

from .model import *
from fastai.torch_core import TensorBase
from fastai.data.block import TransformBlock
from fastcore.transform import Transform
from fastai.vision.augment import RandTransform
import torch.nn.functional as F
import torch
import torchaudio
import torchaudio.transforms

# Cell

def AudioBlock():
    return TransformBlock(type_tfms=TensorAudio.create, batch_tfms=None)

class TensorAudio(TensorBase):

    @classmethod
    def create(cls, o, norm=True):
        o, sr = torchaudio.load(o, normalization=norm)
        o = cls(o)
        o.sr = sr
        o.mode = 'raw'
        return o
    '''
    def show(self, ctx=None):
        if self.mode == 'raw':
            print(self.shape)
            librosa.display.waveplot(np.asarray(self.squeeze()), sr=self.sr)
            #print(img.shape)
    '''

# Cell

class AudioFixLength(Transform):

    def __init__(self, length=0.0):
        self.length = length

    def encodes(self, o: TensorAudio):
        if self.length > 0.0:
            n_samples = int(o.sr * self.length)
            if n_samples < len(o.squeeze()):
                o = torch.split(o, n_samples, dim=1)[0]
            else:
                n_pad = int(o.sr * self.length - len(o.squeeze()))
                n_pre = (torch.rand(1) * n_pad).int()
                n_post = n_pad - n_pre
                o = F.pad(input=o, pad=(n_pre,n_post), mode='constant', value=0)
        return o

class AudioResample(Transform):

    def __init__(self, target_sr=0, device='cpu'):
        self.target_sr = target_sr
        self.device = device

    def encodes(self, o: TensorAudio):
        if self.target_sr != o.sr:
            resample = torchaudio.transforms.Resample(orig_freq=o.sr, new_freq=self.target_sr)
            o = TensorAudio(resample(o))
            o.sr = self.target_sr
        return o

class AudioToMono(Transform):

    def __init__(self, device='cpu'):
        self.device = device

    def encodes(self, o: TensorAudio):
        sr = o.sr
        o = TensorAudio(torch.mean(o,dim=0).unsqueeze(0))
        o.sr = sr
        return o


class AudioRandomCrop(RandTransform):

    def __init__(self, p=1.0, length=0.0):
        super().__init__(p=p)
        self.length = length

    def encodes(self, o: TensorAudio):
        if self.length > 0.0:
            n_samples = int(o.sr * self.length)
            if n_samples < len(o[0]):
                n_cut = len(o[0]) - n_samples
                n_pre = (n_cut * torch.rand(1)).int()
                o = o[:,n_pre:(n_samples + n_pre)]
        return o


class AudioAddNoise(RandTransform):
    "Randomly add noise with probability `p`"
    def __init__(self, p=0.5, device='cpu'):
        super().__init__(p=p)
        self.device=device

    def encodes(self, o: TensorAudio):
        noise_amp = (0.001*torch.rand(1) * torch.max(o)).to(self.device)
        o = o + noise_amp * torch.empty(o.shape).normal_().to(self.device)
        return o


class AudioToTensor(Transform):

    def encodes(self, o: TensorAudio):
        o = tensor(o).float()
        return o
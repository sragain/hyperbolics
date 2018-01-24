import torch
from torch import nn
from torch.autograd import Variable

import numpy as np, math
import random


class Hyperbolic_Parameter(nn.Parameter):
    def __init__(self, project=True):
        super(Hyperbolic_Parameter,self).__init__()
        if project: self.proj()
            
    def __init__(self, x, project=True):
        super(Hyperbolic_Parameter,self).__init__(x)
        if project: self.proj()
             
    def modify_grad_inplace(self):
        d        = self.data.dim() 
        d_p      = self.grad.data
        w_norm   = torch.norm(self.data,2,d - 1, True)
        # This is the inverse of the remanian metric, which we need to correct for.
        hyper_b  = (1 - w_norm**2)**2/4
        new_size = tuple([1] * (d - 1) + [self.data.size(d-1)])
                    
        self.grad.data   = d_p * hyper_b.repeat(*new_size) # multiply pointwise
        # We could do the projection here?
        # NB: THIS IS DEATHLY SLOW. FIX IT
        # if np.any(np.isnan(self.grad.data.cpu().numpy())):
        #     print(self.data)
        #     print(d_p)
        #     raise ValueError("NaN During Hyperbolic")
 
    @staticmethod        
    def _proj(x, eps=1e-8):
        current_norms = torch.norm(x,2,x.dim() - 1)
        mask_idx      = current_norms < 1.0
        modified      = 1./((1+eps)*current_norms)
        modified[mask_idx] = 1.0
        new_size      = [1]*current_norms.dim() + [x.size(x.dim()-1)]
        modified      = modified.unsqueeze(modified.dim()).repeat(*new_size) 
        return x * modified

    def proj(self, eps=1e-8):
        self.data = Hyperbolic_Parameter._proj(self.data, eps=eps)
        
    @staticmethod
    def correct_metric(ps):
        for p in ps:
            if isinstance(p,Hyperbolic_Parameter): 
                p.modify_grad_inplace()

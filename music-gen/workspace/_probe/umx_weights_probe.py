import os
os.environ['TORCH_HOME'] = '/home/user/long-exposure-runs/music-gen/workspace/_probe/torch_home'
os.makedirs(os.environ['TORCH_HOME'], exist_ok=True)
import torch, openunmix
print('openunmix', openunmix.__file__)
try:
    sep = openunmix.umxhq(targets=['vocals'], niter=0, residual=True, wiener_win_len=None)
    print('umxhq loaded OK; type', type(sep))
except Exception as e:
    print('FETCH FAILED', type(e).__name__, str(e)[:400])

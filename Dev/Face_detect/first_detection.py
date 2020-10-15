import tensorflow as tf
import numpy as np
import PIL.Image
from io import BytesIO
from IPython.display import clear_output, Image, display
assert tf.__version__.startswith('2')


def DisplayFractal(a, fmt='jpeg'):
    a_cyclic = (6.28*a/20.0).reshape(list(a.shape)+[1])
    img = np.concatenate([10+20*np.cos(a_cyclic),
                          30+50*np.sin(a_cyclic),
                          155-80*np.cos(a_cyclic)], 2)
    img[a == a.max()] = 0
    a = img
    a = np.uint8(np.clip(a, 0, 255))
    f = BytesIO()
    PIL.Image.fromarray(a).save(f, fmt)
    display(Image(data=f.getvalue()))


Y, X = np.mgrid[-1.3:1.3:0.005, -2:1:0.005]
Z = X+1j*Y
xs = tf.constant(Z.astype(np.complex64))
zs = tf.Variable(xs)
npt_diverged = tf.Variable(tf.zeros_like(xs, tf.bool))
ns = tf.Variable(tf.zeros_like(xs, tf.float32))

for i in range(200):
    zs = zs*zs + xs
    not_diverged = tf.abs(zs) < 4
    ns = ns + tf.cast(not_diverged, tf.float32)
ns = ns.numpy()
DisplayFractal(ns)

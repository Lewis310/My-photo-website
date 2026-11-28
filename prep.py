import cv2, numpy as np
img = cv2.imread('/mnt/user-data/uploads/IMG_5584.jpg')
h, w = img.shape[:2]
print(img.shape, 'channel diff', np.abs(img[...,0].astype(int)-img[...,2].astype(int)).mean())
W = int(np.ceil(h*16/9)); pad = (W-w)//2; W = w+2*pad
R = cv2.copyMakeBorder(img, 0,0,pad,pad, cv2.BORDER_REFLECT).astype(np.float32)
x = np.arange(W, dtype=np.float32)
d = np.maximum(0, np.maximum(pad - x, x-(pad+w-1)))/pad
d = d[None,:,None]
ss = lambda v: (lambda t: t*t*(3-2*t))(np.clip(v,0,1))
B1 = cv2.GaussianBlur(R,(0,0),14); B2 = cv2.GaussianBlur(R,(0,0),50)
w1 = ss(d/0.22); w2 = ss((d-0.15)/0.85)
out = R*(1-w1)+B1*w1
out = out*(1-w2)+B2*w2
out *= (1 - 0.82*d**1.25)
out = np.clip(out,0,255).astype(np.uint8)
cv2.imwrite('extended_full.png', out)
cv2.imwrite('/mnt/user-data/outputs/anim/photo_16x9_extended.jpg', out, [cv2.IMWRITE_JPEG_QUALITY, 93])
print('extended', out.shape, 'pad', pad)
cv2.imwrite('ext_preview.jpg', cv2.resize(out,(1600,900),interpolation=cv2.INTER_AREA))

import cv2, numpy as np, sys, subprocess, os
S0K = 0.7
full = cv2.imread('extended_full.png')
Wk = cv2.resize(full, None, fx=S0K, fy=S0K, interpolation=cv2.INTER_AREA)   # work canvas
H, Wd = Wk.shape[:2]
CX, CY = int((940+1324)*S0K), int(1263*S0K)       # figure centre in work px
HS = 300
FPS, DUR = 24, 12.0
rng = np.random.default_rng(7)

ys, xs = np.mgrid[-HS:HS, -HS:HS].astype(np.float32)
r = np.sqrt(xs**2+ys**2)
r0, r1 = 62, 235
wfall = np.where(r<r0, 1, np.where(r<r1, 0.5*(1+np.cos(np.pi*(r-r0)/(r1-r0))), 0)).astype(np.float32)
sm = lambda v: (lambda t: t*t*(3-2*t))(np.clip(v,0,1))
legm = sm((xs-20)/70).astype(np.float32); armm = sm((-xs-10)/50).astype(np.float32)
rmask = np.clip(1 - (r-70)/70, 0, 1).astype(np.float32)             # where glints may appear

gray = cv2.cvtColor(Wk, cv2.COLOR_BGR2GRAY).astype(np.float32)/255
Lb = cv2.GaussianBlur(gray,(0,0),22)                                  # beam map for dust/shimmer
Lb = np.clip((Lb-0.06)/0.5,0,1)

def ray_kernel(angle_deg, length, falloff):
    n = 2*length+1; k = np.zeros((n,n), np.float32)
    a = np.deg2rad(angle_deg)
    s = np.linspace(-length, length, 6*length)
    px = length + s*np.cos(a); py = length - s*np.sin(a)
    wt = np.exp(-np.abs(s)/falloff)
    x0 = np.floor(px).astype(int); y0 = np.floor(py).astype(int); fx = px-x0; fy = py-y0
    for dx,dy,ww in ((0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)):
        ok = (x0+dx>=0)&(x0+dx<n)&(y0+dy>=0)&(y0+dy<n)
        np.add.at(k, (y0[ok]+dy, x0[ok]+dx), (wt*ww)[ok])
    return k/ k.sum()*3.0

# dust particles (in work px), weighted by beam brightness
NP = 160
dust = np.stack([rng.uniform(CX-900,CX+900,NP), rng.uniform(CY-700,CY+700,NP)],1)
dphase = rng.uniform(0,6.28,NP); dsize = rng.uniform(0.8,2.0,NP)
kx = rng.integers(1,3,NP); ky = rng.integers(1,3,NP); kt = rng.integers(2,6,NP)

def frame(t):
    u = t/DUR
    th = np.deg2rad(7.0*np.sin(2*np.pi*t/12.0+0.5) + 2.0*np.sin(2*np.pi*t/4.0))
    tx = 5*np.sin(2*np.pi*t/12.0+1.0); ty = 9*np.sin(2*np.pi*t/6.0)
    c, s = np.cos(th), np.sin(th)
    dx, dy = xs-tx, ys-ty
    qx = c*dx + s*dy; qy = -s*dx + c*dy
    flex = 6.0*np.sin(2*np.pi*t/4.0)*legm + 5.0*np.sin(2*np.pi*t/3.0+2.0)*armm
    mx = xs + wfall*(qx-xs) + HS
    my = ys + wfall*(qy-ys) + wfall*flex + HS
    roi = Wk[CY-HS:CY+HS, CX-HS:CX+HS]
    patch = cv2.remap(roi, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)/255
    # ---- light refraction: glints off the body, rays rotate with it, prismatic fringe
    L = patch.mean(2)
    hp = L - cv2.GaussianBlur(L,(0,0),9)
    wave = 0.55 + 0.45*np.sin(2*np.pi*((xs*c+ys*s)/110.0 - 5*t/DUR))
    spec = np.clip((hp-0.05)/0.18,0,1)*np.clip((L-0.55)/0.3,0,1)*rmask*wave
    base = 18 + np.rad2deg(th)*1.4
    glint = np.zeros_like(patch)
    for ch, (da, ln) in enumerate(((-2.2,1.18),(0,1.0),(2.2,0.84))):   # B, G, R
        rays = np.zeros(L.shape, np.float32)
        for k in (0,60,120):
            rays += cv2.filter2D(spec, -1, ray_kernel(base+k+da, int(78*ln), 30*ln))
        glint[...,ch] = rays
    bloom = cv2.GaussianBlur(spec,(0,0),5)[...,None]*0.9
    patch = np.clip(patch + 0.6*glint + 0.5*bloom, 0, 1)
    W2 = Wk.copy(); W2[CY-HS:CY+HS, CX-HS:CX+HS] = (patch*255+0.5).astype(np.uint8)
    # ---- camera: slow push-in toward the figure
    z = 1.0
    cxv = Wd/2
    cyv = H/2
    Sc = (1920/Wd)*z
    M = np.float32([[Sc,0,960-Sc*cxv],[0,Sc,540-Sc*cyv]])
    view = cv2.warpAffine(W2, M, (1920,1080), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)/255
    # ---- beam shimmer (soft light drifting up the beams)
    Lv = cv2.warpAffine(Lb, M, (1920,1080), flags=cv2.INTER_LINEAR)
    yy, xx = np.mgrid[0:1080,0:1920].astype(np.float32)
    shim = np.sin(2*np.pi*(yy/(330*z) + t/DUR) + xx/(260*z)) * np.sin(2*np.pi*(yy/(190*z) - 2*t/DUR) - xx/(410*z))
    view *= (1 + 0.07*Lv*shim)[...,None]
    # ---- floating dust in the beams
    layer = np.zeros((1080,1920), np.uint8)
    for i in range(NP):
        px = dust[i,0] + 18*np.sin(2*np.pi*kx[i]*t/DUR+dphase[i]); py = dust[i,1] + 26*np.sin(2*np.pi*ky[i]*t/DUR+dphase[i]*2)
        wx = int(np.clip(px,0,Wd-1)); wy = int(np.clip(py,0,H-1))
        a = Lb[wy,wx]
        if a < 0.12: continue
        ox, oy = Sc*(px-cxv)+960, Sc*(py-cyv)+540
        if 0<=ox<1920 and 0<=oy<1080:
            tw = 0.55+0.45*np.sin(2*np.pi*kt[i]*t/DUR+dphase[i]*3)
            cv2.circle(layer,(int(ox),int(oy)),max(1,int(dsize[i]*Sc*1.4)),int(255*min(1,a*1.3)*tw),-1,cv2.LINE_AA)
    layer = cv2.GaussianBlur(layer,(0,0),0.9).astype(np.float32)/255
    view = np.clip(view + 0.55*layer[...,None], 0, 1)
    # ---- grain + fades
    view += rng.normal(0, 0.011, (1080,1920,1)).astype(np.float32)
    return (np.clip(view,0,1)*255+0.5).astype(np.uint8)

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        for tt in map(float, sys.argv[2:]):
            f = frame(tt); cv2.imwrite(f'test_{tt}.png', f)
            cv2.imwrite(f'testcrop_{tt}.png', f[240:840, 560:1360])
    else:
        n = int(FPS*DUR)
        p = subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','bgr24','-s','1920x1080','-r',str(FPS),'-i','-',
            '-c:v','libx264','-preset','slow','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart','/mnt/user-data/outputs/anim/falling_light_loop_hq.mp4'], stdin=subprocess.PIPE)
        for i in range(n):
            p.stdin.write(frame(i/FPS).tobytes())
        p.stdin.close(); p.wait(); print('done', n)

#!/usr/bin/python
# coding: utf-8
import sys, scipy, pylab
from math import sqrt
import fabio,numpy
from utilstest import UtilsTest, getLogger
logger = getLogger(__file__)
pyFAI = sys.modules["pyFAI"]
import pyFAI.blob_detection


def image_test():
    
    shape = 1000,1000
    xc,yc = 500,500
    rings = range(0,500,50)
    y,x = numpy.ogrid[:shape[0],:shape[1]]
    x -= xc
    y -= yc
    r = numpy.sqrt(x**2+y**2)
    img = numpy.zeros(shape)
    for radius in rings:
        img += numpy.exp(-((r-radius)/2)**2)
        
    y,x = numpy.ogrid[:shape[0],:shape[1]]    
    sin = (numpy.sin(((x-x.size/2)/4)**8))**4 * (numpy.sin(((y-y.size/2)/4)**8))**4      
    img = img * sin
    img = scipy.ndimage.gaussian_filter(img, 1)
    
    
#     img = numpy.zeros((128*4,128*4))
#     a = numpy.linspace(0.5, 8, 16)
#     xc = [64,64,64,64,192,192,192,192,320,320,320,320,448,448,448,448]
#     yc = [64,192,320,448,64,192,320,448,64,192,320,448,64,192,320,448]
#     cpt = 0
#     for sigma in a:
#         img = make_gaussian(img,sigma,xc[cpt],yc[cpt])
#         cpt = cpt + 1

    return img

def make_gaussian(im,sigma,xc,yc):
    e = 0
    angle = 0
    sx = sigma * (1+e)
    sy = sigma * (1-e)
    size = int( 8*sigma +1 )
    if size%2 == 0 :
        size += 1
    x = numpy.arange(0, size, 1, float)
    y = x[:,numpy.newaxis]
#     x = x * 2
    x0 = y0 = size // 2
    gausx = numpy.exp(-4*numpy.log(2) * (x-x0)**2 / sx**2)
    gausy = numpy.exp(-4*numpy.log(2) * (y-y0)**2 / sy**2)
    gaus = 0.01 + 1* gausx * gausy
    im[xc-size/2:xc+size/2+1,yc-size/2:yc+size/2+1] = scipy.ndimage.rotate(gaus,angle, reshape = False)
    return im

if len(UtilsTest.options.args) > 0:
    data = fabio.open(UtilsTest.options.args[0]).data
    if len(UtilsTest.options.args) > 1:
        msk = fabio.open(UtilsTest.options.args[1]).data
    else:
        msk = None
else:
    data = image_test()
    msk = None


bd = pyFAI.blob_detection.BlobDetection(data, mask=msk)

pylab.ion()
f=pylab.figure(1)
ax = f.add_subplot(111)
ax.imshow(numpy.log1p(data), interpolation = 'nearest')

for i in range(10):
    print ('Octave #%i' %i)
    bd._one_octave(True, False , False) #arg 1 = shrinf, arg2=SG (hessian vectoriel si non), arg 3 = 5 pts
    print("Octave #%i Total kp: %i" % (i, bd.keypoints.size))
    print     
    
# bd._one_octave(False, True ,False)
    
print ('Final size of keypoints : %i'% bd.keypoints.size)

i = 0
# for kp  in bd.keypoints:
#     ds = kp.sigma
#     ax.annotate("", xy=(kp.x, kp.y), xytext=(kp.x+ds, kp.y+ds),
#                 arrowprops=dict(facecolor='blue', shrink=0.05),)
sigma = bd.keypoints.sigma
for i,c in enumerate("bgrcmykw"):
#    j = 2 ** i
    m = numpy.logical_and(sigma >= i, sigma < (i + 1))
    ax.plot(bd.keypoints[m].x, bd.keypoints[m].y, "o" + c, label=str(i))
ax.legend()

if sigma.size > 0:
    h = pylab.figure(2)
    x, y, o = pylab.hist(sigma, bins=100)
    h.show()
      
    index = numpy.where(x == x.max())
    kp = bd.keypoints[bd.keypoints.sigma > y[index]]
else : kp = bd.keypoints

# pylab.figure()
# pylab.imshow(numpy.log1p(data), interpolation = 'nearest')
# pylab.plot(kp.x,kp.y,'og')

f.show()
raw_input()

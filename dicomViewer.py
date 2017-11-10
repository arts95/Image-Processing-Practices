import dicom
from matplotlib import pylab, pyplot

ds = dicom.read_file("name-of-file.dcm")
pylab.imshow(ds.pixel_array)
manufacturer = ds['0008', '0070']
pylab.text(8, 15, "Manufacturer: " + manufacturer.value, bbox={'facecolor': 'white', 'alpha': 0.6, 'pad': 7})
pylab.show()

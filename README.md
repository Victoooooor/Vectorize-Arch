# ECE-395-SeniorProj
Raster Vectorization

### Build instructions

##### Setup
Install the `png++` package.  
Install CUDA packages and add the Path variable to Environment Variables in the run configuration.

Create a venv:
```
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```

Build open3d (Arch only):
```
in 3rdparty/libjpeg-turbo/libjpeg-turbo.cmake
replace
$ set(JPEG_TURBO_LIB_DIR ${INSTALL_DIR}/${Open3D_INSTALL_LIB_DIR})
with
$ set(JPEG_TURBO_LIB_DIR ${INSTALL_DIR}/lib64)
```


Example path variable:
```
Path=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.5\extras\CUPTI\lib64\;C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.5\bin\;D:\Program Files\cuda\bin\;
```

### Run instructions
See `src/util/settings.py` for a list of command-line arguments.
```
$ python3 src/main.py -iimg/test9.jpg -oimg/vectorized.svg
```

##### Comparison with other methods
These are our own implementations of the other methods.

Potrace multiscan:
```bash
$ python src/potrace_multiscan.py -iimg/test9.jpg -oimg/potrace.svg
```

Plain blue-noise sampling (without heuristics):
```bash
$ python src/plain_bns.py -iimg/test9.jpg -oimg/bns.svg
```

Evaluate methods and get statistics: this will generate statistics to a timestamped folder in `./img/eval/`.
```bash
$ python src/evaluate.py -iimg/test9.jpg -oimg/evaluate.svg
```

### Sample outputs

##### Original image
![Original image][original-image]

##### Potrace
![Potrace vectorization][potrace-output]

##### Blue-noise sampling
![BNS vectorization][bns-output]

##### Our example
![Our vectorization][our-output]

[original-image]: ./img/test9.jpg
[potrace-output]: ./img/potrace.png
[bns-output]: ./img/bns.png
[our-output]: ./img/vectorized.png
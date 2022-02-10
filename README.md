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

Example path variable:
```
Path=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.5\extras\CUPTI\lib64\;C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.5\bin\;D:\Program Files\cuda\bin\;
```

##### NEW
See `src/util/settings.py` for a list of command-line arguments.
```
$ python3 src/main.py -i img/lab1.jpg -o img/out2.svg
```

TODO: remove old instructions and code

##### Edge detector
```
$ make run_edge ARGS="img/emoji.png img/out.png"
```

##### Blue noise sampling
```bash
(venv) $ python src/sampling/sample.py -i img/test.jpg
```

##### Output to SVG
```bash
(venv) $ python src/util/mesh_to_svg.py
```

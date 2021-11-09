# ECE-395-SeniorProj
Raster Vectorization

### Build instructions

##### Setup
Install the `png++` package.

Create a venv:
```
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```

##### Edge detector
```
$ make run_edge ARGS="img/emoji.png img/out.png"
```

##### Blue noise sampling
```bash
(venv) $ python src/sampling/main.py -i img/test.jpg
```

##### Output to SVG
```bash
(venv) $ python src/util/mesh_to_svg.py
```

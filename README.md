# meep_sandbox
A sandbox demo of EM simulation using meep. The sandbox contains only 1 synthetic example, where there is a cross of material A and a disk of material B and users can use mouse to interact with the system and see simulation result in real-time.

## Installation
Please follow the [instructions](https://meep.readthedocs.io/en/latest/Installation/#official-releases) here to obtain a conda environment with meep. It already contains all the necessary dependency.

## How to use
Simply execute the following after sourcing the meep conda environment by `source ./meep/bin/activate mp`
```
python meep_sandbox.py
```

![Sandbox window](https://github.com/boycetsang/meep_sandbox/blob/master/demo.JPG)

You can then either use the slider or drag the light blur circle to change the simulation.

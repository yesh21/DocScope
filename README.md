# <span style="color:skyblue">DocScope</span>: Local LLM Doc Analysis Tool 


# Installation
```console
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements
```
This is for installing LLamaCPP in macOS<br>
for mac:<br>
&ensp; Using [Home brew](https://formulae.brew.sh/formula/cmake)

 ```console
 # Linux and Mac
CMAKE_ARGS="-DLLAMA_METAL_EMBED_LIBRARY=ON -DLLAMA_METAL=on" pip install llama-cpp-python --no-cache-dir
```

for windows:<br>
&ensp; CMAKE website [Link](https://cmake.org/)
 ```console
# Windows
$env:CMAKE_ARGS = "-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"
pip install llama-cpp-python
```

### Usage
Run the streamlit app
```console
sh run.sh
```
to run flake8 and tests
```console
tox
```

# Profile and Benchmark  Python Code
The purpose of this part is to have a ready made vademecum to profile Python code, with no need to google stuff every time.

## Normal Scripts (no Jupyter)
### Time
Tools to measure time spent inside functions, with the procedures to use them.
* **Snakeviz**
	* generate a ```.prof``` file with the command 
	```bash
	python -m cProfile -o p.prof code_profiling_main.py --dim 10000 --loops 4
	```
	* in a local machine with access to a browser, simply run ```snakeviz p.prof```
	* if we're working remotely, use the following procedure:
		* ```user@remote: snakeviz --server p.prof```
		* ```user@local: ssh -Y -N -f -L localhost:8080:localhost:8080 user@remote```
		* in the local browser, paste the link printed by snakeviz on the remote cluster (e.g. ```http://127.0.0.1:8080/snakeviz/%2Fwork%2Fgallim%2Fdevel%2FUsefulHEPScripts%2Fprofiling%2Fp.prof```)
* **line_profiler**
	* add the decorator ```@profile``` to the functions we want to profile
	* run ```kernprof -l -v code_profiling_main.py --dim 1000 --loops 4```

### Memory Usage
 * **memory_profiler** 
	 * decorate functions with ```@profile```
	 * run ```python -m memory_profiler code_profiling_main.py --dim 1000 --loops 4``` (see [here](https://www.blog.pythonlibrary.org/2016/05/24/python-101-an-intro-to-benchmarking-your-code/) for details )

## IPython/Jupyter
See [here](https://jakevdp.github.io/PythonDataScienceHandbook/01.07-timing-and-profiling.html) for IPython magic commands and [here](https://jiffyclub.github.io/snakeviz/) for Snakeviz.

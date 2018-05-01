all: res.py _res.so

res.py: res.i
	swig -c++ -python res.i

_res.so: res.o res_wrap.o
	g++ -shared res.o res_wrap.o -o _res.so

res.o: res.cxx
	g++ -fPIC -c res.cxx 

res_wrap.o: res_wrap.cxx
	g++ -fPIC -c res_wrap.cxx $$(python3-config --includes --ldflags)

res_wrap.cxx: res.py

clean:
	rm *o res.py res_wrap.cxx

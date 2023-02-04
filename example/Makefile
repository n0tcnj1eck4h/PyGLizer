LDLIBS = -lglfw 
CXXFLAGS = -I.

.PHONY: clean run headers

build: GL.h GL.cpp out

out: main.o GL.o
	$(CXX) $(LDLIBS) $^ -o $@

GL.h GL.cpp:
	python3 ../main.py --generator cpp

clean:
	$(RM) GL.hpp GL.cpp out *.o

run: build
	./out

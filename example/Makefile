build: 
	$(CXX) main.cpp -o main.o -I.. -c
	$(CXX) ../GL.cpp -o GL.o -I.. -c
	$(CXX) -o out main.o GL.o -lglfw
	chmod +x out

clean:
	rm -f *.o out

run: build
	./out

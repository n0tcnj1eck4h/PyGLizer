build: 
	$(CXX) main.cpp -o main.o -I../Output/ -c
	$(CXX) ../Output/GL.cpp -o GL.o -I../Output/ -c
	$(CXX) -o out main.o GL.o -lglfw
	chmod +x out

clean:
	rm -f *.o out

run: build
	./out

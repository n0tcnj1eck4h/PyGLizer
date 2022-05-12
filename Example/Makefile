build: 
	g++ main.cpp -o main.o -I../Output/ -c
	g++ ../Output/GL.cpp -o GL.o -I../Output/ -c
	g++ -o out main.o GL.o -lglfw
	chmod +x out

clean:
	rm *.o out

run: build
	./out

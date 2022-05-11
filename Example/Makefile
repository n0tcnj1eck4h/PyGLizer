build: 
	g++ main.cpp -o main.o -c
	g++ ../GL.cpp -o GL.o -I.. -c
	g++ -o out main.o GL.o -lglfw
	chmod +x out

clean:
	rm *.o out

run: build
	./out

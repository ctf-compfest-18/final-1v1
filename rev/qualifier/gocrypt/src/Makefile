build:
	CGO_ENABLED=0 go build -o chall chall.go
	./chall flag.txt flag.enc
	cp chall flag.enc ../public/

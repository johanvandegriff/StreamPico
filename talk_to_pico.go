package main

import (
	"fmt"
	"go.bug.st/serial"
	"log"
)

func main() {
	// https://pkg.go.dev/go.bug.st/serial

	ports, err := serial.GetPortsList()
	if err != nil {
		log.Fatal(err)
	}
	if len(ports) == 0 {
		log.Fatal("No serial ports found!")
	}
	for _, port := range ports {
		fmt.Printf("Found port: %v\n", port)
	}

	mode := &serial.Mode{
		BaudRate: 9600,
	}
	port, err := serial.Open("/dev/rfcomm0", mode)
	if err != nil {
		log.Fatal(err)
	}
	n, err := port.Write([]byte("C,RGB,10,20,30\n\r"))
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Sent %v bytes\n", n)
}

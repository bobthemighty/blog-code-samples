package main

import (
	"flag"
	"fmt"
)

func main() {
	var message = flag.String("message", "Hello world!", "The log message to send")
	var level = flag.String("level", "info", "The 'levelname' to use; debug, info, warn, error, etc.")
	var format = flag.String("format", "json", "The format to use, 'log4j' or 'json'")
	flag.Parse()

	if *format == "log4j" {
		fmt.Printf("[%s]: %s", *level, *message)
	} else {
		fmt.Printf(`{ "@message": "%s", "@fields":{ "levelname": "%s" } }`, *message, *level)
	}
}

package main

import (
	"flag"
	"fmt"
	"math/rand"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/blackjack/syslog"
)

func main() {

	errorRate := flag.Float64("error-rate", 0.1, "The probability of logging an error expresed as a float between 0 and 1.0")
	tag := flag.String("tag", "dummy-logger", "The program name to use when tagging logs")
	interval := flag.Int("interval", 100, "The number of milliseconds to wait between sending logs")
	flag.Parse()

	sigs := make(chan os.Signal, 1)
	ticker := time.NewTicker(time.Millisecond * time.Duration(*interval))
	done := make(chan bool, 1)

	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)
	syslog.Openlog(*tag, syslog.LOG_PID, syslog.LOG_USER)

	fmt.Printf("Sending log lines every %dms, hit ctrl-c to stop\n", *interval)

	for {
		select {

		case <-sigs:
			ticker.Stop()
			done <- true

		case <-ticker.C:
			r := rand.Float64()
			if r <= *errorRate {
				syslog.Err("Oh noes!")
			} else {
				syslog.Info("Everything is fine!")
			}

		case <-done:
			return
		}
	}

	fmt.Println("Done!")

}

package main

import (
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"syscall"

	Syslog "github.com/blackjack/syslog"
	"github.com/julienschmidt/httprouter"
)

func Stop(srv *http.Server) {
	fmt.Println("Shutting down http server")
	if err := srv.Shutdown(nil); err != nil {
		fmt.Printf("Failed during shutdown %s", err)
	}
}

func Endpoint(w http.ResponseWriter, r *http.Request, p httprouter.Params) {
	time, err := strconv.Atoi(r.URL.Query().Get("time"))
	if err != nil {
		time = 20
	}

	status, err := strconv.Atoi(p.ByName("status"))
	if err != nil {
		fmt.Printf(`{ "@message": "Failed to parse status '%s' as  http status code", "@fields":{ "levelname": "ERROR" }}%s`, p.ByName("status"), "\n")
	}

	fmt.Printf(`{ "@message": "Responded with %d in %dms", "@fields": { "_riemann_metric": { "service": "my-app/response-time", "metric": %d, "attributes": { "status_code": "%d" }}}}%s`, status, time, time, status, "\n")
}

func Start() *http.Server {
	router := httprouter.New()
	router.GET("/:status", Endpoint)
	srv := &http.Server{
		Addr:    "0.0.0.0:8192",
		Handler: router,
	}
	go func() {
		if err := srv.ListenAndServe(); err != nil {
			fmt.Printf("Http ListenAndServe error: %s", err)
		}
	}()
	return srv
}

func handleSignals(sigs chan os.Signal, done chan bool) {
	var srv *http.Server

	srv = Start()
	for {
		sig := <-sigs
		if sig == syscall.SIGHUP {
			fmt.Printf("Received SIGHUP; restarting service")
			Stop(srv)
			srv = Start()
		} else {
			Stop(srv)
			break
		}
	}
	done <- true
}

func main() {
	Syslog.Openlog("my-app", Syslog.LOG_PID, Syslog.LOG_LOCAL3)
	done := make(chan bool, 1)
	sigs := make(chan os.Signal)
	go handleSignals(sigs, done)
	signal.Notify(sigs, syscall.SIGTERM, syscall.SIGINT, syscall.SIGHUP)
	<-done
	fmt.Printf("Exiting")
}

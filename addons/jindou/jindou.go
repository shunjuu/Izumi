package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"os"
	"strings"

	"code.cloudfoundry.org/bytefmt"
)

type job struct {
	Show     string `json:"show"`
	Episode  string `json:"episode"`
	Filesize uint64 `json:"filesize"`
	Sub      string `json:"sub"`
}

func jindou(w http.ResponseWriter, r *http.Request) {
	fmt.Println("Received request, starting...")
	API := "https://api.telegram.org/bot"
	SEND := "/sendMessage"

	var j job
	err := json.NewDecoder(r.Body).Decode(&j)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	fmt.Println("Parsed job for " + j.Episode)

	message := "-------New Upload-------\n"
	message = message + "<b>" + j.Episode + "</b>\n"
	message = message + "\n<i>From: " + j.Show + "</i>"
	message = message + "\n<i>Filesize: " + bytefmt.ByteSize(j.Filesize*bytefmt.BYTE) + "</i>"
	message = message + "\n<i>Type: " + strings.Title(j.Sub) + "</i>"

	form := url.Values{}
	form.Add("chat_id", os.Args[2])
	form.Add("parse_mode", "HTML")
	form.Add("text", message)

	hc := http.Client{}
	req, _ := http.NewRequest("POST", API+os.Args[1]+SEND, strings.NewReader(form.Encode()))
	req.Header.Add("Content-Type", "application/x-www-form-urlencoded")
	hc.Do(req)

	fmt.Println("Completed.")

}

func main() {

	fmt.Println("Starting HTTP Mux server, listening on port 22150")

	// Start http stuff
	mux := http.NewServeMux()
	mux.HandleFunc("/jindou", jindou)
	err := http.ListenAndServe(":22150", mux)
	log.Fatal(err)
}

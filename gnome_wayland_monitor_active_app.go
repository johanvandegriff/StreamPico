package main

import (
	"bufio"
	"fmt"
	"log"
	"os/exec"
	"strings"
)

func readln(buf *bufio.Reader) string {
	line, _, _ := buf.ReadLine()
	return string(line)
}

func main() {
	cmd := exec.Command("dbus-monitor")
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		log.Fatal(err)
	}
	cmd.Start()

	buf := bufio.NewReader(stdout)

	for {
		line := readln(buf)
		if strings.Contains(line, "member=RunningApplicationsChanged") {
			line := readln(buf)
			if strings.Contains(line, "member=GetRunningApplications") {
				last_line := ""
				for line := ""; !strings.Contains(line, "string \"active-on-seats\""); line = readln(buf) {
					if strings.Contains(line, "string \"") {
						last_line = line
					}
				}
				if last_line != "" {
					app := strings.Split(last_line, "\"")[1]
					fmt.Println(app)
				}
			}
		}
	}
}


/*
Example event from dbus-monitor

$ dbus-monitor | grep 'member=RunningApplicationsChanged' -A 30
    ...
signal time=1653308837.299322 sender=:1.14 -> destination=(null destination) serial=629 path=/org/gnome/Shell/Introspect; interface=org.gnome.Shell.Introspect; member=RunningApplicationsChanged
method call time=1653308837.300012 sender=:1.65 -> destination=:1.14 serial=144 path=/org/gnome/Shell/Introspect; interface=org.gnome.Shell.Introspect; member=GetRunningApplications
method return time=1653308837.305183 sender=:1.14 -> destination=:1.65 serial=630 reply_serial=144
   array [
      dict entry(
         string "org.wezfurlong.wezterm.desktop"
         array [
         ]
      )
      dict entry(
         string "org.thonny.Thonny.desktop"
         array [
            dict entry(
               string "active-on-seats"
               variant                   array [
                     string "seat0"
                  ]
            )
         ]
      )
      dict entry(
         string "librewolf.desktop"
         array [
         ]
      )
      dict entry(
         string "rambox.desktop"
         array [
         ]
      )
      dict entry(
    ...
*/


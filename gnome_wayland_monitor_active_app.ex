#TODO docs
defmodule PortLineByLine do
  def open(caller, command) do
    spawn(fn -> _monitor(caller, command) end)
  end
  def _monitor(caller, command) do
    port = Port.open({:spawn, command}, [:binary, :exit_status, :in])
#TODO doesn't kill the shell command when Ctrl-C exits program
#    System.at_exit(fn(_) -> kill_port(port) end) #doesn't work
    _monitor_loop(caller, port, command)
  end
  def _monitor_loop(caller, port, command) do
    receive do
      {^port, {:data, chunk}} ->
        if String.last(chunk) !== "\n", do: raise "didn't end with newline"
        chunk |> String.split("\n", trim: true)
        |> Enum.each(fn(line) -> send(caller, line) end)
      {^port, {:exit_status, _exit_status}} ->
        #IO.puts "port exited with #{_exit_status}, restarting it"
        _monitor(caller, command) #restart the port
      msg ->
        IO.inspect msg
        raise "unexpected message"
    end
    _monitor_loop(caller, port, command)
  end

  def kill_port(port) do
    {:os_pid, pid} = :erlang.port_info(port, :os_pid)
    :os.cmd('kill -9 #{pid}')
  end
end

defmodule MonitorActiveApp do
  def start(caller) do
    spawn(fn -> _monitor(caller) end)
  end
  def _monitor(caller) do
    me = self()
    PortLineByLine.open(me, "dbus-monitor")
    _monitor_recv_loop(caller)
  end
  def _monitor_recv_loop(caller) do
    receive do line ->
      if line =~ ~r/member=RunningApplicationsChanged/ do
        receive do line ->
          if line =~ ~r/member=GetRunningApplications/ do
            _monitor_recv_loop2(:nil, caller)
          end
        end
      end
    end
    _monitor_recv_loop(caller)
  end

  def _monitor_recv_loop2(last_line, caller) do
    receive do line ->
      cond do
        line =~ ~r/string "active-on-seats"/ ->
          [_, app, _] = String.split(last_line, "\"")
          send(caller, app)
        line =~ ~r/string "/ ->
          _monitor_recv_loop2(line, caller)
        true ->
          _monitor_recv_loop2(last_line, caller)
      end
    end
  end

  def recv_puts_forever() do
    receive do a -> IO.puts(a) end
    recv_puts_forever()
  end
end

MonitorActiveApp.start(self())
MonitorActiveApp.recv_puts_forever()



"""
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
"""


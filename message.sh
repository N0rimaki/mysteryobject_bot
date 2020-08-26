sleep 60
lxterminal --geometry=200x24 -t "message log" -e tail -f /home/pi/mysteryobject_bot/log_messages.log 
exit

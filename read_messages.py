import time
import sys
import threading
from pubsub import pub
from meshtastic.serial_interface import SerialInterface

serial_port = '/dev/ttyUSB0'
last_message_time = time.time()
stop_timeout = 1
done = threading.Event()

def handle_text(packet, interface):
    global last_message_time
    text = packet['decoded'].get('text') or \
           packet['decoded'].get('payload', b'').decode('utf-8', 'ignore')
    src = packet.get('fromId')
    if src and text:
        print(f"{src}: {text}")
        last_message_time = time.time()

def on_connect(interface):
    pass

def auto_exit_loop(interface):
    global last_message_time
    while not done.is_set():
        time.sleep(1)
        if time.time() - last_message_time > stop_timeout:
            interface.close()
            done.set()

def main():
    iface = SerialInterface(serial_port)

    pub.subscribe(handle_text, "meshtastic.receive.text")
    pub.subscribe(on_connect, "meshtastic.connection.established")

    threading.Thread(target=auto_exit_loop, args=(iface,), daemon=True).start()

    try:
        done.wait()
        sys.exit(0)
    except KeyboardInterrupt:
        iface.close()
        sys.exit(1)

if __name__ == "__main__":
    main()

import asyncio, sys, json, time

async def rx(reader, writer):
    while riga := await reader.readline():
        try:
            msg = json.loads(riga.decode().strip())
            print(f"\n[{time.strftime('%H:%M:%S', time.localtime(msg['ts']))}] {msg['from']}: {msg['text']}")
            print("> ", end="", flush=True)
        except (json.JSONDecodeError, KeyError, TypeError):
            print("\n[messaggio non valido ignorato]")

async def main(rx_port, tx_port, nome):
    server = await asyncio.start_server(rx, "127.0.0.1", rx_port)   # Opens connection from rx_port
    print("Waiting for connection...")

    while True:  # Retry until other peer is online
        try:
            _, writer = await asyncio.open_connection("127.0.0.1", tx_port)
            break
        except ConnectionRefusedError:
            await asyncio.sleep(1)

    print("Connection estabilished")
    loop = asyncio.get_running_loop()     # Creates a loop for input text
    while True:
        testo = await loop.run_in_executor(None, input, "> ")
        msg = {"from": nome, "text": testo, "ts": time.time()}
        writer.write((json.dumps(msg) + "\n").encode())
        await writer.drain()

# RX port = port where client recieves messages
# TX port = port of the other client to send messages to
if __name__ == "__main__":
    asyncio.run(main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]))       # Insert RX port and TX port
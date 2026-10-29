import asyncio, sys

async def rx(reader, writer):
    while riga := await reader.readline():
        print("\nPeer:", riga.decode().strip())

async def main(rx_port, tx_port):
    server = await asyncio.start_server(rx, "127.0.0.1", rx_port)

    while True:  # Retry until other peer is online
        try:
            _, writer = await asyncio.open_connection("127.0.0.1", tx_port)
            break
        except ConnectionRefusedError:
            await asyncio.sleep(1)

    loop = asyncio.get_running_loop()     # Creates a loop for input text
    while True:
        testo = await loop.run_in_executor(None, input, "> ")
        writer.write((testo + "\n").encode())
        await writer.drain()

# RX port = port where client recieves messages
# TX port = port of the other client to send messages to
asyncio.run(main(int(sys.argv[1]), int(sys.argv[2])))       # Insert RX port and TX port
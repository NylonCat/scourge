import asyncio, sys, json, time, base64
from nacl.signing import SigningKey, VerifyKey
from nacl.exceptions import BadSignatureError

async def rx(reader, writer):
    peer_key = None

    while riga := await reader.readline():
        try:
            msg = json.loads(riga.decode().strip())
            if msg.get("type") == "hello":
                peer_key = VerifyKey(base64.b64decode(msg["sign_pub"]))
                print(f"\n[{msg['from']} sent its public key: {msg['sign_pub']}]")
                print("> ", end="", flush=True)
                continue
            print(f"\n[{time.strftime('%H:%M:%S', time.localtime(msg['ts']))}] {msg['from']}: {msg['text']}")
            print("> ", end="", flush=True)
        except (json.JSONDecodeError, KeyError, TypeError):
            print("\n[messaggio non valido ignorato]")

async def main(rx_port, tx_port, username):
    server = await asyncio.start_server(rx, "127.0.0.1", rx_port)   # Opens connection from rx_port
    writer = None

    # Key generation for signing messages
    signing_keys = SigningKey.generate()        # Public and private keys
    public_key = bytes(signing_keys.verify_key) # Public key converted to bytes

    try:
        print("Waiting for connection...")
        while True:     # Wait for peer to connect
            try:
                _, writer = await asyncio.open_connection("127.0.0.1", tx_port)
                break
            except ConnectionRefusedError:
                await asyncio.sleep(1)

        print("Connection established")

        # Hello message
        hello = {"type": "hello", "from": username, "sign_pub": base64.b64encode(public_key).decode()}
        writer.write((json.dumps(hello) + "\n").encode())
        await writer.drain()

        loop = asyncio.get_running_loop()         # Allows input() to not block all main()
        while True:
            testo = await loop.run_in_executor(None, input, "> ")       # Note: it will generate a KeyboardInterrupt error anyways
            msg = {"from": username, "text": testo, "ts": time.time()}
            writer.write((json.dumps(msg) + "\n").encode())
            await writer.drain()
    except (ConnectionError, EOFError):
        print("\nPeer disconnected")
    finally:
        print("Closing program")
        if writer:      # Avoids errors if connection was never estabilished
            writer.close()
            try:        # Avoids BrokenPipe if peer tries to close a connection with an already down peer
                await writer.wait_closed()
            except (ConnectionError, OSError):
                pass
        server.close()
        await server.wait_closed()

# RX port = port where client recieves messages
# TX port = port of the other client to send messages to
if __name__ == "__main__":
    try:
        asyncio.run(main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]))       # Insert RX port and TX port
    except KeyboardInterrupt:
        pass
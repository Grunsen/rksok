import asyncio
import os
from busines_logic import serve_client


async def run_server(host: str = "0.0.0.0", port: int = 3333):
    if not os.path.exists("phonebook.txt"):
        with open("phonebook.txt", 'w') as f:
            f.write("")
    server = await asyncio.start_server(serve_client, host, port)
    await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(run_server())
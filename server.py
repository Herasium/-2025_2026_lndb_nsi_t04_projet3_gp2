import asyncio

from modules.server import Server


async def run_everything():
    server = Server()
    await asyncio.gather(server.serve())

def main():
    try:
        asyncio.run(run_everything())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
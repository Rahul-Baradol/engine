from ServerEventLoop import ServerEventLoop

if __name__ == "__main__":
    loop = ServerEventLoop('0.0.0.0', 8080)
    loop.run()
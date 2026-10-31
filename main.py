from EventLoop import EventLoop

eventloop = EventLoop()

eventloop.enqueue(lambda: print("A"))
eventloop.enqueue(lambda: print("B"))
eventloop.enqueue(lambda: print("C"))

eventloop.run()
from EventLoop import EventLoop

eventloop = EventLoop()

# eventloop.enqueue(lambda: print("A"))
# eventloop.call_later(2, lambda: print("B"))
# eventloop.enqueue(lambda: print("C"))
# eventloop.call_later(2, lambda: print("D"))

eventloop.call_later(5, lambda: print("A"))
eventloop.call_later(2, lambda: print("B"))
eventloop.call_later(3, lambda: print("C"))


eventloop.run()
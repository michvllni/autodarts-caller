from server import caller_server

def process_common(m, caller_server: caller_server):
    caller_server.broadcast(m)
from server import CallerServer

def process_common(m, CallerServer: CallerServer):
    CallerServer.broadcast(m)
function connectSocket() {
    const script = document.getElementById("socketScript");
    const domain = script.dataset.socketDomain;
    return io(domain, {
        transports: ['websocket'],
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        timeout: 20000
    })
}

let socket = connectSocket();

function emit(event, data) {
    socket.emit('default_event', {
        event: event,
        payload: data
    })
}

// Global Event Handlers
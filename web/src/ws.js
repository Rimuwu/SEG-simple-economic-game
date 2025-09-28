// ws://localhost:8000/ws/connect?client_id={client_id}

export class WebSocketManager {
    constructor(url, consoleObj) {
        this.url = url;
        this.socket = null;
        this.console = consoleObj;
    }
    get_id() {
        return `web_${Date.now()}`;
    }

    connect() {
        const client_id = this.get_id();
        const wsUrl = `${this.url}?client_id=${client_id}`;
        this.socket = new WebSocket(wsUrl);
        this.socket.onopen = () => {
            console.log('WebSocket connection established with client_id:', client_id);
        };
        this.socket.onmessage = (event) => this.onmessage(event);

        console.log('WebSocketManager connected to', wsUrl);

        this.socket.onclose = () => {
            console.log('WebSocket connection closed');
        };
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    check_session(session_id) {
        const request_id = `check_session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        this.socket.send(JSON.stringify({
            type: 'get-session',
            session_id: session_id,
            request_id: request_id
        }));
        return request_id; // Return request_id so caller can match the response
    }

    get_sessions() {
        const request_id = `get_sessions_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        this.socket.send(JSON.stringify({
            type: 'get-sessions',
            request_id: request_id
        }));
        return request_id; // Return request_id so caller can match the response
    }

    ping() {
        // Try different console methods
        setTimeout(() => {
                console.log('test');
            }, 0);
        
        const request_id = `ping_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        this.socket.send(JSON.stringify({ type: 'ping', request_id: request_id }));
        return request_id;
    }

    onmessage(event) {
        const message = JSON.parse(event.data);

        window.console.log('Message received:', message);


        if (message.type === 'response' && message.request_id) {
            if (message.request_id.startsWith('check_session_')) {
                this.handleSessionCheckResponse(message);
            }
            console.log('Response to request_id:', message.request_id, message);
        } else if (message.type && message.type.startsWith('api-')) {
            // this.handleBroadcastMessage(message);
        } else if (message.type === 'error') {
            console.error('WebSocket error:', message.message);
        }
        return message;
    }

    handleSessionCheckResponse(message) {
        if (message.data) {
            console.log('Session exists:', message.data);
        } else {
            console.log('Session not found or error occurred');
        }
    }

    handleBroadcastMessage(message) {
        console.log('Broadcast message received:', message.type, message.data);
        // Handle broadcast messages here - these are sent to all connected clients
        // when game events occur (user created, company actions, etc.)
    }
}

export const SAMPLE_MESSAGES = {
    GET_SESSION: {
        type: 'get-session',
        session_id: 'session_abc123',
        request_id: 'unique_request_id'
    },

    GET_USERS: {
        type: 'get-users',
        session_id: 'session_abc123',
        request_id: 'unique_request_id'
    },

    GET_COMPANIES: {
        type: 'get-companies',
        session_id: 'session_abc123',
        request_id: 'unique_request_id'
    }
}

console.log("WebSocketManager module loaded");

// Create a standalone function for testing
window.testStandaloneFunction = function() {
    console.log("Standalone function called");
    return "Standalone function executed";
};

// Create an arrow function
window.testArrowFunction = () => {
    console.log("Arrow function called");
    return "Arrow function executed";
};
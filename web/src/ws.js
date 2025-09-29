export class WebSocketManager {
    constructor(url, consoleObj) {
        this.url = url;
        this.socket = null;
        this.console = consoleObj;
        this.session_id = null;
        this.map = null;
    this.pendingCallbacks = new Map();
        this.companies = [];
        this._pollInterval = null;
    }
    get_id() {
        return `web_${Date.now()}`;
    }

    connect() {
        const client_id = this.get_id();
        const wsUrl = `${this.url}?client_id=${client_id}`;
        this.socket = new WebSocket(wsUrl);
        this.socket.onopen = () => {
            if (typeof window.log === 'function') {
                window.log('WebSocket connection established with client_id: ' + client_id);
            } else {
                console.log('WebSocket connection established with client_id:', client_id);
            }
        };
        this.socket.onmessage = (event) => this.onmessage(event);

        if (typeof window.log === 'function') {
            window.log('WebSocketManager connected to ' + wsUrl);
        } else {
            console.log('WebSocketManager connected to', wsUrl);
        }

        this.socket.onclose = () => {
            if (typeof window.log === 'function') {
                window.log('WebSocket connection closed');
            } else {
                console.log('WebSocket connection closed');
            }
        };
        this.socket.onerror = (error) => {
            if (typeof window.error === 'function') {
                window.error('WebSocket error: ' + error.toString());
            } else {
                console.error('WebSocket error:', error);
            }
        };
    }

    join_session(session_id, callback = null) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            const error = 'WebSocket is not connected';
            if (typeof window.error === 'function') {
                window.error(error);
            } else {
                console.error(error);
            }
            if (callback) {
                callback({ success: false, error: error });
            }
            return null;
        }

        const request_id = `join_session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        if (callback && typeof callback === 'function') {
            this.pendingCallbacks.set(request_id, callback);
        }
        this.socket.send(JSON.stringify({
            type: 'get-session',
            session_id: session_id,
            request_id: request_id
        }));
        
        
        if (typeof window.log === 'function') {
            window.log('Attempting to join session: ' + session_id);
        } else {
            console.log('Attempting to join session:', session_id);
        }
        
        return request_id;
    }

    load_map() {

    }

    check_session(session_id, callback = null) {
        const request_id = `check_session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        if (callback && typeof callback === 'function') {
            this.pendingCallbacks.set(request_id, callback);
        }
        
        this.socket.send(JSON.stringify({
            type: 'get-session',
            session_id: session_id,
            request_id: request_id
        }));
        
        if (typeof window.log === 'function') {
            window.log('Checking session: ' + session_id);
        } else {
            console.log('Checking session:', session_id);
        }
        
        return request_id;
    }

    get_sessions() {
        const request_id = `get_sessions_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        this.socket.send(JSON.stringify({
            type: 'get-sessions',
            request_id: request_id
        }));
        return request_id;
    }
    get_session() {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            const error = 'WebSocket is not connected';
            if (callback) callback({ success: false, error });
            return null;
        }
        
        const request_id = `get_session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        this.socket.send(JSON.stringify({
            type: 'get-session',
            session_id: this.session_id,
            request_id: request_id
        }));
        window.log("Requesting session info...");
        return request_id;
    }

    get_companies(callback = null) {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            const error = 'WebSocket is not connected';
            if (callback) callback({ success: false, error });
            return null;
        }
        const request_id = `get_companies_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        if (callback && typeof callback === 'function') {
            this.pendingCallbacks.set(request_id, callback);
        }
        this.socket.send(JSON.stringify({
            type: 'get-companies',
            session_id: this.session_id || undefined,
            request_id: request_id
        }));
        if (typeof window.log === 'function') window.log('Requesting companies list...');
        return request_id;
    }

    startPolling(intervalMs = 5000) {
        this.stopPolling();
        this.get_companies();
        this._pollInterval = setInterval(() => {
            this.get_companies();
            this.refreshMap();
        }, intervalMs);
        if (typeof window.log === 'function') window.log('Started polling every ' + intervalMs + 'ms');
    }

    stopPolling() {
        if (this._pollInterval) {
            clearInterval(this._pollInterval);
            this._pollInterval = null;
            if (typeof window.log === 'function') window.log('Stopped polling');
        }
    }

    ping() {
        const request_id = `ping_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        this.socket.send(JSON.stringify({ type: 'ping', request_id: request_id }));
        return request_id;
    }

    onmessage(event) {
        const message = JSON.parse(event.data);

        if (typeof window.log === 'function') {
            window.log('Message received: ' + JSON.stringify(message));
        } else {
            window.console.log('Message received:', message);
        }


        if (message.type === 'response' && message.request_id) {
            if (message.request_id.startsWith('check_session_') || message.request_id.startsWith('join_session_')) {
                this.handleSessionResponse(message);
            } else if (message.request_id.startsWith('get_companies_')) {
                this.handleCompaniesResponse(message);
            }
            if (typeof window.log === 'function') {
                window.log('Response to request_id: ' + message.request_id + ' - ' + JSON.stringify(message));
            } else {
                console.log('Response to request_id:', message.request_id, message);
            }
        } else if (message.type && message.type.startsWith('api-')) {
        } else if (message.type === 'error') {
            if (typeof window.error === 'function') {
                window.error('WebSocket error: ' + message.message);
            } else {
                console.error('WebSocket error:', message.message);
            }
        }
        return message;
    }

    handleCompaniesResponse(message) {
        const requestId = message.request_id;
        const callback = this.pendingCallbacks.get(requestId);
        if (message.data) {
            if (Array.isArray(message.data)) {
                this.companies = message.data;
            } else if (Array.isArray(message.data.companies)) {
                this.companies = message.data.companies;
            } else {
                this.companies = [];
            }
            if (typeof window.log === 'function') window.log('Companies updated: ' + this.companies.length);
            if (callback) callback({ success: true, data: this.companies });
        } else {
            if (callback) callback({ success: false, error: 'No companies data' });
        }
        if (callback) this.pendingCallbacks.delete(requestId);
        window.dispatchEvent(new CustomEvent('companies-updated', { detail: { companies: this.companies } }));
    }

    handleSessionResponse(message) {
        const requestId = message.request_id;
        const callback = this.pendingCallbacks.get(requestId);
        
        if (message.data) {
            this.session_id = message.data.session_id;
            if (message.data.cells && message.data.map_size) {
                this.map = {
                    cells: message.data.cells,
                    size: message.data.map_size,
                    pattern: message.data.map_pattern || 'random'
                };
                
                if (typeof window.log === 'function') {
                    window.log('Map data loaded: ' + message.data.cells.length + ' cells, size: ' + 
                             message.data.map_size.rows + 'x' + message.data.map_size.cols);
                } else {
                    console.log('Map data loaded:', this.map);
                }
                
                this.loadMapToDOM();
            }
            
            if (requestId.startsWith('join_session_')) {
                if (typeof window.log === 'function') {
                    window.log('Successfully joined session: ' + this.session_id);
                } else {
                    console.log('Successfully joined session:', this.session_id);
                }
                
                if (callback) {
                    callback({ success: true, data: message.data });
                }
            } else {
                if (typeof window.log === 'function') {
                    window.log('Session exists: ' + JSON.stringify(message.data));
                } else {
                    console.log('Session exists:', message.data);
                }
                
                if (callback) {
                    callback({ success: true, data: message.data });
                }
            }
        } else {
            if (typeof window.log === 'function') {
                window.log('Session not found or error occurred');
            } else {
                console.log('Session not found or error occurred');
            }
            
            if (callback) {
                callback({ success: false, error: 'Session not found' });
            }
        }
        
        if (callback) {
            this.pendingCallbacks.delete(requestId);
        }
    }

    handleBroadcastMessage(message) {
        if (typeof window.log === 'function') {
            window.log('Broadcast message received: ' + message.type + ' - ' + JSON.stringify(message.data));
        } else {
            console.log('Broadcast message received:', message.type, message.data);
        }
    }

    getCellType(cellName) {
        const cellTypes = {
            'mountain': 0,
            'water': 1,
            'forest': 2,
            'field': 3,
            'city': 4,
            'bank': 5
        };
        return cellTypes[cellName.toLowerCase()] !== undefined ? cellTypes[cellName.toLowerCase()] : 3;
    }

    loadMapToDOM() {
        if (!this.map || !this.map.cells) {
            if (typeof window.log === 'function') {
                window.log('No map data available to load');
            }
            return false;
        }
        
        if (typeof window.setTile === 'function' && typeof window.TileTypes === 'object') {
            const { cells, size } = this.map;
            
            if (typeof window.log === 'function') {
                window.log('Loading map into DOM with ' + cells.length + ' cells, size: ' + size.rows + 'x' + size.cols);
            }
            
            const mapElement = document.getElementById('map');
            if (mapElement && size.cols !== 7) {
                mapElement.style.gridTemplateColumns = `repeat(${size.cols}, 1fr)`;
                if (typeof window.log === 'function') {
                    window.log('Updated map grid to ' + size.cols + ' columns');
                }
            }
            
            for (let i = 0; i < cells.length && i < (size.rows * size.cols); i++) {
                const row = Math.floor(i / size.cols);
                const col = i % size.cols;
                const cellType = this.getCellType(cells[i]);
                const terrainSymbol = this.getTerrainNames(cells[i]);
                window.setTile(row, col, cellType, terrainSymbol, 'var(--text-xs)');
            }
            
            if (typeof window.log === 'function') {
                window.log('Map loaded successfully into DOM');
            }
            return true;
        } else {
            if (typeof window.log === 'function') {
            }
            setTimeout(() => this.loadMapToDOM(), 500);
            return false;
        }
    }

    getTerrainNames(cellName) {
        const symbols = {
            'mountain': 'ГОРЫ',
            'water': 'МОРЕ', 
            'forest': 'ЛЕС',
            'field': 'ПОЛЯ',
            'city': 'ГОРОД',
            'bank': 'БАНК'
        };
        return symbols[cellName.toLowerCase()] || '?';
    }

    refreshMap() {
        this.get_session();
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

if (typeof window.log === 'function') {
    window.log("WebSocketManager module loaded");
} else {
    console.log("WebSocketManager module loaded");
}

window.testStandaloneFunction = function() {
    if (typeof window.log === 'function') {
        window.log("Standalone function called");
    } else {
        console.log("Standalone function called");
    }
    return "Standalone function executed";
};

window.testArrowFunction = () => {
    if (typeof window.log === 'function') {
        window.log("Arrow function called");
    } else {
        console.log("Arrow function called");
    }
    return "Arrow function executed";
};
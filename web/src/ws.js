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
    this.socket.onopen = () => {};
    this.socket.onmessage = (event) => this.onmessage(event);

    this.socket.onclose = () => {};
    this.socket.onerror = (error) => {};
  }

  join_session(session_id, callback = null) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      const error = "WebSocket is not connected";
      if (callback) {
        callback({ success: false, error: error });
      }
      return null;
    }

    const request_id = `join_session_${Date.now()}_${Math.random()
      .toString(36)
      .substr(2, 9)}`;
    if (callback && typeof callback === "function") {
      this.pendingCallbacks.set(request_id, callback);
    }
    this.socket.send(
      JSON.stringify({
        type: "get-session",
        session_id: session_id,
        request_id: request_id,
      })
    );

    return request_id;
  }

  load_map() {}

  check_session(session_id, callback = null) {
    const request_id = `check_session_${Date.now()}_${Math.random()
      .toString(36)
      .substr(2, 9)}`;
    if (callback && typeof callback === "function") {
      this.pendingCallbacks.set(request_id, callback);
    }

    this.socket.send(
      JSON.stringify({
        type: "get-session",
        session_id: session_id,
        request_id: request_id,
      })
    );

    return request_id;
  }

  get_sessions() {
    const request_id = `get_sessions_${Date.now()}_${Math.random()
      .toString(36)
      .substr(2, 9)}`;
    this.socket.send(
      JSON.stringify({
        type: "get-sessions",
        request_id: request_id,
      })
    );
    return request_id;
  }
  get_session() {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      const error = "WebSocket is not connected";
      if (callback) callback({ success: false, error });
      return null;
    }

    const request_id = `get_session_${Date.now()}_${Math.random()
      .toString(36)
      .substr(2, 9)}`;
    this.socket.send(
      JSON.stringify({
        type: "get-session",
        session_id: this.session_id,
        request_id: request_id,
      })
    );
    return request_id;
  }

  get_companies(callback = null) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      const error = "WebSocket is not connected";
      if (callback) callback({ success: false, error });
      return null;
    }
    const request_id = `get_companies_${Date.now()}_${Math.random()
      .toString(36)
      .substr(2, 9)}`;
    if (callback && typeof callback === "function") {
      this.pendingCallbacks.set(request_id, callback);
    }
    this.socket.send(
      JSON.stringify({
        type: "get-companies",
        session_id: this.session_id || undefined,
        request_id: request_id,
      })
    );
    return request_id;
  }

  startPolling(intervalMs = 5000) {
    this.stopPolling();
    this.get_companies();
    this._pollInterval = setInterval(() => {
      this.get_companies();
      this.refreshMap();
      this.loadMapToDOM(); // Force reload map every polling interval
    }, intervalMs);
  }

  stopPolling() {
    if (this._pollInterval) {
      clearInterval(this._pollInterval);
      this._pollInterval = null;
    }
  }

  ping() {
    const request_id = `ping_${Date.now()}_${Math.random()
      .toString(36)
      .substr(2, 9)}`;
    this.socket.send(JSON.stringify({ type: "ping", request_id: request_id }));
    return request_id;
  }

  onmessage(event) {
    const message = JSON.parse(event.data);

    if (message.type === "response" && message.request_id) {
      if (
        message.request_id.startsWith("check_session_") ||
        message.request_id.startsWith("join_session_") ||
        message.request_id.startsWith("get_session_")
      ) {
        this.handleSessionResponse(message);
      } else if (message.request_id.startsWith("get_companies_")) {
        this.handleCompaniesResponse(message);
      }
    } else if (message.type && message.type.startsWith("api-")) {
    } else if (message.type === "error") {
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
      if (callback) callback({ success: true, data: this.companies });
    } else {
      if (callback) callback({ success: false, error: "No companies data" });
    }
    if (callback) this.pendingCallbacks.delete(requestId);
    window.dispatchEvent(
      new CustomEvent("companies-updated", {
        detail: { companies: this.companies },
      })
    );
  }

  handleSessionResponse(message) {
    const requestId = message.request_id;
    const callback = this.pendingCallbacks.get(requestId);
    console.log("Session response:", message);
    console.log(message);
    if (message.data) {
      this.session_id = message.data.session_id;
      if (message.data.cells && message.data.map_size) {
        this.map = {
          cells: message.data.cells,
          size: message.data.map_size,
          pattern: message.data.map_pattern || "random",
        };

        this.loadMapToDOM();
        console.log("Session response loaded map");
      }

      if (requestId.startsWith("join_session_")) {
        if (callback) {
          callback({ success: true, data: message.data });
        }
      } else {
        if (callback) {
          callback({ success: true, data: message.data });
        }
      }
    } else {
      if (callback) {
        callback({ success: false, error: "Session not found" });
      }
    }

    if (callback) {
      this.pendingCallbacks.delete(requestId);
    }
  }

  getCellType(cellName) {
    const cellTypes = {
      mountain: 0,
      water: 1,
      forest: 2,
      field: 3,
      city: 4,
      bank: 5,
    };
    return cellTypes[cellName.toLowerCase()] !== undefined
      ? cellTypes[cellName.toLowerCase()]
      : 3;
  }

  loadMapToDOM() {
    console.log("called LOADMAPTODOM");
    if (!this.map || !this.map.cells) {
      if (typeof console.log === "function") {
        console.log("No map data available to load");
      }
      return false;
    }

    if (
      typeof window.setTile === "function" &&
      typeof window.TileTypes === "object"
    ) {
      const { cells, size } = this.map;

      if (typeof console.log === "function") {
        console.log(
          "Loading map into DOM with " +
            cells.length +
            " cells, size: " +
            size.rows +
            "x" +
            size.cols
        );
      }

      const mapElement = document.getElementById("map");
      if (mapElement && size.cols !== 7) {
        mapElement.style.gridTemplateColumns = `repeat(${size.cols}, 1fr)`;
        if (typeof console.log === "function") {
          console.log("Updated map grid to " + size.cols + " columns");
        }
      }

      for (let i = 0; i < cells.length && i < size.rows * size.cols; i++) {
        const row = Math.floor(i / size.cols);
        const col = i % size.cols;
        const cellType = this.getCellType(cells[i]);
        const terrainSymbol = this.getTerrainNames(cells[i]);
        window.setTile(row, col, cellType, terrainSymbol);
      }

      console.log("Map loaded successfully into DOM");
      return true;
    } else {
      setTimeout(() => this.loadMapToDOM(), 500);
      return false;
    }
  }

  getTerrainNames(cellName) {
    const symbols = {
      mountain: "ГОРЫ",
      water: "МОРЕ",
      forest: "ЛЕС",
      field: "ПОЛЯ",
      city: "ГОРОД",
      bank: "БАНК",
    };
    return symbols[cellName.toLowerCase()] || "?";
  }

  refreshMap() {
    this.get_session();
  }
}

export const SAMPLE_MESSAGES = {
  GET_SESSION: {
    type: "get-session",
    session_id: "session_abc123",
    request_id: "unique_request_id",
  },

  GET_USERS: {
    type: "get-users",
    session_id: "session_abc123",
    request_id: "unique_request_id",
  },

  GET_COMPANIES: {
    type: "get-companies",
    session_id: "session_abc123",
    request_id: "unique_request_id",
  },
};

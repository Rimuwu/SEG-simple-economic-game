/**
 * GameState class - Central store for all game data
 * Manages session, companies, users, map, factories, and exchange data
 */
import { reactive, computed } from 'vue';

export class GameState {
  constructor() {
    // Make the state reactive
    this.state = reactive({
      // Session data
      session: {
        id: null,
        stage: null,
        step: 0,
        max_steps: 0,
        cells: [],
        map_size: { rows: 7, cols: 7 },
        map_pattern: 'random'
      },

      // Companies data
      companies: [],

      // Users data
      users: [],

      // Factories data
      factories: [],

      // Exchange offers data
      exchanges: [],

      // Map data
      map: {
        cells: [],
        size: { rows: 7, cols: 7 },
        pattern: 'random',
        loaded: false
      },

      // Current user data
      currentUser: {
        id: null,
        username: null,
        company_id: null
      },

      // Time data
      timeToNextStage: null,

      // Winner data (for end game)
      winners: {
        capital: null,
        reputation: null,
        economic: null
      },

      // Connection status
      connected: false,
      connecting: false,

      // Error state
      lastError: null
    });
  }

  // ==================== SESSION METHODS ====================

  /**
   * Update session data
   * @param {Object} sessionData - Session data from server
   */
  updateSession(sessionData) {
    if (!sessionData) return;

    this.state.session.id = sessionData.session_id || this.state.session.id;
    this.state.session.stage = sessionData.stage || this.state.session.stage;
    this.state.session.step = sessionData.step ?? this.state.session.step;
    this.state.session.max_steps = sessionData.max_steps ?? this.state.session.max_steps;

    // Update map data if provided
    if (sessionData.cells) {
      this.state.session.cells = sessionData.cells;
      this.state.map.cells = sessionData.cells;
    }

    if (sessionData.map_size) {
      this.state.session.map_size = sessionData.map_size;
      this.state.map.size = sessionData.map_size;
    }

    if (sessionData.map_pattern) {
      this.state.session.map_pattern = sessionData.map_pattern;
      this.state.map.pattern = sessionData.map_pattern;
    }

    // Mark map as loaded if we have cells
    if (sessionData.cells && sessionData.map_size) {
      this.state.map.loaded = true;
    }

    console.log('[GameState] Session updated:', this.state.session);
  }

  /**
   * Clear session data (on disconnect or session leave)
   */
  clearSession() {
    this.state.session = {
      id: null,
      stage: null,
      step: 0,
      max_steps: 0,
      cells: [],
      map_size: { rows: 7, cols: 7 },
      map_pattern: 'random'
    };
    this.state.map.loaded = false;
    console.log('[GameState] Session cleared');
  }

  // ==================== COMPANY METHODS ====================

  /**
   * Update companies list
   * @param {Array} companies - Array of company objects
   */
  updateCompanies(companies) {
    if (!Array.isArray(companies)) {
      console.warn('[GameState] Invalid companies data:', companies);
      return;
    }
    this.state.companies = companies;
    console.log('[GameState] Companies updated:', companies.length);
  }

  /**
   * Get company by ID
   * @param {number} companyId
   * @returns {Object|null}
   */
  getCompanyById(companyId) {
    return this.state.companies.find(c => c.id === companyId) || null;
  }

  /**
   * Get companies by session
   * @param {string} sessionId
   * @returns {Array}
   */
  getCompaniesBySession(sessionId) {
    return this.state.companies.filter(c => c.session_id === sessionId);
  }

  // ==================== USER METHODS ====================

  /**
   * Update users list
   * @param {Array} users - Array of user objects
   */
  updateUsers(users) {
    if (!Array.isArray(users)) {
      console.warn('[GameState] Invalid users data:', users);
      return;
    }
    this.state.users = users;
    console.log('[GameState] Users updated:', users.length);
  }

  /**
   * Set current user
   * @param {Object} user - User object
   */
  setCurrentUser(user) {
    if (!user) return;
    this.state.currentUser = {
      id: user.id,
      username: user.username,
      company_id: user.company_id
    };
    console.log('[GameState] Current user set:', this.state.currentUser);
  }

  /**
   * Get user by ID
   * @param {number} userId
   * @returns {Object|null}
   */
  getUserById(userId) {
    return this.state.users.find(u => u.id === userId) || null;
  }

  // ==================== FACTORY METHODS ====================

  /**
   * Update factories list
   * @param {Array} factories - Array of factory objects
   */
  updateFactories(factories) {
    if (!Array.isArray(factories)) {
      console.warn('[GameState] Invalid factories data:', factories);
      return;
    }
    this.state.factories = factories;
    console.log('[GameState] Factories updated:', factories.length);
  }

  /**
   * Get factories by company
   * @param {number} companyId
   * @returns {Array}
   */
  getFactoriesByCompany(companyId) {
    return this.state.factories.filter(f => f.company_id === companyId);
  }

  // ==================== EXCHANGE METHODS ====================

  /**
   * Update exchange offers list
   * @param {Array} exchanges - Array of exchange offer objects
   */
  updateExchanges(exchanges) {
    if (!Array.isArray(exchanges)) {
      console.warn('[GameState] Invalid exchanges data:', exchanges);
      return;
    }
    this.state.exchanges = exchanges;
    console.log('[GameState] Exchanges updated:', exchanges.length);
  }

  /**
   * Get exchanges by session
   * @param {string} sessionId
   * @returns {Array}
   */
  getExchangesBySession(sessionId) {
    return this.state.exchanges.filter(e => e.session_id === sessionId);
  }

  /**
   * Get exchanges by company
   * @param {number} companyId
   * @returns {Array}
   */
  getExchangesByCompany(companyId) {
    return this.state.exchanges.filter(e => e.company_id === companyId);
  }

  // ==================== MAP METHODS ====================

  /**
   * Get cell type enum from cell name
   * @param {string} cellName
   * @returns {number}
   */
  getCellType(cellName) {
    const cellTypes = {
      mountain: 0,
      water: 1,
      forest: 2,
      field: 3,
      city: 4,
      bank: 5
    };
    return cellTypes[cellName.toLowerCase()] ?? 3;
  }

  /**
   * Get terrain display name
   * @param {string} cellName
   * @returns {string}
   */
  getTerrainName(cellName) {
    const names = {
      mountain: 'ГОРЫ',
      water: 'МОРЕ',
      forest: 'ЛЕС',
      field: 'ПОЛЯ',
      city: 'ГОРОД',
      bank: 'БАНК'
    };
    return names[cellName.toLowerCase()] || '?';
  }

  /**
   * Get map data for rendering
   * @returns {Object}
   */
  getMapData() {
    return {
      cells: this.state.map.cells,
      size: this.state.map.size,
      pattern: this.state.map.pattern,
      loaded: this.state.map.loaded
    };
  }

  // ==================== TIME METHODS ====================

  /**
   * Update time to next stage
   * @param {number} seconds
   */
  updateTimeToNextStage(seconds) {
    this.state.timeToNextStage = seconds;
  }

  /**
   * Get formatted time to next stage
   * @returns {string}
   */
  getFormattedTimeToNextStage() {
    if (this.state.timeToNextStage === null) return '--:--';
    const minutes = Math.floor(this.state.timeToNextStage / 60);
    const seconds = this.state.timeToNextStage % 60;
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }

  // ==================== WINNER METHODS ====================

  /**
   * Update winners data (for end game)
   * @param {Object} winnersData
   */
  updateWinners(winnersData) {
    if (!winnersData) return;
    this.state.winners = {
      capital: winnersData.capital || null,
      reputation: winnersData.reputation || null,
      economic: winnersData.economic || null
    };
    console.log('[GameState] Winners updated:', this.state.winners);
  }

  /**
   * Get winners data
   * @returns {Object}
   */
  getWinners() {
    return this.state.winners;
  }

  // ==================== CONNECTION METHODS ====================

  /**
   * Set connection status
   * @param {boolean} connected
   */
  setConnected(connected) {
    this.state.connected = connected;
    if (connected) {
      this.state.connecting = false;
    }
  }

  /**
   * Set connecting status
   * @param {boolean} connecting
   */
  setConnecting(connecting) {
    this.state.connecting = connecting;
  }

  /**
   * Set last error
   * @param {string|null} error
   */
  setError(error) {
    this.state.lastError = error;
    if (error) {
      console.error('[GameState] Error:', error);
    }
  }

  // ==================== COMPUTED PROPERTIES ====================

  /**
   * Check if session is active
   * @returns {boolean}
   */
  get isSessionActive() {
    return this.state.session.id !== null;
  }

  /**
   * Check if user has a company
   * @returns {boolean}
   */
  get hasCompany() {
    return this.state.currentUser && this.state.currentUser.company_id !== null && this.state.currentUser.company_id !== 0;
  }

  /**
   * Get current user's company
   * @returns {Object|null}
   */
  get currentCompany() {
    if (!this.hasCompany) return null;
    return this.getCompanyById(this.state.currentUser.company_id);
  }

  /**
   * Get session stage display name
   * @returns {string}
   */
  get stageDisplayName() {
    const stages = {
      FreeUserConnect: 'Подключение игроков',
      CellSelect: 'Выбор ячеек',
      Game: 'Игра',
      End: 'Конец игры'
    };
    return stages[this.state.session.stage] || this.state.session.stage || 'Неизвестно';
  }

  // ==================== UTILITY METHODS ====================

  /**
   * Reset all state
   */
  reset() {
    this.clearSession();
    this.state.companies = [];
    this.state.users = [];
    this.state.currentUser = {
      id: null,
      username: null,
      company_id: null
    };
    this.state.factories = [];
    this.state.exchanges = [];
    this.state.map = {
      cells: [],
      size: { rows: 7, cols: 7 },
      pattern: 'random',
      loaded: false
    };
    this.state.timeToNextStage = null;
    this.state.connected = false;
    this.state.connecting = false;
    this.state.lastError = null;
    console.log('[GameState] State reset');
  }

  /**
   * Get the reactive state (for use in Vue components)
   * @returns {Object}
   */
  getState() {
    return this.state;
  }

  /**
   * Export state as JSON
   * @returns {Object}
   */
  toJSON() {
    return JSON.parse(JSON.stringify(this.state));
  }

  /**
   * Log current state (for debugging)
   */
  logState() {
    console.log('[GameState] Current state:', this.toJSON());
  }
}

# DevTools Debug Console Commands

All these functions are available in your browser's DevTools console for debugging the game state.

## 📋 Quick Reference

Type `debugHelp()` in the console to see all available commands.

## 🎮 Available Commands

### State Access

#### `getGameState()`
Get a formatted overview of the current game state with a nice table display.

```javascript
getGameState()
// Outputs:
// 🎮 Current Game State:
// ┌─────────────┬────────────┐
// │ Session ID  │ AFRIKA     │
// │ Stage       │ Game       │
// │ Step        │ 3/15       │
// │ Connected   │ ✅         │
// │ Companies   │ 4          │
// │ Users       │ 8          │
// │ Factories   │ 12         │
// │ Exchanges   │ 5          │
// │ Map Loaded  │ ✅         │
// └─────────────┴────────────┘
// Returns: { session: {...}, companies: [...], ... }
```

#### `getGameStateJSON()`
Get the raw game state as JSON object (useful for copying/saving).

```javascript
const state = getGameStateJSON()
console.log(JSON.stringify(state, null, 2))
```

#### `logGameState()`
Log the entire game state to console using the GameState's built-in logger.

```javascript
logGameState()
// Outputs: [GameState] Current state: {...}
```

---

### 🎯 Specific Data Queries

#### `getSession()`
Get current session information.

```javascript
getSession()
// Returns:
// {
//   id: "AFRIKA",
//   stage: "Game",
//   step: 3,
//   max_steps: 15,
//   cells: ["city", "forest", ...],
//   map_size: { rows: 7, cols: 7 },
//   map_pattern: "random"
// }
```

#### `getCompanies()`
Get all companies with a formatted table view.

```javascript
getCompanies()
// Outputs table with columns: id, name, balance, reputation, cell_position, etc.
// Returns: Array of company objects
```

#### `getUsers()`
Get all users with a formatted table view.

```javascript
getUsers()
// Outputs table with columns: id, username, company_id, session_id
// Returns: Array of user objects
```

#### `getMap()`
Get map data including cells and dimensions.

```javascript
getMap()
// Outputs:
// 🗺️ Map Data: {
//   size: { rows: 7, cols: 7 },
//   cellCount: 49,
//   loaded: true,
//   pattern: "random"
// }
// Returns: { cells: [...], size: {...}, pattern: "...", loaded: true }
```

#### `getExchanges()`
Get all exchange offers with table view.

```javascript
getExchanges()
// Returns: Array of exchange offer objects
```

#### `getFactories()`
Get all factories with table view.

```javascript
getFactories()
// Returns: Array of factory objects
```

#### `getWinners()`
Get game winners (only available after game ends).

```javascript
getWinners()
// Outputs:
// 🏆 Winners: {
//   capital: { id: 1, name: "MegaCorp", balance: 15000 },
//   reputation: { id: 2, name: "GoodCorp", reputation: 950 },
//   economic: null
// }
```

#### `getCurrentUser()`
Get the current user's information.

```javascript
getCurrentUser()
// Outputs:
// 👤 Current User: {
//   id: 123,
//   username: "player1",
//   company_id: 5
// }
```

---

### 🔧 Actions

#### `refreshGameData()`
Manually trigger a refresh of all game data from the server.

```javascript
refreshGameData()
// Fetches: session, companies, users, exchanges, time, etc.
```

#### `refreshMap()`
Refresh the map display.

```javascript
refreshMap()
```

---

### 💡 Direct Access

You can also access the underlying objects directly:

#### `wsManager`
The WebSocketManager instance.

```javascript
// Access the manager
wsManager.socket.readyState  // Check WebSocket connection state

// Send custom messages
wsManager.ping()

// Get specific data
wsManager.get_companies((result) => {
  console.log('Companies:', result)
})

// Check polling status
wsManager._pollInterval  // null if not polling, interval ID if active
```

#### `wsManager.gameState`
The GameState instance.

```javascript
// Access GameState methods
wsManager.gameState.getCompanyById(1)
wsManager.gameState.isSessionActive
wsManager.gameState.hasCompany
wsManager.gameState.currentCompany
wsManager.gameState.stageDisplayName
```

#### `wsManager.state`
The reactive state object (Vue reactive).

```javascript
// Direct state access (reactive)
wsManager.state.session.id
wsManager.state.companies
wsManager.state.users
wsManager.state.map
wsManager.state.connected
wsManager.state.lastError
```

---

## 🔍 Usage Examples

### Check if connected to server
```javascript
wsManager.state.connected  // true/false
```

### Find a specific company
```javascript
const companies = getCompanies()
const myCompany = companies.find(c => c.name === "MegaCorp")
console.log(myCompany)
```

### Watch for stage changes
```javascript
// In console, check repeatedly
setInterval(() => {
  const session = getSession()
  console.log(`Stage: ${session.stage}, Step: ${session.step}/${session.max_steps}`)
}, 5000)
```

### Export state for bug report
```javascript
const state = getGameStateJSON()
copy(JSON.stringify(state, null, 2))
// Now paste into a text file or issue report
```

### Monitor connection status
```javascript
console.log('Connected:', wsManager.state.connected)
console.log('Connecting:', wsManager.state.connecting)
console.log('Last Error:', wsManager.state.lastError)
```

### Get detailed company info
```javascript
const companies = getCompanies()
companies.forEach(c => {
  console.log(`${c.name}: ${c.balance} credits, ${c.reputation} reputation`)
})
```

### Check time to next stage
```javascript
console.log('Time left:', wsManager.gameState.getFormattedTimeToNextStage())
console.log('Raw seconds:', wsManager.state.timeToNextStage)
```

---

## 🐛 Debugging Scenarios

### Game not updating?
```javascript
// Check connection
console.log('Connected:', wsManager.state.connected)

// Check if polling is active
console.log('Polling:', wsManager._pollInterval ? 'Active' : 'Stopped')

// Manually refresh
refreshGameData()
```

### Companies not showing?
```javascript
// Check companies data
const companies = getCompanies()
console.log('Company count:', companies.length)

// Check session
const session = getSession()
console.log('Session ID:', session.id)
```

### Map not loading?
```javascript
const map = getMap()
console.log('Map loaded:', map.loaded)
console.log('Cell count:', map.cells.length)

// Force map refresh
refreshMap()
```

### Winners not appearing?
```javascript
const session = getSession()
console.log('Stage:', session.stage)  // Should be "End"

const winners = getWinners()
console.log('Winners:', winners)
```

---

## 💻 Advanced Usage

### Monitor broadcasts
```javascript
// Listen to all broadcasts
window.addEventListener('ws-broadcast', (event) => {
  console.log('📡 Broadcast:', event.detail.type, event.detail.data)
})
```

### Watch specific state changes
```javascript
// Vue watchers in console (limited, but possible)
const state = wsManager.state
console.log('Watching companies...')
setInterval(() => {
  console.log('Company count:', state.companies.length)
}, 2000)
```

### Test WebSocket connection
```javascript
// Send ping
wsManager.ping()

// Check response in Network tab (WS filter)
```

### Get all pending callbacks
```javascript
console.log('Pending callbacks:', wsManager.pendingCallbacks.size)
wsManager.pendingCallbacks.forEach((cb, reqId) => {
  console.log('Request ID:', reqId)
})
```

---

## 🎨 Tips

1. **Use table view**: Functions like `getCompanies()` use `console.table()` for better visualization
2. **Chain calls**: `getCompanies().filter(c => c.balance > 1000)`
3. **Copy to clipboard**: Use `copy(getGameStateJSON())` in Chrome DevTools
4. **Type ahead**: Start typing `get` and DevTools will autocomplete
5. **Help anytime**: Type `debugHelp()` to see the command list

---

## 🚨 Common Issues

### `wsManager is not defined`
- The page might not be fully loaded yet
- Refresh the page and wait for "Game loaded!" message

### `Cannot read property 'gameState' of null`
- WebSocket might not be initialized
- Check `wsManager` exists: `typeof wsManager`

### Data seems outdated
- Polling might be stopped: `wsManager._pollInterval`
- Manually refresh: `refreshGameData()`

---

Happy debugging! 🎮✨

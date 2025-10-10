# Game Data Flow Documentation

This document explains how game data is fetched, stored, and updated in the web client.

## Architecture Overview

The web client uses a centralized state management approach:
- **GameState.js**: Reactive store for all game data (Vue reactive)
- **WebSocketManager (ws.js)**: Handles WebSocket communication and populates GameState
- **Vue Components**: Read from GameState, display data, send actions via WebSocketManager

## Data Categories

### 1. Session Data (Core)
**Fetched by**: `get_session()`  
**Updates**: `GameState.updateSession()`  
**Contains**:
- Session ID
- Current stage (FreeUserConnect, CellSelect, Game, ChangeTurn, End)
- Current step / max steps
- Map data (cells array, map_size, map_pattern)

**When fetched**:
- On session join
- Regular polling (every 5s)
- On `api-update_session_stage` broadcast

### 2. Time to Next Stage
**Fetched by**: `get_time_to_next_stage()`  
**Updates**: `GameState.updateTimeToNextStage()`  
**Contains**:
- Seconds remaining until next stage
- Current step/stage info

**When fetched**:
- Regular polling (every 5s)
- After joining session

### 3. Companies
**Fetched by**: `get_companies()`  
**Updates**: `GameState.updateCompanies()`  
**Contains** (per company):
- id, name, session_id
- balance, reputation, owner_id
- cell_position (e.g., "3.4")
- users array
- resources (inventory)
- improvements levels
- deposits (bank credits)

**When fetched**:
- Regular polling (every 5s)
- On company-related broadcasts:
  - `api-create_company`
  - `api-company_deleted`
  - `api-user_added_to_company`
  - `api-user_left_company`
  - `api-company_set_position`
  - `api-company_improvement_upgraded`
  - `api-exchange_trade_completed` (to update balances)

### 4. Users
**Fetched by**: `get_users()`  
**Updates**: `GameState.updateUsers()`  
**Contains** (per user):
- id, username
- company_id (0 if no company)
- session_id

**When fetched**:
- Regular polling (every 5s)
- On user-related broadcasts:
  - `api-create_user`
  - `api-update_user`
  - `api-user_deleted`

### 5. Factories
**Fetched by**: `get_factories(company_id)`  
**Updates**: `GameState.updateFactories()`  
**Contains** (per factory):
- id, company_id
- resource_type (what it produces)
- count (production amount)
- complectation status

**When fetched**:
- When user joins company
- When calling `fetchCurrentCompanyData()`
- On `api-factory-start-complectation` broadcast

### 6. Exchange Offers
**Fetched by**: `get_exchanges()`  
**Updates**: `GameState.updateExchanges()`  
**Contains** (per offer):
- id, session_id, company_id
- resource_type, amount, price
- status (active/completed/cancelled)

**When fetched**:
- Regular polling (every 5s)
- On exchange-related broadcasts:
  - `api-exchange_offer_created`
  - `api-exchange_offer_updated`
  - `api-exchange_offer_cancelled`
  - `api-exchange_trade_completed`

### 7. Company-Specific Data

#### Cell Info
**Fetched by**: `get_company_cell_info(company_id)`  
**Contains**:
- Cell type and properties
- Available resources on cell
- Cell-specific bonuses

**When fetched**:
- When calling `fetchCurrentCompanyData()`

#### Improvement Info
**Fetched by**: `get_company_improvement_info(company_id)`  
**Contains**:
- Detailed improvement levels and costs
- Upgrade requirements
- Effects of each improvement

**When fetched**:
- When calling `fetchCurrentCompanyData()`

### 8. Winners (End Game)
**Fetched via**: Broadcast message `api-game_ended`  
**Updates**: `GameState.updateWinners()`  
**Contains**:
- capital winner (company with most money)
- reputation winner (company with most reputation)
- economic winner (company with most economic power)

**When received**:
- Game end (stage changes to End)
- Broadcast: `api-game_ended`

## Data Fetching Workflows

### On Connection
```javascript
wsManager.connect()
// Just establishes WebSocket connection
```

### On Session Join
```javascript
wsManager.join_session(session_id)
// 1. Fetches session data (includes map)
// 2. Calls initializeSession()
```

### Initialize Session
```javascript
wsManager.initializeSession()
// 1. Fetches session + map
// 2. Loads map to DOM
// 3. Calls fetchAllGameData()
// 4. If user has company: calls fetchCurrentCompanyData()
// 5. Starts polling
```

### Fetch All Game Data (Core Loop)
```javascript
wsManager.fetchAllGameData()
// Called in polling loop every 5 seconds
// 1. get_session() - session state and map
// 2. get_time_to_next_stage() - countdown timer
// 3. get_companies() - all companies in session
// 4. get_users() - all users in session
// 5. get_exchanges() - all active offers
```

### Fetch Current Company Data
```javascript
wsManager.fetchCurrentCompanyData()
// Called when user joins a company
// 1. get_company(companyId) - detailed company info
// 2. get_factories(companyId) - company's factories
// 3. get_company_improvement_info(companyId) - improvement details
// 4. get_company_cell_info(companyId) - cell details
```

## Broadcast Messages

All broadcast messages trigger automatic data refetch:

| Broadcast Type | Triggered Refresh |
|----------------|-------------------|
| `api-create_company` | `get_companies()` |
| `api-company_deleted` | `get_companies()` |
| `api-user_added_to_company` | `get_companies()` |
| `api-user_left_company` | `get_companies()` |
| `api-company_set_position` | `get_companies()` |
| `api-company_improvement_upgraded` | `get_companies()` |
| `api-create_user` | `get_users()` |
| `api-update_user` | `get_users()` |
| `api-user_deleted` | `get_users()` |
| `api-update_session_stage` | `get_session()` + map reload |
| `api-session_deleted` | `leaveSession()` if current |
| `api-game_ended` | Updates winners + `get_session()` |
| `api-factory-start-complectation` | `get_factories()` |
| `api-exchange_offer_created` | `get_exchanges()` + `get_companies()` |
| `api-exchange_offer_updated` | `get_exchanges()` + `get_companies()` |
| `api-exchange_offer_cancelled` | `get_exchanges()` + `get_companies()` |
| `api-exchange_trade_completed` | `get_exchanges()` + `get_companies()` |

## Using GameState in Vue Components

### Access State
```javascript
import { wsManager } from '@/ws.js'

// In setup()
const gameState = wsManager.state

// Use in template
<div>{{ gameState.session.stage }}</div>
<div>{{ gameState.companies.length }} companies</div>
```

### Computed Properties
```javascript
const isGameActive = computed(() => {
  return gameState.session.stage === 'Game'
})

const myCompany = computed(() => {
  return wsManager.gameState.currentCompany
})
```

### Watch for Changes
```javascript
import { watch } from 'vue'

watch(() => gameState.session.stage, (newStage, oldStage) => {
  console.log(`Stage changed from ${oldStage} to ${newStage}`)
})
```

### Listen to Custom Events
```javascript
window.addEventListener('ws-broadcast', (event) => {
  const { type, data } = event.detail
  if (type === 'api-game_ended') {
    showWinnerModal(data.winners)
  }
})

window.addEventListener('companies-updated', (event) => {
  const { companies } = event.detail
  console.log('Companies updated:', companies)
})
```

## Data Not Fetched Automatically

Some data types are **not implemented** or are fetched on-demand only:

### Events
- **Status**: Not implemented in API
- **Future**: Would be fetched via `get-events` or included in session data

### Achievements
- **Status**: Not implemented in API
- **Future**: Would be fetched via `get-achievements` per user/company

### Contracts
- **Status**: Partially implemented (table exists, but no API endpoints)
- **Future**: Would be fetched via `get-contracts` per company

### Leaders/Leaderboard
- **Status**: Calculated from companies array
- **Implementation**: Use `gameState.companies` sorted by balance/reputation

## Best Practices

1. **Read from GameState**: Always read data from `wsManager.state` or `wsManager.gameState.state`
2. **Don't Mutate**: Never directly modify GameState - use WebSocketManager methods
3. **Use Computed**: Create computed properties for derived data
4. **Watch Carefully**: Use watchers for reactive updates, but avoid heavy operations
5. **Error Handling**: Check `gameState.lastError` for connection errors
6. **Loading States**: Check `gameState.connecting` and `gameState.connected`

## Example: Full Component Integration

```vue
<script setup>
import { computed, watch, onMounted } from 'vue'
import { wsManager } from '@/ws.js'

const gameState = wsManager.state

const currentStage = computed(() => gameState.session.stage)
const timeLeft = computed(() => wsManager.gameState.getFormattedTimeToNextStage())
const companies = computed(() => gameState.companies)

// Watch for stage changes
watch(currentStage, (newStage) => {
  if (newStage === 'End') {
    showWinners()
  }
})

function showWinners() {
  const winners = wsManager.gameState.getWinners()
  console.log('Winners:', winners)
}

onMounted(() => {
  // Data is already being fetched by polling
  // Just display it reactively
})
</script>

<template>
  <div>
    <h2>Stage: {{ currentStage }}</h2>
    <p>Time left: {{ timeLeft }}</p>
    <ul>
      <li v-for="company in companies" :key="company.id">
        {{ company.name }} - {{ company.balance }} credits
      </li>
    </ul>
  </div>
</template>
```

## Summary

- **Centralized State**: All data in GameState (reactive)
- **Automatic Updates**: Polling every 5s + broadcast-triggered refreshes
- **Separation of Concerns**: WebSocketManager handles network, GameState stores data, Components display
- **Reactive by Design**: Vue's reactive() ensures UI updates automatically
- **Comprehensive Coverage**: Session, companies, users, factories, exchanges, winners all tracked

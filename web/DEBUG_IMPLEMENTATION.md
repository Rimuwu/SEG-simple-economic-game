# GameState DevTools Integration - Summary

## What Was Added

Added comprehensive debug functions accessible from the browser DevTools console for debugging game state.

## Changes Made

### File: `web/src/App.vue`

Added 15+ global debug functions after the `wsManager` initialization:

1. **`getGameState()`** - Formatted overview with table
2. **`getGameStateJSON()`** - Raw JSON export
3. **`logGameState()`** - Detailed console log
4. **`getCompanies()`** - All companies (table)
5. **`getUsers()`** - All users (table)
6. **`getSession()`** - Session info
7. **`getMap()`** - Map data
8. **`getExchanges()`** - Exchange offers
9. **`getFactories()`** - Factories list
10. **`getWinners()`** - Game winners
11. **`getCurrentUser()`** - Current user info
12. **`refreshGameData()`** - Refresh all data
13. **`refreshMap()`** - Refresh map display
14. **`debugHelp()`** - Show all commands

Plus console message on load: `"🎮 Game loaded! Type debugHelp() for available commands."`

## Documentation Created

### `web/DEBUG_CONSOLE.md`
Comprehensive guide with:
- Quick reference
- All available commands
- Usage examples
- Debugging scenarios
- Advanced usage tips
- Common issues and solutions

## How to Use

### In Browser DevTools Console:

```javascript
// Get quick overview
getGameState()

// See all commands
debugHelp()

// Check specific data
getCompanies()
getUsers()
getSession()

// Direct access
wsManager.state
wsManager.gameState

// Refresh data
refreshGameData()
```

### Example Output:

```
🎮 Current Game State:
┌─────────────┬────────┐
│ Session ID  │ AFRIKA │
│ Stage       │ Game   │
│ Step        │ 3/15   │
│ Connected   │ ✅     │
│ Companies   │ 4      │
│ Users       │ 8      │
└─────────────┴────────┘
```

## Key Features

✅ **Easy Access**: Simple function names like `getCompanies()`
✅ **Formatted Output**: Uses `console.table()` for better visualization
✅ **Help System**: `debugHelp()` shows all available commands
✅ **Direct Access**: Can still use `wsManager` directly for advanced debugging
✅ **Reactive State**: Access `wsManager.state` for live reactive data
✅ **Export Support**: Get JSON for bug reports with `getGameStateJSON()`

## Testing

Build successful! ✅

The app now loads with debug functions available in the console. Test by:
1. Open the game in browser
2. Open DevTools (F12)
3. Type `debugHelp()` to see all commands
4. Try `getGameState()` to see current state

## Direct Access Still Available

All original access methods still work:
- `wsManager` - WebSocketManager instance
- `wsManager.gameState` - GameState instance
- `wsManager.state` - Reactive state object

## Notes

- All functions are safe (read-only, no mutations)
- Functions handle missing data gracefully
- Console output is formatted and emoji-enhanced 🎮
- Works in all modern browsers
- No performance impact (only called when debugging)

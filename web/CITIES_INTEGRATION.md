# Cities Integration Guide

This document describes the cities integration into the web frontend.

## Overview

Cities are now fully integrated into the WebSocket client and GameState management system. The implementation includes:

1. **GameState.js** - State management for cities data
2. **ws.js** - WebSocket methods for city operations
3. Automatic updates via broadcasts

---

## GameState.js Changes

### New State Property

```javascript
// Added to reactive state
cities: []
```

### New Methods

#### `updateCities(cities)`
Updates the cities list in state.
```javascript
this.gameState.updateCities(citiesArray);
```

#### `getCityById(cityId)`
Get a specific city by ID.
```javascript
const city = this.gameState.getCityById(1);
```

#### `getCitiesBySession(sessionId)`
Get all cities in a session.
```javascript
const cities = this.gameState.getCitiesBySession('AFRIKA');
```

#### `getCityByPosition(cellPosition)`
Get city at a specific cell position (format: "x.y").
```javascript
const city = this.gameState.getCityByPosition('3.4');
```

#### `getCitiesByBranch(branch)`
Get cities by branch type ('oil', 'metal', 'wood', 'cotton').
```javascript
const oilCities = this.gameState.getCitiesByBranch('oil');
```

#### `getCityDemand(cityId, resourceId)`
Get city's demand for a specific resource.
```javascript
const demand = this.gameState.getCityDemand(1, 'wood_planks');
// Returns: { amount: 200, price: 100 } or null
```

#### `cityHasDemand(cityId, resourceId)`
Check if city has demand for a resource.
```javascript
if (this.gameState.cityHasDemand(1, 'wood_planks')) {
  // City wants this resource
}
```

---

## ws.js Changes

### New Methods

#### `get_cities(callback)`
Fetch all cities in the current session.
```javascript
ws.get_cities((response) => {
  if (response.success) {
    console.log('Cities:', response.data);
  }
});
```

#### `get_city(cityId, callback)`
Fetch a specific city by ID.
```javascript
ws.get_city(1, (response) => {
  if (response.success) {
    console.log('City:', response.data);
  }
});
```

#### `get_city_demands(cityId, callback)`
Fetch current demands for a specific city.
```javascript
ws.get_city_demands(1, (response) => {
  if (response.success) {
    console.log('Demands:', response.data.demands);
    console.log('Branch:', response.data.branch);
  }
});
```

#### `sell_to_city(cityId, companyId, resourceId, amount, password, callback)`
Sell resources to a city.
```javascript
ws.sell_to_city(
  1,                  // cityId
  5,                  // companyId
  'wood_planks',      // resourceId
  50,                 // amount
  'password',         // password
  (response) => {
    if (response.success && response.data.success) {
      console.log('Trade successful!');
      console.log('Total price:', response.data.total_price);
      console.log('Remaining demand:', response.data.remaining_demand);
    }
  }
);
```

### Automatic Polling

Cities are automatically fetched as part of `fetchAllGameData()`, which is called during:
- Initial session connection (`initializeSession()`)
- Regular polling intervals (default: 5 seconds)

### Broadcast Handling

The WebSocket client automatically handles city-related broadcasts:

- **`api-city-create`** - Refreshes cities list
- **`api-city-delete`** - Refreshes cities list
- **`api-city-update-demands`** - Updates specific city or refreshes all
- **`api-city-trade`** - Refreshes cities and companies

---

## City Object Structure

```javascript
{
  id: 1,                        // Unique city ID
  session_id: "AFRIKA",         // Session the city belongs to
  cell_position: "3.4",         // Position on map (x.y)
  branch: "oil",                // Priority branch: oil, metal, wood, cotton
  name: "Золотогорск",         // City name
  demands: {                    // Current demands
    "wood_planks": {
      amount: 200,              // Units needed
      price: 100                // Price per unit
    },
    "fabric": {
      amount: 150,
      price: 250
    }
  }
}
```

---

## Usage Examples

### Example 1: Display Cities on Map

```javascript
// Get all cities for current session
const cities = gameState.getCitiesBySession(gameState.state.session.id);

cities.forEach(city => {
  const [x, y] = city.cell_position.split('.');
  // Render city on map at position (x, y)
  renderCityOnMap(x, y, city);
});
```

### Example 2: Show City Demands

```javascript
// Get city at a specific position
const city = gameState.getCityByPosition('3.4');

if (city && city.demands) {
  Object.entries(city.demands).forEach(([resourceId, demand]) => {
    console.log(`${resourceId}: ${demand.amount} units @ $${demand.price}`);
  });
}
```

### Example 3: Sell to City

```javascript
// Check if city wants a resource
const cityId = 1;
const resourceId = 'wood_planks';

if (gameState.cityHasDemand(cityId, resourceId)) {
  const demand = gameState.getCityDemand(cityId, resourceId);
  
  // Sell to city
  ws.sell_to_city(
    cityId,
    myCompanyId,
    resourceId,
    Math.min(myInventory[resourceId], demand.amount),
    myPassword,
    (response) => {
      if (response.success && response.data.success) {
        alert(`Sold! Earned $${response.data.total_price}`);
      } else {
        alert(`Error: ${response.error || 'Trade failed'}`);
      }
    }
  );
}
```

### Example 4: Listen for City Updates

```javascript
// Listen for city-related broadcasts
window.addEventListener('ws-broadcast', (event) => {
  const { type, data } = event.detail;
  
  switch(type) {
    case 'api-city-create':
      console.log('New city created:', data.city);
      break;
      
    case 'api-city-update-demands':
      console.log('City demands updated:', data);
      // Refresh city display
      break;
      
    case 'api-city-trade':
      console.log('Trade completed:', data);
      alert(`Trade: ${data.amount} ${data.resource_id} for $${data.total_price}`);
      break;
  }
});
```

### Example 5: Find Best City to Sell To

```javascript
function findBestCityForResource(resourceId) {
  const cities = gameState.state.cities;
  let bestCity = null;
  let bestPrice = 0;
  
  cities.forEach(city => {
    const demand = gameState.getCityDemand(city.id, resourceId);
    if (demand && demand.price > bestPrice) {
      bestPrice = demand.price;
      bestCity = city;
    }
  });
  
  return { city: bestCity, price: bestPrice };
}

// Usage
const { city, price } = findBestCityForResource('wood_planks');
if (city) {
  console.log(`Best price: $${price} at ${city.name} (${city.cell_position})`);
}
```

---

## Integration Checklist

- [x] Add cities array to GameState
- [x] Add city update methods to GameState
- [x] Add get_cities() method to WebSocket
- [x] Add get_city() method to WebSocket
- [x] Add get_city_demands() method to WebSocket
- [x] Add sell_to_city() method to WebSocket
- [x] Add response handlers for city methods
- [x] Add broadcast handlers for city events
- [x] Include cities in fetchAllGameData()
- [x] Include cities in session response handling
- [x] Add cities to reset() method

---

## Next Steps for UI Implementation

1. **Map Integration**: Display city markers on the game map
2. **City Panel**: Create UI component showing city details and demands
3. **Trade Interface**: Build form for selling resources to cities
4. **City List**: Display all cities with their branches and demands
5. **Notifications**: Show alerts when city demands update
6. **Best Price Indicator**: Highlight cities offering best prices

---

## API Documentation Reference

For complete API documentation, see:
- Backend: `api/routers/ws_city.py`
- Game Logic: `api/game/citie.py`
- Session Integration: `api/game/session.py` (cities property and to_dict method)

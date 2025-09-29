# WebSocket API Documentation

This document lists all WebSocket message types and their data structures for the SEG (Simple Economic Game) application.

## Connection
- **Endpoint**: `ws://localhost:8000/ws/connect?client_id={client_id}`
- **Status endpoint**: `http://localhost:8000/ws/status`

## Message Format
All messages follow this JSON structure:
```json
{
  "type": "message_type",
  "request_id": "unique_id", // Optional, for responses
  "data": { ... }, // Message-specific data
  "timestamp": 1234567890, // Optional
  "content": "...", // Optional
  // ... other message-specific fields
}
```

---

## User Messages

### `get-users`
**Description**: Get list of users  
**Arguments**: `company_id: Optional[int], session_id: Optional[str], request_id: str`  
**Returns**: Array of User objects  

**User Object Structure**:
```json
{
  "id": 123,
  "username": "player_name",
  "company_id": 456,
  "session_id": "session_abc123"
}
```

### `get-user`
**Description**: Get single user  
**Arguments**: `id: Optional[int], username: Optional[str], company_id: Optional[int], session_id: Optional[str], request_id: str`  
**Returns**: User object (see structure above)

### `create-user`
**Description**: Create a new user  
**Arguments**: `user_id: int, username: str, password: str, session_id: str, request_id: str`  
**Returns**: 
```json
{
  "session_id": "session_abc123",
  "user": {
    "id": 123,
    "username": "player_name",
    "company_id": 0,
    "session_id": "session_abc123"
  }
}
```
**Broadcasts**: `api-create_user`

### `update-user`
**Description**: Update user information  
**Arguments**: `user_id: int, username: Optional[str], company_id: Optional[int], password: str`  
**Returns**:
```json
{
  "session_id": "session_abc123",
  "new": { /* User object */ },
  "old": { /* User object */ }
}
```
**Broadcasts**: `api-update_user`

### `delete-user`
**Description**: Delete a user  
**Arguments**: `user_id: int, password: str`  
**Returns**: Success/error status  
**Broadcasts**: `api-user_deleted`

---

## Company Messages

### `get-companies`
**Description**: Get list of companies  
**Arguments**: `session_id: Optional[int], in_prison: Optional[bool], cell_position: Optional[str], request_id: str`  
**Returns**: Array of Company objects

**Company Object Structure**:
```json
{
  "id": 456,
  "name": "Company Name",
  "reputation": 50,
  "balance": 1000,
  "in_prison": false,
  "credits": [],
  "deposits": [],
  "improvements": {
    "warehouse": "level1",
    "contracts": "level0",
    "mountain": { "station": "level0", "factory": "level0" },
    "forest": { "station": "level0", "factory": "level0" },
    "water": { "station": "level0", "factory": "level0" },
    "field": { "station": "level0", "factory": "level0" }
  },
  "warehouses": {},
  "session_id": "session_abc123",
  "cell_position": "3.4",
  "tax_debt": 0,
  "overdue_steps": 0,
  "secret_code": 123456,
  "last_turn_income": 0,
  "this_turn_income": 0,
  "business_type": "small"
}
```

### `get-company`
**Description**: Get single company  
**Arguments**: `id: Optional[int], name: Optional[str], reputation: Optional[int], balance: Optional[int], in_prison: Optional[bool], session_id: Optional[str], cell_position: Optional[str], request_id: str`  
**Returns**: Company object (see structure above)

### `create-company`
**Description**: Create a new company  
**Arguments**: `name: str, who_create: int, password: str, request_id: str`  
**Returns**:
```json
{
  "session_id": "session_abc123",
  "company": { /* Company object */ }
}
```
**Broadcasts**: `api-create_company`

### `update-company-add-user`
**Description**: Add user to company  
**Arguments**: `user_id: int, secret_code: int, password: str`  
**Returns**: Success/error status  
**Broadcasts**: `api-user_added_to_company`

### `set-company-position`
**Description**: Set company position on map  
**Arguments**: `company_id: int, x: int, y: int, password: str, request_id: str`  
**Returns**:
```json
{
  "result": true,
  "position_now": "3.4"
}
```
**Broadcasts**: `api-company_set_position`

### `update-company-left-user`
**Description**: Remove user from company  
**Arguments**: `user_id: int, company_id: str, password: str`  
**Returns**: Success/error status  
**Broadcasts**: `api-user_left_company`

### `delete-company`
**Description**: Delete a company  
**Arguments**: `company_id: str, password: str`  
**Returns**: Success/error status  
**Broadcasts**: `api-company_deleted`

### `get-company-cell-info`
**Description**: Get information about company's cell  
**Arguments**: `company_id: int, request_id: str`  
**Returns**:
```json
{
  "data": {
    "id": "mountain",
    "label": "Mountain",
    "resource_id": "stone", 
    "max_amount": 3,
    "pickable": true,
    "locations": []
  },
  "type": "CellType"
}
```

### `get-company-improvement-info`
**Description**: Get company improvement information  
**Arguments**: `company_id: int, request_id: str`  
**Returns**: Company improvements object

### `update-company-improve`
**Description**: Upgrade company improvement  
**Arguments**: `company_id: str, improvement_type: str, password: str`  
**Returns**: Success/error status  
**Broadcasts**: `api-company_improvement_upgraded`

### `company-take-credit`
**Description**: Take credit for company  
**Arguments**: `company_id: str, amount: int, period: int, password: str`  
**Returns**: Success/error status  
**Broadcasts**: `api-company_credit_taken`

### `company-pay-credit`
**Description**: Pay credit for company  
**Arguments**: `company_id: str, credit_index: int, amount: int, password: str`  
**Returns**: Success/error status  
**Broadcasts**: `api-company_credit_paid`

### `company-pay-taxes`
**Description**: Pay taxes for company  
**Arguments**: `company_id: str, amount: int, password: str`  
**Returns**: Success/error status  
**Broadcasts**: `api-company_tax_paid`

---

## Session Messages

### `get-sessions`
**Description**: Get list of sessions  
**Arguments**: `stage: Optional[str], request_id: str`  
**Returns**: Array of Session objects

**Session Object Structure**:
```json
{
  "session_id": "session_abc123",
  "cells": ["mountain", "forest", "water", "field"],
  "map_size": { "rows": 7, "cols": 7 },
  "map_pattern": "random",
  "cell_counts": {},
  "stage": "FreeUserConnect",
  "step": 1,
  "max_steps": 15
}
```

### `get-session`
**Description**: Get single session  
**Arguments**: `session_id: Optional[str], stage: Optional[str], request_id: str`  
**Returns**: Session object (see structure above)

### `create-session`
**Description**: Create a new session  
**Arguments**: `session_id: Optional[str], password: str, request_id: str`  
**Returns**:
```json
{
  "session": { /* Session object */ }
}
```

### `update-session-stage`
**Description**: Update session stage  
**Arguments**: `session_id: Optional[str], stage: Literal['FreeUserConnect', 'CellSelect', 'Game', 'End'], password: str`  
**Returns**: Success/error status  
**Broadcasts**: `api-update_session_stage`

### `get-sessions-free-cells`
**Description**: Get free cells in session  
**Arguments**: `session_id: str, request_id: str`  
**Returns**:
```json
{
  "free_cells": ["1.1", "2.3", "4.5"]
}
```

### `delete-session`
**Description**: Delete a session (WARNING: deletes all related users and companies)  
**Arguments**: `session_id: str, password: str, really: bool`  
**Returns**: Success/error status  
**Broadcasts**: `api-session_deleted`

---

## General Messages

### `ping`
**Description**: Ping server  
**Arguments**: `timestamp: str, content: Any`  
**Returns**: Pong message with timestamp and client_id

---

## Broadcast Messages (Server -> Client)

These messages are automatically sent to all connected clients when certain events occur:

### `api-create_user`
```json
{
  "type": "api-create_user",
  "data": {
    "session_id": "session_abc123",
    "user": { /* User object */ }
  }
}
```

### `api-update_user`
```json
{
  "type": "api-update_user", 
  "data": {
    "session_id": "session_abc123",
    "new": { /* User object */ },
    "old": { /* User object */ }
  }
}
```

### `api-user_deleted`
```json
{
  "type": "api-user_deleted",
  "data": {
    "user_id": 123
  }
}
```

### `api-user_left_company`
```json
{
  "type": "api-user_left_company",
  "data": {
    "user_id": 123,
    "company_id": 456
  }
}
```

### `api-create_company`
```json
{
  "type": "api-create_company",
  "data": {
    "session_id": "session_abc123",
    "company": { /* Company object */ }
  }
}
```

### `api-user_added_to_company`
```json
{
  "type": "api-user_added_to_company",
  "data": {
    "company_id": 456,
    "user_id": 123
  }
}
```

### `api-company_set_position`
```json
{
  "type": "api-company_set_position",
  "data": {
    "company_id": 456,
    "old_position": "2.3",
    "new_position": "3.4"
  }
}
```

### `api-company_deleted`
```json
{
  "type": "api-company_deleted",
  "data": {
    "company_id": 456
  }
}
```

### `api-company_improvement_upgraded`
```json
{
  "type": "api-company_improvement_upgraded",
  "data": {
    "company_id": 456,
    "improvement_type": "warehouse",
    "new_level": "level2"
  }
}
```

### `api-company_credit_taken`
```json
{
  "type": "api-company_credit_taken",
  "data": {
    "company_id": 456,
    "amount": 1000,
    "period": 5,
    "credit_id": 1
  }
}
```

### `api-company_credit_paid`
```json
{
  "type": "api-company_credit_paid",
  "data": {
    "company_id": 456,
    "credit_index": 0,
    "amount": 200
  }
}
```

### `api-company_credit_removed`
```json
{
  "type": "api-company_credit_removed",
  "data": {
    "company_id": 456,
    "credit_index": 0
  }
}
```

### `api-company_tax_paid`
Broadcasted when company pays taxes.

### `api-company_resource_added`
```json
{
  "type": "api-company_resource_added",
  "data": {
    "company_id": 456,
    "resource": "stone",
    "amount": 5
  }
}
```

### `api-company_resource_removed`
```json
{
  "type": "api-company_resource_removed",
  "data": {
    "company_id": 456,
    "resource": "stone",
    "amount": 3
  }
}
```

### `api-company_balance_changed`
```json
{
  "type": "api-company_balance_changed",
  "data": {
    "company_id": 456,
    "old_balance": 1000,
    "new_balance": 1200,
    "change": 200
  }
}
```

### `api-company_reputation_changed`
```json
{
  "type": "api-company_reputation_changed",
  "data": {
    "company_id": 456,
    "old_reputation": 50,
    "new_reputation": 55,
    "change": 5
  }
}
```

### `api-company_to_prison`
```json
{
  "type": "api-company_to_prison",
  "data": {
    "company_id": 456
  }
}
```

### `api-update_session_stage`
```json
{
  "type": "api-update_session_stage",
  "data": {
    "session_id": "session_abc123",
    "new_stage": "Game",
    "old_stage": "CellSelect"
  }
}
```

### `api-session_deleted`
```json
{
  "type": "api-session_deleted",
  "data": {
    "session_id": "session_abc123"
  }
}
```

---

## Error Handling

Error messages follow this format:
```json
{
  "type": "error",
  "message": "Error description",
  "available_types": ["list", "of", "available", "message", "types"]
}
```

## Response Format

Responses to requests with `request_id` follow this format:
```json
{
  "type": "response",
  "request_id": "your_request_id",
  "data": { /* Response data */ }
}
```

---

## Session Stages
- `FreeUserConnect`: Users can connect and join
- `CellSelect`: Companies select their positions on the map  
- `Game`: Active gameplay stage
- `End`: Game finished

## Business Types
- `small`: Small business
- `big`: Big business

## Improvement Types
- `warehouse`: Storage capacity
- `contracts`: Contract capacity  
- `mountain`: Mountain resource (station/factory)
- `forest`: Forest resource (station/factory)
- `water`: Water resource (station/factory)
- `field`: Field resource (station/factory)

## Cell Types
Common cell types include:
- `mountain`: Stone resource
- `forest`: Wood resource  
- `water`: Fish resource
- `field`: Grain resource
- `city`: Urban area
- `prison`: Restricted area

## Authentication
Most write operations require a `password` field for authentication.

## Notes
- There's an inconsistency in the source code where `session_id` in `get-users` is annotated as `Optional[int]` but should be `Optional[str]` based on the Session model
- All broadcast messages are sent automatically to all connected clients when the corresponding events occur
- Error responses always include an `error` field with a descriptive message
- The `change` field in balance/reputation change broadcasts represents the amount of change (positive for increase, negative for decrease)
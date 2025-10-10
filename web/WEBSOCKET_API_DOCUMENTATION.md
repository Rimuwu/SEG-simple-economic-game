# WebSocket API Documentation# WebSocket API Documentation# WebSocket API Documentation



This document provides comprehensive documentation for all WebSocket message types and their data structures for the SEG (Simple Economic Game) application.



## ConnectionThis document provides comprehensive documentation for all WebSocket message types and their data structures for the SEG (Simple Economic Game) application.This document lists all WebSocket message types and their data structures for the SEG (Simple Economic Game) application.

- **WebSocket Endpoint**: `ws://localhost:8000/ws/connect?client_id={client_id}`

- **Status Endpoint**: `GET http://localhost:8000/ws/status`

  - Returns list of available message types with their arguments and broadcast messages

## Connection## Connection

## Message Format

All messages follow this JSON structure:- **WebSocket Endpoint**: `ws://localhost:8000/ws/connect?client_id={client_id}`- **WebSocket Endpoint**: `ws://localhost:8000/ws/connect?client_id={client_id}`

```json

{- **Status Endpoint**: `GET http://localhost:8000/ws/status`- **Status Endpoint**: `GET http://localhost:8000/ws/status` (Returns available message types and connection info)

  "type": "message_type",

  "request_id": "unique_id",  - Returns list of available message types with their arguments and broadcast messages

  "password": "auth_password",

  "data": {},## Message Format

  ...

}## Message FormatAll messages follow this JSON structure:

```

All messages follow this JSON structure:```json

## Authentication

Most write operations (create, update, delete) require a `password` field for authentication.```json{



---{  "type": "message_type",



## Table of Contents  "type": "message_type",  "request_id": "unique_id", // Optional, for request-response pattern

- [General Messages](#general-messages)

- [User Messages](#user-messages)  "request_id": "unique_id",  "data": { ... }, // Message-specific data

- [Company Messages](#company-messages)

- [Session Messages](#session-messages)  "password": "auth_password",  "timestamp": 1234567890, // Optional

- [Factory Messages](#factory-messages)

- [Exchange (Market) Messages](#exchange-market-messages)  "data": {},  "content": "...", // Optional

- [Broadcast Messages](#broadcast-messages)

- [Error Handling](#error-handling)  ...  "password": "...", // Required for most write operations

- [Usage Examples](#usage-examples)

}  // ... other message-specific fields

---

```}

## General Messages

```

### `ping`

Test connection and server responsiveness.## Authentication



**Arguments**:Most write operations (create, update, delete) require a `password` field for authentication.## Authentication

- `timestamp: str` (optional)

- `content: Any` (optional)Most write operations (create, update, delete) require a `password` field for authentication. The password is validated using the `check_password` function.



**Response**: Sends `pong` message directly to the requesting client (not a standard response format)---

```json

{---

  "type": "pong",

  "timestamp": "...",## Table of Contents

  "client_id": "your-client-id",

  "content": "Pong!"- [General Messages](#general-messages)## General Messages

}

```- [User Messages](#user-messages)



---- [Company Messages](#company-messages)### `ping`



## User Messages- [Session Messages](#session-messages)**Description**: Ping message to test connection  



### `get-users`- [Factory Messages](#factory-messages)**Arguments**: 

Get list of users filtered by optional criteria.

- [Exchange (Market) Messages](#exchange-market-messages)- `timestamp: str` (optional)

**Arguments**:

- `company_id: Optional[int]`- [Broadcast Messages](#broadcast-messages)- `content: Any` (optional)

- `session_id: Optional[int]` ⚠️ **Note**: Should be `str` but annotated as `int` in code

- `request_id: str`- [Error Handling](#error-handling)



**Returns**: Array of User objects- [Usage Examples](#usage-examples)**Response**: Sends back a `pong` message to the client



**User Object Structure**:```json

```json

{---{

  "id": 123,

  "username": "player_name",  "type": "pong",

  "company_id": 456,

  "session_id": "session_abc123"## General Messages  "timestamp": "...",

}

```  "client_id": "...",



### `get-user`### `ping`  "content": "Pong!"

Get single user by various filters.

Test connection and server responsiveness.}

**Arguments**:

- `id: Optional[int]````

- `username: Optional[str]`

- `company_id: Optional[int]`**Arguments**:

- `session_id: Optional[str]`

- `request_id: str`- `timestamp: str` (optional)---



**Returns**: User object or null- `content: Any` (optional)



### `create-user`## User Messages

Create a new user.

**Response**: Sends `pong` message directly to the requesting client (not a standard response format)

**Arguments**:

- `user_id: int` (required)```json### `get-users`

- `username: str` (required)

- `password: str` (required){**Description**: Get list of users filtered by optional criteria  

- `session_id: str` (required)

- `request_id: str`  "type": "pong",**Arguments**: 



**Returns**:  "timestamp": "...",- `company_id: Optional[int]`

```json

{  "client_id": "your-client-id",- `session_id: Optional[str]`

  "session_id": "session_abc123",

  "user": {  "content": "Pong!"- `request_id: str`

    "id": 123,

    "username": "player_name",}

    "company_id": 0,

    "session_id": "session_abc123"```**Returns**: Array of User objects

  }

}

```

---**Example Request**:

**Broadcasts**: `api-create_user`

```json

**Note**: Does NOT broadcast automatically. Broadcast is triggered in `User.create()` method.

## User Messages{

### `update-user`

Update user information.  "type": "get-users",



**Arguments**:### `get-users`  "session_id": "AFRIKA",

- `user_id: int` (required)

- `username: Optional[str]`Get list of users filtered by optional criteria.  "request_id": "req123"

- `company_id: Optional[int]`

- `password: str` (required)}



**Returns**:**Arguments**:```

```json

{- `company_id: Optional[int]`

  "session_id": "session_abc123",

  "new": { /* Updated User object */ },- `session_id: Optional[str]`**User Object Structure**:

  "old": { /* Previous User object */ }

}- `request_id: str````json

```

{

**Broadcasts**: `api-update_user` to all clients with the update data

**Returns**: Array of User objects  "id": 123,

### `delete-user`

Delete a user.  "username": "player_name",



**Arguments**:**User Object Structure**:  "company_id": 456,

- `user_id: int` (required)

- `password: str` (required)```json  "session_id": "session_abc123"



**Returns**: Success or error{}



**Broadcasts**: `api-user_deleted`  "id": 123,```



**Note**: Does NOT return success message explicitly. Returns nothing on success or error object.  "username": "player_name",



---  "company_id": 456,### `get-user`



## Company Messages  "session_id": "session_abc123"**Description**: Get single user by various filters  



### `get-companies`}**Arguments**: 

Get list of companies filtered by optional criteria.

```- `id: Optional[int]`

**Arguments**:

- `session_id: Optional[int]` ⚠️ **Note**: Should be `str` but annotated as `int` in code- `username: Optional[str]`

- `in_prison: Optional[bool]`

- `cell_position: Optional[str]`### `get-user`- `company_id: Optional[int]`

- `request_id: str`

Get single user by various filters.- `session_id: Optional[str]`

**Returns**: Array of Company objects

- `request_id: str`

**Company Object Structure**:

```json**Arguments**:

{

  "id": 456,- `id: Optional[int]`**Returns**: User object or null if not found

  "name": "Company Name",

  "reputation": 50,- `username: Optional[str]`

  "balance": 1000,

  "in_prison": false,- `company_id: Optional[int]`### `create-user`

  "cell_position": "0:0",

  "session_id": "session_abc123",- `session_id: Optional[str]`**Description**: Create a new user  

  "credits": [],

  "deposits": [],- `request_id: str`**Arguments**: 

  "inventory": {},

  "owner_id": 123,- `user_id: int` - Unique user ID

  "tax_debt": 0,

  "overdue_steps": 0,**Returns**: User object or null- `username: str` - Username

  "secret_code": 123456

}- `password: str` - Authentication password (required)

```

### `create-user`- `session_id: str` - Session to join

### `get-company`

Get single company by various filters.Create a new user.- `request_id: str`



**Arguments**:

- `id: Optional[int]`

- `name: Optional[str]`**Arguments**:**Returns**: 

- `reputation: Optional[int]`

- `balance: Optional[int]`- `user_id: int` (required)```json

- `in_prison: Optional[bool]`

- `session_id: Optional[str]`- `username: str` (required){

- `cell_position: Optional[str]`

- `request_id: str`- `password: str` (required)  "session_id": "session_abc123",



**Returns**: Company object (as dict)- `session_id: str` (required)  "user": {



### `create-company`- `request_id: str`    "id": 123,

Create a new company.

    "username": "player_name",

**Arguments**:

- `name: str` (required)**Returns**:    "company_id": 0,

- `who_create: int` (required) - User ID of creator

- `password: str` (required)```json    "session_id": "session_abc123"

- `request_id: str`

{  }

**Returns**:

```json  "session_id": "session_abc123",}

{

  "session_id": "session_abc123",  "user": {```

  "company": { /* Company object */ }

}    "id": 123,

```

    "username": "player_name",**Broadcasts**: `api-create_user` to all clients

**Broadcasts**: `api-create_company`

    "company_id": 0,

**Note**: Broadcast is triggered in `Company.create()` method, not in the handler.

    "session_id": "session_abc123"**Error Response**:

### `update-company-add-user`

Add user to company using secret code.  }```json



**Arguments**:}{

- `user_id: int` (required)

- `secret_code: int` (required)```  "error": "Error message description"

- `password: str` (required)

}

**Returns**: Nothing on success, or error object

**Broadcasts**: `api-create_user````

**Broadcasts**: `api-user_added_to_company`



**Note**: Broadcast is triggered in `User.add_to_company()` method.

### `update-user`### `update-user`

### `set-company-position`

Set company position on the game map.Update user information.**Description**: Update user information  



**Arguments**:**Arguments**: 

- `company_id: int` (required)

- `x: int` (required)**Arguments**:- `user_id: int` (required)

- `y: int` (required)

- `password: str` (required)- `user_id: int` (required)- `username: Optional[str]` - New username

- `request_id: str`

- `username: Optional[str]`- `company_id: Optional[int]` - New company ID

**Returns**:

```json- `company_id: Optional[int]`- `password: str` (required)

{

  "result": true,- `password: str` (required)

  "position_now": "x:y"

}**Returns**:

```

**Returns**:```json

**Broadcasts**: `api-company_set_position`

```json{

**Note**: Broadcast is triggered in `Company.set_position()` method.

{  "session_id": "session_abc123",

### `update-company-left-user`

Remove user from company.  "session_id": "session_abc123",  "new": { /* Updated User object */ },



**Arguments**:  "new": { /* Updated User object */ },  "old": { /* Previous User object */ }

- `user_id: int` (required)

- `company_id: int` (required)  "old": { /* Previous User object */ }}

- `password: str` (required)

}```

**Returns**: Nothing on success, or error object

```

**Broadcasts**: `api-user_left_company`

**Broadcasts**: `api-update_user` to all clients with the update data

**Note**: Broadcast is triggered in `User.leave_from_company()` method.

**Broadcasts**: `api-update_user`

### `delete-company`

Delete a company.### `delete-user`



**Arguments**:### `delete-user`**Description**: Delete a user  

- `company_id: int` (required)

- `password: str` (required)Delete a user.**Arguments**: 



**Returns**: Nothing on success, or error object- `user_id: int` (required)



**Broadcasts**: `api-company_deleted`**Arguments**:- `password: str` (required)



**Note**: Broadcast is triggered in `Company.delete()` method.- `user_id: int` (required)



### `get-company-cell-info`- `password: str` (required)**Returns**: Success or error message

Get information about the cell where company is located.



**Arguments**:

- `company_id: int` (required)**Returns**: Success or error**Broadcasts**: `api-user_deleted` to all clients

- `request_id: str`



**Returns**:

```json**Broadcasts**: `api-user_deleted`---

{

  "data": { /* Cell info object */ },

  "type": "cell_type"

}---## Company Messages

```



Or `null` if company has no position set.

## Company Messages### `get-companies`

### `get-company-improvement-info`

Get company's improvement information.**Description**: Get list of companies filtered by optional criteria  



**Arguments**:### `get-companies`**Arguments**: 

- `company_id: int` (required)

- `request_id: str`Get list of companies filtered by optional criteria.- `session_id: Optional[str]`



**Returns**: Improvement data object- `in_prison: Optional[bool]`



### `update-company-improve`**Arguments**:- `cell_position: Optional[str]`

Upgrade a company improvement.

- `session_id: Optional[str]`- `request_id: str`

**Arguments**:

- `company_id: int` (required)- `in_prison: Optional[bool]`

- `improvement_type: str` (required)

- `password: str` (required)- `cell_position: Optional[str]`**Returns**: Array of Company objects



**Returns**: Nothing on success, or error object- `request_id: str`



**Broadcasts**: `api-company_improvement_upgraded`**Company Object Structure**:



**Note**: Broadcast is triggered in `Company.improve()` method.**Returns**: Array of Company objects```json



### `company-take-credit`{

Company takes a credit from bank.

**Company Object Structure**:  "id": 456,

**Arguments**:

- `company_id: int` (required)```json  "name": "Company Name",

- `amount: int` (required)

- `period: int` (required) - Credit period in turns{  "reputation": 50,

- `password: str` (required)

- `request_id: str`  "id": 456,  "balance": 1000,



**Returns**: Credit data object  "name": "Company Name",  "in_prison": false,



**Broadcasts**: `api-company_credit_taken`  "reputation": 50,  "cell_position": "0:0",



**Note**: Broadcast is triggered in `Company.take_credit()` method.  "balance": 1000,  "session_id": "session_abc123",



### `company-pay-credit`  "in_prison": false,  "credits": [],

Pay off company credit.

  "cell_position": "0:0",  "deposits": [],

**Arguments**:

- `company_id: int` (required)  "session_id": "session_abc123",  "inventory": {},

- `credit_index: int` (required)

- `amount: int` (required)  "credits": [],  "owner_id": 123

- `password: str` (required)

  "deposits": [],  "improvements": {

**Returns**: Nothing on success, or error object

  "inventory": {},    "warehouse": "level1",

**Broadcasts**: `api-company_credit_paid`

  "owner_id": 123,    "contracts": "level0",

**Note**: Broadcast is triggered in `Company.pay_credit()` method.

  "tax_debt": 0,    "mountain": { "station": "level0", "factory": "level0" },

### `company-take-deposit`

Company creates a deposit in bank.  "overdue_steps": 0,    "forest": { "station": "level0", "factory": "level0" },



**Arguments**:  "secret_code": 123456    "water": { "station": "level0", "factory": "level0" },

- `company_id: int` (required)

- `amount: int` (required)}    "field": { "station": "level0", "factory": "level0" }

- `period: int` (required) - Deposit period in turns

- `password: str` (required)```  },

- `request_id: str`

  "warehouses": {},

**Returns**: Deposit data object

### `get-company`  "session_id": "session_abc123",

**Broadcasts**: `api-company_deposit_taken`

Get single company by various filters.  "cell_position": "3.4",

**Note**: Broadcast is triggered in `Company.take_deposit()` method.

  "tax_debt": 0,

### `company-withdraw-deposit`

Withdraw company deposit.**Arguments**:  "overdue_steps": 0,



**Arguments**:- `id: Optional[int]`  "secret_code": 123456,

- `company_id: int` (required)

- `deposit_index: int` (required)- `name: Optional[str]`  "last_turn_income": 0,

- `password: str` (required)

- `reputation: Optional[int]`  "this_turn_income": 0,

**Returns**: `{"success": True}` on success, or error object

- `balance: Optional[int]`  "business_type": "small"

**Broadcasts**: `api-company_deposit_withdrawn`

- `in_prison: Optional[bool]`}

**Note**: Broadcast is triggered in `Company.withdraw_deposit()` method.

- `session_id: Optional[str]````

### `company-pay-taxes`

Pay company taxes.- `cell_position: Optional[str]`



**Arguments**:- `request_id: str`### `get-company`

- `company_id: int` (required)

- `amount: int` (required)**Description**: Get single company  

- `password: str` (required)

**Returns**: Company object**Arguments**: `id: Optional[int], name: Optional[str], reputation: Optional[int], balance: Optional[int], in_prison: Optional[bool], session_id: Optional[str], cell_position: Optional[str], request_id: str`  

**Returns**: Nothing on success, or error object

**Returns**: Company object (see structure above)

**Broadcasts**: `api-company_tax_paid`

### `create-company`

**Note**: Broadcast is triggered in `Company.pay_taxes()` method.

Create a new company.### `create-company`

### `company-complete-free-factories`

Bulk reconfigure free factories.**Description**: Create a new company  



**Arguments**:**Arguments**:**Arguments**: `name: str, who_create: int, password: str, request_id: str`  

- `company_id: int` (required)

- `find_resource: Optional[str]` - Filter factories by current resource- `name: str` (required)**Returns**:

- `new_resource: str` (required)

- `count: int` (required)- `who_create: int` (required) - User ID of creator```json

- `produce_status: Optional[bool]` (default: false)

- `password: str` (required)- `password: str` (required){



**Returns**: `{"success": True}` on success, or error object- `request_id: str`  "session_id": "session_abc123",



**Broadcasts**: `api-factory-start-complectation` (for each factory)  "company": { /* Company object */ }



**Note**: Broadcasts are triggered in `Company.complete_free_factories()` method.**Returns**:}



### `notforgame-update-company-balance````json```

⚠️ **ADMIN ONLY - NOT FOR GAME USE**

{**Broadcasts**: `api-create_company`

Update company balance directly.

  "session_id": "session_abc123",

**Arguments**:

- `company_id: int` (required)  "company": { /* Company object */ }### `update-company-add-user`

- `balance_change: int` (required) - Positive to add, negative to subtract

- `password: str` (required)}**Description**: Add user to company  



**Returns**: Nothing on success, or error object```**Arguments**: `user_id: int, secret_code: int, password: str`  



**Broadcasts**: None**Returns**: Success/error status  



### `notforgame-update-company-items`**Broadcasts**: `api-create_company`**Broadcasts**: `api-user_added_to_company`

⚠️ **ADMIN ONLY - NOT FOR GAME USE**



Update company inventory items directly.

### `update-company-add-user`### `set-company-position`

**Arguments**:

- `company_id: int` (required)Add user to company using secret code.**Description**: Set company position on map  

- `item_id: str` (required)

- `quantity_change: int` (required) - Positive to add, negative to subtract**Arguments**: `company_id: int, x: int, y: int, password: str, request_id: str`  

- `password: str` (required)

**Arguments**:**Returns**:

**Returns**: Nothing on success, or error object

- `user_id: int` (required)```json

**Broadcasts**: None (but triggers company resource broadcasts internally)

- `secret_code: int` (required){

### `notforgame-update-company-name`

Update company name.- `password: str` (required)  "result": true,



**Arguments**:  "position_now": "3.4"

- `company_id: int` (required)

- `new_name: str` (required)**Returns**: Success or error}

- `password: str` (required)

```

**Returns**: Nothing on success, or error object

**Broadcasts**: `api-user_added_to_company`**Broadcasts**: `api-company_set_position`

**Broadcasts**: `api-company_name_updated`



**Note**: This handler DOES broadcast directly (unlike most others).

### `set-company-position`### `update-company-left-user`

---

Set company position on the game map.**Description**: Remove user from company  

## Session Messages

**Arguments**: `user_id: int, company_id: str, password: str`  

### `get-sessions`

Get list of game sessions.**Arguments**:**Returns**: Success/error status  



**Arguments**:- `company_id: int` (required)**Broadcasts**: `api-user_left_company`

- `stage: Optional[str]` - Filter by stage

- `request_id: str`- `x: int` (required)



**Returns**: Array of Session objects- `y: int` (required)### `delete-company`



**Session Object Structure**:- `password: str` (required)**Description**: Delete a company  

```json

{- `request_id: str`**Arguments**: `company_id: str, password: str`  

  "session_id": "AFRIKA",

  "stage": "Game",**Returns**: Success/error status  

  "step": 5,

  "max_steps": 100**Returns**:**Broadcasts**: `api-company_deleted`

}

``````json



**Session Stages**:{### `get-company-cell-info`

- `FreeUserConnect` - Players can connect and create users

- `CellSelect` - Companies select their starting positions  "result": true,**Description**: Get information about company's cell  

- `Game` - Main game phase

- `End` - Game ended  "position_now": "x:y"**Arguments**: `company_id: int, request_id: str`  



### `get-session`}**Returns**:

Get single session.

``````json

**Arguments**:

- `session_id: Optional[str]`{

- `stage: Optional[str]`

- `request_id: str`**Broadcasts**: `api-company_set_position`  "data": {



**Returns**: Session object or null    "id": "mountain",



### `create-session`### `update-company-left-user`    "label": "Mountain",

Create a new game session.

Remove user from company.    "resource_id": "stone", 

**Arguments**:

- `session_id: Optional[str]` - If not provided, auto-generated    "max_amount": 3,

- `password: str` (required)

- `request_id: str`**Arguments**:    "pickable": true,



**Returns**:- `user_id: int` (required)    "locations": []

```json

{- `company_id: int` (required)  },

  "session": { /* Session object */ }

}- `password: str` (required)  "type": "CellType"

```

}

**Broadcasts**: None

**Returns**: Success or error```

### `update-session-stage`

Update session stage.



**Arguments**:**Broadcasts**: `api-user_left_company`### `get-company-improvement-info`

- `session_id: Optional[str]` (required, despite Optional annotation)

- `stage: str` (required) - One of: 'FreeUserConnect', 'CellSelect', 'Game', 'End'**Description**: Get company improvement information  

- `add_shedule: Optional[bool]` (default: true) - Whether to start timer for next stage

- `password: str` (required)### `delete-company`**Arguments**: `company_id: int, request_id: str`  



**Returns**: Nothing on success, or error objectDelete a company.**Returns**: Company improvements object



**Broadcasts**: `api-update_session_stage`



**Note**: Broadcast is triggered in `Session.update_stage()` method.**Arguments**:### `update-company-improve`



### `get-sessions-free-cells`- `company_id: int` (required)**Description**: Upgrade company improvement  

Get list of available cells for company placement.

- `password: str` (required)**Arguments**: `company_id: str, improvement_type: str, password: str`  

**Arguments**:

- `session_id: str` (required)**Returns**: Success/error status  

- `request_id: str`

**Returns**: Success or error**Broadcasts**: `api-company_improvement_upgraded`

**Returns**:

```json

{

  "free_cells": ["0:0", "1:0", "0:1", ...]**Broadcasts**: `api-company_deleted`### `company-take-credit`

}

```**Description**: Take credit for company  



### `delete-session`### `get-company-cell-info`**Arguments**: `company_id: str, amount: int, period: int, password: str`  

⚠️ **WARNING**: Deletes all related users and companies!

Get information about the cell where company is located.**Returns**: Success/error status  

Delete a session.

**Broadcasts**: `api-company_credit_taken`

**Arguments**:

- `session_id: str` (required)**Arguments**:

- `password: str` (required)

- `really: bool` (required) - Must be true to confirm- `company_id: int` (required)### `company-pay-credit`



**Returns**: Nothing on success, or error object- `request_id: str`**Description**: Pay credit for company  



**Broadcasts**: `api-session_deleted`**Arguments**: `company_id: str, credit_index: int, amount: int, password: str`  



**Note**: Broadcast is triggered in `Session.delete()` method.**Returns**:**Returns**: Success/error status  



### `get-session-time-to-next-stage````json**Broadcasts**: `api-company_credit_paid`

Get time remaining until next stage.

{

**Arguments**:

- `session_id: str` (required)  "data": { /* Cell info object */ },### `company-pay-taxes`

- `request_id: str`

  "type": "cell_type"**Description**: Pay taxes for company  

**Returns**:

```json}**Arguments**: `company_id: str, amount: int, password: str`  

{

  "time_to_next_stage": 120,```**Returns**: Success/error status  

  "stage_now": "CellSelect",

  "max_steps": 100,**Broadcasts**: `api-company_tax_paid`

  "step": 0

}### `get-company-improvement-info`

```

Get company's improvement information.---

**Broadcasts**: None



---

**Arguments**:## Session Messages

## Factory Messages

- `company_id: int` (required)

### `get-factories`

Get list of factories.- `request_id: str`### `get-sessions`



**Arguments**:**Description**: Get list of sessions  

- `company_id: int` (required)

- `complectation: Optional[str]` - Filter by resource type**Returns**: Improvement data object**Arguments**: `stage: Optional[str], request_id: str`  

- `produce: Optional[bool]` - Filter by production status

- `is_auto: Optional[bool]` - Filter by auto-production status**Returns**: Array of Session objects

- `request_id: str`

### `update-company-improve`

**Returns**:

```jsonUpgrade a company improvement.**Session Object Structure**:

{

  "factories": [ /* Array of Factory objects */ ]```json

}

```**Arguments**:{



**Factory Object Structure**:- `company_id: int` (required)  "session_id": "session_abc123",

```json

{- `improvement_type: str` (required)  "cells": ["mountain", "forest", "water", "field"],

  "id": 789,

  "company_id": 456,- `password: str` (required)  "map_size": { "rows": 7, "cols": 7 },

  "complectation": "iron",

  "produce": true,  "map_pattern": "random",

  "is_auto": false,

  "complectation_step": 0**Returns**: Success or error  "cell_counts": {},

}

```  "stage": "FreeUserConnect",



### `get-factory`**Broadcasts**: `api-company_improvement_upgraded`  "step": 1,

Get single factory information.

  "max_steps": 15

**Arguments**:

- `factory_id: int` (required)### `company-take-credit`}

- `request_id: str`

Company takes a credit from bank.```

**Returns**:

```json

{

  "factory": { /* Factory object */ }**Arguments**:### `get-session`

}

```- `company_id: int` (required)**Description**: Get single session  



### `factory-recomplectation`- `amount: int` (required)**Arguments**: `session_id: Optional[str], stage: Optional[str], request_id: str`  

Reconfigure factory to produce different resource.

- `period: int` (required) - Credit period in turns**Returns**: Session object (see structure above)

**Arguments**:

- `factory_id: int` (required)- `password: str` (required)

- `new_complectation: str` (required)

- `password: str` (required)- `request_id: str`### `create-session`



**Returns**:**Description**: Create a new session  

```json

{**Returns**: Credit data object**Arguments**: `session_id: Optional[str], password: str, request_id: str`  

  "success": true

}**Returns**:

```

**Broadcasts**: `api-company_credit_taken````json

**Broadcasts**: `api-factory-start-complectation`

{

**Note**: Broadcast is triggered in `Factory.pere_complete()` method.

### `company-pay-credit`  "session": { /* Session object */ }

### `factory-set-produce`

Set factory production status.Pay off company credit.}



**Arguments**:```

- `factory_id: int` (required)

- `produce: bool` (required) - true to start, false to stop**Arguments**:



**Returns**:- `company_id: int` (required)### `update-session-stage`

```json

{- `credit_index: int` (required)**Description**: Update session stage  

  "success": true

}- `amount: int` (required)**Arguments**: `session_id: Optional[str], stage: Literal['FreeUserConnect', 'CellSelect', 'Game', 'End'], password: str`  

```

- `password: str` (required)**Returns**: Success/error status  

**Broadcasts**: None

**Broadcasts**: `api-update_session_stage`

### `factory-set-auto`

Set factory auto-production status.**Returns**: Success or error



**Arguments**:### `get-sessions-free-cells`

- `factory_id: int` (required)

- `is_auto: bool` (required) - true for automatic, false for manual**Broadcasts**: `api-company_credit_paid`**Description**: Get free cells in session  



**Returns**:**Arguments**: `session_id: str, request_id: str`  

```json

{### `company-take-deposit`**Returns**:

  "success": true

}Company creates a deposit in bank.```json

```

{

**Broadcasts**: None

**Arguments**:  "free_cells": ["1.1", "2.3", "4.5"]

---

- `company_id: int` (required)}

## Exchange (Market) Messages

- `amount: int` (required)```

### `get-exchanges`

Get list of market offers.- `period: int` (required) - Deposit period in turns



**Arguments**:- `password: str` (required)### `delete-session`

- `session_id: Optional[str]`

- `company_id: Optional[int]` - Filter by seller company- `request_id: str`**Description**: Delete a session (WARNING: deletes all related users and companies)  

- `sell_resource: Optional[str]` - Filter by resource being sold

- `offer_type: Optional[str]` - Filter by type: 'money' or 'barter'**Arguments**: `session_id: str, password: str, really: bool`  

- `request_id: str`

**Returns**: Deposit data object**Returns**: Success/error status  

**Returns**: Array of Exchange offer objects (as dicts)

**Broadcasts**: `api-session_deleted`

**Exchange Offer Object Structure**:

```json**Broadcasts**: `api-company_deposit_taken`

{

  "id": 101,---

  "company_id": 456,

  "session_id": "AFRIKA",### `company-withdraw-deposit`

  "sell_resource": "iron",

  "sell_amount_per_trade": 10,Withdraw company deposit.## General Messages

  "count_offers": 5,

  "total_stock": 50,

  "offer_type": "money",

  "price": 100,**Arguments**:### `ping`

  "barter_resource": null,

  "barter_amount": null- `company_id: int` (required)**Description**: Ping server  

}

```- `deposit_index: int` (required)**Arguments**: `timestamp: str, content: Any`  



### `get-exchange`- `password: str` (required)**Returns**: Pong message with timestamp and client_id

Get single market offer.



**Arguments**:

- `id: int` (required)**Returns**: Success or error---

- `request_id: str`



**Returns**: Exchange offer object (as dict)

**Broadcasts**: `api-company_deposit_withdrawn`## Broadcast Messages (Server -> Client)

### `create-exchange-offer`

Create a new market offer.



**Arguments**:### `company-pay-taxes`These messages are automatically sent to all connected clients when certain events occur:

- `company_id: int` (required)

- `session_id: str` (required)Pay company taxes.

- `sell_resource: str` (required)

- `sell_amount_per_trade: int` (required)### `api-create_user`

- `count_offers: int` (required)

- `offer_type: str` (required) - 'money' or 'barter'**Arguments**:```json

- `price: Optional[int]` - Required if offer_type='money'

- `barter_resource: Optional[str]` - Required if offer_type='barter'- `company_id: int` (required){

- `barter_amount: Optional[int]` - Required if offer_type='barter'

- `password: str` (required)- `amount: int` (required)  "type": "api-create_user",

- `request_id: str`

- `password: str` (required)  "data": {

**Returns**:

```json    "session_id": "session_abc123",

{

  "session_id": "AFRIKA",**Returns**: Success or error    "user": { /* User object */ }

  "offer": { /* Exchange offer object */ }

}  }

```

**Broadcasts**: `api-company_tax_paid`}

**Broadcasts**: `api-exchange_offer_created`

```

**Note**: Broadcast is triggered in `Exchange.create()` method.

### `company-complete-free-factories`

**Example - Money Offer**:

```jsonBulk reconfigure free factories.### `api-update_user`

{

  "type": "create-exchange-offer",```json

  "company_id": 456,

  "session_id": "AFRIKA",**Arguments**:{

  "sell_resource": "iron",

  "sell_amount_per_trade": 10,- `company_id: int` (required)  "type": "api-update_user", 

  "count_offers": 5,

  "offer_type": "money",- `find_resource: Optional[str]` - Filter factories by current resource  "data": {

  "price": 100,

  "password": "secret123",- `new_resource: str` (required)    "session_id": "session_abc123",

  "request_id": "req456"

}- `count: int` (required)    "new": { /* User object */ },

```

- `produce_status: Optional[bool]` (default: false)    "old": { /* User object */ }

**Example - Barter Offer**:

```json- `password: str` (required)  }

{

  "type": "create-exchange-offer",}

  "company_id": 456,

  "session_id": "AFRIKA",**Returns**: Success or error```

  "sell_resource": "iron",

  "sell_amount_per_trade": 10,

  "count_offers": 5,

  "offer_type": "barter",**Broadcasts**: `api-factory-start-complectation` (for each factory)### `api-user_deleted`

  "barter_resource": "wood",

  "barter_amount": 15,```json

  "password": "secret123",

  "request_id": "req456"### `notforgame-update-company-balance`{

}

```⚠️ **ADMIN ONLY - NOT FOR GAME USE**  "type": "api-user_deleted",



### `update-exchange-offer`  "data": {

Update existing market offer.

Update company balance directly.    "user_id": 123

**Arguments**:

- `offer_id: int` (required)  }

- `sell_amount_per_trade: Optional[int]`

- `price: Optional[int]` - For money offers**Arguments**:}

- `barter_amount: Optional[int]` - For barter offers

- `password: str` (required)- `company_id: int` (required)```

- `request_id: str`

- `balance_change: int` (required) - Positive to add, negative to subtract

**Returns**:

```json- `password: str` (required)### `api-user_left_company`

{

  "session_id": "AFRIKA",```json

  "new": { /* Updated offer */ },

  "old": { /* Previous offer */ }**Returns**: Success or error{

}

```  "type": "api-user_left_company",



**Broadcasts**: `api-exchange_offer_updated`### `notforgame-update-company-items`  "data": {



**Note**: Broadcast is triggered in `Exchange.update_offer()` method.⚠️ **ADMIN ONLY - NOT FOR GAME USE**    "user_id": 123,



### `cancel-exchange-offer`    "company_id": 456

Cancel market offer (returns goods to seller).

Update company inventory items directly.  }

**Arguments**:

- `offer_id: int` (required)}

- `password: str` (required)

- `request_id: str`**Arguments**:```



**Returns**:- `company_id: int` (required)

```json

{- `item_id: str` (required)### `api-create_company`

  "session_id": "AFRIKA",

  "offer_id": 101,- `quantity_change: int` (required) - Positive to add, negative to subtract```json

  "company_id": 456,

  "status": "cancelled"- `password: str` (required){

}

```  "type": "api-create_company",



**Broadcasts**: `api-exchange_offer_cancelled`**Returns**: Success or error  "data": {



**Note**: Broadcast is triggered in `Exchange.cancel_offer()` method.    "session_id": "session_abc123",



### `buy-exchange-offer`### `notforgame-update-company-name`    "company": { /* Company object */ }

Buy from market offer.

Update company name.  }

**Arguments**:

- `offer_id: int` (required)}

- `buyer_company_id: int` (required)

- `quantity: int` (required) - Number of trades to execute**Arguments**:```

- `password: str` (required)

- `request_id: str`- `company_id: int` (required)



**Returns**:- `new_name: str` (required)### `api-user_added_to_company`

```json

{- `password: str` (required)```json

  "session_id": "AFRIKA",

  "offer_id": 101,{

  "buyer_company_id": 789,

  "seller_company_id": 456,**Returns**: Success or error  "type": "api-user_added_to_company",

  "sell_resource": "iron",

  "sell_amount": 10,  "data": {

  "offer_type": "money",

  "quantity": 1,**Broadcasts**: `api-company_name_updated`    "company_id": 456,

  "old_stock": 50,

  "new_stock": 40,    "user_id": 123

  "status": "completed",

  "total_price": 100---  }

}

```}



For barter offers, response includes:## Session Messages```

```json

{

  ...

  "barter_resource": "wood",### `get-sessions`### `api-company_set_position`

  "barter_amount": 15

}Get list of game sessions.```json

```

{

**Broadcasts**: `api-exchange_trade_completed`

**Arguments**:  "type": "api-company_set_position",

**Note**: Broadcast is triggered in `Exchange.buy()` method.

- `stage: Optional[str]` - Filter by stage  "data": {

---

- `request_id: str`    "company_id": 456,

## Broadcast Messages

    "old_position": "2.3",

These messages are automatically sent to all connected clients when certain events occur. Most broadcasts are triggered in the model methods (User, Company, Session, etc.) rather than in the WebSocket handlers.

**Returns**: Array of Session objects    "new_position": "3.4"

### User Broadcasts

  }

#### `api-create_user`

Sent when a new user is created (triggered in `User.create()`).**Session Object Structure**:}



#### `api-update_user````json```

Sent when user information is updated (triggered in `handle_update_user` handler).

{

#### `api-user_deleted`

Sent when a user is deleted (triggered in `User.delete()`).  "session_id": "AFRIKA",### `api-company_deleted`



### Company Broadcasts  "stage": "Game",```json



#### `api-create_company`  "step": 5,{

Sent when a new company is created (triggered in `Company.create()`).

  "max_steps": 100  "type": "api-company_deleted",

#### `api-user_added_to_company`

Sent when a user joins a company (triggered in `User.add_to_company()`).}  "data": {



#### `api-company_set_position````    "company_id": 456

Sent when company position is changed (triggered in `Company.set_position()`).

  }

#### `api-user_left_company`

Sent when a user leaves a company (triggered in `User.leave_from_company()`).**Session Stages**:}



#### `api-company_deleted`- `FreeUserConnect` - Players can connect and create users```

Sent when a company is deleted (triggered in `Company.delete()`).

- `CellSelect` - Companies select their starting positions

#### `api-company_improvement_upgraded`

Sent when a company upgrades an improvement (triggered in `Company.improve()`).- `Game` - Main game phase### `api-company_improvement_upgraded`



#### `api-company_credit_taken`- `End` - Game ended```json

Sent when a company takes a credit (triggered in `Company.take_credit()`).

{

#### `api-company_credit_paid`

Sent when a company pays a credit (triggered in `Company.pay_credit()`).### `get-session`  "type": "api-company_improvement_upgraded",



#### `api-company_deposit_taken`Get single session.  "data": {

Sent when a company creates a deposit (triggered in `Company.take_deposit()`).

    "company_id": 456,

#### `api-company_deposit_withdrawn`

Sent when a company withdraws a deposit (triggered in `Company.withdraw_deposit()`).**Arguments**:    "improvement_type": "warehouse",



#### `api-company_tax_paid`- `session_id: Optional[str]`    "new_level": "level2"

Sent when a company pays taxes (triggered in `Company.pay_taxes()`).

- `stage: Optional[str]`  }

#### `api-company_name_updated`

Sent when a company name is updated (triggered in `handle_notforgame_update_company_name` handler).- `request_id: str`}



### Factory Broadcasts```



#### `api-factory-start-complectation`**Returns**: Session object or null

Sent when factory reconfiguration starts (triggered in `Factory.pere_complete()`).

### `api-company_credit_taken`

### Session Broadcasts

### `create-session````json

#### `api-update_session_stage`

Sent when session stage is updated (triggered in `Session.update_stage()`).Create a new game session.{



#### `api-session_deleted`  "type": "api-company_credit_taken",

Sent when a session is deleted (triggered in `Session.delete()`).

**Arguments**:  "data": {

### Exchange Broadcasts

- `session_id: Optional[str]` - If not provided, auto-generated    "company_id": 456,

#### `api-exchange_offer_created`

Sent when a market offer is created (triggered in `Exchange.create()`).- `password: str` (required)    "amount": 1000,



#### `api-exchange_offer_updated`- `request_id: str`    "period": 5,

Sent when a market offer is updated (triggered in `Exchange.update_offer()`).

    "credit_id": 1

#### `api-exchange_offer_cancelled`

Sent when a market offer is cancelled (triggered in `Exchange.cancel_offer()`).**Returns**:  }



#### `api-exchange_trade_completed````json}

Sent when a trade is completed (triggered in `Exchange.buy()`).

{```

---

  "session": { /* Session object */ }

## Error Handling

}### `api-company_credit_paid`

All message handlers can return error responses:

``````json

```json

{{

  "error": "Error message description"

}### `update-session-stage`  "type": "api-company_credit_paid",

```

Update session stage.  "data": {

**Common Errors**:

- `"Missing required fields"` or `"Missing required field: {field_name}"` - Required parameters not provided    "company_id": 456,

- `"User not found"` - User ID doesn't exist

- `"Company not found"` - Company ID doesn't exist**Arguments**:    "credit_index": 0,

- `"Session not found"` - Session ID doesn't exist

- `"Factory not found"` - Factory ID doesn't exist- `session_id: str` (required)    "amount": 200

- `"Exchange offer not found"` - Offer ID doesn't exist

- Authentication errors from password validation- `stage: str` (required) - One of: 'FreeUserConnect', 'CellSelect', 'Game', 'End'  }



**Note**: Many handlers return nothing on success (not even a success message), only errors are explicitly returned.- `add_shedule: Optional[bool]` (default: true) - Whether to start timer for next stage}



---- `password: str` (required)```



## Request-Response Pattern



Handlers that return data support the request-response pattern using `request_id`:**Returns**: Success or error### `api-company_credit_removed`



**Client sends**:```json

```json

{**Broadcasts**: `api-update_session_stage`{

  "type": "get-user",

  "id": 123,  "type": "api-company_credit_removed",

  "request_id": "req-unique-id-123"

}### `get-sessions-free-cells`  "data": {

```

Get list of available cells for company placement.    "company_id": 456,

**Server responds**:

```json    "credit_index": 0

{

  "type": "response",**Arguments**:  }

  "request_id": "req-unique-id-123",

  "data": { /* Response data or null */ }- `session_id: str` (required)}

}

```- `request_id: str````



**Important**: If a handler returns `None` or doesn't return anything, the response data will be `null`.



---**Returns**:### `api-company_tax_paid`



## Usage Examples```jsonBroadcasted when company pays taxes.



### Connecting to WebSocket{



```javascript  "free_cells": ["0:0", "1:0", "0:1", ...]### `api-company_resource_added`

const ws = new WebSocket('ws://localhost:8000/ws/connect?client_id=my-client-123');

}```json

ws.onopen = () => {

  console.log('Connected to SEG WebSocket');```{

};

  "type": "api-company_resource_added",

ws.onmessage = (event) => {

  const message = JSON.parse(event.data);### `delete-session`  "data": {

  console.log('Received:', message);

  ⚠️ **WARNING**: Deletes all related users and companies!    "company_id": 456,

  // Handle different message types

  if (message.type === 'response' && message.request_id) {    "resource": "stone",

    // Check if data is null (no explicit response from handler)

    if (message.data === null) {Delete a session.    "amount": 5

      console.log('Operation completed (no data returned)');

    } else {  }

      handleResponse(message.request_id, message.data);

    }**Arguments**:}

  } else if (message.type === 'pong') {

    console.log('Pong received');- `session_id: str` (required)```

  } else if (message.type.startsWith('api-')) {

    handleBroadcast(message);- `password: str` (required)

  } else if (message.type === 'error') {

    console.error('Error:', message.message);- `really: bool` (required) - Must be true to confirm### `api-company_resource_removed`

    console.log('Available types:', message.available_types);

  }```json

};

**Returns**: Success or error{

ws.onerror = (error) => {

  console.error('WebSocket error:', error);  "type": "api-company_resource_removed",

};

**Broadcasts**: `api-session_deleted`  "data": {

ws.onclose = () => {

  console.log('WebSocket connection closed');    "company_id": 456,

};

```### `get-session-time-to-next-stage`    "resource": "stone",



### Creating a SessionGet time remaining until next stage.    "amount": 3



```javascript  }

ws.send(JSON.stringify({

  type: 'create-session',**Arguments**:}

  session_id: 'GAME_001',

  password: 'your-password',- `session_id: str` (required)```

  request_id: 'req-001'

}));- `request_id: str`

```

### `api-company_balance_changed`

### Creating a User

**Returns**:```json

```javascript

ws.send(JSON.stringify({```json{

  type: 'create-user',

  user_id: 12345,{  "type": "api-company_balance_changed",

  username: 'JohnDoe',

  password: 'your-password',  "time_to_next_stage": 120,  "data": {

  session_id: 'GAME_001',

  request_id: 'req-002'  "stage_now": "CellSelect",    "company_id": 456,

}));

```  "max_steps": 100,    "old_balance": 1000,



### Creating a Company  "step": 0    "new_balance": 1200,



```javascript}    "change": 200

ws.send(JSON.stringify({

  type: 'create-company',```  }

  name: 'Tech Corp',

  who_create: 12345,}

  password: 'your-password',

  request_id: 'req-003'---```

}));

```



### Getting Companies in a Session## Factory Messages### `api-company_reputation_changed`



```javascript```json

ws.send(JSON.stringify({

  type: 'get-companies',### `get-factories`{

  session_id: 'GAME_001',  // Note: session_id annotated as int but should be str

  request_id: 'req-004'Get list of factories.  "type": "api-company_reputation_changed",

}));

```  "data": {



### Creating a Market Offer (Money)**Arguments**:    "company_id": 456,



```javascript- `company_id: int` (required)    "old_reputation": 50,

ws.send(JSON.stringify({

  type: 'create-exchange-offer',- `complectation: Optional[str]` - Filter by resource type    "new_reputation": 55,

  company_id: 456,

  session_id: 'GAME_001',- `produce: Optional[bool]` - Filter by production status    "change": 5

  sell_resource: 'iron',

  sell_amount_per_trade: 10,- `is_auto: Optional[bool]` - Filter by auto-production status  }

  count_offers: 5,

  offer_type: 'money',- `request_id: str`}

  price: 100,

  password: 'your-password',```

  request_id: 'req-005'

}));**Returns**:

```

```json### `api-company_to_prison`

### Buying from Market

{```json

```javascript

ws.send(JSON.stringify({  "factories": [ /* Array of Factory objects */ ]{

  type: 'buy-exchange-offer',

  offer_id: 101,}  "type": "api-company_to_prison",

  buyer_company_id: 789,

  quantity: 2,```  "data": {

  password: 'your-password',

  request_id: 'req-006'    "company_id": 456

}));

```**Factory Object Structure**:  }



### Ping-Pong```json}



```javascript{```

ws.send(JSON.stringify({

  type: 'ping',  "id": 789,

  timestamp: Date.now().toString(),

  content: 'Are you there?'  "company_id": 456,### `api-update_session_stage`

}));

```  "complectation": "iron",```json



### Handling Broadcasts  "produce": true,{



```javascript  "is_auto": false,  "type": "api-update_session_stage",

function handleBroadcast(message) {

  switch(message.type) {  "complectation_step": 0  "data": {

    case 'api-create_user':

      console.log('New user created:', message.data);}    "session_id": "session_abc123",

      break;

    case 'api-exchange_trade_completed':```    "new_stage": "Game",

      console.log('Trade completed:', message.data);

      updateMarketUI();    "old_stage": "CellSelect"

      break;

    case 'api-update_session_stage':### `get-factory`  }

      console.log('Session stage changed:', message.data);

      updateGameStage(message.data.new_stage);Get single factory information.}

      break;

    // ... handle other broadcast types```

  }

}**Arguments**:

```

- `factory_id: int` (required)### `api-session_deleted`

---

- `request_id: str````json

## Important Notes & Known Issues

{

1. **Type Annotation Issues**:

   - `get-users`: `session_id` is annotated as `Optional[int]` but should be `Optional[str]`**Returns**:  "type": "api-session_deleted",

   - `get-companies`: `session_id` is annotated as `Optional[int]` but should be `Optional[str]`

   - These work with string values despite the annotation```json  "data": {



2. **Return Value Inconsistencies**:{    "session_id": "session_abc123"

   - Many write operations return nothing on success (causing `data: null` in responses)

   - Only errors are explicitly returned as `{"error": "message"}`  "factory": { /* Factory object */ }  }

   - Some operations return success objects like `{"success": true}`

}}

3. **Broadcast Sources**:

   - Most broadcasts are triggered in model methods (User, Company, Session classes)``````

   - NOT in the WebSocket handlers themselves

   - Exception: `api-update_user` and `api-company_name_updated` broadcast from handlers



4. **Password Security**: ### `factory-recomplectation`---

   - Store and transmit passwords securely

   - Consider using HTTPS/WSS for productionReconfigure factory to produce different resource.



5. **Session Lifecycle**: ## Error Handling

   - Sessions progress: `FreeUserConnect` → `CellSelect` → `Game` → `End`

**Arguments**:

6. **Factory Reconfiguration**: 

   - Factories have a `complectation_step` that tracks reconfiguration progress- `factory_id: int` (required)Error messages follow this format:



7. **Market Mechanics**:- `new_complectation: str` (required)```json

   - Money offers: Buyer pays `price` per trade

   - Barter offers: Buyer exchanges resources- `password: str` (required){

   - `total_stock` = `sell_amount_per_trade` × `count_offers`

  "type": "error",

8. **Cell Positions**: 

   - Formatted as `"x:y"` (e.g., `"0:0"`, `"3:4"`)**Returns**:  "message": "Error description",



9. **Request IDs**: ```json  "available_types": ["list", "of", "available", "message", "types"]

   - Use unique IDs to match responses with requests

   - Always check if `data` is `null` (operation succeeded but no data returned){}



10. **Administrative Functions**:   "success": true```

    - Messages starting with `notforgame-` are for admin/testing only

}

11. **Connection Status**: 

    - Check `/ws/status` endpoint to see all available message types and current connections```## Response Format



12. **Broadcast Handling**: 

    - All clients receive broadcast messages

    - Implement proper filtering in your client application**Broadcasts**: `api-factory-start-complectation`Responses to requests with `request_id` follow this format:



13. **Error Handling**: ```json

    - Always check for `error` field in responses before processing data

    - Check if `data === null` which means success without explicit return value### `factory-set-produce`{


Set factory production status.  "type": "response",

  "request_id": "your_request_id",

**Arguments**:  "data": { /* Response data */ }

- `factory_id: int` (required)}

- `produce: bool` (required) - true to start, false to stop```



**Returns**:---

```json

{## Session Stages

  "success": true- `FreeUserConnect`: Users can connect and join

}- `CellSelect`: Companies select their positions on the map  

```- `Game`: Active gameplay stage

- `End`: Game finished

### `factory-set-auto`

Set factory auto-production status.## Business Types

- `small`: Small business

**Arguments**:- `big`: Big business

- `factory_id: int` (required)

- `is_auto: bool` (required) - true for automatic, false for manual## Improvement Types

- `warehouse`: Storage capacity

**Returns**:- `contracts`: Contract capacity  

```json- `mountain`: Mountain resource (station/factory)

{- `forest`: Forest resource (station/factory)

  "success": true- `water`: Water resource (station/factory)

}- `field`: Field resource (station/factory)

```

## Cell Types

---Common cell types include:

- `mountain`: Stone resource

## Exchange (Market) Messages- `forest`: Wood resource  

- `water`: Fish resource

### `get-exchanges`- `field`: Grain resource

Get list of market offers.- `city`: Urban area

- `prison`: Restricted area

**Arguments**:

- `session_id: Optional[str]`## Authentication

- `company_id: Optional[int]` - Filter by seller companyMost write operations require a `password` field for authentication.

- `sell_resource: Optional[str]` - Filter by resource being sold

- `offer_type: Optional[str]` - Filter by type: 'money' or 'barter'## Notes

- `request_id: str`- There's an inconsistency in the source code where `session_id` in `get-users` is annotated as `Optional[int]` but should be `Optional[str]` based on the Session model

- All broadcast messages are sent automatically to all connected clients when the corresponding events occur

**Returns**: Array of Exchange offer objects- Error responses always include an `error` field with a descriptive message

- The `change` field in balance/reputation change broadcasts represents the amount of change (positive for increase, negative for decrease)
**Exchange Offer Object Structure**:
```json
{
  "id": 101,
  "company_id": 456,
  "session_id": "AFRIKA",
  "sell_resource": "iron",
  "sell_amount_per_trade": 10,
  "count_offers": 5,
  "total_stock": 50,
  "offer_type": "money",
  "price": 100,
  "barter_resource": null,
  "barter_amount": null
}
```

### `get-exchange`
Get single market offer.

**Arguments**:
- `id: int` (required)
- `request_id: str`

**Returns**: Exchange offer object

### `create-exchange-offer`
Create a new market offer.

**Arguments**:
- `company_id: int` (required)
- `session_id: str` (required)
- `sell_resource: str` (required)
- `sell_amount_per_trade: int` (required)
- `count_offers: int` (required)
- `offer_type: str` (required) - 'money' or 'barter'
- `price: Optional[int]` - Required if offer_type='money'
- `barter_resource: Optional[str]` - Required if offer_type='barter'
- `barter_amount: Optional[int]` - Required if offer_type='barter'
- `password: str` (required)
- `request_id: str`

**Returns**:
```json
{
  "session_id": "AFRIKA",
  "offer": { /* Exchange offer object */ }
}
```

**Broadcasts**: `api-exchange_offer_created`

**Example - Money Offer**:
```json
{
  "type": "create-exchange-offer",
  "company_id": 456,
  "session_id": "AFRIKA",
  "sell_resource": "iron",
  "sell_amount_per_trade": 10,
  "count_offers": 5,
  "offer_type": "money",
  "price": 100,
  "password": "secret123",
  "request_id": "req456"
}
```

**Example - Barter Offer**:
```json
{
  "type": "create-exchange-offer",
  "company_id": 456,
  "session_id": "AFRIKA",
  "sell_resource": "iron",
  "sell_amount_per_trade": 10,
  "count_offers": 5,
  "offer_type": "barter",
  "barter_resource": "wood",
  "barter_amount": 15,
  "password": "secret123",
  "request_id": "req456"
}
```

### `update-exchange-offer`
Update existing market offer.

**Arguments**:
- `offer_id: int` (required)
- `sell_amount_per_trade: Optional[int]`
- `price: Optional[int]` - For money offers
- `barter_amount: Optional[int]` - For barter offers
- `password: str` (required)
- `request_id: str`

**Returns**:
```json
{
  "session_id": "AFRIKA",
  "new": { /* Updated offer */ },
  "old": { /* Previous offer */ }
}
```

**Broadcasts**: `api-exchange_offer_updated`

### `cancel-exchange-offer`
Cancel market offer (returns goods to seller).

**Arguments**:
- `offer_id: int` (required)
- `password: str` (required)
- `request_id: str`

**Returns**:
```json
{
  "session_id": "AFRIKA",
  "offer_id": 101,
  "company_id": 456,
  "status": "cancelled"
}
```

**Broadcasts**: `api-exchange_offer_cancelled`

### `buy-exchange-offer`
Buy from market offer.

**Arguments**:
- `offer_id: int` (required)
- `buyer_company_id: int` (required)
- `quantity: int` (required) - Number of trades to execute
- `password: str` (required)
- `request_id: str`

**Returns**:
```json
{
  "session_id": "AFRIKA",
  "offer_id": 101,
  "buyer_company_id": 789,
  "seller_company_id": 456,
  "sell_resource": "iron",
  "sell_amount": 10,
  "offer_type": "money",
  "quantity": 1,
  "old_stock": 50,
  "new_stock": 40,
  "status": "completed",
  "total_price": 100
}
```

For barter offers, response includes:
```json
{
  ...
  "barter_resource": "wood",
  "barter_amount": 15
}
```

**Broadcasts**: `api-exchange_trade_completed`

---

## Broadcast Messages

These messages are automatically sent to all connected clients when certain events occur.

### User Broadcasts

#### `api-create_user`
Sent when a new user is created.

#### `api-update_user`
Sent when user information is updated.

#### `api-user_deleted`
Sent when a user is deleted.

### Company Broadcasts

#### `api-create_company`
Sent when a new company is created.

#### `api-user_added_to_company`
Sent when a user joins a company.

#### `api-company_set_position`
Sent when company position is changed.

#### `api-user_left_company`
Sent when a user leaves a company.

#### `api-company_deleted`
Sent when a company is deleted.

#### `api-company_improvement_upgraded`
Sent when a company upgrades an improvement.

#### `api-company_credit_taken`
Sent when a company takes a credit.

#### `api-company_credit_paid`
Sent when a company pays a credit.

#### `api-company_deposit_taken`
Sent when a company creates a deposit.

#### `api-company_deposit_withdrawn`
Sent when a company withdraws a deposit.

#### `api-company_tax_paid`
Sent when a company pays taxes.

#### `api-company_name_updated`
Sent when a company name is updated.

### Factory Broadcasts

#### `api-factory-start-complectation`
Sent when factory reconfiguration starts.

### Session Broadcasts

#### `api-update_session_stage`
Sent when session stage is updated.

#### `api-session_deleted`
Sent when a session is deleted.

### Exchange Broadcasts

#### `api-exchange_offer_created`
Sent when a market offer is created.

#### `api-exchange_offer_updated`
Sent when a market offer is updated.

#### `api-exchange_offer_cancelled`
Sent when a market offer is cancelled.

#### `api-exchange_trade_completed`
Sent when a trade is completed.

---

## Error Handling

All message handlers can return error responses:

```json
{
  "error": "Error message description"
}
```

**Common Errors**:
- `"Missing required fields"` - Required parameters not provided
- `"User not found"` - User ID doesn't exist
- `"Company not found"` - Company ID doesn't exist
- `"Session not found"` - Session ID doesn't exist
- `"Factory not found"` - Factory ID doesn't exist
- `"Exchange offer not found"` - Offer ID doesn't exist
- Authentication errors from password validation

---

## Request-Response Pattern

Many handlers support the request-response pattern using `request_id`:

**Client sends**:
```json
{
  "type": "get-user",
  "id": 123,
  "request_id": "req-unique-id-123"
}
```

**Server responds**:
```json
{
  "type": "response",
  "request_id": "req-unique-id-123",
  "data": { /* Response data */ }
}
```

---

## Usage Examples

### Connecting to WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/connect?client_id=my-client-123');

ws.onopen = () => {
  console.log('Connected to SEG WebSocket');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
  
  // Handle different message types
  if (message.type === 'response' && message.request_id) {
    handleResponse(message.request_id, message.data);
  } else if (message.type === 'pong') {
    console.log('Pong received');
  } else if (message.type.startsWith('api-')) {
    handleBroadcast(message);
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket connection closed');
};
```

### Creating a Session

```javascript
ws.send(JSON.stringify({
  type: 'create-session',
  session_id: 'GAME_001',
  password: 'your-password',
  request_id: 'req-001'
}));
```

### Creating a User

```javascript
ws.send(JSON.stringify({
  type: 'create-user',
  user_id: 12345,
  username: 'JohnDoe',
  password: 'your-password',
  session_id: 'GAME_001',
  request_id: 'req-002'
}));
```

### Creating a Company

```javascript
ws.send(JSON.stringify({
  type: 'create-company',
  name: 'Tech Corp',
  who_create: 12345,
  password: 'your-password',
  request_id: 'req-003'
}));
```

### Getting Companies in a Session

```javascript
ws.send(JSON.stringify({
  type: 'get-companies',
  session_id: 'GAME_001',
  request_id: 'req-004'
}));
```

### Creating a Market Offer (Money)

```javascript
ws.send(JSON.stringify({
  type: 'create-exchange-offer',
  company_id: 456,
  session_id: 'GAME_001',
  sell_resource: 'iron',
  sell_amount_per_trade: 10,
  count_offers: 5,
  offer_type: 'money',
  price: 100,
  password: 'your-password',
  request_id: 'req-005'
}));
```

### Buying from Market

```javascript
ws.send(JSON.stringify({
  type: 'buy-exchange-offer',
  offer_id: 101,
  buyer_company_id: 789,
  quantity: 2,
  password: 'your-password',
  request_id: 'req-006'
}));
```

### Ping-Pong

```javascript
ws.send(JSON.stringify({
  type: 'ping',
  timestamp: Date.now().toString(),
  content: 'Are you there?'
}));
```

### Handling Broadcasts

```javascript
function handleBroadcast(message) {
  switch(message.type) {
    case 'api-create_user':
      console.log('New user created:', message.data);
      break;
    case 'api-exchange_trade_completed':
      console.log('Trade completed:', message.data);
      updateMarketUI();
      break;
    case 'api-update_session_stage':
      console.log('Session stage changed:', message.data);
      updateGameStage(message.data.new_stage);
      break;
    // ... handle other broadcast types
  }
}
```

---

## Notes

1. **Password Security**: Store and transmit passwords securely. Consider using HTTPS for production.

2. **Session Lifecycle**: Sessions progress through stages:
   - `FreeUserConnect` → `CellSelect` → `Game` → `End`

3. **Factory Reconfiguration**: Factories have a `complectation_step` that tracks reconfiguration progress.

4. **Market Mechanics**:
   - Money offers: Buyer pays `price` per trade
   - Barter offers: Buyer exchanges resources
   - `total_stock` = `sell_amount_per_trade` × `count_offers`

5. **Cell Positions**: Formatted as `"x:y"` (e.g., `"0:0"`, `"3:4"`)

6. **Request IDs**: Use unique IDs to match responses with requests in async environments.

7. **Administrative Functions**: Messages starting with `notforgame-` are for admin/testing only.

8. **Connection Status**: Check `/ws/status` endpoint to see all available message types and current connections.

9. **Broadcast Handling**: All clients receive broadcast messages - implement proper filtering in your client application.

10. **Error Handling**: Always check for `error` field in responses before processing data.

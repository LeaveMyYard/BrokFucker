# Error codes for Binance (2019-09-25)
Errors consist of two parts: an error code and a message. Codes are universal,
 but messages can vary. Here is the error JSON payload:
```javascript
{
  "code":-1121,
  "msg":"Invalid symbol."
}
```


## 10xx - General Server or Network issues
#### -1000 UNKNOWN
 * An unknown error occured while processing the request.

#### -1001 DISCONNECTED
 * Internal error; unable to process your request. Please try again.

#### -1002 UNAUTHORIZED
 * You are not authorized to execute this request.

#### -1003 TOO_MANY_REQUESTS
 * Too many requests queued.
 * Too much request weight used; please use the websocket for live updates to avoid polling the API.
 * Too much request weight used; current limit is %s request weight per %s %s. Please use the websocket for live updates to avoid polling the API.
 * Way too much request weight used; IP banned until %s. Please use the websocket for live updates to avoid bans.

#### -1006 UNEXPECTED_RESP
 * An unexpected response was received from the message bus. Execution status unknown.

#### -1007 TIMEOUT
 * Timeout waiting for response from backend server. Send status unknown; execution status unknown.

#### -1014 UNKNOWN_ORDER_COMPOSITION
 * Unsupported order combination.

#### -1015 TOO_MANY_ORDERS
 * Too many new orders.
 * Too many new orders; current limit is %s orders per %s.

#### -1016 SERVICE_SHUTTING_DOWN
 * This service is no longer available.

#### -1020 UNSUPPORTED_OPERATION
 * This operation is not supported.

#### -1021 INVALID_TIMESTAMP
 * Timestamp for this request is outside of the recvWindow.
 * Timestamp for this request was 1000ms ahead of the server's time.

#### -1022 INVALID_SIGNATURE
 * Signature for this request is not valid.


## 11xx - Request issues
#### -1100 ILLEGAL_CHARS
 * Illegal characters found in a parameter.
 * Illegal characters found in parameter '%s'; legal range is '%s'.

#### -1101 TOO_MANY_PARAMETERS
 * Too many parameters sent for this endpoint.
 * Too many parameters; expected '%s' and received '%s'.
 * Duplicate values for a parameter detected.

#### -1102 MANDATORY_PARAM_EMPTY_OR_MALFORMED
 * A mandatory parameter was not sent, was empty/null, or malformed.
 * Mandatory parameter '%s' was not sent, was empty/null, or malformed.
 * Param '%s' or '%s' must be sent, but both were empty/null!

#### -1103 UNKNOWN_PARAM
 * An unknown parameter was sent.

#### -1104 UNREAD_PARAMETERS
 * Not all sent parameters were read.
 * Not all sent parameters were read; read '%s' parameter(s) but was sent '%s'.

#### -1105 PARAM_EMPTY
 * A parameter was empty.
 * Parameter '%s' was empty.

#### -1106 PARAM_NOT_REQUIRED
 * A parameter was sent when not required.
 * Parameter '%s' sent when not required.

## 12xx - Registration issues
#### -1200 EMAIL_USED
 * Email is already in use.

#### -1201 PASSWORD_SIZE_INCORRECT
 * A password size is less than 8.
 * A password size is bigger than 32.
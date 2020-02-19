# Error codes for Binance (2019-09-25)
Errors consist of two parts: an error code and a message. Codes are universal,
 but messages can vary. Here is the error JSON payload:
```javascript
{
  "code":-1200,
  "msg":"Email is already in use."
}
```


## 10xx - General Server or Network issues
#### -1000 UNKNOWN
 * An unknown error occured while processing the request.

#### -1001 NOT_FOUND
 * The stuff you requested for is not found.

#### -1002 UNAUTHORIZED
 * You are not authorized to execute this request.


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
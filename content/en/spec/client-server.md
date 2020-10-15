---
title: Client-Server API
type: docs
weight: 10
---

{{unstable\_warning\_block\_CLIENT\_RELEASE\_LABEL}}

The client-server API provides a simple lightweight API to let clients
send messages, control rooms and synchronise conversation history. It is
designed to support both lightweight clients which store no state and
lazy-load data from the server as required - as well as heavyweight
clients which maintain a full local persistent copy of server state.

Changelog
---------

**Version: %CLIENT\_RELEASE\_LABEL%**

{{client\_server\_changelog}}

This version of the specification is generated from
[matrix-doc](https://github.com/matrix-org/matrix-doc) as of Git commit
[{{git\_version}}](https://github.com/matrix-org/matrix-doc/tree/%7B%7Bgit_rev%7D%7D).

For the full historical changelog, see
<https://github.com/matrix-org/matrix-doc/blob/master/changelogs/client_server.rst>

### Other versions of this specification

The following other versions are also available, in reverse
chronological order:

-   [HEAD](https://matrix.org/docs/spec/client_server/unstable.html):
    Includes all changes since the latest versioned release.
-   [r0.6.1](https://matrix.org/docs/spec/client_server/r0.6.1.html)
-   [r0.6.0](https://matrix.org/docs/spec/client_server/r0.6.0.html)
-   [r0.5.0](https://matrix.org/docs/spec/client_server/r0.5.0.html)
-   [r0.4.0](https://matrix.org/docs/spec/client_server/r0.4.0.html)
-   [r0.3.0](https://matrix.org/docs/spec/client_server/r0.3.0.html)
-   [r0.2.0](https://matrix.org/docs/spec/client_server/r0.2.0.html)
-   [r0.1.0](https://matrix.org/docs/spec/client_server/r0.1.0.html)
-   [r0.0.1](https://matrix.org/docs/spec/r0.0.1/client_server.html)
-   [r0.0.0](https://matrix.org/docs/spec/r0.0.0/client_server.html)
-   [Legacy](https://matrix.org/docs/spec/legacy/#client-server-api):
    The last draft before the spec was formally released in version
    r0.0.0.

API Standards
-------------

The mandatory baseline for client-server communication in Matrix is
exchanging JSON objects over HTTP APIs. HTTPS is recommended for
communication, although HTTP may be supported as a fallback to support
basic HTTP clients. More efficient optional transports will in future be
supported as optional extensions - e.g. a packed binary encoding over
stream-cipher encrypted TCP socket for low-bandwidth/low-roundtrip
mobile usage. For the default HTTP transport, all API calls use a
Content-Type of `application/json`. In addition, all strings MUST be
encoded as UTF-8. Clients are authenticated using opaque `access_token`
strings (see [Client Authentication](#client-authentication) for
details), passed as a query string parameter on all requests.

The names of the API endpoints for the HTTP transport follow a
convention of using underscores to separate words (for example
`/delete_devices`). The key names in JSON objects passed over the API
also follow this convention.

Note

There are a few historical exceptions to this rule, such as
`/createRoom`. A future version of this specification will address the
inconsistency.

Any errors which occur at the Matrix API level MUST return a "standard
error response". This is a JSON object which looks like:

    {
      "errcode": "<error code>",
      "error": "<error message>"
    }

The `error` string will be a human-readable error message, usually a
sentence explaining what went wrong. The `errcode` string will be a
unique string which can be used to handle an error message e.g.
`M_FORBIDDEN`. These error codes should have their namespace first in
ALL CAPS, followed by a single \_ to ease separating the namespace from
the error code. For example, if there was a custom namespace
`com.mydomain.here`, and a `FORBIDDEN` code, the error code should look
like `COM.MYDOMAIN.HERE_FORBIDDEN`. There may be additional keys
depending on the error, but the keys `error` and `errcode` MUST always
be present.

Errors are generally best expressed by their error code rather than the
HTTP status code returned. When encountering the error code `M_UNKNOWN`,
clients should prefer the HTTP status code as a more reliable reference
for what the issue was. For example, if the client receives an error
code of `M_NOT_FOUND` but the request gave a 400 Bad Request status
code, the client should treat the error as if the resource was not
found. However, if the client were to receive an error code of
`M_UNKNOWN` with a 400 Bad Request, the client should assume that the
request being made was invalid.

The common error codes are:

`M_FORBIDDEN`  
Forbidden access, e.g. joining a room without permission, failed login.

`M_UNKNOWN_TOKEN`  
The access token specified was not recognised.

An additional response parameter, `soft_logout`, might be present on the
response for 401 HTTP status codes. See [the soft logout
section](#soft-logout) for more information.

`M_MISSING_TOKEN`  
No access token was specified for the request.

`M_BAD_JSON`  
Request contained valid JSON, but it was malformed in some way, e.g.
missing required keys, invalid values for keys.

`M_NOT_JSON`  
Request did not contain valid JSON.

`M_NOT_FOUND`  
No resource was found for this request.

`M_LIMIT_EXCEEDED`  
Too many requests have been sent in a short period of time. Wait a while
then try again.

`M_UNKNOWN`  
An unknown error has occurred.

Other error codes the client might encounter are:

`M_UNRECOGNIZED`  
The server did not understand the request.

`M_UNAUTHORIZED`  
The request was not correctly authorized. Usually due to login failures.

`M_USER_DEACTIVATED`  
The user ID associated with the request has been deactivated. Typically
for endpoints that prove authentication, such as `/login`.

`M_USER_IN_USE`  
Encountered when trying to register a user ID which has been taken.

`M_INVALID_USERNAME`  
Encountered when trying to register a user ID which is not valid.

`M_ROOM_IN_USE`  
Sent when the room alias given to the `createRoom` API is already in
use.

`M_INVALID_ROOM_STATE`  
Sent when the initial state given to the `createRoom` API is invalid.

`M_THREEPID_IN_USE`  
Sent when a threepid given to an API cannot be used because the same
threepid is already in use.

`M_THREEPID_NOT_FOUND`  
Sent when a threepid given to an API cannot be used because no record
matching the threepid was found.

`M_THREEPID_AUTH_FAILED`  
Authentication could not be performed on the third party identifier.

`M_THREEPID_DENIED`  
The server does not permit this third party identifier. This may happen
if the server only permits, for example, email addresses from a
particular domain.

`M_SERVER_NOT_TRUSTED`  
The client's request used a third party server, eg. identity server,
that this server does not trust.

`M_UNSUPPORTED_ROOM_VERSION`  
The client's request to create a room used a room version that the
server does not support.

`M_INCOMPATIBLE_ROOM_VERSION`  
The client attempted to join a room that has a version the server does
not support. Inspect the `room_version` property of the error response
for the room's version.

`M_BAD_STATE`  
The state change requested cannot be performed, such as attempting to
unban a user who is not banned.

`M_GUEST_ACCESS_FORBIDDEN`  
The room or resource does not permit guests to access it.

`M_CAPTCHA_NEEDED`  
A Captcha is required to complete the request.

`M_CAPTCHA_INVALID`  
The Captcha provided did not match what was expected.

`M_MISSING_PARAM`  
A required parameter was missing from the request.

`M_INVALID_PARAM`  
A parameter that was specified has the wrong value. For example, the
server expected an integer and instead received a string.

`M_TOO_LARGE`  
The request or entity was too large.

`M_EXCLUSIVE`  
The resource being requested is reserved by an application service, or
the application service making the request has not created the resource.

`M_RESOURCE_LIMIT_EXCEEDED`  
The request cannot be completed because the homeserver has reached a
resource limit imposed on it. For example, a homeserver held in a shared
hosting environment may reach a resource limit if it starts using too
much memory or disk space. The error MUST have an `admin_contact` field
to provide the user receiving the error a place to reach out to.
Typically, this error will appear on routes which attempt to modify
state (eg: sending messages, account data, etc) and not routes which
only read state (eg: `/sync`, get account data, etc).

`M_CANNOT_LEAVE_SERVER_NOTICE_ROOM`  
The user is unable to reject an invite to join the server notices room.
See the [Server Notices](#server-notices) module for more information.

The client-server API typically uses `HTTP PUT` to submit requests with
a client-generated transaction identifier. This means that these
requests are idempotent. The scope of a transaction identifier is a
particular access token. It **only** serves to identify new requests
from retransmits. After the request has finished, the `{txnId}` value
should be changed (how is not specified; a monotonically increasing
integer is recommended).

Some API endpoints may allow or require the use of `POST` requests
without a transaction ID. Where this is optional, the use of a `PUT`
request is strongly recommended.

{{versions\_cs\_http\_api}}

Web Browser Clients
-------------------

It is realistic to expect that some clients will be written to be run
within a web browser or similar environment. In these cases, the
homeserver should respond to pre-flight requests and supply Cross-Origin
Resource Sharing (CORS) headers on all requests.

Servers MUST expect that clients will approach them with `OPTIONS`
requests, allowing clients to discover the CORS headers. All endpoints
in this specification s upport the `OPTIONS` method, however the server
MUST NOT perform any logic defined for the endpoints when approached
with an `OPTIONS` request.

When a client approaches the server with a request, the server should
respond with the CORS headers for that route. The recommended CORS
headers to be returned by servers on all requests are:

    Access-Control-Allow-Origin: *
    Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
    Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept, Authorization

Server Discovery
----------------

In order to allow users to connect to a Matrix server without needing to
explicitly specify the homeserver's URL or other parameters, clients
SHOULD use an auto-discovery mechanism to determine the server's URL
based on a user's Matrix ID. Auto-discovery should only be done at login
time.

In this section, the following terms are used with specific meanings:

`PROMPT`  
Retrieve the specific piece of information from the user in a way which
fits within the existing client user experience, if the client is
inclined to do so. Failure can take place instead if no good user
experience for this is possible at this point.

`IGNORE`  
Stop the current auto-discovery mechanism. If no more auto-discovery
mechanisms are available, then the client may use other methods of
determining the required parameters, such as prompting the user, or
using default values.

`FAIL_PROMPT`  
Inform the user that auto-discovery failed due to invalid/empty data and
`PROMPT` for the parameter.

`FAIL_ERROR`  
Inform the user that auto-discovery did not return any usable URLs. Do
not continue further with the current login process. At this point,
valid data was obtained, but no server is available to serve the client.
No further guess should be attempted and the user should make a
conscientious decision what to do next.

### Well-known URI

Note

Servers hosting the `.well-known` JSON file SHOULD offer CORS headers,
as per the [CORS](#CORS) section in this specification.

The `.well-known` method uses a JSON file at a predetermined location to
specify parameter values. The flow for this method is as follows:

1.  Extract the server name from the user's Matrix ID by splitting the
    Matrix ID at the first colon.
2.  Extract the hostname from the server name.
3.  Make a GET request to `https://hostname/.well-known/matrix/client`.
    1.  If the returned status code is 404, then `IGNORE`.
    2.  If the returned status code is not 200, or the response body is
        empty, then `FAIL_PROMPT`.
    3.  Parse the response body as a JSON object
        1.  If the content cannot be parsed, then `FAIL_PROMPT`.
    4.  Extract the `base_url` value from the `m.homeserver` property.
        This value is to be used as the base URL of the homeserver.
        1.  If this value is not provided, then `FAIL_PROMPT`.
    5.  Validate the homeserver base URL:
        1.  Parse it as a URL. If it is not a URL, then `FAIL_ERROR`.
        2.  Clients SHOULD validate that the URL points to a valid
            homeserver before accepting it by connecting to the
            `/_matrix/client/versions`\_ endpoint, ensuring that it does
            not return an error, and parsing and validating that the
            data conforms with the expected response format. If any step
            in the validation fails, then `FAIL_ERROR`. Validation is
            done as a simple check against configuration errors, in
            order to ensure that the discovered address points to a
            valid homeserver.
    6.  If the `m.identity_server` property is present, extract the
        `base_url` value for use as the base URL of the identity server.
        Validation for this URL is done as in the step above, but using
        `/_matrix/identity/api/v1` as the endpoint to connect to. If the
        `m.identity_server` property is present, but does not have a
        `base_url` value, then `FAIL_ERROR`.

{{wellknown\_cs\_http\_api}}

Client Authentication
---------------------

Most API endpoints require the user to identify themselves by presenting
previously obtained credentials in the form of an `access_token` query
parameter or through an Authorization Header of `Bearer $access_token`.
An access token is typically obtained via the [Login](#login) or
[Registration](#Registration) processes.

Note

This specification does not mandate a particular format for the access
token. Clients should treat it as an opaque byte sequence. Servers are
free to choose an appropriate format. Server implementors may like to
investigate [macaroons](http://research.google.com/pubs/pub41892.html).

### Using access tokens

Access tokens may be provided in two ways, both of which the homeserver
MUST support:

1.  Via a query string parameter, `access_token=TheTokenHere`.
2.  Via a request header, `Authorization: Bearer TheTokenHere`.

Clients are encouraged to use the `Authorization` header where possible
to prevent the access token being leaked in access/HTTP logs. The query
string should only be used in cases where the `Authorization` header is
inaccessible for the client.

When credentials are required but missing or invalid, the HTTP call will
return with a status of 401 and the error code, `M_MISSING_TOKEN` or
`M_UNKNOWN_TOKEN` respectively.

### Relationship between access tokens and devices

Client [devices](../index.html#devices) are closely related to access
tokens. Matrix servers should record which device each access token is
assigned to, so that subsequent requests can be handled correctly.

By default, the [Login](#login) and [Registration](#Registration)
processes auto-generate a new `device_id`. A client is also free to
generate its own `device_id` or, provided the user remains the same,
reuse a device: in either case the client should pass the `device_id` in
the request body. If the client sets the `device_id`, the server will
invalidate any access token previously assigned to that device. There is
therefore at most one active access token assigned to each device at any
one time.

### Soft logout

When a request fails due to a 401 status code per above, the server can
include an extra response parameter, `soft_logout`, to indicate if the
client's persisted information can be retained. This defaults to
`false`, indicating that the server has destroyed the session. Any
persisted state held by the client, such as encryption keys and device
information, must not be reused and must be discarded.

When `soft_logout` is true, the client can acquire a new access token by
specifying the device ID it is already using to the login API. In most
cases a `soft_logout: true` response indicates that the user's session
has expired on the server-side and the user simply needs to provide
their credentials again.

In either case, the client's previously known access token will no
longer function.

### User-Interactive Authentication API

#### Overview

Some API endpoints require authentication that interacts with the user.
The homeserver may provide many different ways of authenticating, such
as user/password auth, login via a single-sign-on server (SSO), etc.
This specification does not define how homeservers should authorise
their users but instead defines the standard interface which
implementations should follow so that ANY client can login to ANY
homeserver.

The process takes the form of one or more 'stages'. At each stage the
client submits a set of data for a given authentication type and awaits
a response from the server, which will either be a final success or a
request to perform an additional stage. This exchange continues until
the final success.

For each endpoint, a server offers one or more 'flows' that the client
can use to authenticate itself. Each flow comprises a series of stages,
as described above. The client is free to choose which flow it follows,
however the flow's stages must be completed in order. Failing to follow
the flows in order must result in an HTTP 401 response, as defined
below. When all stages in a flow are complete, authentication is
complete and the API call succeeds.

#### User-interactive API in the REST API

In the REST API described in this specification, authentication works by
the client and server exchanging JSON dictionaries. The server indicates
what authentication data it requires via the body of an HTTP 401
response, and the client submits that authentication data via the `auth`
request parameter.

A client should first make a request with no `auth` parameter[1]. The
homeserver returns an HTTP 401 response, with a JSON body, as follows:

    HTTP/1.1 401 Unauthorized
    Content-Type: application/json

    {
      "flows": [
        {
          "stages": [ "example.type.foo", "example.type.bar" ]
        },
        {
          "stages": [ "example.type.foo", "example.type.baz" ]
        }
      ],
      "params": {
          "example.type.baz": {
              "example_key": "foobar"
          }
      },
      "session": "xxxxxx"
    }

In addition to the `flows`, this object contains some extra information:

params  
This section contains any information that the client will need to know
in order to use a given type of authentication. For each authentication
type presented, that type may be present as a key in this dictionary.
For example, the public part of an OAuth client ID could be given here.

session  
This is a session identifier that the client must pass back to the
homeserver, if one is provided, in subsequent attempts to authenticate
in the same API call.

The client then chooses a flow and attempts to complete the first stage.
It does this by resubmitting the same request with the addition of an
`auth` key in the object that it submits. This dictionary contains a
`type` key whose value is the name of the authentication type that the
client is attempting to complete. It must also contain a `session` key
with the value of the session key given by the homeserver, if one was
given. It also contains other keys dependent on the auth type being
attempted. For example, if the client is attempting to complete auth
type `example.type.foo`, it might submit something like this:

    POST /_matrix/client/r0/endpoint HTTP/1.1
    Content-Type: application/json

    {
      "a_request_parameter": "something",
      "another_request_parameter": "something else",
      "auth": {
          "type": "example.type.foo",
          "session": "xxxxxx",
          "example_credential": "verypoorsharedsecret"
      }
    }

If the homeserver deems the authentication attempt to be successful but
still requires more stages to be completed, it returns HTTP status 401
along with the same object as when no authentication was attempted, with
the addition of the `completed` key which is an array of auth types the
client has completed successfully:

    HTTP/1.1 401 Unauthorized
    Content-Type: application/json

    {
      "completed": [ "example.type.foo" ],
      "flows": [
        {
          "stages": [ "example.type.foo", "example.type.bar" ]
        },
        {
          "stages": [ "example.type.foo", "example.type.baz" ]
        }
      ],
      "params": {
          "example.type.baz": {
              "example_key": "foobar"
          }
      },
      "session": "xxxxxx"
    }

Individual stages may require more than one request to complete, in
which case the response will be as if the request was unauthenticated
with the addition of any other keys as defined by the auth type.

If the homeserver decides that an attempt on a stage was unsuccessful,
but the client may make a second attempt, it returns the same HTTP
status 401 response as above, with the addition of the standard
`errcode` and `error` fields describing the error. For example:

    HTTP/1.1 401 Unauthorized
    Content-Type: application/json

    {
      "errcode": "M_FORBIDDEN",
      "error": "Invalid password",
      "completed": [ "example.type.foo" ],
      "flows": [
        {
          "stages": [ "example.type.foo", "example.type.bar" ]
        },
        {
          "stages": [ "example.type.foo", "example.type.baz" ]
        }
      ],
      "params": {
          "example.type.baz": {
              "example_key": "foobar"
          }
      },
      "session": "xxxxxx"
    }

If the request fails for a reason other than authentication, the server
returns an error message in the standard format. For example:

    HTTP/1.1 400 Bad request
    Content-Type: application/json

    {
      "errcode": "M_EXAMPLE_ERROR",
      "error": "Something was wrong"
    }

If the client has completed all stages of a flow, the homeserver
performs the API call and returns the result as normal. Completed stages
cannot be retried by clients, therefore servers must return either a 401
response with the completed stages, or the result of the API call if all
stages were completed when a client retries a stage.

Some authentication types may be completed by means other than through
the Matrix client, for example, an email confirmation may be completed
when the user clicks on the link in the email. In this case, the client
retries the request with an auth dict containing only the session key.
The response to this will be the same as if the client were attempting
to complete an auth state normally, i.e. the request will either
complete or request auth, with the presence or absence of that auth type
in the 'completed' array indicating whether that stage is complete.

##### Example

At a high level, the requests made for an API call completing an auth
flow with three stages will resemble the following diagram:

    _______________________
    |       Stage 0         |
    | No auth               |
    |  ___________________  |
    | |_Request_1_________| | <-- Returns "session" key which is used throughout.
    |_______________________|
             |
             |
    _________V_____________
    |       Stage 1         |
    | type: "<auth type1>"  |
    |  ___________________  |
    | |_Request_1_________| |
    |_______________________|
             |
             |
    _________V_____________
    |       Stage 2         |
    | type: "<auth type2>"  |
    |  ___________________  |
    | |_Request_1_________| |
    |  ___________________  |
    | |_Request_2_________| |
    |  ___________________  |
    | |_Request_3_________| |
    |_______________________|
             |
             |
    _________V_____________
    |       Stage 3         |
    | type: "<auth type3>"  |
    |  ___________________  |
    | |_Request_1_________| | <-- Returns API response
    |_______________________|

##### Authentication types

This specification defines the following auth types:  
-   `m.login.password`
-   `m.login.recaptcha`
-   `m.login.sso`
-   `m.login.email.identity`
-   `m.login.msisdn`
-   `m.login.dummy`

#### Password-based

Type  
`m.login.password`

Description  
The client submits an identifier and secret password, both sent in
plain-text.

To use this authentication type, clients should submit an auth dict as
follows:

    {
      "type": "m.login.password",
      "identifier": {
        ...
      },
      "password": "<password>",
      "session": "<session ID>"
    }

where the `identifier` property is a user identifier object, as
described in [Identifier types](#identifier-types).

For example, to authenticate using the user's Matrix ID, clients would
submit:

    {
      "type": "m.login.password",
      "identifier": {
        "type": "m.id.user",
        "user": "<user_id or user localpart>"
      },
      "password": "<password>",
      "session": "<session ID>"
    }

Alternatively reply using a 3PID bound to the user's account on the
homeserver using the `/account/3pid`\_ API rather then giving the `user`
explicitly as follows:

    {
      "type": "m.login.password",
      "identifier": {
        "type": "m.id.thirdparty",
        "medium": "<The medium of the third party identifier.>",
        "address": "<The third party address of the user>"
      },
      "password": "<password>",
      "session": "<session ID>"
    }

In the case that the homeserver does not know about the supplied 3PID,
the homeserver must respond with 403 Forbidden.

#### Google ReCaptcha

Type  
`m.login.recaptcha`

Description  
The user completes a Google ReCaptcha 2.0 challenge

To use this authentication type, clients should submit an auth dict as
follows:

    {
      "type": "m.login.recaptcha",
      "response": "<captcha response>",
      "session": "<session ID>"
    }

#### Single Sign-On

Type  
`m.login.sso`

Description  
Authentication is supported by authorising with an external single
sign-on provider.

A client wanting to complete authentication using SSO should use the
[Fallback](#fallback) mechanism. See [SSO during User-Interactive
Authentication](#sso-during-user-interactive-authentication) for more
information.

#### Email-based (identity / homeserver)

Type  
`m.login.email.identity`

Description  
Authentication is supported by authorising an email address with an
identity server, or homeserver if supported.

Prior to submitting this, the client should authenticate with an
identity server (or homeserver). After authenticating, the session
information should be submitted to the homeserver.

To use this authentication type, clients should submit an auth dict as
follows:

    {
      "type": "m.login.email.identity",
      "threepidCreds": [
        {
          "sid": "<identity server session id>",
          "client_secret": "<identity server client secret>",
          "id_server": "<url of identity server authed with, e.g. 'matrix.org:8090'>",
          "id_access_token": "<access token previously registered with the identity server>"
        }
      ],
      "session": "<session ID>"
    }

Note that `id_server` (and therefore `id_access_token`) is optional if
the `/requestToken` request did not include them.

#### Phone number/MSISDN-based (identity / homeserver)

Type  
`m.login.msisdn`

Description  
Authentication is supported by authorising a phone number with an
identity server, or homeserver if supported.

Prior to submitting this, the client should authenticate with an
identity server (or homeserver). After authenticating, the session
information should be submitted to the homeserver.

To use this authentication type, clients should submit an auth dict as
follows:

    {
      "type": "m.login.msisdn",
      "threepidCreds": [
        {
          "sid": "<identity server session id>",
          "client_secret": "<identity server client secret>",
          "id_server": "<url of identity server authed with, e.g. 'matrix.org:8090'>",
          "id_access_token": "<access token previously registered with the identity server>"
        }
      ],
      "session": "<session ID>"
    }

Note that `id_server` (and therefore `id_access_token`) is optional if
the `/requestToken` request did not include them.

#### Dummy Auth

Type  
`m.login.dummy`

Description  
Dummy authentication always succeeds and requires no extra parameters.
Its purpose is to allow servers to not require any form of
User-Interactive Authentication to perform a request. It can also be
used to differentiate flows where otherwise one flow would be a subset
of another flow. eg. if a server offers flows `m.login.recaptcha` and
`m.login.recaptcha, m.login.email.identity` and the client completes the
recaptcha stage first, the auth would succeed with the former flow, even
if the client was intending to then complete the email auth stage. A
server can instead send flows `m.login.recaptcha, m.login.dummy` and
`m.login.recaptcha, m.login.email.identity` to fix the ambiguity.

To use this authentication type, clients should submit an auth dict with
just the type and session, if provided:

    {
      "type": "m.login.dummy",
      "session": "<session ID>"
    }

##### Fallback

Clients cannot be expected to be able to know how to process every
single login type. If a client does not know how to handle a given login
type, it can direct the user to a web browser with the URL of a fallback
page which will allow the user to complete that login step out-of-band
in their web browser. The URL it should open is:

    /_matrix/client/%CLIENT_MAJOR_VERSION%/auth/<auth type>/fallback/web?session=<session ID>

Where `auth type` is the type name of the stage it is attempting and
`session ID` is the ID of the session given by the homeserver.

This MUST return an HTML page which can perform this authentication
stage. This page must use the following JavaScript when the
authentication has been completed:

    if (window.onAuthDone) {
        window.onAuthDone();
    } else if (window.opener && window.opener.postMessage) {
        window.opener.postMessage("authDone", "*");
    }

This allows the client to either arrange for the global function
`onAuthDone` to be defined in an embedded browser, or to use the HTML5
[cross-document
messaging](https://www.w3.org/TR/webmessaging/#web-messaging) API, to
receive a notification that the authentication stage has been completed.

Once a client receives the notificaton that the authentication stage has
been completed, it should resubmit the request with an auth dict with
just the session ID:

    {
      "session": "<session ID>"
    }

#### Example

A client webapp might use the following javascript to open a popup
window which will handle unknown login types:

    /**
     * Arguments:
     *     homeserverUrl: the base url of the homeserver (eg "https://matrix.org")
     *
     *     apiEndpoint: the API endpoint being used (eg
     *        "/_matrix/client/%CLIENT_MAJOR_VERSION%/account/password")
     *
     *     loginType: the loginType being attempted (eg "m.login.recaptcha")
     *
     *     sessionID: the session ID given by the homeserver in earlier requests
     *
     *     onComplete: a callback which will be called with the results of the request
     */
    function unknownLoginType(homeserverUrl, apiEndpoint, loginType, sessionID, onComplete) {
        var popupWindow;

        var eventListener = function(ev) {
            // check it's the right message from the right place.
            if (ev.data !== "authDone" || ev.origin !== homeserverUrl) {
                return;
            }

            // close the popup
            popupWindow.close();
            window.removeEventListener("message", eventListener);

            // repeat the request
            var requestBody = {
                auth: {
                    session: sessionID,
                },
            };

            request({
                method:'POST', url:apiEndpint, json:requestBody,
            }, onComplete);
        };

        window.addEventListener("message", eventListener);

        var url = homeserverUrl +
            "/_matrix/client/%CLIENT_MAJOR_VERSION%/auth/" +
            encodeURIComponent(loginType) +
            "/fallback/web?session=" +
            encodeURIComponent(sessionID);


       popupWindow = window.open(url);
    }

##### Identifier types

Some authentication mechanisms use a user identifier object to identify
a user. The user identifier object has a `type` field to indicate the
type of identifier being used, and depending on the type, has other
fields giving the information required to identify the user as described
below.

This specification defines the following identifier types:  
-   `m.id.user`
-   `m.id.thirdparty`
-   `m.id.phone`

#### Matrix User ID

Type  
`m.id.user`

Description  
The user is identified by their Matrix ID.

A client can identify a user using their Matrix ID. This can either be
the fully qualified Matrix user ID, or just the localpart of the user
ID.

    "identifier": {
      "type": "m.id.user",
      "user": "<user_id or user localpart>"
    }

#### Third-party ID

Type  
`m.id.thirdparty`

Description  
The user is identified by a third-party identifier in canonicalised
form.

A client can identify a user using a 3PID associated with the user's
account on the homeserver, where the 3PID was previously associated
using the `/account/3pid`\_ API. See the [3PID
Types](../appendices.html#pid-types) Appendix for a list of Third-party
ID media.

    "identifier": {
      "type": "m.id.thirdparty",
      "medium": "<The medium of the third party identifier>",
      "address": "<The canonicalised third party address of the user>"
    }

#### Phone number

Type  
`m.id.phone`

Description  
The user is identified by a phone number.

A client can identify a user using a phone number associated with the
user's account, where the phone number was previously associated using
the `/account/3pid`\_ API. The phone number can be passed in as entered
by the user; the homeserver will be responsible for canonicalising it.
If the client wishes to canonicalise the phone number, then it can use
the `m.id.thirdparty` identifier type with a `medium` of `msisdn`
instead.

    "identifier": {
      "type": "m.id.phone",
      "country": "<The country that the phone number is from>",
      "phone": "<The phone number>"
    }

The `country` is the two-letter uppercase ISO-3166-1 alpha-2 country
code that the number in `phone` should be parsed as if it were dialled
from.

### Login

A client can obtain access tokens using the `/login` API.

Note that this endpoint does <span class="title-ref">not</span>
currently use the [User-Interactive Authentication
API](#user-interactive-authentication-api).

For a simple username/password login, clients should submit a `/login`
request as follows:

    {
      "type": "m.login.password",
      "identifier": {
        "type": "m.id.user",
        "user": "<user_id or user localpart>"
      },
      "password": "<password>"
    }

Alternatively, a client can use a 3PID bound to the user's account on
the homeserver using the `/account/3pid`\_ API rather then giving the
`user` explicitly, as follows:

    {
      "type": "m.login.password",
      "identifier": {
        "medium": "<The medium of the third party identifier>",
        "address": "<The canonicalised third party address of the user>"
      },
      "password": "<password>"
    }

In the case that the homeserver does not know about the supplied 3PID,
the homeserver must respond with `403 Forbidden`.

To log in using a login token, clients should submit a `/login` request
as follows:

    {
      "type": "m.login.token",
      "token": "<login token>"
    }

As with [token-based]() interactive login, the `token` must encode the
user ID. In the case that the token is not valid, the homeserver must
respond with `403 Forbidden` and an error code of `M_FORBIDDEN`.

If the homeserver advertises `m.login.sso` as a viable flow, and the
client supports it, the client should redirect the user to the
`/redirect` endpoint for [client login via SSO](#client-login-via-sso).
After authentication is complete, the client will need to submit a
`/login` request matching `m.login.token`.

{{login\_cs\_http\_api}}

{{logout\_cs\_http\_api}}

#### Login Fallback

If a client does not recognize any or all login flows it can use the
fallback login API:

    GET /_matrix/static/client/login/

This returns an HTML and JavaScript page which can perform the entire
login process. The page will attempt to call the JavaScript function
`window.onLogin` when login has been successfully completed.

Non-credential parameters valid for the `/login` endpoint can be
provided as query string parameters here. These are to be forwarded to
the login endpoint during the login process. For example:

    GET /_matrix/static/client/login/?device_id=GHTYAJCE

### Account registration and management

{{registration\_cs\_http\_api}}

##### Notes on password management

Warning

Clients SHOULD enforce that the password provided is suitably complex.
The password SHOULD include a lower-case letter, an upper-case letter, a
number and a symbol and be at a minimum 8 characters in length. Servers
MAY reject weak passwords with an error code `M_WEAK_PASSWORD`.

### Adding Account Administrative Contact Information

A homeserver may keep some contact information for administrative use.
This is independent of any information kept by any identity servers,
though can be proxied (bound) to the identity server in many cases.

Note

This section deals with two terms: "add" and "bind". Where "add" (or
"remove") is used, it is speaking about an identifier that was not bound
to an identity server. As a result, "bind" (or "unbind") references an
identifier that is found in an identity server. Note that an identifer
can be added and bound at the same time, depending on context.

{{administrative\_contact\_cs\_http\_api}}

### Current account information

{{whoami\_cs\_http\_api}}

##### Notes on identity servers

Identity servers in Matrix store bindings (relationships) between a
user's third party identifier, typically email or phone number, and
their user ID. Once a user has chosen an identity server, that identity
server should be used by all clients.

Clients can see which identity server the user has chosen through the
`m.identity_server` account data event, as described below. Clients
SHOULD refrain from making requests to any identity server until the
presence of `m.identity_server` is confirmed as (not) present. If
present, the client SHOULD check for the presence of the `base_url`
property in the event's content. If the `base_url` is present, the
client SHOULD use the identity server in that property as the identity
server for the user. If the `base_url` is missing, or the account data
event is not present, the client SHOULD use whichever default value it
normally would for an identity server, if applicable. Clients SHOULD NOT
update the account data with the default identity server when the user
is missing an identity server in their account data.

Clients SHOULD listen for changes to the `m.identity_server` account
data event and update the identity server they are contacting as a
result.

If the client offers a way to set the identity server to use, it MUST
update the value of `m.identity_server` accordingly. A `base_url` of
`null` MUST be treated as though the user does not want to use an
identity server, disabling all related functionality as a result.

Clients SHOULD refrain from populating the account data as a migration
step for users who are lacking the account data, unless the user sets
the identity server within the client to a value. For example, a user
which has no `m.identity_server` account data event should not end up
with the client's default identity server in their account data, unless
the user first visits their account settings to set the identity server.

{{m\_identity\_server\_event}}

Capabilities negotiation
------------------------

A homeserver may not support certain operations and clients must be able
to query for what the homeserver can and can't offer. For example, a
homeserver may not support users changing their password as it is
configured to perform authentication against an external system.

The capabilities advertised through this system are intended to
advertise functionality which is optional in the API, or which depend in
some way on the state of the user or server. This system should not be
used to advertise unstable or experimental features - this is better
done by the `/versions` endpoint.

Some examples of what a reasonable capability could be are:

-   Whether the server supports user presence.
-   Whether the server supports optional features, such as the user or
    room directories.
-   The rate limits or file type restrictions imposed on clients by the
    server.

Some examples of what should **not** be a capability are:

-   Whether the server supports a feature in the `unstable`
    specification.
-   Media size limits - these are handled by the
    `/media/%CLIENT_MAJOR_VERSION%/config` API.
-   Optional encodings or alternative transports for communicating with
    the server.

Capabilities prefixed with `m.` are reserved for definition in the
Matrix specification while other values may be used by servers using the
Java package naming convention. The capabilities supported by the Matrix
specification are defined later in this section.

{{capabilities\_cs\_http\_api}}

### `m.change_password` capability

This capability has a single flag, `enabled`, which indicates whether or
not the user can use the `/account/password` API to change their
password. If not present, the client should assume that password changes
are possible via the API. When present, clients SHOULD respect the
capability's `enabled` flag and indicate to the user if they are unable
to change their password.

An example of the capability API's response for this capability is:

    {
      "capabilities": {
        "m.change_password": {
          "enabled": false
        }
      }
    }

### `m.room_versions` capability

This capability describes the default and available room versions a
server supports, and at what level of stability. Clients should make use
of this capability to determine if users need to be encouraged to
upgrade their rooms.

An example of the capability API's response for this capability is:

    {
      "capabilities": {
        "m.room_versions": {
          "default": "1",
          "available": {
            "1": "stable",
            "2": "stable",
            "3": "unstable",
            "custom-version": "unstable"
          }
        }
      }
    }

This capability mirrors the same restrictions of [room
versions](../index.html#room-versions) to describe which versions are
stable and unstable. Clients should assume that the `default` version is
`stable`. Any version not explicitly labelled as `stable` in the
`available` versions is to be treated as `unstable`. For example, a
version listed as `future-stable` should be treated as `unstable`.

The `default` version is the version the server is using to create new
rooms. Clients should encourage users with sufficient permissions in a
room to upgrade their room to the `default` version when the room is
using an `unstable` version.

When this capability is not listed, clients should use `"1"` as the
default and only stable `available` room version.

Pagination
----------

Note

The paths referred to in this section are not actual endpoints. They
only serve as examples to explain how pagination functions.

Pagination is the process of dividing a dataset into multiple discrete
pages. Matrix makes use of pagination to allow clients to view extremely
large datasets. These datasets are not limited to events in a room (for
example clients may want to paginate a list of rooms in addition to
events within those rooms). Regardless of what is being paginated, there
is a common approach which is used to give clients an easy way of
selecting subsets of a potentially changing dataset. Each endpoint that
uses pagination may use different parameters. However the theme among
them is that they take a `from` and `to` token, and occasionally a
`limit` and `dir`. Together, these parameters describe the position in a
data set, where `from` and `to` are known as "stream tokens" matching
the regular expression `[a-zA-Z0-9.=_-]+`. If supported, the `dir`
defines the direction of events to return: either forwards (`f`) or
backwards (`b`). The response may contain tokens that can be used for
retrieving results before or after the returned set. These tokens may be
called <span class="title-ref">start</span> or <span
class="title-ref">prev\_batch</span> for retrieving the previous result
set, or <span class="title-ref">end</span>, <span
class="title-ref">next\_batch</span> or <span
class="title-ref">next\_token</span> for retrieving the next result set.

In the following examples, 'START' and 'END' are placeholders to signify
the start and end of the data sets respectively.

For example, if an endpoint had events E1 -&gt; E15. The client wants
the last 5 events and doesn't know any previous events:

    S                                                    E
    |-E1-E2-E3-E4-E5-E6-E7-E8-E9-E10-E11-E12-E13-E14-E15-|
    |                               |                    |
    |                          _____|  <--backwards--    |
    |__________________       |         |        ________|
                       |      |         |        |
     GET /somepath?to=START&limit=5&dir=b&from=END
     Returns:
       E15,E14,E13,E12,E11

Another example: a public room list has rooms R1 -&gt; R17. The client
is showing 5 rooms at a time on screen, and is on page 2. They want to
now show page 3 (rooms R11 -&gt; 15):

    S                                                           E
    |  0  1  2  3  4  5  6  7  8  9  10  11  12  13  14  15  16 | stream token
    |-R1-R2-R3-R4-R5-R6-R7-R8-R9-R10-R11-R12-R13-R14-R15-R16-R17| room
                      |____________| |________________|
                            |                |
                        Currently            |
                        viewing              |
                                             |
                             GET /roomslist?from=9&to=END&limit=5
                             Returns: R11,R12,R13,R14,R15

Note that tokens are treated in an *exclusive*, not inclusive, manner.
The end token from the initial request was '9' which corresponded to
R10. When the 2nd request was made, R10 did not appear again, even
though from=9 was specified. If you know the token, you already have the
data.

Responses for pagination-capable endpoints SHOULD have a `chunk` array
alongside the applicable stream tokens to represent the result set.

In general, when the end of a result set is reached the applicable
stream token will be excluded from the response. For example, if a user
was backwards-paginating events in a room they'd eventually reach the
first event in the room. In this scenario, the `prev_batch` token would
be excluded from the response. Some paginated endpoints are open-ended
in one direction, such as endpoints which expose an event stream for an
active room. In this case, it is not possible for the client to reach
the true "end" of the data set and therefore should always be presented
with a token to keep moving forwards.

Filtering
---------

Filters can be created on the server and can be passed as a parameter to
APIs which return events. These filters alter the data returned from
those APIs. Not all APIs accept filters.

### Lazy-loading room members

Membership events often take significant resources for clients to track.
In an effort to reduce the number of resources used, clients can enable
"lazy-loading" for room members. By doing this, servers will attempt to
only send membership events which are relevant to the client.

It is important to understand that lazy-loading is not intended to be a
perfect optimisation, and that it may not be practical for the server to
calculate precisely which membership events are relevant to the client.
As a result, it is valid for the server to send redundant membership
events to the client to ease implementation, although such redundancy
should be minimised where possible to conserve bandwidth.

In terms of filters, lazy-loading is enabled by enabling
`lazy_load_members` on a `RoomEventFilter` (or a `StateFilter` in the
case of `/sync` only). When enabled, lazy-loading aware endpoints (see
below) will only include membership events for the `sender` of events
being included in the response. For example, if a client makes a `/sync`
request with lazy-loading enabled, the server will only return
membership events for the `sender` of events in the timeline, not all
members of a room.

When processing a sequence of events (e.g. by looping on `/sync` or
paginating `/messages`), it is common for blocks of events in the
sequence to share a similar set of senders. Rather than responses in the
sequence sending duplicate membership events for these senders to the
client, the server MAY assume that clients will remember membership
events they have already been sent, and choose to skip sending
membership events for members whose membership has not changed. These
are called 'redundant membership events'. Clients may request that
redundant membership events are always included in responses by setting
`include_redundant_members` to true in the filter.

The expected pattern for using lazy-loading is currently:

-   Client performs an initial /sync with lazy-loading enabled, and
    receives only the membership events which relate to the senders of
    the events it receives.
-   Clients which support display-name tab-completion or other
    operations which require rapid access to all members in a room
    should call /members for the currently selected room, with an `?at`
    parameter set to the /sync response's from token. The member list
    for the room is then maintained by the state in subsequent
    incremental /sync responses.
-   Clients which do not support tab-completion may instead pull in
    profiles for arbitrary users (e.g. read receipts, typing
    notifications) on demand by querying the room state or `/profile`.

The current endpoints which support lazy-loading room members are:

-   `/sync`\_
-   `/rooms/<room_id>/messages`\_
-   `/rooms/{roomId}/context/{eventId}`\_

### API endpoints

{{filter\_cs\_http\_api}}

Events
------

The model of conversation history exposed by the client-server API can
be considered as a list of events. The server 'linearises' the
eventually-consistent event graph of events into an 'event stream' at
any given point in time:

    [E0]->[E1]->[E2]->[E3]->[E4]->[E5]

Warning

The format of events can change depending on room version. Check the
[room version specification](../index.html#room-versions) for specific
details on what to expect for event formats. Examples contained within
the client-server specification are expected to be compatible with all
specified room versions, however some differences may still apply.

For this version of the specification, clients only need to worry about
the event ID format being different depending on room version. Clients
should not be parsing the event ID, and instead be treating it as an
opaque string. No changes should be required to support the currently
available room versions.

### Types of room events

Room events are split into two categories:

State Events  
These are events which update the metadata state of the room (e.g. room
topic, room membership etc). State is keyed by a tuple of event `type`
and a `state_key`. State in the room with the same key-tuple will be
overwritten.

Message events  
These are events which describe transient "once-off" activity in a room:
typically communication such as sending an instant message or setting up
a VoIP call.

This specification outlines several events, all with the event type
prefix `m.`. (See [Room Events](#room-events) for the m. event
specification.) However, applications may wish to add their own type of
event, and this can be achieved using the REST API detailed in the
following sections. If new events are added, the event `type` key SHOULD
follow the Java package naming convention, e.g.
`com.example.myapp.event`. This ensures event types are suitably
namespaced for each application and reduces the risk of clashes.

Note

Events are not limited to the types defined in this specification. New
or custom event types can be created on a whim using the Java package
naming convention. For example, a `com.example.game.score` event can be
sent by clients and other clients would receive it through Matrix,
assuming the client has access to the `com.example` namespace.

Note that the structure of these events may be different than those in
the server-server API.

{{common\_event\_fields}}

{{common\_room\_event\_fields}}

##### State Event Fields

In addition to the fields of a Room Event, State Events have the
following fields.

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 16%" />
<col style="width: 67%" />
</colgroup>
<thead>
<tr class="header">
<th>Key</th>
<th>Type</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>state_key</td>
<td>string</td>
<td><strong>Required.</strong> A unique key which defines the overwriting semantics for this piece of room state. This value is often a zero-length string. The presence of this key makes this event a State Event. State keys starting with an <code>@</code> are reserved for referencing user IDs, such as room members. With the exception of a few events, state events set with a given user's ID as the state key MUST only be set by that user.</td>
</tr>
<tr class="even">
<td>prev_content</td>
<td>EventContent</td>
<td>Optional. The previous <code>content</code> for this event. If there is no previous content, this key will be missing.</td>
</tr>
</tbody>
</table>

### Size limits

The complete event MUST NOT be larger than 65535 bytes, when formatted
as a [PDU for the Server-Server
protocol](../server_server/%SERVER_RELEASE_LABEL%#pdus), including any
signatures, and encoded as [Canonical
JSON](../appendices.html#canonical-json).

There are additional restrictions on sizes per key:

-   `sender` MUST NOT exceed 255 bytes (including domain).
-   `room_id` MUST NOT exceed 255 bytes.
-   `state_key` MUST NOT exceed 255 bytes.
-   `type` MUST NOT exceed 255 bytes.
-   `event_id` MUST NOT exceed 255 bytes.

Some event types have additional size restrictions which are specified
in the description of the event. Additional keys have no limit other
than that implied by the total 65 KB limit on events.

### Room Events

Note

This section is a work in progress.

This specification outlines several standard event types, all of which
are prefixed with `m.`

{{m\_room\_canonical\_alias\_event}}

{{m\_room\_create\_event}}

{{m\_room\_join\_rules\_event}}

{{m\_room\_member\_event}}

{{m\_room\_power\_levels\_event}}

{{m\_room\_redaction\_event}}

##### Historical events

Some events within the `m.` namespace might appear in rooms, however
they serve no significant meaning in this version of the specification.
They are:

-   `m.room.aliases`

Previous versions of the specification have more information on these
events.

### Syncing

To read events, the intended flow of operation is for clients to first
call the `/sync`\_ API without a `since` parameter. This returns the
most recent message events for each room, as well as the state of the
room at the start of the returned timeline. The response also includes a
`next_batch` field, which should be used as the value of the `since`
parameter in the next call to `/sync`. Finally, the response includes,
for each room, a `prev_batch` field, which can be passed as a `start`
parameter to the `/rooms/<room_id>/messages`\_ API to retrieve earlier
messages.

You can visualise the range of events being returned as:

    [E0]->[E1]->[E2]->[E3]->[E4]->[E5]
               ^                      ^
               |                      |
         prev_batch: '1-2-3'        next_batch: 'a-b-c'

Clients then receive new events by "long-polling" the homeserver via the
`/sync` API, passing the value of the `next_batch` field from the
response to the previous call as the `since` parameter. The client
should also pass a `timeout` parameter. The server will then hold open
the HTTP connection for a short period of time waiting for new events,
returning early if an event occurs. Only the `/sync` API (and the
deprecated `/events` API) support long-polling in this way.

The response for such an incremental sync can be visualised as:

    [E0]->[E1]->[E2]->[E3]->[E4]->[E5]->[E6]
                                      ^     ^
                                      |     |
                                      |  next_batch: 'x-y-z'
                                    prev_batch: 'a-b-c'

Normally, all new events which are visible to the client will appear in
the response to the `/sync` API. However, if a large number of events
arrive between calls to `/sync`, a "limited" timeline is returned,
containing only the most recent message events. A state "delta" is also
returned, summarising any state changes in the omitted part of the
timeline. The client may therefore end up with "gaps" in its knowledge
of the message timeline. The client can fill these gaps using the
`/rooms/<room_id>/messages`\_ API. This situation looks like this:

    | gap |
    | <-> |
    [E0]->[E1]->[E2]->[E3]->[E4]->[E5]->[E6]->[E7]->[E8]->[E9]->[E10]
          ^                        ^
          |                        |
     prev_batch: 'd-e-f'       next_batch: 'u-v-w'

Warning

Events are ordered in this API according to the arrival time of the
event on the homeserver. This can conflict with other APIs which order
events based on their partial ordering in the event graph. This can
result in duplicate events being received (once per distinct API
called). Clients SHOULD de-duplicate events based on the event ID when
this happens.

Note

The `/sync` API returns a `state` list which is separate from the
`timeline`. This `state` list allows clients to keep their model of the
room state in sync with that on the server. In the case of an initial
(`since`-less) sync, the `state` list represents the complete state of
the room at the **start** of the returned timeline (so in the case of a
recently-created room whose state fits entirely in the `timeline`, the
`state` list will be empty).

In the case of an incremental sync, the `state` list gives a delta
between the state of the room at the `since` parameter and that at the
start of the returned `timeline`. (It will therefore be empty unless the
timeline was `limited`.)

In both cases, it should be noted that the events returned in the
`state` list did **not** necessarily take place just before the returned
`timeline`, so clients should not display them to the user in the
timeline.

Rationale

An early design of this specification made the `state` list represent
the room state at the end of the returned timeline, instead of the
start. This was unsatisfactory because it led to duplication of events
between the `state` list and the `timeline`, but more importantly, it
made it difficult for clients to show the timeline correctly.

In particular, consider a returned timeline \[M0, S1, M2\], where M0 and
M2 are both messages sent by the same user, and S1 is a state event
where that user changes their displayname. If the `state` list
represents the room state at the end of the timeline, the client must
take a copy of the state dictionary, and *rewind* S1, in order to
correctly calculate the display name for M0.

{{sync\_cs\_http\_api}}

{{old\_sync\_cs\_http\_api}}

### Getting events for a room

There are several APIs provided to `GET` events for a room:

{{rooms\_cs\_http\_api}}

{{message\_pagination\_cs\_http\_api}}

{{room\_initial\_sync\_cs\_http\_api}}

### Sending events to a room

{{room\_state\_cs\_http\_api}}

**Examples**

Valid requests look like:

    PUT /rooms/!roomid:domain/state/m.example.event
    { "key" : "without a state key" }

    PUT /rooms/!roomid:domain/state/m.another.example.event/foo
    { "key" : "with 'foo' as the state key" }

In contrast, these requests are invalid:

    POST /rooms/!roomid:domain/state/m.example.event/
    { "key" : "cannot use POST here" }

    PUT /rooms/!roomid:domain/state/m.another.example.event/foo/11
    { "key" : "txnIds are not supported" }

Care should be taken to avoid setting the wrong `state key`:

    PUT /rooms/!roomid:domain/state/m.another.example.event/11
    { "key" : "with '11' as the state key, but was probably intended to be a txnId" }

The `state_key` is often used to store state about individual users, by
using the user ID as the `state_key` value. For example:

    PUT /rooms/!roomid:domain/state/m.favorite.animal.event/%40my_user%3Aexample.org
    { "animal" : "cat", "reason": "fluffy" }

In some cases, there may be no need for a `state_key`, so it can be
omitted:

    PUT /rooms/!roomid:domain/state/m.room.bgd.color
    { "color": "red", "hex": "#ff0000" }

{{room\_send\_cs\_http\_api}}

### Redactions

Since events are extensible it is possible for malicious users and/or
servers to add keys that are, for example offensive or illegal. Since
some events cannot be simply deleted, e.g. membership events, we instead
'redact' events. This involves removing all keys from an event that are
not required by the protocol. This stripped down event is thereafter
returned anytime a client or remote server requests it. Redacting an
event cannot be undone, allowing server owners to delete the offending
content from the databases. Events that have been redacted include a
`redacted_because` key whose value is the event that caused it to be
redacted, which may include a reason.

The exact algorithm to apply against an event is defined in the [room
version specification](../index.html#room-versions).

The server should add the event causing the redaction to the `unsigned`
property of the redacted event, under the `redacted_because` key. When a
client receives a redaction event it should change the redacted event in
the same way a server does.

Note

Redacted events can still affect the state of the room. When redacted,
state events behave as though their properties were simply not
specified, except those protected by the redaction algorithm. For
example, a redacted `join` event will still result in the user being
considered joined. Similarly, a redacted topic does not necessarily
cause the topic to revert to what is was prior to the event - it causes
the topic to be removed from the room.

##### Events

{{m\_room\_redaction\_event}}

##### Client behaviour

{{redaction\_cs\_http\_api}}

Rooms
-----

### Creation

The homeserver will create an `m.room.create` event when a room is
created, which serves as the root of the event graph for this room. This
event also has a `creator` key which contains the user ID of the room
creator. It will also generate several other events in order to manage
permissions in this room. This includes:

-   `m.room.power_levels` : Sets the power levels of users and required power  
    levels for various actions within the room such as sending events.

-   `m.room.join_rules` : Whether the room is "invite-only" or not.

See [Room Events](#room-events) for more information on these events. To
create a room, a client has to use the following API.

{{create\_room\_cs\_http\_api}}

### Room aliases

Servers may host aliases for rooms with human-friendly names. Aliases
take the form `#friendlyname:server.name`.

As room aliases are scoped to a particular homeserver domain name, it is
likely that a homeserver will reject attempts to maintain aliases on
other domain names. This specification does not provide a way for
homeservers to send update requests to other servers. However,
homeservers MUST handle `GET` requests to resolve aliases on other
servers; they should do this using the federation API if necessary.

Rooms do not store a list of all aliases present on a room, though
members of the room with relevant permissions may publish preferred
aliases through the `m.room.canonical_alias` state event. The aliases in
the state event should point to the room ID they are published within,
however room aliases can and do drift to other room IDs over time.
Clients SHOULD NOT treat the aliases as accurate. They SHOULD be checked
before they are used or shared with another user. If a room appears to
have a room alias of `#alias:example.com`, this SHOULD be checked to
make sure that the room's ID matches the `room_id` returned from the
request.

{{directory\_cs\_http\_api}}

### Permissions

Note

This section is a work in progress.

Permissions for rooms are done via the concept of power levels - to do
any action in a room a user must have a suitable power level. Power
levels are stored as state events in a given room. The power levels
required for operations and the power levels for users are defined in
`m.room.power_levels`, where both a default and specific users' power
levels can be set. By default all users have a power level of 0, other
than the room creator whose power level defaults to 100. Users can grant
other users increased power levels up to their own power level. For
example, user A with a power level of 50 could increase the power level
of user B to a maximum of level 50. Power levels for users are tracked
per-room even if the user is not present in the room. The keys contained
in `m.room.power_levels` determine the levels required for certain
operations such as kicking, banning and sending state events. See
[m.room.power\_levels]() for more information.

Clients may wish to assign names to particular power levels. A suggested
mapping is as follows: - 0 User - 50 Moderator - 100 Admin

### Room membership

Users need to be a member of a room in order to send and receive events
in that room. There are several states in which a user may be, in
relation to a room:

-   Unrelated (the user cannot send or receive events in the room)
-   Invited (the user has been invited to participate in the room, but
    is not yet participating)
-   Joined (the user can send and receive events in the room)
-   Banned (the user is not allowed to join the room)

There is an exception to the requirement that a user join a room before
sending events to it: users may send an `m.room.member` event to a room
with `content.membership` set to `leave` to reject an invitation if they
have currently been invited to a room but have not joined it.

Some rooms require that users be invited to it before they can join;
others allow anyone to join. Whether a given room is an "invite-only"
room is determined by the room config key `m.room.join_rules`. It can
have one of the following values:

`public`  
This room is free for anyone to join without an invite.

`invite`  
This room can only be joined if you were invited.

The allowable state transitions of membership are:

    /ban
    +------------------------------------------------------+
    |                                                      |
    |  +----------------+  +----------------+              |
    |  |    /leave      |  |                |              |
    |  |                v  v                |              |
    /invite    +--------+           +-------+             |              |
    ------------>| invite |<----------| leave |----+        |              |
    +--------+  /invite  +-------+    |        |              |
    |                   |    ^      |        |              |
    |                   |    |      |        |              |
    /join |   +---------------+    |      |        |              |
    |   | /join if           |      |        |              |
    |   | join_rules         |      | /ban   | /unban       |
    |   | public      /leave |      |        |              |
    v   v               or   |      |        |              |
    +------+            /kick  |      |        |              |
    ------------>| join |-------------------+      |        |              |
    /join       +------+                          v        |              |
    if             |                           +-----+     |              |
    join_rules     +-------------------------->| ban |-----+              |
    public                   /ban              +-----+                    |
             ^ ^                      |
             | |                      |
    ----------------------------------------------+ +----------------------+
    /ban

{{list\_joined\_rooms\_cs\_http\_api}}

##### Joining rooms

{{inviting\_cs\_http\_api}}

{{joining\_cs\_http\_api}}

##### Leaving rooms

A user can leave a room to stop receiving events for that room. A user
must have been invited to or have joined the room before they are
eligible to leave the room. Leaving a room to which the user has been
invited rejects the invite. Once a user leaves a room, it will no longer
appear in the response to the `/sync`\_ API unless it is explicitly
requested via a filter with the `include_leave` field set to `true`.

Whether or not they actually joined the room, if the room is an
"invite-only" room the user will need to be re-invited before they can
re-join the room.

A user can also forget a room which they have left. Rooms which have
been forgotten will never appear the response to the `/sync`\_ API,
until the user re-joins or is re-invited.

A user may wish to force another user to leave a room. This can be done
by 'kicking' the other user. To do so, the user performing the kick MUST
have the required power level. Once a user has been kicked, the
behaviour is the same as if they had left of their own accord. In
particular, the user is free to re-join if the room is not
"invite-only".

{{leaving\_cs\_http\_api}}

{{kicking\_cs\_http\_api}}

##### Banning users in a room

A user may decide to ban another user in a room. 'Banning' forces the
target user to leave the room and prevents them from re-joining the
room. A banned user will not be treated as a joined user, and so will
not be able to send or receive events in the room. In order to ban
someone, the user performing the ban MUST have the required power level.
To ban a user, a request should be made to `/rooms/<room_id>/ban`\_
with:

    {
      "user_id": "<user id to ban>"
      "reason": "string: <reason for the ban>"
    }

Banning a user adjusts the banned member's membership state to `ban`.
Like with other membership changes, a user can directly adjust the
target member's state, by making a request to
`/rooms/<room id>/state/m.room.member/<user id>`:

    {
      "membership": "ban"
    }

A user must be explicitly unbanned with a request to
`/rooms/<room_id>/unban`\_ before they can re-join the room or be
re-invited.

{{banning\_cs\_http\_api}}

### Listing rooms

{{list\_public\_rooms\_cs\_http\_api}}

User Data
---------

### User Directory

{{users\_cs\_http\_api}}

### Profiles

{{profile\_cs\_http\_api}}

##### Events on Change of Profile Information

Because the profile display name and avatar information are likely to be
used in many places of a client's display, changes to these fields cause
an automatic propagation event to occur, informing likely-interested
parties of the new values. This change is conveyed using two separate
mechanisms:

-   a `m.room.member` event (with a `join` membership) is sent to every
    room the user is a member of, to update the `displayname` and
    `avatar_url`.
-   a `m.presence` presence status update is sent, again containing the
    new values of the `displayname` and `avatar_url` keys, in addition
    to the required `presence` key containing the current presence state
    of the user.

Both of these should be done automatically by the homeserver when a user
successfully changes their display name or avatar URL fields.

Additionally, when homeservers emit room membership events for their own
users, they should include the display name and avatar URL fields in
these events so that clients already have these details to hand, and do
not have to perform extra round trips to query it.

Security
--------

### Rate limiting

Homeservers SHOULD implement rate limiting to reduce the risk of being
overloaded. If a request is refused due to rate limiting, it should
return a standard error response of the form:

    {
      "errcode": "M_LIMIT_EXCEEDED",
      "error": "string",
      "retry_after_ms": integer (optional)
    }

The `retry_after_ms` key SHOULD be included to tell the client how long
they have to wait in milliseconds before they can try again.

Modules
-------

Modules are parts of the Client-Server API which are not universal to
all endpoints. Modules are strictly defined within this specification
and should not be mistaken for experimental extensions or optional
features. A compliant server implementation MUST support all modules and
supporting specification (unless the implementation only targets clients
of certain profiles, in which case only the required modules for those
feature profiles MUST be implemented). A compliant client implementation
MUST support all the required modules and supporting specification for
the [Feature Profile](#feature-profiles) it targets.

### Instant Messaging

This module adds support for sending human-readable messages to a room.
It also adds support for associating human-readable information with the
room itself such as a room name and topic.

##### Events

{{m\_room\_message\_event}}

{{m\_room\_message\_feedback\_event}}

Usage of this event is discouraged for several reasons:  
-   The number of feedback events will grow very quickly with the number
    of users in the room. This event provides no way to "batch"
    feedback, unlike the [receipts module](#module:receipts).
-   Pairing feedback to messages gets complicated when paginating as
    feedback arrives before the message it is acknowledging.
-   There are no guarantees that the client has seen the event ID being
    acknowledged.

{{m\_room\_name\_event}}

{{m\_room\_topic\_event}}

{{m\_room\_avatar\_event}}

{{m\_room\_pinned\_events\_event}}

###### m.room.message msgtypes

Each [m.room.message]() MUST have a `msgtype` key which identifies the
type of message being sent. Each type has their own required and
optional keys, as outlined below. If a client cannot display the given
`msgtype` then it SHOULD display the fallback plain text `body` key
instead.

Some message types support HTML in the event content that clients should
prefer to display if available. Currently `m.text`, `m.emote`, and
`m.notice` support an additional `format` parameter of
`org.matrix.custom.html`. When this field is present, a `formatted_body`
with the HTML must be provided. The plain text version of the HTML
should be provided in the `body`.

Clients should limit the HTML they render to avoid Cross-Site Scripting,
HTML injection, and similar attacks. The strongly suggested set of HTML
tags to permit, denying the use and rendering of anything else, is:
`font`, `del`, `h1`, `h2`, `h3`, `h4`, `h5`, `h6`, `blockquote`, `p`,
`a`, `ul`, `ol`, `sup`, `sub`, `li`, `b`, `i`, `u`, `strong`, `em`,
`strike`, `code`, `hr`, `br`, `div`, `table`, `thead`, `tbody`, `tr`,
`th`, `td`, `caption`, `pre`, `span`, `img`.

Not all attributes on those tags should be permitted as they may be
avenues for other disruption attempts, such as adding `onclick` handlers
or excessively large text. Clients should only permit the attributes
listed for the tags below. Where `data-mx-bg-color` and `data-mx-color`
are listed, clients should translate the value (a 6-character hex color
code) to the appropriate CSS/attributes for the tag.

`font`  
`data-mx-bg-color`, `data-mx-color`

`span`  
`data-mx-bg-color`, `data-mx-color`

`a`  
`name`, `target`, `href` (provided the value is not relative and has a
scheme matching one of: `https`, `http`, `ftp`, `mailto`, `magnet`)

`img`  
`width`, `height`, `alt`, `title`, `src` (provided it is a [Matrix
Content (MXC) URI](#module:content))

`ol`  
`start`

`code`  
`class` (only classes which start with `language-` for syntax
highlighting)

Additionally, web clients should ensure that *all* `a` tags get a
`rel="noopener"` to prevent the target page from referencing the
client's tab/window.

Tags must not be nested more than 100 levels deep. Clients should only
support the subset of tags they can render, falling back to other
representations of the tags where possible. For example, a client may
not be able to render tables correctly and instead could fall back to
rendering tab-delimited text.

In addition to not rendering unsafe HTML, clients should not emit unsafe
HTML in events. Likewise, clients should not generate HTML that is not
needed, such as extra paragraph tags surrounding text due to Rich Text
Editors. HTML included in events should otherwise be valid, such as
having appropriate closing tags, appropriate attributes (considering the
custom ones defined in this specification), and generally valid
structure.

A special tag, `mx-reply`, may appear on rich replies (described below)
and should be allowed if, and only if, the tag appears as the very first
tag in the `formatted_body`. The tag cannot be nested and cannot be
located after another tag in the tree. Because the tag contains HTML, an
`mx-reply` is expected to have a partner closing tag and should be
treated similar to a `div`. Clients that support rich replies will end
up stripping the tag and its contents and therefore may wish to exclude
the tag entirely.

Note

A future iteration of the specification will support more powerful and
extensible message formatting options, such as the proposal
[MSC1225](https://github.com/matrix-org/matrix-doc/issues/1225).

{{msgtype\_events}}

##### Client behaviour

Clients SHOULD verify the structure of incoming events to ensure that
the expected keys exist and that they are of the right type. Clients can
discard malformed events or display a placeholder message to the user.
Redacted `m.room.message` events MUST be removed from the client. This
can either be replaced with placeholder text (e.g. "\[REDACTED\]") or
the redacted message can be removed entirely from the messages view.

Events which have attachments (e.g. `m.image`, `m.file`) SHOULD be
uploaded using the [content repository module](#module:content) where
available. The resulting `mxc://` URI can then be used in the `url` key.

Clients MAY include a client generated thumbnail image for an attachment
under a `info.thumbnail_url` key. The thumbnail SHOULD also be a
`mxc://` URI. Clients displaying events with attachments can either use
the client generated thumbnail or ask its homeserver to generate a
thumbnail from the original attachment using the [content repository
module](#module:content).

###### Recommendations when sending messages

In the event of send failure, clients SHOULD retry requests using an
exponential-backoff algorithm for a certain amount of time T. It is
recommended that T is no longer than 5 minutes. After this time, the
client should stop retrying and mark the message as "unsent". Users
should be able to manually resend unsent messages.

Users may type several messages at once and send them all in quick
succession. Clients SHOULD preserve the order in which they were sent by
the user. This means that clients should wait for the response to the
previous request before sending the next request. This can lead to
head-of-line blocking. In order to reduce the impact of head-of-line
blocking, clients should use a queue per room rather than a global
queue, as ordering is only relevant within a single room rather than
between rooms.

###### Local echo

Messages SHOULD appear immediately in the message view when a user
presses the "send" button. This should occur even if the message is
still sending. This is referred to as "local echo". Clients SHOULD
implement "local echo" of messages. Clients MAY display messages in a
different format to indicate that the server has not processed the
message. This format should be removed when the server responds.

Clients need to be able to match the message they are sending with the
same message which they receive from the event stream. The echo of the
same message from the event stream is referred to as "remote echo". Both
echoes need to be identified as the same message in order to prevent
duplicate messages being displayed. Ideally this pairing would occur
transparently to the user: the UI would not flicker as it transitions
from local to remote. Flickering can be reduced through clients making
use of the transaction ID they used to send a particular event. The
transaction ID used will be included in the event's `unsigned` data as
`transaction_id` when it arrives through the event stream.

Clients unable to make use of the transaction ID are likely to
experience flickering when the remote echo arrives on the event stream
*before* the request to send the message completes. In that case the
event arrives before the client has obtained an event ID, making it
impossible to identify it as a remote echo. This results in the client
displaying the message twice for some time (depending on the server
responsiveness) before the original request to send the message
completes. Once it completes, the client can take remedial actions to
remove the duplicate event by looking for duplicate event IDs.

###### Calculating the display name for a user

Clients may wish to show the human-readable display name of a room
member as part of a membership list, or when they send a message.
However, different members may have conflicting display names. Display
names MUST be disambiguated before showing them to the user, in order to
prevent spoofing of other users.

To ensure this is done consistently across clients, clients SHOULD use
the following algorithm to calculate a disambiguated display name for a
given user:

1.  Inspect the `m.room.member` state event for the relevant user id.
2.  If the `m.room.member` state event has no `displayname` field, or if
    that field has a `null` value, use the raw user id as the display
    name. Otherwise:
3.  If the `m.room.member` event has a `displayname` which is unique
    among members of the room with `membership: join` or
    `membership: invite`, use the given `displayname` as the
    user-visible display name. Otherwise:
4.  The `m.room.member` event has a non-unique `displayname`. This
    should be disambiguated using the user id, for example "display name
    (@id:homeserver.org)".

Developers should take note of the following when implementing the above
algorithm:

-   The user-visible display name of one member can be affected by
    changes in the state of another member. For example, if
    `@user1:matrix.org` is present in a room, with `displayname: Alice`,
    then when `@user2:example.com` joins the room, also with
    `displayname: Alice`, *both* users must be given disambiguated
    display names. Similarly, when one of the users then changes their
    display name, there is no longer a clash, and *both* users can be
    given their chosen display name. Clients should be alert to this
    possibility and ensure that all affected users are correctly
    renamed.
-   The display name of a room may also be affected by changes in the
    membership list. This is due to the room name sometimes being based
    on user display names (see [Calculating the display name for a
    room](#calculating-the-display-name-for-a-room)).
-   If the entire membership list is searched for clashing display
    names, this leads to an O(N^2) implementation for building the list
    of room members. This will be very inefficient for rooms with large
    numbers of members. It is recommended that client implementations
    maintain a hash table mapping from `displayname` to a list of room
    members using that name. Such a table can then be used for efficient
    calculation of whether disambiguation is needed.

###### Displaying membership information with messages

Clients may wish to show the display name and avatar URL of the room
member who sent a message. This can be achieved by inspecting the
`m.room.member` state event for that user ID (see [Calculating the
display name for a user](#calculating-the-display-name-for-a-user)).

When a user paginates the message history, clients may wish to show the
**historical** display name and avatar URL for a room member. This is
possible because older `m.room.member` events are returned when
paginating. This can be implemented efficiently by keeping two sets of
room state: old and current. As new events arrive and/or the user
paginates back in time, these two sets of state diverge from each other.
New events update the current state and paginated events update the old
state. When paginated events are processed sequentially, the old state
represents the state of the room *at the time the event was sent*. This
can then be used to set the historical display name and avatar URL.

###### Calculating the display name for a room

Clients may wish to show a human-readable name for a room. There are a
number of possibilities for choosing a useful name. To ensure that rooms
are named consistently across clients, clients SHOULD use the following
algorithm to choose a name:

1.  If the room has an [m.room.name]() state event with a non-empty
    `name` field, use the name given by that field.
2.  If the room has an [m.room.canonical\_alias]() state event with a
    valid `alias` field, use the alias given by that field as the name.
    Note that clients should avoid using `alt_aliases` when calculating
    the room name.
3.  If none of the above conditions are met, a name should be composed
    based on the members of the room. Clients should consider
    [m.room.member]() events for users other than the logged-in user, as
    defined below.
    1.  If the number of `m.heroes` for the room are greater or equal to
        `m.joined_member_count + m.invited_member_count - 1`, then use
        the membership events for the heroes to calculate display names
        for the users ([disambiguating them if
        required](#calculating-the-display-name-for-a-user)) and
        concatenating them. For example, the client may choose to show
        "Alice, Bob, and Charlie (@charlie:example.org)" as the room
        name. The client may optionally limit the number of users it
        uses to generate a room name.
    2.  If there are fewer heroes than
        `m.joined_member_count + m.invited_member_count - 1`, and
        `m.joined_member_count + m.invited_member_count` is greater than
        1, the client should use the heroes to calculate display names
        for the users ([disambiguating them if
        required](#calculating-the-display-name-for-a-user)) and
        concatenating them alongside a count of the remaining users. For
        example, "Alice, Bob, and 1234 others".
    3.  If `m.joined_member_count + m.invited_member_count` is less than
        or equal to 1 (indicating the member is alone), the client
        should use the rules above to indicate that the room was empty.
        For example, "Empty Room (was Alice)", "Empty Room (was Alice
        and 1234 others)", or "Empty Room" if there are no heroes.

Clients SHOULD internationalise the room name to the user's language
when using the `m.heroes` to calculate the name. Clients SHOULD use
minimum 5 heroes to calculate room names where possible, but may use
more or less to fit better with their user experience.

###### Forming relationships between events

In some cases, events may wish to reference other events. This could be
to form a thread of messages for the user to follow along with, or to
provide more context as to what a particular event is describing.
Currently, the only kind of relation defined is a "rich reply" where a
user may reference another message to create a thread-like conversation.

Relationships are defined under an `m.relates_to` key in the event's
`content`. If the event is of the type `m.room.encrypted`, the
`m.relates_to` key MUST NOT be covered by the encryption and instead be
put alongside the encryption information held in the `content`.

####### Rich replies

Users may wish to reference another message when forming their own
message, and clients may wish to better embed the referenced message for
the user to have a better context for the conversation being had. This
sort of embedding another message in a message is known as a "rich
reply", or occasionally just a "reply".

A rich reply is formed through use of an `m.relates_to` relation for
`m.in_reply_to` where a single key, `event_id`, is used to reference the
event being replied to. The referenced event ID SHOULD belong to the
same room where the reply is being sent. Clients should be cautious of
the event ID belonging to another room, or being invalid entirely. Rich
replies can only be constructed in the form of `m.room.message` events
with a `msgtype` of `m.text` or `m.notice`. Due to the fallback
requirements, rich replies cannot be constructed for types of `m.emote`,
`m.file`, etc. Rich replies may reference any other `m.room.message`
event, however. Rich replies may reference another event which also has
a rich reply, infinitely.

An `m.in_reply_to` relationship looks like the following:

    {
      ...
      "type": "m.room.message",
      "content": {
        "msgtype": "m.text",
        "body": "<body including fallback>",
        "format": "org.matrix.custom.html",
        "formatted_body": "<HTML including fallback>",
        "m.relates_to": {
          "m.in_reply_to": {
            "event_id": "$another:event.com"
          }
        }
      }
    }

######## Fallbacks and event representation

Some clients may not have support for rich replies and therefore need a
fallback to use instead. Clients that do not support rich replies should
render the event as if rich replies were not special.

Clients that do support rich replies MUST provide the fallback format on
replies, and MUST strip the fallback before rendering the reply. Rich
replies MUST have a `format` of `org.matrix.custom.html` and therefore a
`formatted_body` alongside the `body` and appropriate `msgtype`. The
specific fallback text is different for each `msgtype`, however the
general format for the `body` is:

    > <@alice:example.org> This is the original body

    This is where the reply goes

The `formatted_body` should use the following template:

    <mx-reply>
      <blockquote>
        <a href="https://matrix.to/#/!somewhere:example.org/$event:example.org">In reply to</a>
        <a href="https://matrix.to/#/@alice:example.org">@alice:example.org</a>
        <br />
        <!-- This is where the related event's HTML would be. -->
      </blockquote>
    </mx-reply>
    This is where the reply goes.

If the related event does not have a `formatted_body`, the event's
`body` should be considered after encoding any HTML special characters.
Note that the `href` in both of the anchors use a [matrix.to
URI](../appendices.html#matrix-to-navigation).

######### Stripping the fallback

Clients which support rich replies MUST strip the fallback from the
event before rendering the event. This is because the text provided in
the fallback cannot be trusted to be an accurate representation of the
event. After removing the fallback, clients are recommended to represent
the event referenced by `m.in_reply_to` similar to the fallback's
representation, although clients do have creative freedom for their user
interface. Clients should prefer the `formatted_body` over the `body`,
just like with other `m.room.message` events.

To strip the fallback on the `body`, the client should iterate over each
line of the string, removing any lines that start with the fallback
prefix ("&gt; ", including the space, without quotes) and stopping when
a line is encountered without the prefix. This prefix is known as the
"fallback prefix sequence".

To strip the fallback on the `formatted_body`, the client should remove
the entirety of the `mx-reply` tag.

######### Fallback for `m.text`, `m.notice`, and unrecognised message types

Using the prefix sequence, the first line of the related event's `body`
should be prefixed with the user's ID, followed by each line being
prefixed with the fallback prefix sequence. For example:

    > <@alice:example.org> This is the first line
    > This is the second line

    This is the reply

The `formatted_body` uses the template defined earlier in this section.

######### Fallback for `m.emote`

Similar to the fallback for `m.text`, each line gets prefixed with the
fallback prefix sequence. However an asterisk should be inserted before
the user's ID, like so:

    > * <@alice:example.org> feels like today is going to be a great day

    This is the reply

The `formatted_body` has a subtle difference for the template where the
asterisk is also inserted ahead of the user's ID:

    <mx-reply>
      <blockquote>
        <a href="https://matrix.to/#/!somewhere:example.org/$event:example.org">In reply to</a>
        * <a href="https://matrix.to/#/@alice:example.org">@alice:example.org</a>
        <br />
        <!-- This is where the related event's HTML would be. -->
      </blockquote>
    </mx-reply>
    This is where the reply goes.

######### Fallback for `m.image`, `m.video`, `m.audio`, and `m.file`

The related event's `body` would be a file name, which may not be very
descriptive. The related event should additionally not have a `format`
or `formatted_body` in the `content` - if the event does have a `format`
and/or `formatted_body`, those fields should be ignored. Because the
filename alone may not be descriptive, the related event's `body` should
be considered to be `"sent a file."` such that the output looks similar
to the following:

    > <@alice:example.org> sent a file.

    This is the reply

    <mx-reply>
      <blockquote>
        <a href="https://matrix.to/#/!somewhere:example.org/$event:example.org">In reply to</a>
        <a href="https://matrix.to/#/@alice:example.org">@alice:example.org</a>
        <br />
        sent a file.
      </blockquote>
    </mx-reply>
    This is where the reply goes.

For `m.image`, the text should be `"sent an image."`. For `m.video`, the
text should be `"sent a video."`. For `m.audio`, the text should be
`"sent an audio file"`.

##### Server behaviour

Homeservers SHOULD reject `m.room.message` events which don't have a
`msgtype` key, or which don't have a textual `body` key, with an HTTP
status code of 400.

##### Security considerations

Messages sent using this module are not encrypted, although end to end
encryption is in development (see [E2E module]()).

Clients should sanitise **all displayed keys** for unsafe HTML to
prevent Cross-Site Scripting (XSS) attacks. This includes room names and
topics.

### Voice over IP

This module outlines how two users in a room can set up a Voice over IP
(VoIP) call to each other. Voice and video calls are built upon the
WebRTC 1.0 standard. Call signalling is achieved by sending [message
events](#sect:events) to the room. In this version of the spec, only
two-party communication is supported (e.g. between two peers, or between
a peer and a multi-point conferencing unit). This means that clients
MUST only send call events to rooms with exactly two participants.

##### Events

{{voip\_events}}

##### Client behaviour

A call is set up with message events exchanged as follows:

    Caller                    Callee
    [Place Call]
    m.call.invite ----------->
    m.call.candidate -------->
    [..candidates..] -------->
                            [Answers call]
           <--------------- m.call.answer
     [Call is active and ongoing]
           <--------------- m.call.hangup

Or a rejected call:

    Caller                      Callee
    m.call.invite ------------>
    m.call.candidate --------->
    [..candidates..] --------->
                             [Rejects call]
             <-------------- m.call.hangup

Calls are negotiated according to the WebRTC specification.

###### Glare

"Glare" is a problem which occurs when two users call each other at
roughly the same time. This results in the call failing to set up as
there already is an incoming/outgoing call. A glare resolution algorithm
can be used to determine which call to hangup and which call to answer.
If both clients implement the same algorithm then they will both select
the same call and the call will be successfully connected.

As calls are "placed" to rooms rather than users, the glare resolution
algorithm outlined below is only considered for calls which are to the
same room. The algorithm is as follows:

-   If an `m.call.invite` to a room is received whilst the client is
    **preparing to send** an `m.call.invite` to the same room:
    -   the client should cancel its outgoing call and instead
        automatically accept the incoming call on behalf of the user.
-   If an `m.call.invite` to a room is received **after the client has
    sent** an `m.call.invite` to the same room and is waiting for a
    response:
    -   the client should perform a lexicographical comparison of the
        call IDs of the two calls and use the *lesser* of the two calls,
        aborting the greater. If the incoming call is the lesser, the
        client should accept this call on behalf of the user.

The call setup should appear seamless to the user as if they had simply
placed a call and the other party had accepted. This means any media
stream that had been setup for use on a call should be transferred and
used for the call that replaces it.

##### Server behaviour

The homeserver MAY provide a TURN server which clients can use to
contact the remote party. The following HTTP API endpoints will be used
by clients in order to get information about the TURN server.

{{voip\_cs\_http\_api}}

##### Security considerations

Calls should only be placed to rooms with one other user in them. If
they are placed to group chat rooms it is possible that another user
will intercept and answer the call.

### Typing Notifications

Users may wish to be informed when another user is typing in a room.
This can be achieved using typing notifications. These are ephemeral
events scoped to a `room_id`. This means they do not form part of the
[Event Graph](index.html#event-graphs) but still have a `room_id` key.

##### Events

{{m\_typing\_event}}

##### Client behaviour

When a client receives an `m.typing` event, it MUST use the user ID list
to **REPLACE** its knowledge of every user who is currently typing. The
reason for this is that the server *does not remember* users who are not
currently typing as that list gets big quickly. The client should mark
as not typing any user ID who is not in that list.

It is recommended that clients store a `boolean` indicating whether the
user is typing or not. Whilst this value is `true` a timer should fire
periodically every N seconds to send a typing HTTP request. The value of
N is recommended to be no more than 20-30 seconds. This request should
be re-sent by the client to continue informing the server the user is
still typing. As subsequent requests will replace older requests, a
safety margin of 5 seconds before the expected timeout runs out is
recommended. When the user stops typing, the state change of the
`boolean` to `false` should trigger another HTTP request to inform the
server that the user has stopped typing.

{{typing\_cs\_http\_api}}

##### Security considerations

Clients may not wish to inform everyone in a room that they are typing
and instead only specific users in the room.

### Receipts

This module adds in support for receipts. These receipts are a form of
acknowledgement of an event. This module defines a single
acknowledgement: `m.read` which indicates that the user has read up to a
given event.

Sending a receipt for each event can result in sending large amounts of
traffic to a homeserver. To prevent this from becoming a problem,
receipts are implemented using "up to" markers. This marker indicates
that the acknowledgement applies to all events "up to and including" the
event specified. For example, marking an event as "read" would indicate
that the user had read all events *up to* the referenced event. See the
[Receiving notifications](#receiving-notifications) section for more
information on how read receipts affect notification counts.

##### Events

Each `user_id`, `receipt_type` pair must be associated with only a
single `event_id`.

{{m\_receipt\_event}}

##### Client behaviour

In `/sync`, receipts are listed under the `ephemeral` array of events
for a given room. New receipts that come down the event streams are
deltas which update existing mappings. Clients should replace older
receipt acknowledgements based on `user_id` and `receipt_type` pairs.
For example:

    Client receives m.receipt:
      user = @alice:example.com
      receipt_type = m.read
      event_id = $aaa:example.com

    Client receives another m.receipt:
      user = @alice:example.com
      receipt_type = m.read
      event_id = $bbb:example.com

    The client should replace the older acknowledgement for $aaa:example.com with
    this one for $bbb:example.com

Clients should send read receipts when there is some certainty that the
event in question has been **displayed** to the user. Simply receiving
an event does not provide enough certainty that the user has seen the
event. The user SHOULD need to *take some action* such as viewing the
room that the event was sent to or dismissing a notification in order
for the event to count as "read". Clients SHOULD NOT send read receipts
for events sent by their own user.

A client can update the markers for its user by interacting with the
following HTTP APIs.

{{receipts\_cs\_http\_api}}

##### Server behaviour

For efficiency, receipts SHOULD be batched into one event per room
before delivering them to clients.

Receipts are sent across federation as EDUs with type `m.receipt`. The
format of the EDUs are:

    {
        <room_id>: {
            <receipt_type>: {
                <user_id>: { <content> }
            },
            ...
        },
        ...
    }

These are always sent as deltas to previously sent receipts. Currently
only a single `<receipt_type>` should be used: `m.read`.

##### Security considerations

As receipts are sent outside the context of the event graph, there are
no integrity checks performed on the contents of `m.receipt` events.

### Fully read markers

The history for a given room may be split into three sections: messages
the user has read (or indicated they aren't interested in them),
messages the user might have read some but not others, and messages the
user hasn't seen yet. The "fully read marker" (also known as a "read
marker") marks the last event of the first section, whereas the user's
read receipt marks the last event of the second section.

##### Events

The user's fully read marker is kept as an event in the room's [account
data](#client-config). The event may be read to determine the user's
current fully read marker location in the room, and just like other
account data events the event will be pushed down the event stream when
updated.

The fully read marker is kept under an `m.fully_read` event. If the
event does not exist on the user's account data, the fully read marker
should be considered to be the user's read receipt location.

{{m\_fully\_read\_event}}

##### Client behaviour

The client cannot update fully read markers by directly modifying the
`m.fully_read` account data event. Instead, the client must make use of
the read markers API to change the values.

The read markers API can additionally update the user's read receipt
(`m.read`) location in the same operation as setting the fully read
marker location. This is because read receipts and read markers are
commonly updated at the same time, and therefore the client might wish
to save an extra HTTP call. Providing an `m.read` location performs the
same task as a request to `/receipt/m.read/$event:example.org`.

{{read\_markers\_cs\_http\_api}}

##### Server behaviour

The server MUST prevent clients from setting `m.fully_read` directly in
room account data. The server must additionally ensure that it treats
the presence of `m.read` in the `/read_markers` request the same as how
it would for a request to `/receipt/m.read/$event:example.org`.

Upon updating the `m.fully_read` event due to a request to
`/read_markers`, the server MUST send the updated account data event
through to the client via the event stream (eg: `/sync`), provided any
applicable filters are also satisfied.

### Presence

Each user has the concept of presence information. This encodes:

-   Whether the user is currently online
-   How recently the user was last active (as seen by the server)
-   Whether a given client considers the user to be currently idle
-   Arbitrary information about the user's current status (e.g. "in a
    meeting").

This information is collated from both per-device (`online`, `idle`,
`last_active`) and per-user (status) data, aggregated by the user's
homeserver and transmitted as an `m.presence` event. Presence events are
sent to interested parties where users share a room membership.

User's presence state is represented by the `presence` key, which is an
enum of one of the following:

-   `online` : The default state when the user is connected to an event
    stream.
-   `unavailable` : The user is not reachable at this time e.g. they are
    idle.
-   `offline` : The user is not connected to an event stream or is
    explicitly suppressing their profile information from being sent.

##### Events

{{presence\_events}}

##### Client behaviour

Clients can manually set/get their presence using the HTTP APIs listed
below.

{{presence\_cs\_http\_api}}

###### Last active ago

The server maintains a timestamp of the last time it saw a pro-active
event from the user. A pro-active event may be sending a message to a
room or changing presence state to `online`. This timestamp is presented
via a key called `last_active_ago` which gives the relative number of
milliseconds since the pro-active event.

To reduce the number of presence updates sent to clients the server may
include a `currently_active` boolean field when the presence state is
`online`. When true, the server will not send further updates to the
last active time until an update is sent to the client with either a)
`currently_active` set to false or b) a presence state other than
`online`. During this period clients must consider the user to be
currently active, irrespective of the last active time.

The last active time must be up to date whenever the server gives a
presence event to the client. The `currently_active` mechanism should
purely be used by servers to stop sending continuous presence updates,
as opposed to disabling last active tracking entirely. Thus clients can
fetch up to date last active times by explicitly requesting the presence
for a given user.

###### Idle timeout

The server will automatically set a user's presence to `unavailable` if
their last active time was over a threshold value (e.g. 5 minutes).
Clients can manually set a user's presence to `unavailable`. Any
activity that bumps the last active time on any of the user's clients
will cause the server to automatically set their presence to `online`.

##### Security considerations

Presence information is shared with all users who share a room with the
target user. In large public rooms this could be undesirable.

### Content repository

The content repository (or "media repository") allows users to upload
files to their homeserver for later use. For example, files which the
user wants to send to a room would be uploaded here, as would an avatar
the user wants to use.

Uploads are POSTed to a resource on the user's local homeserver which
returns a MXC URI which can later be used to GET the download. Content
is downloaded from the recipient's local homeserver, which must first
transfer the content from the origin homeserver using the same API
(unless the origin and destination homeservers are the same).

When serving content, the server SHOULD provide a
`Content-Security-Policy` header. The recommended policy is
`sandbox; default-src 'none'; script-src 'none'; plugin-types application/pdf; style-src 'unsafe-inline'; object-src 'self';`.

##### Matrix Content (MXC) URIs

Content locations are represented as Matrix Content (MXC) URIs. They
look like:

    mxc://<server-name>/<media-id>

    <server-name> : The name of the homeserver where this content originated, e.g. matrix.org
    <media-id> : An opaque ID which identifies the content.

##### Client behaviour

Clients can upload and download content using the following HTTP APIs.

{{content\_repo\_cs\_http\_api}}

###### Thumbnails

The homeserver SHOULD be able to supply thumbnails for uploaded images
and videos. The exact file types which can be thumbnailed are not
currently specified - see [Issue
\#1938](https://github.com/matrix-org/matrix-doc/issues/1938) for more
information.

The thumbnail methods are "crop" and "scale". "scale" tries to return an
image where either the width or the height is smaller than the requested
size. The client should then scale and letterbox the image if it needs
to fit within a given rectangle. "crop" tries to return an image where
the width and height are close to the requested size and the aspect
matches the requested size. The client should scale the image if it
needs to fit within a given rectangle.

The dimensions given to the thumbnail API are the minimum size the
client would prefer. Servers must never return thumbnails smaller than
the client's requested dimensions, unless the content being thumbnailed
is smaller than the dimensions. When the content is smaller than the
requested dimensions, servers should return the original content rather
than thumbnail it.

Servers SHOULD produce thumbnails with the following dimensions and
methods:

-   32x32, crop
-   96x96, crop
-   320x240, scale
-   640x480, scale
-   800x600, scale

In summary:  
-   "scale" maintains the original aspect ratio of the image
-   "crop" provides an image in the aspect ratio of the sizes given in
    the request
-   The server will return an image larger than or equal to the
    dimensions requested where possible.

Servers MUST NOT upscale thumbnails under any circumstance. Servers MUST
NOT return a smaller thumbnail than requested, unless the original
content makes that impossible.

##### Security considerations

The HTTP GET endpoint does not require any authentication. Knowing the
URL of the content is sufficient to retrieve the content, even if the
entity isn't in the room.

MXC URIs are vulnerable to directory traversal attacks such as
`mxc://127.0.0.1/../../../some_service/etc/passwd`. This would cause the
target homeserver to try to access and return this file. As such,
homeservers MUST sanitise MXC URIs by allowing only alphanumeric
(`A-Za-z0-9`), `_` and `-` characters in the `server-name` and
`media-id` values. This set of whitelisted characters allows URL-safe
base64 encodings specified in RFC 4648. Applying this character
whitelist is preferable to blacklisting `.` and `/` as there are
techniques around blacklisted characters (percent-encoded characters,
UTF-8 encoded traversals, etc).

Homeservers have additional content-specific concerns:

-   Clients may try to upload very large files. Homeservers should not
    store files that are too large and should not serve them to clients,
    returning a HTTP 413 error with the `M_TOO_LARGE` code.

-   Clients may try to upload very large images. Homeservers should not
    attempt to generate thumbnails for images that are too large,
    returning a HTTP 413 error with the `M_TOO_LARGE` code.

-   Remote homeservers may host very large files or images. Homeservers
    should not proxy or thumbnail large files or images from remote
    homeservers, returning a HTTP 502 error with the `M_TOO_LARGE` code.

-   Clients may try to upload a large number of files. Homeservers
    should limit the number and total size of media that can be uploaded
    by clients, returning a HTTP 403 error with the `M_FORBIDDEN` code.

-   Clients may try to access a large number of remote files through a
    homeserver. Homeservers should restrict the number and size of
    remote files that it caches.

-   Clients or remote homeservers may try to upload malicious files
    targeting vulnerabilities in either the homeserver thumbnailing or
    the client decoders.

    ### Send-to-Device messaging<span id="module:to_device"></span>

    This module provides a means by which clients can exchange
    signalling messages without them being stored permanently as part of
    a shared communication history. A message is delivered exactly once
    to each client device.

    The primary motivation for this API is exchanging data that is
    meaningless or undesirable to persist in the room DAG - for example,
    one-time authentication tokens or key data. It is not intended for
    conversational data, which should be sent using the normal
    `/rooms/<room_id>/send`\_ API for consistency throughout Matrix.

    ##### Client behaviour

    To send a message to other devices, a client should call
    `/sendToDevice`\_. Only one message can be sent to each device per
    transaction, and they must all have the same event type. The device
    ID in the request body can be set to `*` to request that the message
    be sent to all known devices.

    If there are send-to-device messages waiting for a client, they will
    be returned by `/sync`\_, as detailed in Extensions to /sync\_.
    Clients should inspect the `type` of each returned event, and ignore
    any they do not understand.

    ##### Server behaviour

    Servers should store pending messages for local users until they are
    successfully delivered to the destination device. When a client
    calls `/sync`\_ with an access token which corresponds to a device
    with pending messages, the server should list the pending messages,
    in order of arrival, in the response body.

    When the client calls `/sync` again with the `next_batch` token from
    the first response, the server should infer that any send-to-device
    messages in that response have been delivered successfully, and
    delete them from the store.

    If there is a large queue of send-to-device messages, the server
    should limit the number sent in each `/sync` response. 100 messages
    is recommended as a reasonable limit.

    If the client sends messages to users on remote domains, those
    messages should be sent on to the remote servers via
    [federation](../server_server/%SERVER_RELEASE_LABEL%.html#send-to-device-messaging).

    ##### Protocol definitions

    {{to\_device\_cs\_http\_api}}

    ###### Extensions to /sync

    This module adds the following properties to the `/sync`\_ response:

    <table>
    <thead>
    <tr class="header">
    <th>Parameter</th>
    <th>Type</th>
    <th>Description</th>
    </tr>
    </thead>
    <tbody>
    <tr class="odd">
    <td><p>to_device</p></td>
    <td><p>ToDevice</p></td>
    <td><p>Optional. Information on the send-to-device messages for the client device.</p></td>
    </tr>
    </tbody>
    </table>

    `ToDevice`

    <table>
    <thead>
    <tr class="header">
    <th>Parameter</th>
    <th>Type</th>
    <th>Description</th>
    </tr>
    </thead>
    <tbody>
    <tr class="odd">
    <td>events</td>
    <td>[Event]</td>
    <td>List of send-to-device messages.</td>
    </tr>
    </tbody>
    </table>

    `Event`

    <table>
    <thead>
    <tr class="header">
    <th>Parameter</th>
    <th>Type</th>
    <th>Description</th>
    </tr>
    </thead>
    <tbody>
    <tr class="odd">
    <td><p>content</p></td>
    <td><p>EventContent</p></td>
    <td><p>The content of this event. The fields in this object will vary depending on the type of event.</p></td>
    </tr>
    <tr class="even">
    <td><p>sender</p></td>
    <td><p>string</p></td>
    <td><p>The Matrix user ID of the user who sent this event.</p></td>
    </tr>
    <tr class="odd">
    <td>type</td>
    <td>string</td>
    <td>The type of event.</td>
    </tr>
    </tbody>
    </table>

    Example response:

        {
          "next_batch": "s72595_4483_1934",
          "rooms": {"leave": {}, "join": {}, "invite": {}},
          "to_device": {
            "events": [
              {
                "sender": "@alice:example.com",
                "type": "m.new_device",
                "content": {
                  "device_id": "XYZABCDE",
                  "rooms": ["!726s6s6q:example.com"]
                }
              }
            ]
          }
        }

### Send-to-Device messaging<span id="module:to_device"></span>

This module provides a means by which clients can exchange signalling
messages without them being stored permanently as part of a shared
communication history. A message is delivered exactly once to each
client device.

The primary motivation for this API is exchanging data that is
meaningless or undesirable to persist in the room DAG - for example,
one-time authentication tokens or key data. It is not intended for
conversational data, which should be sent using the normal
`/rooms/<room_id>/send`\_ API for consistency throughout Matrix.

##### Client behaviour

To send a message to other devices, a client should call
`/sendToDevice`\_. Only one message can be sent to each device per
transaction, and they must all have the same event type. The device ID
in the request body can be set to `*` to request that the message be
sent to all known devices.

If there are send-to-device messages waiting for a client, they will be
returned by `/sync`\_, as detailed in Extensions to /sync\_. Clients
should inspect the `type` of each returned event, and ignore any they do
not understand.

##### Server behaviour

Servers should store pending messages for local users until they are
successfully delivered to the destination device. When a client calls
`/sync`\_ with an access token which corresponds to a device with
pending messages, the server should list the pending messages, in order
of arrival, in the response body.

When the client calls `/sync` again with the `next_batch` token from the
first response, the server should infer that any send-to-device messages
in that response have been delivered successfully, and delete them from
the store.

If there is a large queue of send-to-device messages, the server should
limit the number sent in each `/sync` response. 100 messages is
recommended as a reasonable limit.

If the client sends messages to users on remote domains, those messages
should be sent on to the remote servers via
[federation](../server_server/%SERVER_RELEASE_LABEL%.html#send-to-device-messaging).

##### Protocol definitions

{{to\_device\_cs\_http\_api}}

###### Extensions to /sync

This module adds the following properties to the `/sync`\_ response:

<table>
<thead>
<tr class="header">
<th>Parameter</th>
<th>Type</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><p>to_device</p></td>
<td><p>ToDevice</p></td>
<td><p>Optional. Information on the send-to-device messages for the client device.</p></td>
</tr>
</tbody>
</table>

`ToDevice`

<table>
<thead>
<tr class="header">
<th>Parameter</th>
<th>Type</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>events</td>
<td>[Event]</td>
<td>List of send-to-device messages.</td>
</tr>
</tbody>
</table>

`Event`

<table>
<thead>
<tr class="header">
<th>Parameter</th>
<th>Type</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><p>content</p></td>
<td><p>EventContent</p></td>
<td><p>The content of this event. The fields in this object will vary depending on the type of event.</p></td>
</tr>
<tr class="even">
<td><p>sender</p></td>
<td><p>string</p></td>
<td><p>The Matrix user ID of the user who sent this event.</p></td>
</tr>
<tr class="odd">
<td>type</td>
<td>string</td>
<td>The type of event.</td>
</tr>
</tbody>
</table>

Example response:

    {
      "next_batch": "s72595_4483_1934",
      "rooms": {"leave": {}, "join": {}, "invite": {}},
      "to_device": {
        "events": [
          {
            "sender": "@alice:example.com",
            "type": "m.new_device",
            "content": {
              "device_id": "XYZABCDE",
              "rooms": ["!726s6s6q:example.com"]
            }
          }
        ]
      }
    }

### Guest Access

There are times when it is desirable for clients to be able to interact
with rooms without having to fully register for an account on a
homeserver or join the room. This module specifies how these clients
should interact with servers in order to participate in rooms as guests.

Guest users retrieve access tokens from a homeserver using the ordinary
[register
endpoint](#post-matrix-client-%CLIENT_MAJOR_VERSION%-register),
specifying the `kind` parameter as `guest`. They may then interact with
the client-server API as any other user would, but will only have access
to a subset of the API as described the Client behaviour subsection
below. Homeservers may choose not to allow this access at all to their
local users, but have no information about whether users on other
homeservers are guests or not.

Guest users can also upgrade their account by going through the ordinary
`register` flow, but specifying the additional POST parameter
`guest_access_token` containing the guest's access token. They are also
required to specify the `username` parameter to the value of the local
part of their username, which is otherwise optional.

This module does not fully factor in federation; it relies on individual
homeservers properly adhering to the rules set out in this module,
rather than allowing all homeservers to enforce the rules on each other.

##### Events

{{m\_room\_guest\_access\_event}}

##### Client behaviour

The following API endpoints are allowed to be accessed by guest accounts
for retrieving events:

-   [GET
    /rooms/:room\_id/state](#get-matrix-client-%CLIENT_MAJOR_VERSION%-rooms-roomid-state)
-   [GET
    /rooms/:room\_id/context/:event\_id](#get-matrix-client-%CLIENT_MAJOR_VERSION%-rooms-roomid-context-eventid)
-   [GET
    /rooms/:room\_id/event/:event\_id](#get-matrix-client-%CLIENT_MAJOR_VERSION%-rooms-roomid-event-eventid)
-   [GET
    /rooms/:room\_id/state/:event\_type/:state\_key](#get-matrix-client-%CLIENT_MAJOR_VERSION%-rooms-roomid-state-eventtype-statekey)
-   [GET
    /rooms/:room\_id/messages](#get-matrix-client-%CLIENT_MAJOR_VERSION%-rooms-roomid-messages)
-   [GET
    /rooms/:room\_id/initialSync](#get-matrix-client-%CLIENT_MAJOR_VERSION%-rooms-roomid-initialsync)
-   [GET /sync](#get-matrix-client-%CLIENT_MAJOR_VERSION%-sync)
-   [GET /events](#peeking_events_api) as used for room previews.

The following API endpoints are allowed to be accessed by guest accounts
for sending events:

-   [POST
    /rooms/:room\_id/join](#post-matrix-client-%CLIENT_MAJOR_VERSION%-rooms-roomid-join)
-   [POST
    /rooms/:room\_id/leave](#post-matrix-client-%CLIENT_MAJOR_VERSION%-rooms-roomid-leave)
-   [PUT
    /rooms/:room\_id/send/m.room.message/:txn\_id](#put-matrix-client-%CLIENT_MAJOR_VERSION%-rooms-roomid-send-eventtype-txnid)
-   [PUT
    /sendToDevice/{eventType}/{txnId}](#put-matrix-client-%CLIENT_MAJOR_VERSION%-sendtodevice-eventtype-txnid)

The following API endpoints are allowed to be accessed by guest accounts
for their own account maintenance:

-   [PUT
    /profile/:user\_id/displayname](#put-matrix-client-%CLIENT_MAJOR_VERSION%-profile-userid-displayname)
-   [GET /devices](#get-matrix-client-%CLIENT_MAJOR_VERSION%-devices)
-   [GET
    /devices/{deviceId}](#get-matrix-client-%CLIENT_MAJOR_VERSION%-devices-deviceid)
-   [PUT
    /devices/{deviceId}](#put-matrix-client-%CLIENT_MAJOR_VERSION%-devices-deviceid)

The following API endpoints are allowed to be accessed by guest accounts
for end-to-end encryption:

-   [POST
    /keys/upload](#post-matrix-client-%CLIENT_MAJOR_VERSION%-keys-upload)
-   [POST
    /keys/query](#post-matrix-client-%CLIENT_MAJOR_VERSION%-keys-query)
-   [POST
    /keys/claim](#post-matrix-client-%CLIENT_MAJOR_VERSION%-keys-claim)

##### Server behaviour

Servers MUST only allow guest users to join rooms if the
`m.room.guest_access` state event is present on the room, and has the
`guest_access` value `can_join`. If the `m.room.guest_access` event is
changed to stop this from being the case, the server MUST set those
users' `m.room.member` state to `leave`.

##### Security considerations

Each homeserver manages its own guest accounts itself, and whether an
account is a guest account or not is not information passed from server
to server. Accordingly, any server participating in a room is trusted to
properly enforce the permissions outlined in this section.

Homeservers may want to enable protections such as captchas for guest
registration to prevent spam, denial of service, and similar attacks.

### Room Previews

It is sometimes desirable to offer a preview of a room, where a user can
"lurk" and read messages posted to the room, without joining the room.
This can be particularly effective when combined with [Guest
Access](#guest-access).

Previews are implemented via the `world_readable` [Room History
Visibility](). setting, along with a special version of the [GET
/events](#get-matrix-client-%CLIENT_MAJOR_VERSION%-events) endpoint.

##### Client behaviour

A client wishing to view a room without joining it should call [GET
/rooms/:room\_id/initialSync](#get-matrix-client-%CLIENT_MAJOR_VERSION%-rooms-roomid-initialsync),
followed by [GET /events](#peeking_events_api). Clients will need to do
this in parallel for each room they wish to view.

Clients can of course also call other endpoints such as [GET
/rooms/:room\_id/messages](#get-matrix-client-%CLIENT_MAJOR_VERSION%-rooms-roomid-messages)
and [GET /search](#get-matrix-client-%CLIENT_MAJOR_VERSION%-search) to
access events outside the `/events` stream.

{{peeking\_events\_cs\_http\_api}}

##### Server behaviour

For clients which have not joined a room, servers are required to only
return events where the room state at the event had the
`m.room.history_visibility` state event present with
`history_visibility` value `world_readable`.

##### Security considerations

Clients may wish to display to their users that rooms which are
`world_readable` *may* be showing messages to non-joined users. There is
no way using this module to find out whether any non-joined guest users
*do* see events in the room, or to list or count any lurking users.

### Room Tagging

Users can add tags to rooms. Tags are namespaced strings used to label
rooms. A room may have multiple tags. Tags are only visible to the user
that set them but are shared across all their devices.

##### Events

The tags on a room are received as single `m.tag` event in the
`account_data` section of a room. The content of the `m.tag` event is a
`tags` key whose value is an object mapping the name of each tag to
another object.

The JSON object associated with each tag gives information about the
tag, e.g how to order the rooms with a given tag.

Ordering information is given under the `order` key as a number between
0 and 1. The numbers are compared such that 0 is displayed first.
Therefore a room with an `order` of `0.2` would be displayed before a
room with an `order` of `0.7`. If a room has a tag without an `order`
key then it should appear after the rooms with that tag that have an
`order` key.

The name of a tag MUST NOT exceed 255 bytes.

The tag namespace is defined as follows:

-   The namespace `m.*` is reserved for tags defined in the Matrix
    specification. Clients must ignore any tags in this namespace they
    don't understand.
-   The namespace `u.*` is reserved for user-defined tags. The portion
    of the string after the `u.` is defined to be the display name of
    this tag. No other semantics should be inferred from tags in this
    namespace.
-   A client or app willing to use special tags for advanced
    functionality should namespace them similarly to state keys:
    `tld.name.*`
-   Any tag in the `tld.name.*` form but not matching the namespace of
    the current client should be ignored
-   Any tag not matching the above rules should be interpreted as a user
    tag from the `u.*` namespace, as if the name had already had `u.`
    stripped from the start (ie. the name of the tag is used as the
    display name directly). These non-namespaced tags are supported for
    historical reasons. New tags should use one of the defined
    namespaces above.

Several special names are listed in the specification: The following
tags are defined in the `m.*` namespace:

-   `m.favourite`: The user's favourite rooms. These should be shown
    with higher precedence than other rooms.
-   `m.lowpriority`: These should be shown with lower precedence than
    others.
-   `m.server_notice`: Used to identify [Server Notice
    Rooms](#module-server-notices).

{{m\_tag\_event}}

##### Client Behaviour

{{tags\_cs\_http\_api}}

### Client Config

Clients can store custom config data for their account on their
homeserver. This account data will be synced between different devices
and can persist across installations on a particular device. Users may
only view the account data for their own account

The account\_data may be either global or scoped to a particular rooms.

##### Events

The client receives the account data as events in the `account_data`
sections of a `/sync`.

These events can also be received in a `/events` response or in the
`account_data` section of a room in `/sync`. `m.tag` events appearing in
`/events` will have a `room_id` with the room the tags are for.

##### Client Behaviour

{{account\_data\_cs\_http\_api}}

##### Server Behaviour

Servers MUST reject clients from setting account data for event types
that the server manages. Currently, this only includes
[m.fully\_read]().

### Server Administration

This module adds capabilities for server administrators to inspect
server state and data.

##### Client Behaviour

{{admin\_cs\_http\_api}}

### Event Context

This API returns a number of events that happened just before and after
the specified event. This allows clients to get the context surrounding
an event.

##### Client behaviour

There is a single HTTP API for retrieving event context, documented
below.

{{event\_context\_cs\_http\_api}}

##### Security considerations

The server must only return results that the user has permission to see.

### SSO client login/authentication

Single Sign-On (SSO) is a generic term which refers to protocols which
allow users to log into applications via a single web-based
authentication portal. Examples include OpenID Connect, "Central
Authentication Service" (CAS) and SAML.

This module allows a Matrix homeserver to delegate user authentication
to an external authentication server supporting one of these protocols.
In this process, there are three systems involved:

> -   A Matrix client, using the APIs defined this specification, which
>     is seeking to authenticate a user to a Matrix homeserver.
> -   A Matrix homeserver, implementing the APIs defined in this
>     specification, but which is delegating user authentication to the
>     authentication server.
> -   An "authentication server", which is responsible for
>     authenticating the user.

This specification is concerned only with communication between the
Matrix client and the homeserver, and is independent of the SSO protocol
used to communicate with the authentication server. Different Matrix
homeserver implementations might support different SSO protocols.

Clients and homeservers implementing the SSO flow will need to consider
both [login](#login) and [user-interactive
authentication](#user-interactive authentication). The flow is similar
in both cases, but there are slight differences.

Typically, SSO systems require a single "callback" URI to be configured
at the authentication server. Once the user is authenticated, their
browser is redirected to that URI. It is up to the Matrix homeserver
implementation to implement a suitable endpoint. For example, for CAS
authentication the homeserver should provide a means for the
administrator to configure where the CAS server is and the REST
endpoints which consume the ticket.

##### Client login via SSO

An overview of the process is as follows:

1.  The Matrix client calls `GET /login`\_ to find the supported login
    types, and the homeserver includes a flow with
    `"type": "m.login.sso"` in the response.
2.  To initiate the `m.login.sso` login type, the Matrix client
    instructs the user's browser to navigate to the
    `/login/sso/redirect`\_ endpoint on the user's homeserver.
3.  The homeserver responds with an HTTP redirect to the SSO user
    interface, which the browser follows.
4.  The authentication server and the homeserver interact to verify the
    user's identity and other authentication information, potentially
    using a number of redirects.
5.  The browser is directed to the `redirectUrl` provided by the client
    with a `loginToken` query parameter for the client to log in with.
6.  The client exchanges the login token for an access token by calling
    the `/login`\_ endpoint with a `type` of `m.login.token`.

For native applications, typically steps 1 to 4 are carried out by
opening an embedded web view.

These steps are illustrated as follows:

    Matrix Client                        Matrix Homeserver      Auth Server
        |                                       |                   |
        |-------------(0) GET /login----------->|                   |
        |<-------------login types--------------|                   |
        |                                       |                   |
        |   Webview                             |                   |
        |      |                                |                   |
        |----->|                                |                   |
        |      |--(1) GET /login/sso/redirect-->|                   |
        |      |<---------(2) 302---------------|                   |
        |      |                                |                   |
        |      |<========(3) Authentication process================>|
        |      |                                |                   |
        |      |<--(4) redirect to redirectUrl--|                   |
        |<-----|                                |                   |
        |                                       |                   |
        |---(5) POST /login with login token--->|                   |
        |<-------------access token-------------|                   |

Note

In the older [r0.4.0
version](https://matrix.org/docs/spec/client_server/r0.4.0.html#cas-based-client-login)
of this specification it was possible to authenticate via CAS when the
homeserver provides a `m.login.cas` login flow. This specification
deprecates the use of `m.login.cas` to instead prefer `m.login.sso`,
which is the same process with the only change being which redirect
endpoint to use: for `m.login.cas`, use `/cas/redirect` and for
`m.login.sso` use `/sso/redirect` (described below). The endpoints are
otherwise the same.

###### Client behaviour

The client starts the process by instructing the browser to navigate to
`/login/sso/redirect`\_ with an appropriate `redirectUrl`. Once
authentication is successful, the browser will be redirected to that
`redirectUrl`.

{{sso\_login\_redirect\_cs\_http\_api}}

####### Security considerations

1.  CSRF attacks via manipulation of parameters on the `redirectUrl`

    Clients should validate any requests to the `redirectUrl`. In
    particular, it may be possible for attackers to falsify any query
    parameters, leading to cross-site request forgery (CSRF) attacks.

    For example, consider a web-based client at
    `https://client.example.com`, which wants to initiate SSO login on
    the homeserver at `server.example.org`. It does this by storing the
    homeserver name in a query parameter for the `redirectUrl`: it
    redirects to
    `https://server.example.org/login/sso/redirect?redirectUrl=https://client.example.com?hs=server.example.org`.

    An attacker could trick a victim into following a link to
    `https://server.example.org/login/sso/redirect?redirectUrl=https://client.example.com?hs=evil.com`,
    which would result in the client sending a login token for the
    victim's account to the attacker-controlled site `evil.com`.

    To guard against this, clients MUST NOT store state (such as the
    address of the homeserver being logged into) anywhere it can be
    modified by external processes.

    Instead, the state could be stored in
    [localStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)
    or in a cookie.

2.  For added security, clients SHOULD include a unique identifier in
    the `redirectUrl` and reject any callbacks that do not contain a
    recognised identifier, to guard against unsolicited login attempts
    and replay attacks.

###### Server behaviour

####### Redirecting to the Authentication server

The server should handle
`/_matrix/client/%CLIENT_MAJOR_VERSION%/login/sso/redirect` as follows:

1.  It should build a suitable request for the SSO system.
2.  It should store enough state that the flow can be securely resumed
    after the SSO process completes. One way to do this is by storing a
    cookie which is stored in the user's browser, by adding a
    `Set-Cookie` header to the response.
3.  It should redirect the user's browser to the SSO login page with the
    appropriate parameters.

See also the "Security considerations" below.

####### Handling the callback from the Authentication server

Note that there will normally be a single callback URI which is used for
both login and user-interactive authentication: it is up to the
homeserver implementation to distinguish which is taking place.

The homeserver should validate the response from the SSO system: this
may require additional calls to the authentication server, and/or may
require checking a signature on the response.

The homeserver then proceeds as follows:

1.  The homeserver MUST map the user details received from the
    authentication server to a valid [Matrix user
    identifier](../appendices.html#user-identifiers). The guidance in
    [Mapping from other character
    sets](../appendices.html#mapping-from-other-character-sets) may be
    useful.
2.  If the generated user identifier represents a new user, it should be
    registered as a new user.
3.  The homeserver should generate a short-term login token. This is an
    opaque token, suitable for use with the `m.login.token` type of the
    `/login`\_ API. The lifetime of this token SHOULD be limited to
    around five seconds.
4.  The homeserver adds a query parameter of `loginToken`, with the
    value of the generated login token, to the `redirectUrl` given in
    the `/_matrix/client/%CLIENT_MAJOR_VERSION%/login/sso/redirect`
    request. (Note: `redirectURL` may or may not include existing query
    parameters. If it already includes one or more `loginToken`
    parameters, they should be removed before adding the new one.)
5.  The homeserver redirects the user's browser to the URI thus built.

###### Security considerations

1.  Homeservers should ensure that login tokens are not sent to
    malicious clients.

    For example, consider a homeserver at `server.example.org`. An
    attacker tricks a victim into following a link to
    `https://server.example.org/login/sso/redirect?redirectUrl=https://evil.com`,
    resulting in a login token being sent to the attacker-controlled
    site `evil.com`. This is a form of cross-site request forgery
    (CSRF).

    To mitigate this, Homeservers SHOULD confirm with the user that they
    are happy to grant access to their matrix account to the site named
    in the `redirectUrl`. This can be done either *before* redirecting
    to the SSO login page when handling the
    `/_matrix/client/%CLIENT_MAJOR_VERSION%/login/sso/redirect`
    endpoint, or *after* login when handling the callback from the
    authentication server. (If the check is performed before
    redirecting, it is particularly important that the homeserver guards
    against unsolicited authentication attempts as below).

    It may be appropriate to whitelist a set of known-trusted client
    URLs in this process. In particular, the homeserver's own [login
    fallback](#login-fallback) implementation could be excluded.

2.  For added security, homeservers SHOULD guard against unsolicited
    authentication attempts by tracking pending requests. One way to do
    this is to set a cookie when handling
    `/_matrix/client/%CLIENT_MAJOR_VERSION%/login/sso/redirect`, which
    is checked and cleared when handling the callback from the
    authentication server.

##### SSO during User-Interactive Authentication

[User-interactive authentication](#user-interactive authentication) is
used by client-server endpoints which require additional confirmation of
the user's identity (beyond holding an access token). Typically this
means that the user must re-enter their password, but for homeservers
which delegate to an SSO server, this means redirecting to the
authentication server during user-interactive auth.

The implemementation of this is based on the [Fallback](#fallback)
mechanism for user-interactive auth.

##### Client behaviour

Clients do not need to take any particular additional steps beyond
ensuring that the fallback mechanism has been implemented, and treating
the `m.login.sso` authentication type the same as any other unknown type
(i.e. they should open a browser window for
`/_matrix/client/%CLIENT_MAJOR_VERSION%/auth/m.login.sso/fallback/web?session=<session_id>`.
Once the flow has completed, the client retries the request with the
session only.)

##### Server behaviour

###### Redirecting to the Authentication server

The server should handle
`/_matrix/client/%CLIENT_MAJOR_VERSION%/auth/m.login.sso/fallback/web`
in much the same way as
`/_matrix/client/%CLIENT_MAJOR_VERSION%/login/sso/redirect`, which is to
say:

1.  It should build a suitable request for the SSO system.
2.  It should store enough state that the flow can be securely resumed
    after the SSO process completes. One way to do this is by storing a
    cookie which is stored in the user's browser, by adding a
    `Set-Cookie` header to the response.
3.  It should redirect the user's browser to the SSO login page with the
    appropriate parameters.

See also the "Security considerations" below.

####### Handling the callback from the Authentication server

Note that there will normally be a single callback URI which is used for
both login and user-interactive authentication: it is up to the
homeserver implementation to distinguish which is taking place.

The homeserver should validate the response from the SSO system: this
may require additional calls to the authentication server, and/or may
require checking a signature on the response.

The homeserver then returns the [user-interactive authentication
fallback
completion](#user-interactive authentication fallback completion) page
to the user's browser.

####### Security considerations

1.  Confirming the operation

    The homeserver SHOULD confirm that the user is happy for the
    operation to go ahead. The goal of the user-interactive
    authentication operation is to guard against a compromised
    `access_token` being used to take over the user's account. Simply
    redirecting the user to the SSO system is insufficient, since they
    may not realise what is being asked of them, or the SSO system may
    even confirm the authentication automatically.

    For example, the homeserver might serve a page with words to the
    effect of:

    > A client is trying to remove a device from your account. To
    > confirm this action, re-authenticate with single sign-on. If you
    > did not expect this, your account may be compromised!

    This confirmation could take place before redirecting to the SSO
    authentication page (when handling the
    `/_matrix/client/%CLIENT_MAJOR_VERSION%/auth/m.login.sso/fallback/web`
    endpoint), or *after* authentication when handling the callback from
    the authentication server. (If the check is performed before
    redirecting, it is particularly important that the homeserver guards
    against unsolicited authentication attempts as below).

2.  For added security, homeservers SHOULD guard against unsolicited
    authentication attempts by tracking pending requests. One way to do
    this is to set a cookie when handling
    `/_matrix/client/%CLIENT_MAJOR_VERSION%/auth/m.login.sso/fallback/web`,
    which is checked and cleared when handling the callback from the
    authentication server.

### Direct Messaging

All communication over Matrix happens within a room. It is sometimes
desirable to offer users the concept of speaking directly to one
particular person. This module defines a way of marking certain rooms as
'direct chats' with a given person. This does not restrict the chat to
being between exactly two people since this would preclude the presence
of automated 'bot' users or even a 'personal assistant' who is able to
answer direct messages on behalf of the user in their absence.

A room may not necessarily be considered 'direct' by all members of the
room, but a signalling mechanism exists to propagate the information of
whether a chat is 'direct' to an invitee.

##### Events

{{m\_direct\_event}}

##### Client behaviour

To start a direct chat with another user, the inviting user's client
should set the `is_direct` flag to `/createRoom`\_. The client should do
this whenever the flow the user has followed is one where their
intention is to speak directly with another person, as opposed to
bringing that person in to a shared room. For example, clicking on
'Start Chat' beside a person's profile picture would imply the
`is_direct` flag should be set.

The invitee's client may use the `is_direct` flag in the
[m.room.member]() event to automatically mark the room as a direct chat
but this is not required: it may for example, prompt the user, or ignore
the flag altogether.

Both the inviting client and the invitee's client should record the fact
that the room is a direct chat by storing an `m.direct` event in the
account data using `/user/<user_id>/account_data/<type>`\_.

##### Server behaviour

When the `is_direct` flag is given to `/createRoom`\_, the home server
must set the `is_direct` flag in the invite member event for any users
invited in the `/createRoom`\_ call.

### Ignoring Users

With all the communication through Matrix it may be desirable to ignore
a particular user for whatever reason. This module defines how clients
and servers can implement the ignoring of users.

##### Events

{{m\_ignored\_user\_list\_event}}

##### Client behaviour

To ignore a user, effectively blocking them, the client should add the
target user to the `m.ignored_user_list` event in their account data
using `/user/<user_id>/account_data/<type>`\_. Once ignored, the client
will no longer receive events sent by that user, with the exception of
state events. The client should either hide previous content sent by the
newly ignored user or perform a new `/sync` with no previous token.

Invites to new rooms by ignored users will not be sent to the client.
The server may optionally reject the invite on behalf of the client.

State events will still be sent to the client, even if the user is
ignored. This is to ensure parts, such as the room name, do not appear
different to the user just because they ignored the sender.

To remove a user from the ignored users list, remove them from the
account data event. The server will resume sending events from the
previously ignored user, however it should not send events that were
missed while the user was ignored. To receive the events that were sent
while the user was ignored the client should perform a fresh sync. The
client may also un-hide any events it previously hid due to the user
becoming ignored.

##### Server behaviour

Following an update of the `m.ignored_user_list`, the sync API for all
clients should immediately start ignoring (or un-ignoring) the user.
Clients are responsible for determining if they should hide previously
sent events or to start a new sync stream.

Servers must still send state events sent by ignored users to clients.

Servers must not send room invites from ignored users to clients.
Servers may optionally decide to reject the invite, however.

### Sticker Messages

This module allows users to send sticker messages in to rooms or direct
messaging sessions.

Sticker messages are specialised image messages that are displayed
without controls (e.g. no "download" link, or light-box view on click,
as would be displayed for for [m.image]() events).

Sticker messages are intended to provide simple "reaction" events in the
message timeline. The matrix client should provide some mechanism to
display the sticker "body" e.g. as a tooltip on hover, or in a modal
when the sticker image is clicked.

##### Events

Sticker events are received as a single `m.sticker` event in the
`timeline` section of a room, in a `/sync`.

{{m\_sticker\_event}}

##### Client behaviour

Clients supporting this message type should display the image content
from the event URL directly in the timeline.

A thumbnail image should be provided in the `info` object. This is
largely intended as a fallback for clients that do not fully support the
`m.sticker` event type. In most cases it is fine to set the thumbnail
URL to the same URL as the main event content.

It is recommended that sticker image content should be 512x512 pixels in
size or smaller. The dimensions of the image file should be twice the
intended display size specified in the `info` object in order to assist
rendering sharp images on higher DPI screens.

### Reporting Content

Users may encounter content which they find inappropriate and should be
able to report it to the server administrators or room moderators for
review. This module defines a way for users to report content.

Content is reported based upon a negative score, where -100 is "most
offensive" and 0 is "inoffensive".

##### Client behaviour

{{report\_content\_cs\_http\_api}}

##### Server behaviour

Servers are free to handle the reported content however they desire.
This may be a dedicated room to alert server administrators to the
reported content or some other mechanism for notifying the appropriate
people.

### Third Party Networks

Application services can provide access to third party networks via
bridging. This allows Matrix users to communicate with users on other
communication platforms, with messages ferried back and forth by the
application service. A single application service may bridge multiple
third party networks, and many individual locations within those
networks. A single third party network location may be bridged to
multiple Matrix rooms.

##### Third Party Lookups

A client may wish to provide a rich interface for joining third party
locations and connecting with third party users. Information necessary
for such an interface is provided by third party lookups.

{{third\_party\_lookup\_cs\_http\_api}}

### OpenID

This module allows users to verify their identity with a third party
service. The third party service does need to be matrix-aware in that it
will need to know to resolve matrix homeservers to exchange the user's
token for identity information.

{{openid\_cs\_http\_api}}

### Server Access Control Lists (ACLs) for rooms

In some scenarios room operators may wish to prevent a malicious or
untrusted server from participating in their room. Sending an
[m.room.server\_acl]() state event into a room is an effective way to
prevent the server from participating in the room at the federation
level.

Server ACLs can also be used to make rooms only federate with a limited
set of servers, or retroactively make the room no longer federate with
any other server, similar to setting the `m.federate` value on the
[m.room.create]() event.

{{m\_room\_server\_acl\_event}}

Note

Port numbers are not supported because it is unclear to parsers whether
a port number should be matched or an IP address literal. Additionally,
it is unlikely that one would trust a server running on a particular
domain's port but not a different port, especially considering the
server host can easily change ports.

Note

CIDR notation is not supported for IP addresses because Matrix does not
encourage the use of IPs for identifying servers. Instead, a blanket
`allow_ip_literals` is provided to cover banning them.

##### Client behaviour

Clients are not expected to perform any additional duties beyond sending
the event. Clients should describe changes to the server ACLs to the
user in the user interface, such as in the timeline.

Clients may wish to kick affected users from the room prior to denying a
server access to the room to help prevent those servers from
participating and to provide feedback to the users that they have been
excluded from the room.

##### Server behaviour

Servers MUST prevent blacklisted servers from sending events or
participating in the room when an [m.room.server\_acl]() event is
present in the room state. Which APIs are specifically affected are
described in the Server-Server API specification.

Servers should still send events to denied servers if they are still
residents of the room.

##### Security considerations

Server ACLs are only effective if every server in the room honours them.
Servers that do not honour the ACLs may still permit events sent by
denied servers into the room, leaking them to other servers in the room.
To effectively enforce an ACL in a room, the servers that do not honour
the ACLs should be denied in the room as well.

### User, room, and group mentions

This module allows users to mention other users, rooms, and groups
within a room message. This is achieved by including a [matrix.to
URI](../appendices.html#matrix-to-navigation) in the HTML body of an
[m.room.message]() event. This module does not have any server-specific
behaviour to it.

Mentions apply only to [m.room.message]() events where the `msgtype` is
`m.text`, `m.emote`, or `m.notice`. The `format` for the event must be
`org.matrix.custom.html` and therefore requires a `formatted_body`.

To make a mention, reference the entity being mentioned in the
`formatted_body` using an anchor, like so:

    {
        "body": "Hello Alice!",
        "msgtype": "m.text",
        "format": "org.matrix.custom.html",
        "formatted_body": "Hello <a href='https://matrix.to/#/@alice:example.org'>Alice</a>!"
    }

##### Client behaviour

In addition to using the appropriate `matrix.to URI` for the mention,
clients should use the following guidelines when making mentions in
events to be sent:

-   When mentioning users, use the user's potentially ambiguous display
    name for the anchor's text. If the user does not have a display
    name, use the user's ID.
-   When mentioning rooms, use the canonical alias for the room. If the
    room does not have a canonical alias, prefer one of the aliases
    listed on the room. If no alias can be found, fall back to the room
    ID. In all cases, use the alias/room ID being linked to as the
    anchor's text.
-   When referencing groups, use the group ID as the anchor's text.

The text component of the anchor should be used in the event's `body`
where the mention would normally be represented, as shown in the example
above.

Clients should display mentions differently from other elements. For
example, this may be done by changing the background color of the
mention to indicate that it is different from a normal link.

If the current user is mentioned in a message (either by a mention as
defined in this module or by a push rule), the client should show that
mention differently from other mentions, such as by using a red
background color to signify to the user that they were mentioned.

When clicked, the mention should navigate the user to the appropriate
room, group, or user information.

### Room Upgrades

From time to time, a room may need to be upgraded to a different room
version for a variety for reasons. This module defines a way for rooms
to upgrade to a different room version when needed.

##### Events

{{m\_room\_tombstone\_event}}

##### Client behaviour

Clients which understand `m.room.tombstone` events and the `predecessor`
field on `m.room.create` events should communicate to the user that the
room was upgraded. One way of accomplishing this would be hiding the old
room from the user's room list and showing banners linking between the
old and new room - ensuring that permalinks work when referencing the
old room. Another approach may be to virtually merge the rooms such that
the old room's timeline seamlessly continues into the new timeline
without the user having to jump between the rooms.

{{room\_upgrades\_cs\_http\_api}}

##### Server behaviour

When the client requests to upgrade a known room to a known version, the
server:

1.  Checks that the user has permission to send `m.room.tombstone`
    events in the room.

2.  Creates a replacement room with a `m.room.create` event containing a
    `predecessor` field and the applicable `room_version`.

3.  Replicates transferable state events to the new room. The exact
    details for what is transferred is left as an implementation detail,
    however the recommended state events to transfer are:

    -   `m.room.server_acl`
    -   `m.room.encryption`
    -   `m.room.name`
    -   `m.room.avatar`
    -   `m.room.topic`
    -   `m.room.guest_access`
    -   `m.room.history_visibility`
    -   `m.room.join_rules`
    -   `m.room.power_levels`

    Membership events should not be transferred to the new room due to
    technical limitations of servers not being able to impersonate
    people from other homeservers. Additionally, servers should not
    transfer state events which are sensitive to who sent them, such as
    events outside of the Matrix namespace where clients may rely on the
    sender to match certain criteria.

4.  Moves any local aliases to the new room.

5.  Sends a `m.room.tombstone` event to the old room to indicate that it
    is not intended to be used any further.

6.  If possible, the power levels in the old room should also be
    modified to prevent sending of events and inviting new users. For
    example, setting `events_default` and `invite` to the greater of
    `50` and `users_default + 1`.

When a user joins the new room, the server should automatically
transfer/replicate some of the user's personalized settings such as
notifications, tags, etc.

### Server Notices

Homeserver hosts often want to send messages to users in an official
capacity, or have resource limits which affect a user's ability to use
the homeserver. For example, the homeserver may be limited to a certain
number of active users per month and has exceeded that limit. To
communicate this failure to users, the homeserver would use the Server
Notices room.

The aesthetics of the room (name, topic, avatar, etc) are left as an
implementation detail. It is recommended that the homeserver decorate
the room such that it looks like an official room to users.

##### Events

Notices are sent to the client as normal `m.room.message` events with a
`msgtype` of `m.server_notice` in the server notices room. Events with a
`m.server_notice` `msgtype` outside of the server notice room must be
ignored by clients.

The specified values for `server_notice_type` are:

`m.server_notice.usage_limit_reached`  
The server has exceeded some limit which requires the server
administrator to intervene. The `limit_type` describes the kind of limit
reached. The specified values for `limit_type` are:

`monthly_active_user`  
The server's number of active users in the last 30 days has exceeded the
maximum. New connections are being refused by the server. What defines
"active" is left as an implementation detail, however servers are
encouraged to treat syncing users as "active".

{{m\_room\_message\_m\_server\_notice\_event}}

##### Client behaviour

Clients can identify the server notices room by the `m.server_notice`
tag on the room. Active notices are represented by the [pinned
events](#m-room-pinned-events) in the server notices room. Server notice
events pinned in that room should be shown to the user through special
UI and not through the normal pinned events interface in the client. For
example, clients may show warning banners or bring up dialogs to get the
user's attention. Events which are not server notice events and are
pinned in the server notices room should be shown just like any other
pinned event in a room.

The client must not expect to be able to reject an invite to join the
server notices room. Attempting to reject the invite must result in a
`M_CANNOT_LEAVE_SERVER_NOTICE_ROOM` error. Servers should not prevent
the user leaving the room after joining the server notices room, however
the same error code must be used if the server will prevent leaving the
room.

##### Server behaviour

Servers should manage exactly 1 server notices room per user. Servers
must identify this room to clients with the `m.server_notice` tag.
Servers should invite the target user rather than automatically join
them to the server notice room.

How servers send notices to clients, and which user they use to send the
events, is left as an implementation detail for the server.

### Moderation policy lists

With Matrix being an open network where anyone can participate, a very
wide range of content exists and it is important that users are
empowered to select which content they wish to see, and which content
they wish to block. By extension, room moderators and server admins
should also be able to select which content they do not wish to host in
their rooms and servers.

The protocol's position on this is one of neutrality: it should not be
deciding what content is undesirable for any particular entity and
should instead be empowering those entities to make their own decisions.
As such, a generic framework for communicating "moderation policy lists"
or "moderation policy rooms" is described. Note that this module only
describes the data structures and not how they should be interpreting:
the entity making the decisions on filtering is best positioned to
interpret the rules how it sees fit.

Moderation policy lists are stored as room state events. There are no
restrictions on how the rooms can be configured (they could be public,
private, encrypted, etc).

There are currently 3 kinds of entities which can be affected by rules:
`user`, `server`, and `room`. All 3 are described with
`m.policy.rule.<kind>` state events. The `state_key` for a policy rule
is an arbitrary string decided by the sender of the rule.

Rules contain recommendations and reasons for the rule existing. The
`reason` is a human-readable string which describes the
`recommendation`. Currently only one recommendation, `m.ban`, is
specified.

##### `m.ban` recommendation

When this recommendation is used, the entities affected by the rule
should be banned from participation where possible. The enforcement of
this is deliberately left as an implementation detail to avoid the
protocol imposing its opinion on how the policy list is to be
interpreted. However, a suggestion for a simple implementation is as
follows:

-   Is a `user` rule...
    -   Applied to a user: The user should be added to the subscriber's
        ignore list.
    -   Applied to a room: The user should be banned from the room
        (either on sight or immediately).
    -   Applied to a server: The user should not be allowed to send
        invites to users on the server.
-   Is a `room` rule...
    -   Applied to a user: The user should leave the room and not join
        it
        ([MSC2270](https://github.com/matrix-org/matrix-doc/pull/2270)-style
        ignore).
    -   Applied to a room: No-op because a room cannot ban itself.
    -   Applied to a server: The server should prevent users from
        joining the room and from receiving invites to it.
-   Is a `server` rule...
    -   Applied to a user: The user should not receive events or invites
        from the server.
    -   Applied to a room: The server is added as a denied server in the
        ACLs.
    -   Applied to a server: The subscriber should avoid federating with
        the server as much as possible by blocking invites from the
        server and not sending traffic unless strictly required (no
        outbound invites).

##### Subscribing to policy lists

This is deliberatly left as an implementation detail. For
implementations using the Client-Server API, this could be as easy as
joining or peeking the room. Joining or peeking is not required,
however: an implementation could poll for updates or use a different
technique for receiving updates to the policy's rules.

##### Sharing

In addition to sharing a direct reference to the room which contains the
policy's rules, plain http or https URLs can be used to share links to
the list. When the URL is approached with a `Accept: application/json`
header or has `.json` appended to the end of the URL, it should return a
JSON object containing a `room_uri` property which references the room.
Currently this would be a `matrix.to` URI, however in future it could be
a Matrix-schemed URI instead. When not approached with the intent of
JSON, the service could return a user-friendly page describing what is
included in the ban list.

##### Events

The `entity` described by the state events can contain `*` and `?` to
match zero or more and one or more characters respectively. Note that
rules against rooms can describe a room ID or room alias - the
subscriber is responsible for resolving the alias to a room ID if
desired.

{{m\_policy\_rule\_user\_event}}

{{m\_policy\_rule\_room\_event}}

{{m\_policy\_rule\_server\_event}}

##### Client behaviour

As described above, the client behaviour is deliberatly left undefined.

##### Server behaviour

Servers have no additional requirements placed on them by this module.

##### Security considerations

This module could be used to build a system of shared blacklists, which
may create a divide within established communities if not carefully
deployed. This may well not be a suitable solution for all communities.

Depending on how implementations handle subscriptions, user IDs may be
linked to policy lists and therefore expose the views of that user. For
example, a client implementation which joins the user to the policy room
would expose the user's ID to observers of the policy room. In future,
[MSC1228](https://github.com/matrix-org/matrix-doc/pulls/1228) and
[MSC1777](https://github.com/matrix-org/matrix-doc/pulls/1777) (or
similar) could help solve this concern.

[1] A request to an endpoint that uses User-Interactive Authentication
never succeeds without auth. Homeservers may allow requests that don't
require auth by offering a stage with only the `m.login.dummy` auth
type, but they must still give a 401 response to requests with no auth
data.

## Guest access

It may be desirable to allow users without a fully registered user
account to ephemerally access Matrix rooms. This module specifies
limited ways of doing so.

Note that this is not currently a complete anonymous access solution; in
particular, it only allows servers to provided anonymous access to rooms
in which they are already participating, and relies on individual
homeservers to adhere to the conventions which this module sets, rather
than allowing all participating homeservers to enforce them.

### Events

{{m\_room\_guest\_accessibility}}

### Client behaviour

A client can register for guest access using the FOO endpoint. From that
point on, they can interact with a limited subset of the existing
client-server API, as if they were a fully registered user, using the
access token granted to them by the server.

These users are only allowed to make calls in relation to rooms which
have the `m.room.history_visibility` event set to `world_readable`.

The APIs they are allowed to hit are:

/rooms/{roomId}/messages /rooms/{roomId}/state
/rooms/{roomId}/state/{eventType}/{stateKey} /events

### Server behaviour

Does the server need to handle any of the new events in a special way
(e.g. typing timeouts, presence). Advice on how to persist events and/or
requests are recommended to aid implementation. Federation-specific
logic should be included here.

### Security considerations

This includes privacy leaks: for example leaking presence info. How do
misbehaving clients or servers impact this module? This section should
always be included, if only to say "we've thought about it but there
isn't anything to do here".

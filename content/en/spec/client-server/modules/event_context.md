---
title: Event Context
type: docs
weight: 10
---

This API returns a number of events that happened just before and after
the specified event. This allows clients to get the context surrounding
an event.

## Client behaviour

There is a single HTTP API for retrieving event context, documented
below.

{{% http-api spec="client-server" api= "event_context" %}}

## Security considerations

The server must only return results that the user has permission to see.

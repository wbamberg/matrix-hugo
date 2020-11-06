---
title: Reporting Content
type: docs
weight: 10
---

Users may encounter content which they find inappropriate and should be
able to report it to the server administrators or room moderators for
review. This module defines a way for users to report content.

Content is reported based upon a negative score, where -100 is "most
offensive" and 0 is "inoffensive".

## Client behaviour

{{report\_content\_cs\_http\_api}}

## Server behaviour

Servers are free to handle the reported content however they desire.
This may be a dedicated room to alert server administrators to the
reported content or some other mechanism for notifying the appropriate
people.
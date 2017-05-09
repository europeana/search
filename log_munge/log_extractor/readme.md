# Purpose
This package is a small library for extracting information in (relatively) human-readable form from our
ELK-stack logging framework. Note that this logging framework issues bespoke messages in a unique format; these classes are not easily generalisable to parsing logs from other sources.

# Overview

The overall procedure for extracting information from the logs is:

1. First, we loop through the logs between two designated temporal endpoints, extracting session IDs
2. Then we retrieve all queries and actions associated with these session IDs
3. Filter as necessary
4. Post-process for readability.

Step 1 is performed by the `SessionExtractor`.

[fill in remainder as work proceeds]

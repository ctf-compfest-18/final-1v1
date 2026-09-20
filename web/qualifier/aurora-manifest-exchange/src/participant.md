# Aurora Manifest Exchange

Author: PolarBear7

Aurora Freight has moved partner shipment approvals into a new manifest exchange. The public validation console and the internal dispatch worker were migrated separately, and operations reports that the two components do not always agree on a manifest after approval.

Audit the exchange and recover the sealed export label.

Connection: http://34.1.203.129:4007

## Hints

1. Compare what the validation stage reads with what the release stage reads.
2. The manifest is processed as JSON more than once. Pay attention to how repeated fields are interpreted.
3. A successful release creates a short-lived asynchronous handoff before the label can be retrieved.

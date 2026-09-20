# Queue Zero

Author: PolarBear7

Northline Claims is rolling out a compensation queue for delayed shipments. A single-use claim receipt should be redeemed once before the queue marks it as settled, but recent operational reports show duplicate processing under unusual load.

Audit the claim flow and recover the sealed release label.

Connection: http://34.1.203.129:4013

## Hints

1. A claim receipt is intended to be single-use, but inspect the exact order of validation and state changes.
2. The settlement lanes share one receipt and respond asynchronously. Test their behavior under concurrent requests.
3. The release package requires distinct fragments from the settlement flow.

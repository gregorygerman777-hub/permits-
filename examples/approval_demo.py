"""Two-terminal approval demo; simulates delivery without sending anything."""
from __future__ import annotations

import argparse

from permitd import Gate, RED


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', default='permitd.db', help='shared permit database')
    parser.add_argument('--to', default='alice')
    parser.add_argument('--body', default='hello from the loop')
    parser.add_argument('--permit-id', help='retry a previously approved proposal')
    args = parser.parse_args()
    gate = Gate(db=args.db)

    @gate.tool(tier=RED, description='simulate message delivery')
    def send_message(to: str, body: str) -> str:
        return f'simulated delivery to {to}: {body!r}'

    result = gate.call('send_message', {'to': args.to, 'body': args.body},
                       permit_id=args.permit_id)
    if result.ok:
        print(result.result)
        return 0
    print(result.error)
    if result.permit:
        print(f'Permit ID: {result.permit["id"]}')
        print('Approve using permitd --db <same database> approve <permit ID>,')
        print('then rerun this demo with the same arguments and --permit-id <permit ID>.')
        return 0
    return 1


if __name__ == '__main__':
    raise SystemExit(main())

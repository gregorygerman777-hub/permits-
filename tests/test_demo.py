"""Exercise the documented demo across separate CLI processes."""
import subprocess
import sys
from pathlib import Path

from permitd import AuditLog, SqliteStore


def test_demo_requires_approval_and_refuses_replay(tmp_path):
    script = Path(__file__).resolve().parents[1] / 'examples' / 'approval_demo.py'
    db = tmp_path / 'permitd.db'
    command = [sys.executable, str(script), '--db', str(db)]
    proposed = subprocess.run(command, capture_output=True, text=True, check=True)
    assert 'simulated delivery' not in proposed.stdout
    permit = SqliteStore(db).list()[0]
    subprocess.run([sys.executable, '-m', 'permitd.cli', '--db', str(db),
                    'approve', permit.id], capture_output=True, check=True)
    retry = command + ['--permit-id', permit.id]
    executed = subprocess.run(retry, capture_output=True, text=True, check=True)
    assert 'simulated delivery to alice' in executed.stdout
    replay = subprocess.run(retry, capture_output=True, text=True)
    assert replay.returncode == 1
    assert 'already_used' in replay.stdout
    audit = AuditLog(tmp_path / 'permitd_audit.jsonl')
    assert audit.verify().ok
    assert [r['event'] for r in audit.tail()] == [
        'proposed', 'approved', 'executed', 'refused']

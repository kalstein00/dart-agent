"""Versioned identity acceptance at the consumer boundary."""
import copy
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from prepare_release import versioned_identity

CONTRACT = {
    "releaseVersion": "2.1.0", "protocolVersion": 2, "formatVersion": 2,
    "contractVersion": "1.0.0",
    "fingerprint": {"algorithm": "sha256", "projectionVersion": 1, "value": "a" * 64},
}


class VersionedIdentityTests(unittest.TestCase):
    def test_protocol_3_identity_accepts_only_the_pinned_release_and_contract(self):
        baseline = copy.deepcopy(CONTRACT)
        baseline.update(releaseVersion='2.1.1', protocolVersion=3, contractVersion='2.0.0')
        response = dict(ok=True, protocolVersion=3, data=dict(version='2.1.1', contract=baseline))
        versioned_identity(response, baseline)
        for field, value in (('protocolVersion', 2), ('contractVersion', '1.0.0'),
                             ('releaseVersion', '2.1.0')):
            altered = copy.deepcopy(response)
            altered['data']['contract'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                versioned_identity(altered, baseline)
        response['protocolVersion'] = 2
        with self.assertRaises(ValueError):
            versioned_identity(response, baseline)

    def test_exact_identity_is_accepted(self):
        versioned_identity({"ok": True, "protocolVersion": 2,
                            "data": {"version": "2.1.0", "contract": CONTRACT}}, CONTRACT)

    def test_missing_or_mismatched_identity_is_rejected(self):
        for field in ("releaseVersion", "protocolVersion", "formatVersion", "contractVersion", "fingerprint"):
            with self.subTest(field=field):
                altered = copy.deepcopy(CONTRACT)
                del altered[field]
                with self.assertRaises((ValueError, KeyError)):
                    versioned_identity({"ok": True, "protocolVersion": 2,
                                        "data": {"version": "2.1.0", "contract": altered}}, CONTRACT)
        altered = copy.deepcopy(CONTRACT)
        altered["contractVersion"] = "1.1.0"
        with self.assertRaises(ValueError):
            versioned_identity({"ok": True, "protocolVersion": 2,
                                "data": {"version": "2.1.0", "contract": altered}}, CONTRACT)

    def test_failed_or_legacy_response_is_not_accepted(self):
        for response in ({"ok": False}, {"ok": True, "protocolVersion": 2,
                                         "data": {"version": "2.1.0", "contract": {}}}):
            with self.assertRaises((ValueError, KeyError)):
                versioned_identity(response, CONTRACT)

    def test_fingerprint_and_protocol_mismatch_are_rejected(self):
        for field, value in (("fingerprint", {"algorithm": "sha256", "projectionVersion": 1, "value": "b" * 64}),
                             ("protocolVersion", 3)):
            altered = copy.deepcopy(CONTRACT)
            altered[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                versioned_identity({"ok": True, "protocolVersion": 2,
                                    "data": {"version": "2.1.0", "contract": altered}}, CONTRACT)

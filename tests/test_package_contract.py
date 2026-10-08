from __future__ import annotations

import unittest

from scripts.validate_skills import validate


class PublicSkillContractTests(unittest.TestCase):
    def test_all_public_packages_have_complete_contracts(self) -> None:
        self.assertEqual(validate(), [])


if __name__ == "__main__":
    unittest.main()

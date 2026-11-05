import unittest
import sys
import os
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from main import run

class TestExcelFullSkill(unittest.TestCase):
    def setUp(self):
        self.tmp_xlsx = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False).name

    def test_create_excel(self):
        res = run({"action":"create", "file_path": self.tmp_xlsx})
        self.assertEqual(res["status"], "success")

    def test_write_and_calc_formula(self):
        run({"action":"create", "file_path": self.tmp_xlsx})
        # Write basic data
        run({"action":"write_cell","file_path":self.tmp_xlsx,"row":1,"col":1,"value":10})
        run({"action":"write_cell","file_path":self.tmp_xlsx,"row":2,"col":1,"value":20})
        # Write sum formula
        res_form = run({
            "action":"write_formula",
            "file_path":self.tmp_xlsx,
            "row":3,"col":1,
            "formula":"=SUM(A1:A2)"
        })
        self.assertEqual(res_form["status"], "success")

    def test_check_bad_formula(self):
        res = run({"action":"check_formula","formula":"=SUM(A1:A2"})
        self.assertEqual(res["status"], "success")
        self.assertFalse(res["data"]["is_formula_valid"])

    def test_optimize_formula(self):
        res = run({"action":"optimize_formula","formula":"=SUM(A:A)"})
        self.assertEqual(res["status"], "success")

    def tearDown(self):
        if os.path.exists(self.tmp_xlsx):
            os.unlink(self.tmp_xlsx)

if __name__ == "__main__":
    unittest.main()

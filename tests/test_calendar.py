import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from calendars import boc_events
class CalendarTests(unittest.TestCase):
 def test_explicit_year_and_html_entities(self):
  raw='<table><caption>Schedule for 2027</caption><tr><td>January&nbsp;27</td><td>Interest rate announcement</td></tr></table>'
  self.assertEqual(boc_events(raw,'https://www.bankofcanada.ca/')[0]['date'],'2027-01-27')
 def test_missing_table_does_not_invent_dates(self):
  with self.assertRaises(ValueError):boc_events('<p>Temporarily unavailable</p>','https://www.bankofcanada.ca/')

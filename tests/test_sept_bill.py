import pytest
import yaml
from home_energy.load_esb import load_hdf
from home_energy.tariff import bill_summary

raw_hdf = "data/raw/hdf_kwh_30min.csv"

with open("config/system.yaml") as f:
    cfg = yaml.safe_load(f)

plan = cfg["tariffs"]["electric_ireland_current"]
charges = cfg["regulated_charges"]

def test_september_bill_from_half_hours():
    usage = load_hdf(raw_hdf).loc["2026-09-04":"2026-10-03"]
    bill = bill_summary(plan, usage, days=30, charges=charges, start_date="2026-09-04", months=1)

    assert len(usage) == 30 * 48                                   
    assert bill["import_cost"] == pytest.approx(113.22, abs=0.6)   
    assert bill["export_credit"] == pytest.approx(67.86, abs=0.1)
    assert bill["net_cost"] == pytest.approx(53.41, abs=0.5)
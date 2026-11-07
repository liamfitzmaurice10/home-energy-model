import pytest
from home_energy.load_esb import load_hdf
from home_energy.tariff import load_plan, bill_summary

raw_hdf = "data/raw/hdf_kwh_30min.csv"

def test_september_bill_from_half_hours():
    plan = load_plan("electric_ireland_current", path="config/system.yaml")
    usage = load_hdf(raw_hdf).loc["2026-09-04":"2026-10-03"]
    bill = bill_summary(plan, usage, days=30, months=1)

    assert len(usage) == 30 * 48                                   
    assert bill["import_cost"] == pytest.approx(113.22, abs=0.6)   
    assert bill["export_credit"] == pytest.approx(67.86, abs=0.1)
    assert bill["net_cost"] == pytest.approx(53.41, abs=0.5)
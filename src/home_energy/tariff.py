import pandas as pd
import yaml

def _rate_by_hour(plan):
    """Import price by plan for each hour of the day 0-23.
    Checks there is no overlap or missing hours.
    Returns a dictionary with {hour: rate for that hour}"""
    rates = plan["import_rates"]
    if sorted(h for rate in rates for h in rate["hours"]) != list(range(24)):
        raise ValueError("At least one hour extra or missing")
    return {hour: rate["eur_per_kwh"] for rate in rates for hour in rate["hours"]}

def load_plan(name, path="config/system.yaml"):
    """Read plan from the YAML file."""
    with open(path) as f:
        return yaml.safe_load(f)["tariffs"][name]

def price_per_kwh(index, plan):
    """Import price for each timestamp. 
    Input index must be in Dublin time."""
    return pd.Series(index.hour, index=index).map(_rate_by_hour(plan))

def bill_summary(plan, usage, days, months=None, apply_discounts=True):
    """Bill breakdown for a period of usage"""
    if months is None:
        months = (days*12) / 365

    import_cost = (usage["import_kwh"]*price_per_kwh(usage.index, plan)).sum()
    export_credit = usage["export_kwh"].sum()*plan["export_rates"][0]["eur_per_kwh"]

    discount = 0
    if apply_discounts:
        for disc in plan.get("discounts", []):
            discount += import_cost*disc["pct"] / 100

    standing = plan["standing_charge_eur_per_day"] * days
    levies = sum(l["eur_per_month"] * months for l in plan.get("levies", []))
    before_vat = import_cost - discount + standing + levies
    vat = before_vat * plan["vat_pct"] / 100    

    return {
        "import_cost": import_cost, "discount": discount, "standing": standing,
        "levies": levies, "vat": vat, "export_credit": export_credit,
        "net_cost": before_vat + vat - export_credit,
    }
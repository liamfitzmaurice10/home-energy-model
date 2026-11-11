import pandas as pd
import numpy as np

def _rate_table(plan):
    """Import price by plan for each hour of the day 0-23.  
    Checks there is no overlap or missing hours."""
    day_num = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
    table = [None] * 168  
    
    for rate in plan["import_rates"]:
        days = [day_num[day] for day in rate.get("days", day_num)]
        
        for day in days:
            for hour in rate["hours"]:
                index = day * 24 + hour
                if table[index] is not None:
                    raise ValueError("There is either overlap or missing hours") 
                table[index] = rate["eur_per_kwh"]

    if None in table:
        raise ValueError("At least one hour is missing")

    return table

def price_per_kwh(index, plan):
    table = _rate_table(plan)
    return pd.Series([table[day*24 + h] for day, h in zip(index.day_of_week, index.hour)], index=index)

def bill_summary(plan, usage, days, charges, start_date=None,months=None, apply_discounts=True):
    """Bill breakdown for a period of usage"""
    if months is None:
        months = (days*12) / 365
    if start_date is None:
        start_date = pd.Timestamp.today()
    start = pd.Timestamp(start_date).date()

    import_cost = (usage["import_kwh"]*price_per_kwh(usage.index, plan)).sum()
    export_credit = usage["export_kwh"].sum()*plan["export_rates"][0]["eur_per_kwh"]

    discount = 0
    if apply_discounts:
        for disc in plan.get("discounts", []):
            discount += import_cost*disc["pct"] / 100

    standing = plan["standing_charge_eur_per_day"] * days
    pso = max((e for e in charges["pso_levy"] if e["valid_from"] <= start),
            key=lambda e: e["valid_from"])["eur_per_month"] * months
    vat_pct = max((e for e in charges["vat_pct"] if e["valid_from"] <= start),
                key=lambda e: e["valid_from"])["pct"]
    before_vat = import_cost - discount + standing + pso
    vat = before_vat * vat_pct / 100
    
    return {
        "import_cost": import_cost, "discount": discount, "standing": standing,
        "levies": pso, "vat": vat, "export_credit": export_credit,
        "net_cost": before_vat + vat - export_credit,
    }
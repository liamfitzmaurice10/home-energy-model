import pandas as pd

def load_hdf(path):    
    """Read ESB HDF kWh file and return a table indexed by interval start in Dublin time.
    import_kwh and export_kwh columns. Any export before solar was installed set to 0."""
    #This is derived from the original EDA in notebooks\ 01_EDA_esb_data.ipynb
    df = pd.read_csv(path).iloc[::-1]
    
    df = df[["Read Value", "Read Type", "Read Date and End Time"]].copy()
    df["end_interval"] = pd.to_datetime(df["Read Date and End Time"], dayfirst = True)
    
    imp = df[df["Read Type"] == "Active Import Interval (kWh)"].set_index("end_interval")
    exp = df[df["Read Type"] == "Active Export Interval (kWh)"].set_index("end_interval")

    imp.index = imp.index.tz_localize("Europe/Dublin", ambiguous= "infer")
    exp.index = exp.index.tz_localize("Europe/Dublin", ambiguous= "infer")

    df2 = pd.concat([imp["Read Value"].rename("import_kwh"), exp["Read Value"].rename("export_kwh")],
                    axis=1, sort = False).sort_index()
    
    first_export = exp.index.min()
    df2.loc[df2.index < first_export, "export_kwh"] = 0.0

    df2.index = df2.index - pd.Timedelta(minutes=30)
    df2.index.name = "start_interval"

    assert df2.index.is_unique
    return df2
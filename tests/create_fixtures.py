"""One-off script to create test fixtures mimicking CAMELS-CH format."""

from pathlib import Path

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "camels_ch"

# --- Static attributes: topographic (with Latin-1 chars) ---
topo_csv = (
    "# Topographic attributes for CAMELS-CH\n"
    "# Source: Höge et al. (2023)\n"
    "gauge_id,gauge_name,gauge_lat(deg),gauge_lon(deg),area(km2),elev_mean(m),country\n"
    '2004,"Zürich - Unterhard",47.3982,8.5182,77.5,556.0,CH\n'
    '2007,"Münster",46.4930,8.2655,52.3,2110.0,CH\n'
    '3001,"Bellinzona",46.1945,9.0170,1515.0,1670.0,CH\n'
)

# --- Static attributes: climate ---
climate_csv = (
    "# Climate attributes for CAMELS-CH\n"
    "gauge_id,p_mean(mm/d),pet_mean(mm/d),aridity_index(-),t_mean(degC)\n"
    "2004,3.8,2.1,0.55,9.5\n"
    "2007,4.2,1.8,0.43,3.2\n"
    "3001,5.1,2.0,0.39,7.1\n"
)

# --- Static attributes: supplement ---
supplement_csv = (
    "# Supplementary attributes\n"
    "gauge_id,forest_frac(%),urban_frac(%)\n"
    "2004,35.2,12.5\n"
    "2007,42.1,2.3\n"
    "3001,55.0,5.1\n"
)

# --- Static attributes: simulation-based ---
sim_attr_csv = (
    "# Simulation-based attributes from PREVAH\n"
    "gauge_id,runoff_ratio_sim(-),baseflow_index_sim(-)\n"
    "2004,0.55,0.42\n"
    "2007,0.72,0.38\n"
    "3001,0.65,0.51\n"
)

# --- Time series: observation_based (3 basins, 5 days each) ---
OBS_HEADER = (
    "gauge_id,date,discharge_vol(m3/s),discharge_spec(mm/d),waterlevel(m),"
    "precipitation(mm/d),temperature_min(degC),temperature_mean(degC),"
    "temperature_max(degC),rel_sun_dur(%),swe(mm)\n"
)

obs_data = {
    "2004": [
        "2004,1981-01-01,1.5,0.8,101.2,2.3,-3.1,0.5,4.2,45.0,10.0\n",
        "2004,1981-01-02,1.8,0.9,101.5,0.0,-4.2,-0.8,2.1,72.0,10.5\n",
        "2004,1981-01-03,1.6,0.85,101.3,5.1,-1.0,1.2,3.5,15.0,12.0\n",
        "2004,1981-01-04,2.1,1.1,102.0,3.2,-2.5,0.1,2.8,30.0,14.0\n",
        "2004,1981-01-05,1.9,1.0,101.8,0.5,-3.0,-0.5,2.0,60.0,13.5\n",
    ],
    "2007": [
        "2007,1981-01-01,0.8,0.6,88.5,3.1,-8.0,-4.5,-1.0,20.0,55.0\n",
        "2007,1981-01-02,0.9,0.65,88.8,0.0,-9.1,-5.2,-2.0,80.0,55.5\n",
        "2007,1981-01-03,0.7,0.55,88.3,6.2,-5.5,-3.0,0.5,10.0,60.0\n",
        "2007,1981-01-04,1.1,0.8,89.2,4.0,-7.0,-4.0,-1.5,25.0,63.0\n",
        "2007,1981-01-05,1.0,0.75,89.0,1.0,-8.5,-5.0,-2.5,55.0,62.0\n",
    ],
    "3001": [
        "3001,1981-01-01,25.0,1.4,200.1,4.5,-1.0,2.0,5.5,35.0,30.0\n",
        "3001,1981-01-02,28.0,1.6,201.0,0.0,-2.0,1.0,4.0,65.0,30.5\n",
        "3001,1981-01-03,22.0,1.2,199.5,8.0,0.5,3.5,7.0,8.0,33.0\n",
        "3001,1981-01-04,30.0,1.7,202.0,5.5,-1.5,1.5,4.5,22.0,36.0\n",
        "3001,1981-01-05,26.0,1.45,200.8,1.2,-2.5,0.5,3.0,50.0,35.0\n",
    ],
}

# --- Time series: simulation_based ---
SIM_HEADER = (
    "gauge_id,date,discharge_vol_sim(m3/s),discharge_spec_sim(mm/d),"
    "precipitation_sim(mm/d),temperature_sim(degC),radiation_sim(W/m2),"
    "sun_duration_sim(h),wind_sim(m/s),rel_humidity_sim(%),"
    "pet_sim(mm/d),et_sim(mm/d),intercept_et_sim(mm/d),"
    "intercept_storage_sim(mm)\n"
)

sim_data = {
    "2004": [
        "2004,1981-01-01,1.4,0.75,2.4,0.6,80.0,3.2,2.5,75.0,1.5,0.8,0.1,0.05\n",
        "2004,1981-01-02,1.7,0.88,0.1,-0.7,120.0,5.1,1.8,65.0,1.8,0.9,0.12,0.04\n",
        "2004,1981-01-03,1.5,0.82,5.0,1.3,40.0,1.0,3.2,85.0,0.8,0.5,0.08,0.06\n",
        "2004,1981-01-04,2.0,1.05,3.3,0.2,60.0,2.0,2.8,80.0,1.2,0.7,0.09,0.05\n",
        "2004,1981-01-05,1.8,0.95,0.6,-0.4,100.0,4.0,2.0,70.0,1.6,0.85,0.11,0.04\n",
    ],
    "2007": [
        "2007,1981-01-01,0.7,0.55,3.2,-4.6,50.0,1.5,4.0,90.0,0.5,0.3,0.05,0.02\n",
        "2007,1981-01-02,0.85,0.62,0.1,-5.3,90.0,6.0,3.5,80.0,0.7,0.4,0.06,0.02\n",
        "2007,1981-01-03,0.65,0.5,6.0,-3.1,25.0,0.8,5.0,95.0,0.3,0.2,0.04,0.03\n",
        "2007,1981-01-04,1.0,0.75,4.1,-4.1,45.0,1.8,4.2,88.0,0.6,0.35,0.05,0.02\n",
        "2007,1981-01-05,0.95,0.7,1.1,-5.1,75.0,3.5,3.8,82.0,0.65,0.38,0.06,0.02\n",
    ],
    "3001": [
        "3001,1981-01-01,24.0,1.35,4.6,2.1,70.0,2.5,3.0,78.0,1.8,1.0,0.15,0.08\n",
        "3001,1981-01-02,27.0,1.55,0.1,1.1,110.0,4.5,2.2,68.0,2.1,1.2,0.18,0.07\n",
        "3001,1981-01-03,21.0,1.15,7.8,3.6,30.0,0.5,4.0,90.0,0.6,0.4,0.07,0.09\n",
        "3001,1981-01-04,29.0,1.65,5.6,1.6,55.0,1.5,3.2,82.0,1.4,0.8,0.12,0.08\n",
        "3001,1981-01-05,25.0,1.4,1.3,0.6,95.0,3.8,2.5,72.0,1.7,0.95,0.14,0.07\n",
    ],
}


def _write_geometry_fixtures() -> None:
    """Write a synthetic shapefile with 3 basin polygons in EPSG:2056."""
    import geopandas as gpd_
    from shapely.geometry import Polygon

    # Irregular, roughly elongated polygons in approximate LV95 coordinates.
    # Catchments are narrower upstream (top) and wider downstream (bottom),
    # like a leaf or fan shape.

    # Basin 2004: centered ~(602500, 202500), ~5 km extent
    poly_2004 = Polygon(
        [
            (602500, 205000),  # upstream tip
            (603400, 204500),
            (604200, 203500),
            (604800, 202200),
            (604500, 201000),
            (603200, 200200),
            (601800, 200000),
            (600600, 200800),
            (600200, 202000),
            (600800, 203500),
            (601700, 204600),
            (602500, 205000),  # close
        ]
    )

    # Basin 2007: centered ~(662500, 152500), ~5 km extent
    poly_2007 = Polygon(
        [
            (662400, 155000),  # upstream tip
            (663500, 154300),
            (664200, 153200),
            (664600, 151800),
            (664100, 150600),
            (663000, 150000),
            (661600, 150100),
            (660700, 150900),
            (660300, 152100),
            (660800, 153500),
            (661700, 154500),
            (662400, 155000),  # close
        ]
    )

    # Basin 3001: centered ~(725000, 125000), ~10 km extent (much larger)
    poly_3001 = Polygon(
        [
            (724500, 132000),  # upstream tip
            (726500, 131000),
            (728500, 129500),
            (730000, 127500),
            (730200, 125000),
            (729500, 122500),
            (727500, 120500),
            (725000, 119500),
            (722500, 119800),
            (720500, 121000),
            (719500, 123000),
            (719800, 125500),
            (720800, 127800),
            (722000, 129800),
            (723200, 131200),
            (724500, 132000),  # close
        ]
    )

    geometries = [poly_2004, poly_2007, poly_3001]
    gdf = gpd_.GeoDataFrame(
        {"gauge_id": ["2004", "2007", "3001"], "area_km2": [77.5, 52.3, 1515.0]},
        geometry=geometries,
        crs="EPSG:2056",
    )
    shp_dir = FIXTURE_DIR / "catchment_delineations" / "LV95" / "Shapes_LV95"
    shp_dir.mkdir(parents=True, exist_ok=True)
    shp_path = shp_dir / "CAMELS_CH_catchments.shp"
    gdf.to_file(shp_path)


def main() -> None:
    # Write attribute files (Latin-1 for topo to test encoding)
    topo_path = FIXTURE_DIR / "static_attributes" / "CAMELS_CH_topographic_attributes.csv"
    topo_path.write_bytes(topo_csv.encode("latin-1"))

    climate_path = FIXTURE_DIR / "static_attributes" / "CAMELS_CH_climate_attributes_obs.csv"
    climate_path.write_text(climate_csv, encoding="utf-8")

    supp_path = FIXTURE_DIR / "static_attributes" / "supplements" / "CAMELS_CH_supplement.csv"
    supp_path.write_text(supplement_csv, encoding="utf-8")

    sim_attr_path = (
        FIXTURE_DIR / "static_attributes" / "simulation_based" / "CAMELS_CH_sim_attrs.csv"
    )
    sim_attr_path.write_text(sim_attr_csv, encoding="utf-8")

    # Write observation time series
    for gauge_id, rows in obs_data.items():
        obs_path = (
            FIXTURE_DIR
            / "timeseries"
            / "observation_based"
            / f"CAMELS_CH_obs_based_{gauge_id}.csv"
        )
        obs_path.write_text(OBS_HEADER + "".join(rows), encoding="utf-8")

    # Write simulation time series
    for gauge_id, rows in sim_data.items():
        sim_path = (
            FIXTURE_DIR / "timeseries" / "simulation_based" / f"CAMELS_CH_sim_based_{gauge_id}.csv"
        )
        sim_path.write_text(SIM_HEADER + "".join(rows), encoding="utf-8")

    _write_geometry_fixtures()

    print("Fixtures created.")


if __name__ == "__main__":
    main()

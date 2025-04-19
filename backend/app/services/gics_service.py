import json
from pathlib import Path
from typing import Optional, Dict
from functools import lru_cache


GICS_FILE = Path(__file__).parent.parent / "data" / "gics.json"

def load_gics():
    with open(GICS_FILE, "r") as f:
        return json.load(f)

def get_all_sectors():
    with open(GICS_FILE, "r") as f:
        gics_data = json.load(f)
    sectors = sorted(set(item["sector_name"] for item in gics_data))
    return {"sectors": sectors}

def filter_gics_data(
    filter_type: str,
    sector: Optional[str],
    industry_group: Optional[str],
    industry: Optional[str],
    sub_industry: Optional[str],
):
    gics_data = load_gics()

    def matches(value: Optional[str], target: str) -> bool:
        if value is None or value.lower() == "all":
            return True
        return value.lower() in target.lower()

    filtered = [
        item for item in gics_data
        if matches(sector, item["sector_name"])
        and matches(industry_group, item["industry_group_name"])
        and matches(industry, item["industry_name"])
        and matches(sub_industry, item["sub_industry_name"])
    ]

    filter_map = {
        "sector": ("sector_code", "sector_name"),
        "industry_group": ("industry_group_code", "industry_group_name"),
        "industry": ("industry_code", "industry_name"),
        "sub_industry": ("sub_industry_code", "sub_industry_name"),
    }

    if filter_type not in filter_map:
        return {"error": f"Invalid filter_type '{filter_type}'. Must be one of: {list(filter_map.keys())}"}

    code_field, name_field = filter_map[filter_type]

    seen = set()
    values = []
    for item in filtered:
        key = (item[code_field], item[name_field])
        if key not in seen:
            seen.add(key)
            values.append({"code": item[code_field], "name": item[name_field]})

    return {
        "type": filter_type,
        "values": sorted(values, key=lambda x: x["name"]),
        "count": len(values)
    }


def get_gics_hierarchy():
    gics_data = load_gics()
    hierarchy = {}

    for item in gics_data:
        sec_code, sec_name = item["sector_code"], item["sector_name"]
        grp_code, grp_name = item["industry_group_code"], item["industry_group_name"]
        ind_code, ind_name = item["industry_code"], item["industry_name"]
        sub_code, sub_name = item["sub_industry_code"], item["sub_industry_name"]

        sec = hierarchy.setdefault(sec_code, {
            "code": sec_code, "name": sec_name, "industry_groups": {}
        })
        grp = sec["industry_groups"].setdefault(grp_code, {
            "code": grp_code, "name": grp_name, "industries": {}
        })
        ind = grp["industries"].setdefault(ind_code, {
            "code": ind_code, "name": ind_name, "sub_industries": []
        })
        ind["sub_industries"].append({"code": sub_code, "name": sub_name})

    # Convert dict to list recursively
    return [
        {
            "code": sec["code"],
            "name": sec["name"],
            "industry_groups": [
                {
                    "code": grp["code"],
                    "name": grp["name"],
                    "industries": [
                        {
                            "code": ind["code"],
                            "name": ind["name"],
                            "sub_industries": ind["sub_industries"]
                        } for ind in grp["industries"].values()
                    ]
                } for grp in sec["industry_groups"].values()
            ]
        }
        for sec in hierarchy.values()
    ]


@lru_cache()
def get_industry_to_group_map() -> Dict[str, str]:
    gics_data = load_gics()
    mapping = {}
    for item in gics_data:
        mapping[item["industry_name"]] = item["industry_group_name"]
    return mapping
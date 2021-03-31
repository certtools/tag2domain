import os

os.environ["ENABLE_MSM2TAG"] = "True"
os.environ["MSM2TAG_DB_CONFIG"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "config",
    "db.cfg"
)

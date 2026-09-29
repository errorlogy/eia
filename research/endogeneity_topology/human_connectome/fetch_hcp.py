"""Download the 4 HCP subjects used by brain_eia.py from neurolib's public dataset into ./data."""

from pathlib import Path
from urllib.request import urlretrieve

BASE = "https://raw.githubusercontent.com/neurolib-dev/neurolib/master/neurolib/data/datasets/hcp/subjects"
SUBJECTS = ["101309", "102311", "102816", "131217"]
FILES = ["structural/DTI_CM.mat", "structural/DTI_LEN.mat", "functional/TC_rsfMRI_REST1_LR.mat"]

data = Path(__file__).parent / "data"
data.mkdir(exist_ok=True)
for s in SUBJECTS:
    for f in FILES:
        out = data / f"{s}_{Path(f).name}"
        if not out.exists():
            urlretrieve(f"{BASE}/{s}/{f}", out)
            print("fetched", out.name)

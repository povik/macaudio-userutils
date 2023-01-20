#!/usr/bin/env python3
import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from macaudioutils.setup import *

set("Headphone Playback Mux", "Primary")
set("Speaker Playback Mux", "Secondary")
set("Speaker", 40)
set("ISENSE", True)
set("VSENSE", True)

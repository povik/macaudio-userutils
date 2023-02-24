import os

def require_debugfs():
    if os.path.ismount("/sys/kernel/debug"):
        return
    os.system("mount -t debugfs none /sys/kernel/debug")

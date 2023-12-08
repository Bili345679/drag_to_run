import sys
import os
from ez import t, f

sys_argv_list = sys.argv
for sys_argv in sys_argv_list:
    print(sys_argv)
try:
    f.json_dump(
        sys_argv_list,
        os.path.dirname(sys_argv_list[0])
        + "/python_sys_argv_log/%s.json" % (t.get_data_time()),
    )
except Exception:
    print("保存log失败")
os.system("pause")

import termcolor
from termcolor import colored
import threading
import queue
import time
import os

# ┌─┬─┐
# │ │ │
# ├─┼─┤
# │ │ │
# └─┴─┘

try:
    from ez import f, t
except:
    import f, t

os.system("color")

print_buffer = queue.Queue()
print_lock = threading.Lock()

color_dict = {
    "important": "blue",
    "info": "white",
    "warning": "yellow",
    "error": "red",
    "success": "green",
}

global term_col
term_col = os.get_terminal_size().columns
term_col_no_time = term_col - 22

last_timestamp = None
last_c_param = {"color": "white"}

is_hide_pr = False

# 添加队列
def pr(content=None, **kwargs):
    params = {
        "timestamp": kwargs["timestamp"] if "timestamp" in kwargs else time.time(),
        "content": content,
        "c_param": format_color_param(kwargs),
    }

    if "end" in kwargs:
        params["end"] = kwargs["end"]

    if "segregation" in kwargs:
        params["segregation"] = kwargs["segregation"]
    print_lock.acquire()
    print_buffer.put(params)
    print_lock.release()

def pr_debug(content=None, debug_flag=True,**kwargs):
    if debug_flag:
        pr(content,**kwargs)

# 颜色参数格式化
def format_color_param(params):
    def c_param_type(param):
        if param in termcolor.COLORS:
            return "color"
        if param in termcolor.HIGHLIGHTS:
            return "on_color"
        if param in termcolor.ATTRIBUTES:
            return "attrs"
        return False

    new_params = {}
    color = False
    on_light = False
    attrs = []
    if "c_param" in params:
        c_param = params["c_param"]
        if isinstance(c_param, str):
            type = c_param_type(c_param)
            if type is False:
                pass
            elif type != "attrs":
                c_param_type[type] = c_param
            else:
                new_params["attrs"] = [c_param]
        else:
            for each in c_param:
                print(each)
                if not isinstance(each, str):
                    continue
                type = c_param_type(each)
                if type is False:
                    continue
                elif type != "attrs":
                    new_params[type] = each
                else:
                    if "attrs" not in new_params:
                        new_params["attrs"] = []
                    new_params["attrs"].append(each)

    if "color" in params:
        color = params["color"]
        if color in color_dict.keys():
            new_params["color"] = color_dict[color]
        elif color in termcolor.COLORS:
            new_params["color"] = color
    else:
        new_params["color"] = "white"

    if "on_color" in params:
        on_light = params["on_color"]
        if on_light in termcolor.HIGHLIGHTS:
            new_params["on_color"] = on_light

    if "attrs" in params:
        attrs = params["attrs"]
        if isinstance(attrs, str) and attrs in termcolor.ATTRIBUTES:
            new_params["attrs"] = [attrs]
        elif isinstance(attrs, list):
            attr_list = [attr for attr in attrs if attr in termcolor.ATTRIBUTES]
            if attr_list:
                new_params["attrs"] = attr_list

    return new_params

##########################################
##########################################
##########################################

# 格式化打印
def format_print(
    content="",
    timestamp=False,
    c_param=False,
    end=None,
    segregation=False,
    indents=0,
    head_end=" ",
):
    if c_param is not False:
        # if indents == 0:
        global last_c_param
        last_c_param = c_param
    else:
        c_param = last_c_param

    if timestamp is not False:
        # if indents == 0:
        global last_timestamp
        last_timestamp = timestamp
    elif timestamp is not None:
        # is false
        timestamp = last_timestamp
    # if timestamp is False:
    #     timestamp = time.time()

    # 头
    head_list = []
    if indents > 0 or timestamp is None:
        # 不带时间
        # head_end = ""
        head_list = [head_end]
    elif timestamp == "now":
        head_list = ["[", colored(t.get_data_time(), **c_param), "]", head_end]
    else:
        head_list = ["[", colored(t.get_data_time(timestamp), **c_param), "]", head_end]
    head = "".join(head_list)
    # 分隔
    if segregation:
        format_print(pr_segregation(time=timestamp), head_end="")
        return True

    # 内容
    if isinstance(content, str):
        # 字符串
        if len(content) > term_col - len(head):
            content = "".join([content[: term_col - len(head) - 3], "..."])
        print(head + content, end=end)
    elif isinstance(content, (int, float, bool)):
        # 整数，浮点，布朗
        print(head + str(content), end=end)
    elif isinstance(content, list):
        # 列表
        if indents == 0:
            format_print()
        format_print_list(content, indents)
    elif isinstance(content, dict):
        # 字典
        if indents == 0:
            format_print()
        format_print_dict(content, indents)
    else:
        print(head + str(content), end=end)

##########################################
##########################################
##########################################

# 格式化打印列表
def format_print_list(content, indents):
    if indents == 0:
        format_print(pr_segregation("start", None), timestamp=None, head_end="")

    num = 0
    for each in content:
        if num == 0:
            table_ls = "┌"
            # table_ls = "├"
        elif num == len(content) - 1:
            table_ls = "└"
        else:
            table_ls = "├"

        head_end = "".join(["│", "".ljust(indents, "│"), table_ls, " "])
        format_print(each, indents=indents + 1, head_end=head_end)
        num += 1

    if indents == 0:
        format_print(pr_segregation("end", None), head_end="")


# 格式化打印字典
def format_print_dict(content, indents):
    if indents == 0:
        format_print(pr_segregation("start", None), timestamp=None, head_end="")

    num = 0
    for each in content:
        if num == 0:
            table_ls = "┌"
            # table_ls = "├"
        elif num == len(content) - 1:
            table_ls = "└"
        else:
            table_ls = "├"

        head_end_list = [
            "│",
            "".ljust(indents, "│"),
            table_ls,
            " ",
            each,
            " (",
            type_str(content[each]),
            "): ",
        ]
        head_end = "".join(head_end_list)
        head_end_no_name = "".join(head_end_list[:-2])
        if isinstance(content[each], (list, dict)):
            format_print("", indents=indents + 1, head_end=head_end)
            format_print(content[each], indents=indents + 1, head_end=head_end)
        else:
            format_print(content[each], indents=indents + 1, head_end=head_end)
        num += 1

    if indents == 0:
        format_print(pr_segregation("end", None), head_end="")


# 表格分割线
def pr_segregation(s_e=False, time=True):
    str_list = []
    if time is not None:
        segregation = "".ljust(term_col_no_time - 22, "─")
        str_list = [" "]
    else:
        segregation = "".ljust(term_col - 2, "─")

    if s_e == "start":
        # str_list += ["┌", segregation, "┐"]
        str_list += ["┌", segregation, "─"]
    elif s_e == "end":
        # str_list += ["└", segregation, "┘"]
        str_list += ["└", segregation, "─"]
    else:
        str_list += ["─", segregation, "─"]
    return "".join(str_list)


# 对象类型转字符串
def type_str(obj):
    full = str(type(obj))
    type_str_full = full[full.find("'") + 1 : full.rfind("'")]
    return type_str_full


# 打印线程
class pr_thread(threading.Thread):
    def __init__(self, print_intervals=0.015):
        threading.Thread.__init__(self)
        self.print_intervals = print_intervals

    def run(self):
        while True:
            print_lock.acquire()
            pr_data_list = []
            while not print_buffer.empty():
                pr_data_list.append(print_buffer.get())
            print_lock.release()

            self.refresh_term_col()
            if pr_data_list:
                # 有打印任务
                if self.last_pr_queue_empty_flag:
                    print("".ljust(term_col, " "), end="\r")
                self.last_pr_queue_empty_flag = False
                self.print(pr_data_list)
            else:
                # 无打印任务
                self.last_pr_queue_empty_flag = True
                if not is_hide_pr:
                    format_print(timestamp="now", end="\r")
            if not threading.main_thread().is_alive():
                break
            time.sleep(self.print_intervals)

    # 执行打印
    def print(self, pr_data_list):
        for each_pr_data in pr_data_list:
            if not is_hide_pr:
                format_print(**each_pr_data)
        print("", flush=True, end="")

    # 刷新终端宽度
    def refresh_term_col(self):
        global term_col, term_col_no_time
        term_col = os.get_terminal_size().columns
        term_col_no_time = term_col - 2


thread = pr_thread()
# threading.Thread.daemon = True
thread.start()

if __name__ == "__main__":
    import termcolor

    # 颜色
    for each in termcolor.COLORS.keys():
        pr("!@#$%^&*()_+\tcolor=" + each, color=each)

    for each in termcolor.HIGHLIGHTS.keys():
        pr("!@#$%^&*()_+\ton_color=" + each, on_color=each)

    for each in termcolor.ATTRIBUTES.keys():
        pr("!@#$%^&*()_+\tattrs=" + each, attrs=each)

    pr(
        "!@#$%^&*()_+\tattrs=list(termcolor.ATTRIBUTES.keys())",
        attrs=list(termcolor.ATTRIBUTES.keys()),
    )

    pr(
        "!@#$%^&*()_+\tparams=[grey, on_white, underline, blink]",
        c_param=["grey", "on_white", "underline", "blink"],
    )

    # 分隔符
    pr(segregation=True)
    pr(segregation=True, timestamp=None)

    # 列表
    test_list = [
        "test_1",
        "test_2",
        "test_3",
        [
            "test_1",
            "test_2",
            "test_3",
            ["test_1", "test_2", "test_3"],
            "test_4",
            "test_5",
            "test_6",
        ],
        "test_4",
        "test_5",
        "test_6",
    ]
    pr(test_list)

    # 字典
    test_dict = {
        "v1": "test_1",
        "v2": "test_2",
        "v3": "test_3",
        "v4": [
            123,
            4.56,
            False,
        ],
        "v5": 123,
        "v6": 4.56,
        "v7": True,
        "v8": {
            "v9": 123,
            "v10": 1.56,
            "v11": False,
        },
        "v12": [],
        "v13": {},
    }
    pr(test_dict)

    for num in range(10):
        pr(num)

    start_time = time.perf_counter()
    while True:
        # 添加输入内容
        pr(time.time())
        time.sleep(0.1)
        if time.perf_counter() - start_time > 1:
            break

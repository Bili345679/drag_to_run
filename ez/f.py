import os
import json
import hashlib
import shutil

t_flag = True
try:
    from ez import t
except:
    try:
        import t
    except:
        t_flag = False

file_piece_len = 16 * 1024 * 1024

##################
# 复制文件/文件夹 #
##################

# 复制文件/文件夹
# org_path 原文件或文件夹地址
#   c:/test_file
#   c:/test_folder
# tgt_path 目标路径
#   d:/
# 结果
#   d:/test_file
#   d:/test_folder
def copy_f(
    org_path: str | list,
    tgt_path: str,
    **kwargs,
):
    copy_res = {}
    if isinstance(org_path, str):
        org_path = [org_path]
    for each_path in org_path:
        if not os.path.exists(each_path):
            copy_res[each_path] = False
        elif os.path.isfile(each_path):
            copy_res[each_path] = copy_file(each_path, tgt_path, **kwargs)
        elif os.path.isdir(each_path):
            copy_res[each_path] = copy_folder(each_path, tgt_path, **kwargs)
        else:
            copy_res[each_path] = False
    return copy_res


# 复制文件
# when_exists 重复时操作
# check 复制完后检查文件内容是否相同
# rm_org 复制完成后是否删除原文件(如果校验文件内容不通过则不删除，如果不校验则删除，如果校验通过则删除)
def copy_file(
    org_path: str,
    tgt_path: str,
    check: bool = True,
    rm_org: bool = False,
    when_exists: str = "new",
    **kwargs,
):
    pr(f"cpfile: copying {os.path.basename(org_path)} to {os.path.basename(tgt_path)}")
    if not os.path.exists(org_path) or not os.path.isfile(org_path):
        return False

    tgt_path = ez_w_path(
        path_end_add_shash(tgt_path) + os.path.basename(org_path),
        when_exists=when_exists,
        **kwargs,
    )
    if tgt_path is False:
        return False

    over_path = tgt_path
    failed_path = tgt_path + ".cpfail"
    tgt_path += ".cping"
    if when_exists == "overwrite":
        if os.path.exists(over_path):
            os.remove(over_path)
        if os.path.exists(failed_path):
            os.remove(failed_path)
        if os.path.exists(tgt_path):
            os.remove(tgt_path)
    else:
        if os.path.exists(over_path):
            return False
        if os.path.exists(failed_path):
            return False
        if os.path.exists(tgt_path):
            return False

    shutil.copy2(org_path, tgt_path)

    check_res = None
    # none 和 true 皆为成功
    if check:
        check_res = file_is_same(org_path, tgt_path)

    if rm_org:
        if check_res is not False:
            os.remove(org_path)

    color = "success"
    if check_res is False:
        color = "error"

    pr(
        f"cpfile: copyed {os.path.basename(org_path)} to {os.path.basename(tgt_path)} {check_res}",
        color=color,
    )

    if check_res is False:
        os.rename(tgt_path, failed_path)
        return False
    else:
        os.rename(tgt_path, over_path)
        return True


# 复制文件夹
#  file_list 文件夹内需要复制的文件
#  flie_list 如果内容包括相对路径，则是相对于org_path的路径
#    比如
#       org_path = C:/a/b
#       file_list = ["./file_1","C:/a/b/file_2","C:/c/d/file_3"]
#       则会复制["C:/a/b/file_1","C:/a/b/file_2"]
def copy_folder(
    org_path: str,
    tgt_path: str,
    check: bool = True,
    rm_org: bool = False,
    when_parent_exists="overwrite",
    when_son_folder_exists="overwrite",
    when_son_file_exists="new",
    file_list=False,
    **kwargs,
):
    org_path = os.path.abspath(org_path)
    tgt_path = os.path.abspath(tgt_path)
    pr(
        f"cpfolder: copying {os.path.basename(org_path)} to {os.path.basename(tgt_path)}"
    )

    if not os.path.exists(org_path) or not os.path.isdir(org_path):
        return False

    # 准备复制的文件列表
    org_file_list, org_folder_list = scaner_folder(org_path)
    if file_list is False:
        file_copy_res = {
            relpath_to_abspath(file_path, org_path): None for file_path in org_file_list
        }
    else:
        file_copy_res = {
            relpath_to_abspath(file_path, org_path): None for file_path in file_list
        }
        new_file_list = []
        for each_file_abs_path in list(file_copy_res.keys()):
            if not is_file_in_folder(each_file_abs_path, org_path):
                # 不在原文件夹下的文件
                file_copy_res[each_file_abs_path] = False
            else:
                new_file_list.append(each_file_abs_path)
        org_file_list = new_file_list

    # 替换路径
    folder_replace_dict = {}

    tgt_path = ez_w_path(
        path_end_add_shash(tgt_path) + os.path.basename(org_path),
        when_exists=when_parent_exists,
        is_file=False,
        **kwargs,
    )
    mkdir(tgt_path)
    shutil.copystat(org_path, tgt_path)
    # 替换路径
    org_path = format_path(org_path)
    tgt_path = format_path(tgt_path)
    folder_replace_dict[org_path] = tgt_path

    # 复制文件夹
    for each_org_folder in org_folder_list:
        # 初定目标文件夹名
        # each_folder_tgt_path = path_end_add_shash(tgt_path) + os.path.relpath(
        #     each_org_folder, org_path
        # )
        # 替换上级路径
        org_dir = format_path(os.path.dirname(each_org_folder))
        # p.format_print(folder_replace_dict)
        each_folder_tgt_path = replace_path_start(
            each_org_folder, org_dir, folder_replace_dict[org_dir]
        )

        # 替换后目标文件夹名
        each_folder_tgt_path = ez_w_path(
            each_folder_tgt_path, when_exists=when_son_folder_exists
        )
        # 创建文件并复制状态
        mkdir(each_folder_tgt_path)
        shutil.copystat(each_org_folder, each_folder_tgt_path)

        # 替换路径
        each_org_folder = format_path(each_org_folder)
        each_folder_tgt_path = format_path(each_folder_tgt_path)
        folder_replace_dict[each_org_folder] = each_folder_tgt_path

    # 复制文件
    for each_org_file in org_file_list:
        # 替换路径
        org_dir = format_path(os.path.dirname(each_org_file))
        tgt_dir = folder_replace_dict[org_dir]

        # 执行复制
        res = copy_file(
            each_org_file, tgt_dir, check, rm_org, when_exists=when_son_file_exists
        )

        file_copy_res[each_org_file] = res

    pr(f"cpfolder: copyed {os.path.basename(org_path)} to {os.path.basename(tgt_path)}")
    return file_copy_res


###########
# 便捷读写 #
###########

# 写json
def json_dump(content, path: str, encoding="utf8", ensure_ascii=False, **kwargs):
    path = ez_w_path(path, **kwargs)
    if path is False:
        return False
    with open(path, "w", encoding=encoding) as file:
        json.dump(content, file, ensure_ascii=ensure_ascii)
    return path


# 读json
def json_load(path: str, encoding="utf8"):
    with open(path, "r", encoding=encoding) as file:
        return json.load(file)


# 写文件
def file_write(content: str | bytes, path: str, mode=False, encoding="utf8", **kwargs):
    path = ez_w_path(path, **kwargs)
    if path is False:
        return False

    if mode is not False:
        pass
    elif isinstance(content, bytes):
        mode = "wb"
        encoding = None
    elif isinstance(content, str):
        mode = "w"
    else:
        return False

    if mode == "wb":
        encoding = None

    with open(path, mode=mode, encoding=encoding) as file:
        file.write(content)
    return path


# 读文件
def file_read(path, mode="r", encoding="utf8"):
    with open(path, mode=mode, encoding=encoding) as file:
        return file.read()


###########
# 路径处理 #
###########

# 不覆盖文件，新建文件名
def un_exists_path(path: str, is_file: bool = True, path_find: bool = True, **kwargs):
    if os.path.exists(path):
        num = 1
        dir_name = os.path.dirname(path)
        base_name = os.path.basename(path)

        # 序号添加位置
        if is_file and path_find:
            base_name_cut_locat = base_name.find(".")
        else:
            base_name_cut_locat = base_name.rfind(".")

        # 是文件还是文件夹(文件夹补在最后)
        if is_file and base_name_cut_locat != -1:
            file_name_start = base_name[:base_name_cut_locat]
            file_name_end = base_name[base_name_cut_locat:]
        else:
            file_name_start = file_name_start = base_name
            file_name_end = ""

        while True:
            temp_path = f"{dir_name}/{file_name_start} ({num}){file_name_end}"
            if os.path.exists(temp_path):
                num += 1
            else:
                break
        return temp_path
    return path


# 不合并文件夹，新建文件夹名
def not_merge_folder_path(path: str, **kwargs):
    return un_exists_path(path, mode="folder", **kwargs)


# 创建文件所在路径文件夹
def mk_folder_dir(path: str):
    folder_dir = os.path.dirname(path)
    if not os.path.exists(folder_dir):
        mkdir(folder_dir)


# 递归创建文件夹
def mkdir(path: str):
    # path_node_list = cut_shash(os.path.realpath(path))
    path = replace_path_char(path)
    path_node_list = cut_shash(path)
    for num in range(len(path_node_list)):
        temp_path = "\\".join(path_node_list[0 : num + 1])
        if os.path.exists(temp_path):
            if os.path.isfile(temp_path):
                raise ("创建路径经过节点中有同名文件，无法创建路径")
            continue
        os.mkdir(temp_path)


def ez_w_path(path: str, when_exists: str = "new", **kwargs):
    # 有重名文件时处理方法
    if not os.path.exists(path):
        # 无重名文件
        pass
    elif when_exists == "pass":
        # 跳过
        return False
    elif when_exists == "new":
        # 重命名
        path = un_exists_path(path, **kwargs)
    elif when_exists == "overwrite":
        # 覆盖
        pass
    else:
        return False

    # 替换路径中无法使用的字符
    path = replace_path_char(path)

    # 创建路径中必须的文件夹
    mk_folder_dir(path)

    return path


#################
# 路径字符串处理 #
#################

# 替换路径不可用字符
def replace_path_char(path: str):
    path = path.replace(":", "：")
    path = path.replace("*", "＊")
    path = path.replace("?", "？")
    path = path.replace('"', "＂")
    path = path.replace("<", "＜")
    path = path.replace(">", "＞")
    path = path.replace("|", "｜")
    if path[1] == "：":
        path = path[0] + ":" + path[2:]
    return path


# 在路径结尾添加(斜杠/反斜杠)
def path_end_add_shash(path: str, shash: bool = True):
    if path[-1] == "\\" or path[-1] == "/":
        return path
    else:
        if shash:
            return path + "/"
        else:
            return path + "\\"


# 在路径结尾删除(斜杠/反斜杠)
def path_end_rmv_shash(path: str):
    if path[-1] == "\\" or path[-1] == "/":
        return path[:-1]
    else:
        return path


# 替换斜杠
def replace_shash(str: str, to_shash: bool = True):
    if to_shash:
        return str.replace("/", "\\")
    else:
        return str.replace("\\", "/")


# 斜杠分割
def cut_shash(str: str, shash_type: bool = False):
    if shash_type is False:
        str = replace_shash(str)
        return str.split("\\")
    if shash_type == "\\":
        return str.split("\\")
    if shash_type == "/":
        return str.split("/")


# 格式化路径
def format_path(path: str):
    return path_end_rmv_shash(replace_shash(path, False))


# 合并为绝对路径
def relpath_to_abspath(file_path, folder_path):
    file_path = replace_shash(file_path, False)
    folder_path = replace_shash(folder_path, False)

    if os.path.isabs(file_path):
        return file_path

    # folder_path = path_end_rmv_shash(folder_path)
    # while True:
    #     if file_path[0:3] == "../":
    #         file_path = file_path[3:]
    #         folder_path = folder_path[: folder_path.rfind("/")]
    #     else:
    #         break
    # while True:
    #     if file_path[0:2] == "./":
    #         file_path = file_path[2:]
    #     else:
    #         break
    # while True:
    #     if file_path[0:1] == "/":
    #         file_path = file_path[1:]
    #     else:
    #         break

    # return os.path.realpath(path_end_add_shash(folder_path) + file_path)
    return replace_shash(os.path.realpath(folder_path + file_path), False)


# # 替换路径
def replace_path_start(path, path_from, path_to):
    path = format_path(path)
    path_from = format_path(path_from)
    path_to = format_path(path_to)
    if not path[: len(path_from)] == path_from:
        raise ("替换路径时，path和path_from没有重回")
    else:
        path = path_end_add_shash(path_to) + path[len(path_from) + 1 :]
        return path


###########
# 文件校验 #
###########

# 获取文件hash
def hash_file(path: str, hash_type: str, upper=True):
    if isinstance(hash_type, str):
        hash_type_list = [hash_type]
    elif isinstance(hash_type, list):
        hash_type_list = hash_type

    hash_obj_list = []
    for each_hash_type in hash_type_list:
        hash_obj_list.append(hashlib.new(each_hash_type))

    with open(path, "rb") as file:
        while True:
            piece = file.read(file_piece_len)
            for each_hash_obj in hash_obj_list:
                each_hash_obj.update(piece)
            if len(piece) < file_piece_len:
                break

    hash_str_list = []
    for each_hash_obj in hash_obj_list:
        hash_str = each_hash_obj.hexdigest()
        if upper:
            hash_str = hash_str.upper()
        hash_str_list.append(hash_str)

    if len(hash_str_list) == 1:
        return hash_str_list[0]

    return hash_str_list


# 文件内容是否相同
def file_is_same(path_1: str, path_2: str, check_type="content"):
    print(path_1)
    print(path_2)
    # 文件是否存在
    if not os.path.exists(path_1) or not os.path.exists(path_2):
        return False

    # 对比文件长度
    if os.stat(path_1).st_size != os.stat(path_1).st_size:
        return False

    # 对比文件内容
    if check_type == "content":
        file_1 = open(path_1, "rb")
        file_2 = open(path_2, "rb")
        piece_1 = file_1.read(file_piece_len)
        piece_2 = file_2.read(file_piece_len)
        while len(piece_1) > file_piece_len:
            print("piece")
            if piece_1 != piece_2:
                return False
            piece_1 = file_1.read(file_piece_len)
            piece_2 = file_2.read(file_piece_len)
        else:
            if piece_1 != piece_2:
                return False
        return True

    # 对比hash值
    file_1_hash = hash_file(path_1, check_type)
    file_2_hash = hash_file(path_2, check_type)
    if file_1_hash != file_2_hash:
        return False
    else:
        return True


# 对比文件夹内容是否相同
def folder_is_same(path_1, path_2, check_type="content"):
    pass


# 文件夹内容区别
def dif_of_folder(path_1, path_2, **kwargs):
    file_list_1, folder_list_1 = scaner_folder(path_1, False)
    file_list_2, folder_list_2 = scaner_folder(path_2, False)

    print(len(file_list_1))
    print(len(file_list_2))

    res = {
        "file_list_1": {},
        "file_list_2": {},
        "folder_list_1": {},
        "folder_list_2": {},
    }

    file_list_1 = [
        replace_path_start(each_path, path_1, "./") for each_path in file_list_1
    ]
    file_list_2 = [
        replace_path_start(each_path, path_2, "./") for each_path in file_list_2
    ]
    folder_list_1 = [
        replace_path_start(each_path, path_1, "./") for each_path in folder_list_1
    ]
    folder_list_2 = [
        replace_path_start(each_path, path_2, "./") for each_path in folder_list_2
    ]

    # 多出来的文件
    more_file_of_path_1 = list(set(file_list_1).difference(set(file_list_2)))
    more_file_of_path_2 = list(set(file_list_2).difference(set(file_list_1)))
    more_folder_of_path_1 = list(set(folder_list_1).difference(set(folder_list_2)))
    more_folder_of_path_2 = list(set(folder_list_1).difference(set(folder_list_1)))

    for each in more_file_of_path_1:
        res["file_list_1"][each] = "more"
    for each in more_file_of_path_2:
        res["file_list_2"][each] = "more"
    for each in more_folder_of_path_1:
        res["folder_list_1"][each] = "more"
    for each in more_folder_of_path_2:
        res["folder_list_2"][each] = "more"

    # 不同的文件
    same_name_file_list = list(set(file_list_1).intersection(set(file_list_2)))
    same_name_folder_list = list(set(folder_list_1).intersection(set(folder_list_2)))

    for each_file in same_name_file_list:
        file_check_res = file_is_same(
            os.path.join(path_1, each_file), os.path.join(path_2, each_file)
        )
        if file_check_res is False:
            res["file_list_1"][each_file] = "different"
            res["file_list_2"][each_file] = "different"

    # 不同的文件夹
    for each_file in list(res["file_list_1"].keys()):
        res["folder_list_1"][os.path.dirname(each_file)] = "different"

    for each_file in list(res["file_list_2"].keys()):
        res["folder_list_2"][os.path.dirname(each_file)] = "different"

    return res


# 读取OpenHashTab导出文件
def load_open_hash_tab_file(path: str, **kwargs):
    hash_res = {}
    content = file_read(path, **kwargs)
    if content is False:
        return False

    flag = False
    line_list = content.split("\n")
    this_hash_type = ""
    for each_line in line_list:
        if each_line == "#":
            flag = True
        if flag is False:
            continue
        if each_line == "":
            continue

        if each_line[0] == "#":
            this_hash_type = each_line[1 : each_line.find("#", 1)]
        else:
            this_hash_str = each_line[: each_line.find(" ")]
            this_file_path = each_line[each_line.find(" ") + 1 :]

            if not this_file_path in hash_res:
                hash_res[this_file_path] = {}

            hash_res[this_file_path][this_hash_type] = this_hash_str

    return hash_res


# hash类型
hash_type_list = [
    "SHA1",
    "sha1",
    "MD5",
    "md5",
    "SHA256",
    "sha256",
    "SHA224",
    "sha224",
    "SHA512",
    "sha512",
    "SHA384",
    "sha384",
    "blake2b",
    "blake2s",
    "sha3_224",
    "sha3_256",
    "sha3_384",
    "sha3_512",
    # "shake_128",
    # "shake_256",
]

# 各hash类型长度
hash_type_len_list = {
    "SHA1": 40,
    "sha1": 40,
    "MD5": 32,
    "md5": 32,
    "SHA256": 64,
    "sha256": 64,
    "SHA224": 56,
    "sha224": 56,
    "SHA512": 128,
    "sha512": 128,
    "SHA384": 96,
    "sha384": 96,
    "blake2b": 128,
    "blake2s": 64,
    "sha3_224": 56,
    "sha3_256": 64,
    "sha3_384": 96,
    "sha3_512": 128,
}

#############
# 扫描文件夹 #
#############


# 扫描文件夹
def scaner_folder(path: str, abs=True):
    file_list = []
    folder_list = []
    try:
        son_path_list = os.listdir(path)
    except:
        return file_list, folder_list

    for son_path in son_path_list:
        son_path = os.path.join(path, son_path)
        if abs:
            son_path = os.path.abspath(son_path)
        son_path = format_path(son_path)
        if os.path.isfile(son_path):
            file_list.append(son_path)
        elif os.path.isdir(son_path):
            folder_list.append(son_path)

            # 子文件夹
            son_file_list, son_folder_list = scaner_folder(son_path, abs)
            file_list.extend(son_file_list)
            folder_list.extend(son_folder_list)
        else:
            print("ERROR\t" + son_path)
    return file_list, folder_list


# 文件/文件夹 是否在文件夹内
def is_file_in_folder(file_path, folder_path):
    file_path = replace_shash(file_path, False)
    folder_path = replace_shash(folder_path, False)

    if not os.path.abspath(file_path):
        file_path = relpath_to_abspath(file_path, folder_path)
    if not os.path.exists(file_path):
        return False

    if (
        len(file_path) > len(folder_path)
        and file_path[: len(folder_path)] == folder_path
        and file_path[len(folder_path)] == "/"
    ):
        return True
    else:
        return False


###########
# 外界函数 #
###########
def pr(content, **kwargs):
    print(content, **kwargs)

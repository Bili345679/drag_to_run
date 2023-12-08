import time

# 大约一毫秒小睡
def tiny_sleep():
    start_time = time.time()
    while time.time() == start_time:
        pass


def sleep(sleep_time=False, sleep_to=False, start_time=False, early_wake=False):
    if not start_time:
        start_time = time.time()

    if sleep_time:
        # 从睡眠时间算醒来时间
        sleep_to = sleep_time + start_time
    elif not sleep_to:
        # 既没有睡眠时间，也没有醒来时间，直接退出
        return False

    # 当前时间
    now_time = time.time()

    # 是否允许提前醒来
    if early_wake:
        # 间隔和
        interval_sum = 0
        # 间隔次数
        interval_count = 0
        # 最后更新时间
        last_time = now_time
        avg_interval = False

    # 苏醒方式
    wake_type = 1
    time_list = [now_time]
    # 在当前时间小于目标时间时循环
    while now_time < sleep_to:
        # 如果时间更新
        if early_wake and not last_time == now_time:
            time_list.append(now_time)
            # 增加间隔和
            interval_sum += now_time - last_time
            # 增加间隔次数
            interval_count += 1
            # 平均间隔
            avg_interval = interval_sum / interval_count
            # 预测下一次更新是否会超过目标时间
            if avg_interval + now_time > sleep_to:
                wake_type = 2
                break
            last_time = now_time
        # 再次获取当前时间
        now_time = time.time()

    res = {
        "sleep_time": sleep_time,
        "sleep_to": sleep_to,
        "start_time": start_time,
        "real_sleep_time": time.time() - start_time,
        "wake_time": time.time(),
        "wake_type": wake_type,
    }
    if early_wake:
        res["avg_interval"] = avg_interval
        res["interval_sum"] = interval_sum
        res["interval_count"] = interval_count
    return res


# 精准睡眠
def precise_sleep(sleep_time=False, sleep_to=False, start_time=False):
    if not start_time:
        start_time = time.perf_counter()

    if sleep_time:
        # 从睡眠时间算醒来时间
        sleep_to = sleep_time + start_time
    elif not sleep_to:
        # 既没有睡眠时间，也没有醒来时间，直接退出
        return False

    # 在当前时间小于目标时间时循环
    while time.perf_counter() < sleep_to:
        pass

    res = {
        "sleep_time": sleep_time,
        "sleep_to": sleep_to,
        "start_time": start_time,
        "real_sleep_time": time.perf_counter() - start_time,
        "wake_time": time.perf_counter(),
    }
    return res


# 获取格式化时间
def get_data_time(timestamp=False):
    if not timestamp:
        timestamp = time.time()
    timestamp = time.localtime(timestamp)
    return time.strftime("%Y-%m-%d_%H-%M-%S", timestamp)

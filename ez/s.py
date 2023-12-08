def str_between(str, start, end):
    start = str.find(start) + len(start)
    end = str.find(end, start)
    return str[start:end]
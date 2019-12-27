def dict_arrange(key_to_candidate_list):
    """

    :param key_to_candidate_list:
    :return: list_key_to_candidate
    """

    ret = []
    data_len = []
    index1 = []
    index2 = {}
    for i in key_to_candidate_list.keys():
        data_len.append(len(key_to_candidate_list[i]))
        index1.append(i)
        index2[i] = 0
    while True:
        key_to_candidate = {}
        for i in range(len(index1)):
            key_to_candidate[index1[i]] = key_to_candidate_list[index1[i]][
                index2[index1[i]]]

        ret.append(key_to_candidate)

        total0 = 0
        for i in range(len(index1)):
            cur = len(index1) - i - 1
            if index2[index1[cur]] < data_len[cur] - 1:
                index2[index1[cur]] += 1
                break
            else:
                index2[index1[cur]] = 0
                total0 += 1

        if total0 == len(index1):
            break

    return ret

if __name__ == "__main__":
    a = {0: [1, 2, 3, 4], 1: [5, 6, 7, 8], 2: [9, 10, 11]}
    list_key_to_candidate = dict_arrange(a)
    print(len(list_key_to_candidate))
    for key_to_candidate in list_key_to_candidate:
        print(key_to_candidate)

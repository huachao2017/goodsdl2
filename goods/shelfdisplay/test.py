def test():
    a = {0:[1,2,3,4],1:[5,6,7,8],2:[9,10,11]}

    data_len = []
    index1 = []
    index2 = {}
    for i in a.keys():
        data_len.append(len(a[i]))
        index1.append(i)
        index2[i]=0


    total = 0
    while True:
        for i in range(len(index1)):
            print("{}".format(a[index1[i]][index2[index1[i]]]), end=",")

        print("")
        total += 1

        total0 = 0
        for i in range(len(index1)):
            cur = len(index1) - i - 1
            if index2[index1[cur]] < data_len[cur]-1:
                index2[index1[cur]] += 1
                break
            else:
                index2[index1[cur]] = 0
                total0 += 1

        if total0 == len(index1):
            break

    print(total)


if __name__ == "__main__":
    test()
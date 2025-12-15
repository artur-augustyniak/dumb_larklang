sum(arr)
{
    # assumes arr has at least 3 elements
    s = arr[0] + arr[1] + arr[2];
    return s;
}

main()
{
    # array with trailing comma
    a = [ 10, 20, 30, ];
    print("original a:");
    print(a);

    # modify elements
    a[0] = 100;
    a[2] = a[1] + 5;

    print("modified a:");
    print(a);

    # array without trailing comma
    b = [1, 2, 3, 4,];
    print("b:");
    print(b);

    s = sum(a);
    print("sum of first 3 of a:");
    print(s);
}


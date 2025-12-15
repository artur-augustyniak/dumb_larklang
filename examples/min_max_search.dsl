arraymin(a)
{
    i = 1;
    cur = a[0];

    while (i < 5)
    {
        if (a[i] < cur)
        {
            cur = a[i];
        }
        else
        {
            z = 0;
        }
        i = i + 1;
    }

    return cur;
}

arraymax(a)
{
    i = 1;
    cur = a[0];

    while (i < 5)
    {
        if (a[i] > cur)
        {
            cur = a[i];
        }
        else
        {
            z = 0;
        }
        i = i + 1;
    }

    return cur;
}

main()
{
    a = [ 7, 3, 9, 2, 5, ];
    print("array a:");
    print(a);

    mn = arraymin(a);
    mx = arraymax(a);

    print("min:");
    print(mn);

    print("max:");
    print(mx);

    spread = mx - mn;
    print("max - min:");
    print(spread);
}


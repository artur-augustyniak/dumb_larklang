fact(n)
{
    if (n == 0)
    {
        return 1;
    }
    else
    {
    }

    i = 1;
    acc = 1;

    while (i < (n + 1))
    {
        
        acc = acc * i;
        i = i + 1;
    }

    return acc;
}

main()
{
    print("enter n for factorial:");
    n = inpnum();

    f = fact(n);
    print("factorial is:");
    print(f);
}


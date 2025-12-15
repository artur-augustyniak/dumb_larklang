readandsum(limit)
{
    i = 0;
    total = 0;

    while (i < limit)
    {
        print("current total:");
        print(total);
        print("enter a number (0 to stop):");

        x = inpnum();

        if (x == 0)
        {
            print("stopping early");
            return total;
        }
        else
        {
        }

        total = total + x;
        i = i + 1;
    }

    
    return total;
}

main()
{
    print("how many numbers max?");
    n = inpnum();

    res = readandsum(n);
    print("final total:");
    print(res);
}


add(x)
{
    # returns x + 10
    res = x + 10;
    return res;
}

square(x)
{
    res = x * x;
    return res;
}

main()
{
    a = 5;
    b = add(a);
    c = square(b);

    print("a:");
    print(a);
    print("b = a + 10:");
    print(b);
    print("c = (a + 10)^2:");
    print(c);

    
    d = add((square(3)));
    print("d = add(square(3)):");
    print(d);
}


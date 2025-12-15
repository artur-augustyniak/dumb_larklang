sort(a)
{
    
    print(a);
    len = 7;
    i = 0;
    while(i < 7)
    {
        j = 0;
        while (j < 7)
        {
            if (a[j] > a[i])
            {
                tmpa = a[i];
                a[i] = a[j];
                a[j] = tmpa;
            }
            else{

            }
            j = j +1;
        }
        
        i = i + 1;
    }
    print(a);
}


some(l)
{
    i = 1;
    p = 2 + l;
    print(p);
    while (i < 6)
    {
        print(i);
        print("type 0 to finish");
        print(l);
        d = inpnum();
        if (d == 0)
        {
            print("will ret");
            return i;
        }
        else
        {
        }
        i = i + 1;
    }
}

foo(){
    return 125;
}

main()
{
    a = [ 5, 6, 12, 45, 78, 12, 1, ];
    sort(a);
    a = [1,3,5,];
    a[2] = 7;
    a[2] = 10;
    print(a[2]);
    #b = a[1];
    res = some(7 + foo());
    print(res);
}

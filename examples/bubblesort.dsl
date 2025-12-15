main()
{
    a = [ 5, 6, 12, 45, 78, 12, 1, ];
    print("Unsorted:");
    print(a);

    len = 7;
    i = 0;

    while(i < len){
        j = 0;
        while(j < len){

            if(a[j] > a[i]){
                tmp = a[i];
                a[i] = a[j];
                a[j] = tmp;
            }else{
                z = 0;
            }
            j = j + 1;
        }
        i = i + 1;
    }

    print("I-------------");
    print("Sorted:");
    print(a);
}

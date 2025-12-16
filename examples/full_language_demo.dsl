sqrtguesscond(guessses){
    guess = guessses[0];
    nextguess = guessses[1];
    tolerance = 1 / 1000000000;
    if(nextguess - guess > tolerance){
        return 1;
    }else{
        if(nextguess - guess > tolerance){
            return 1;
        }else{
            return 0;
        }

    }

}


sqrt(number) {
    if (number < 0) {
        return "error";
    }else{
        if (number == 0) {
            return number;
        }else{
        }

        if (number == 1) {
            return number;
        }else{
        }

        guess = number / 2;
        nextguess = (guess + number / guess) / 2;
        guesses = [guess, nextguess];
    
        while (sqrtguesscond(guesses)) {
            guess = nextguess;
            nextguess = (guess + number / guess) / 2;
        }
        return nextguess;
    }
}

save(v){
    print("saving val");
    print(v);

}

foo(asd){
    
    z = 1;
    a = 7;
    b = 1;
    
    v = (a) + (-b);
    
    j = ( 123 + (-3) );
    print("jot");
    print(j);
    x = (3 + 3);
    y = 5;
    print("d");
    asdf = ("123" + "sdfsdfsdf");
    print(v);
    z = 1;
    print(z);
    d = "dupa";
    print(d);
    #c = (-(2 + (124 * 5))) / sqrt(z);
    c = (((-1) + (124 * 5)) / sqrt(a));
    save(c);
    if(asd > 0){
        foo(asd -1 );
    }else{

    }
    1 + 1;

}


a(abz){

    someval = (((1 + 2) + 3) + asd);
    
        z = (1);
    1 + 1;
    while(1){
        #a = (a + 1);
        z = 1;
        lalala((((-1) + (124 * 5)) / sqrt((((-1) + (124 * 5)) / sqrt(a)))));
        dupa("asdas");
    }
    2 + 2;

    while((a + 1)){
        #a = (a + 1);
        z = 1;
        dupa("asdas");
    }

    - 234;
    #combined = 1 + (someval + 4)
    

    #string = "dup a";


    #res = 2 + baz()


    # 1 + 1
    #ab = 111
    #de = 11.1
    #other(cd)
}

#comment. 123

some(zzz){
    
}

ifwhile(){

    #z = (1);

    if(1)
    {
        while(1){
        #a = (a + 1);
        z = 1;
        dupa("asdas");
    }
    2 + 2;
    }else
    {

        while((cond(1))){
        #a = (a + 1);
        z = 1;
        lalala((((-1) + (124 * 5)) / sqrt((((-1) + (124 * 5)) / sqrt(a)))));
        dupa("asdas");
    }

    }

    1 + 1;
    while(1)
    {
        #a = (a + 1);
        z = 1;
        dupa("asdas");}
    2 + 2;

    while((a + 1)){
        #a = (a + 1);
        z = 1;
        dupa("asdas");
    }
}



main(){
    print("Hel lo");
    foo(2);
    1 + 1;
    
    #foo("sdf");
    #foo((-1));
    
    #lalala((((-1) + (124 * 5)) / sqrt((((-1) + (124 * 5)) / sqrt(a)))));
    return 42;
}





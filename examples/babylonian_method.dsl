sqrtguesscond(guessses){
    guess = guessses[0];
    nextguess = guessses[1];
    tolerance = 1 / 10000;
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


main(){
    print(sqrt(4));
}
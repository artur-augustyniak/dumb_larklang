#!/usr/bin/env python3

import sys
from dumblang import parse_and_execute



CLBKS = {
    "strlen" : ("builtin", len)
}


PROGRAM = '''
main(){
    print(env);
    if(strlen(env) > 0){
        print(env[0]);
    }else{
        print("just enter?");
    }
    
    return strlen(env);
}
'''


if __name__ == "__main__":

    while True:
        o = parse_and_execute(PROGRAM, input(), CLBKS)
        print(o)
        print("#" * 80)
    


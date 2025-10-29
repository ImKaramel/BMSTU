#!/bin/sh
flex lab1.5.l 
g++ lex.yy.c 
./a.out in.txt
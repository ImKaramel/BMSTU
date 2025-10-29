% Лабораторная работа № 1.1 ‹Раскрутка самоприменимого компилятора›
% 27 фебраля 2024 г.
% Александрова Ольга, ИУ9-61Б

# Цель работы
Целью данной работы является ознакомление с раскруткой самоприменимых компиляторов 
на примере модельного компилятора.

# Индивидуальный вариант 

Компилятор P5. Заменить запись операции <> на !=.

# Реализация

### Различие между файлами pcom.pas и pcom2.pas: ###
####  До внесенных изменений  ####

```pascal
chtp = (letter,number,special,illegal,chstrquo,chcolon,chperiod,
    chlt,chgt,chlparen,chspace,chlcmt);
_______________________________________________________________________ 
until chartp[ch] in [special,illegal,chstrquo,chcolon,
                                chperiod,chlt,chgt,chlparen,chspace,chlcmt];
_______________________________________________________________________ 
          else op := ltop
        end;
      chneop:
         begin nextch; sy := relop;
          if ch = '=' then
            begin op := neop; nextch end;
         end;
_______________________________________________________________________ 
ssy['^'] := arrow ;   ssy['<'] := relop;    ssy['>'] := relop;
_______________________________________________________________________ 
sop['='] := eqop; sop['<'] := ltop;  sop['>'] := gtop;
```

#### Строки кода после внесенных изменений ####

```pascal

chtp = (letter,number,special,illegal,chstrquo,chcolon,chperiod,chlt, 
    chneop, chgt,chlparen,chspace,chlcmt);
_______________________________________________________________________ 
until chartp[ch] in [special,illegal,chstrquo,chcolon,chperiod,chlt, 
_______________________________________________________________________ 
    chneop, chgt,chlparen,chspace,chlcmt];

          else op := ltop
        end;
      chneop:
         begin nextch; sy := relop;
          if ch = '=' then
            begin op := neop; nextch end;
         end;
_______________________________________________________________________ 
ssy['^'] := arrow ; ssy['<'] := relop; ssy['>'] := relop; ssy['!'] := relop; 
_______________________________________________________________________ 
sop['='] := eqop; sop['<'] := ltop;  sop['>'] := gtop; sop['!'] := neop;
_______________________________________________________________________ 
      chartp['!'] := chneop ;
```

# Тестирование

```pascal
program CompareToTen(output);
var
    number: integer;
begin
    number := 5;

    if 5 != 10 then
        writeln('OK')   
    else
        writeln('EQ');  
end.
```

Вывод тестового примера на `stdout`

```
OK
```
# Вывод

Я ознакомилась с понятием раскрутки самоприменимого компилятора, изучв устройство компилятора P5. 
Во время реализации лабораторной работы были получены навыки работы с интерпретатором pint и решены 
проблемы компиляции компилятора P5 на ОС Mac OS, применив скомпилированный pint из курсовой работы 
[https://github.com/bmstu-iu9/P5-Interpreter](https://github.com/bmstu-iu9/P5-Interpreter).

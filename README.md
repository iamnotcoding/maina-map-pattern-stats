# How to use 

## From command line
```
python main.py osu_file_path
```

## From other python files
```
from calc import from_file

file_path = input()
stats_dic = from_file(file_path)
```

# Requirments 
* python3.7 or up 

# Example

```
python main.py .\test_files\delay.osu

{
    "SINGLE_STREAM": 21.527069306998985,
    "JUMP_STREAM": 5.086612926001816,
    "HAND_STREAM": 0.12376087744467555,
    "JACK": 1.2693609263815653,
    "TRILL": 0.2016504489119267,
    "OVERALL": 28.20845448573897
}
```
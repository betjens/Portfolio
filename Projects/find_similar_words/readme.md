# Find Similar Words

A small analyst project which helps identify words and correct it based on a list of 'valid words'.

Here is a small sample of its usage:

```
valid_words = ['Coca Cola']
invalid_words = ['Coco Colo', 'CocoCoco', 'CaCoPaco','Un related']
```

Output

| raw        | clean      | corrected | precision           |
|------------|------------|-----------|---------------------|
| coco colo  | coco colo  | Coca Cola | 0.4                 |
| cocococo   | cocococo   | Coca Cola | 0.30000000000000004 |
| cacopaco   | cacopaco   | Coca Cola | 0.19999999999999996 |
| un related | un related | Invalid   | 0.0                 |
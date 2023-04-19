#!/bin/bash
for file in *.cu; do
    nvcc -o "./compiles/${file%}.out" "$file" 
done

#
# string str = "hello world";
# str.substr(0, str.length() - 3);
# str.erase(0, 5);
 
# substr: 截取开始到结束长度的子字符串，上面的例子截取的是str除去末尾三个字符的剩余子字符串
# erase: 表示删除固定长度的字符串，上面的例子是删除字符串开始的五个字符的剩余子字符串。

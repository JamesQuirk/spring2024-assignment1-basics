# CS336 Assignment 1 (basics): Building a Transformer LM - Problems

## Problem (unicode1)

(a)
```python
>>> chr(0)
'\x00'
```

(b) printed as (zero-length) empty space.
```python
>>> repr(chr(0))
"'\x00'"
>>> print(chr(0))

```

(c) When printed, the value is formatted into a zero-length string
```python
>>> "this is a test" + chr(0) + "string"
'this is a test\x00string'
>>> print("this is a test" + chr(0) + "string")
this is a teststring
```

## Problem (unicode2)

(a) ASCII characters are encoded as a single byte in UTF-8 and non-ASCII are encoded in 2-4 bytes. Whereas, UTF-8 will use 2 for ASCII & 3 or more for non-ASCII. UTF-32 will use 4 bytes for all characters. Both UTF-16 & UTF-32 pad with `\x00`. Therefore, UTF-8 is advantageous for text which is marjority ASCII characters (e.g. English text); not so good for Asian text.
```python
>>> s
'hello! こんにちは!'
>>> s.encode("utf-8")
b'hello! \xe3\x81\x93\xe3\x82\x93\xe3\x81\xab\xe3\x81\xa1\xe3\x81\xaf!'
>>> s.encode("utf-16")
b'\xff\xfeh\x00e\x00l\x00l\x00o\x00!\x00 \x00S0\x930k0a0o0!\x00'
>>> s.encode("utf-32")
b'\xff\xfe\x00\x00h\x00\x00\x00e\x00\x00\x00l\x00\x00\x00l\x00\x00\x00o\x00\x00\x00!\x00\x00\x00 \x00\x00\x00S0\x00\x00\x930\x00\x00k0\x00\x00a0\x00\x00o0\x00\x00!\x00\x00\x00'
>>> list(s.encode("utf-8"))
[104, 101, 108, 108, 111, 33, 32, 227, 129, 147, 227, 130, 147, 227, 129, 171, 227, 129, 161, 227, 129, 175, 33]
>>> list(s.encode("utf-16"))
[255, 254, 104, 0, 101, 0, 108, 0, 108, 0, 111, 0, 33, 0, 32, 0, 83, 48, 147, 48, 107, 48, 97, 48, 111, 48, 33, 0]
>>> list(s.encode("utf-32"))
[255, 254, 0, 0, 104, 0, 0, 0, 101, 0, 0, 0, 108, 0, 0, 0, 108, 0, 0, 0, 111, 0, 0, 0, 33, 0, 0, 0, 32, 0, 0, 0, 83, 48, 0, 0, 147, 48, 0, 0, 107, 48, 0, 0, 97, 48, 0, 0, 111, 48, 0, 0, 33, 0, 0, 0]
>>> len(s.encode("utf-8"))
23
>>> len(s.encode("utf-16"))
28
>>> len(s.encode("utf-32"))
56
```

(b) The function attempts to decode each byte individually. This is invalid for non-ASCII characters, which yield an *"unexpected end of data"* error. To correctly decode these characters, the full (2-4)-byte set is needed.
```python
>>> def decode_utf8_bytes_to_str_wrong(bytestring: bytes):
...     return "".join([bytes([b]).decode("utf-8") for b in bytestring])
>>> decode_utf8_bytes_to_str_wrong("hello".encode("utf-8"))
'hello'
>>> decode_utf8_bytes_to_str_wrong(s.encode("utf-8"))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<stdin>", line 2, in decode_utf8_bytes_to_str_wrong
  File "<stdin>", line 2, in <listcomp>
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe3 in position 0: unexpected end of data
>>> b"\xe3".decode("utf-8")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe3 in position 0: unexpected end of data
>>> b"\xe3\x81".decode("utf-8")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
UnicodeDecodeError: 'utf-8' codec can't decode bytes in position 0-1: unexpected end of data
>>> b"\xe3\x81\x93".decode("utf-8")
'こ'
```

(c) `\xD800\xDC00`: This sequence falls within the range reserved for surrogate pairs in UTF-16 encoding, which are used to encode characters outside the Basic Multilingual Plane (BMP). However, when these bytes are not used correctly as part of a valid surrogate pair, they do not correspond to any valid Unicode character. (MS CoPilot, Nov 2024)

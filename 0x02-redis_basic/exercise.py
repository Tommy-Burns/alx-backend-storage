#!/usr/bin/env python3
"""
a python module to set up an environment for redis
"""
from typing import Union, Callable
from uuid import uuid4
from functools import wraps
import redis
from redis import exceptions


def count_calls(method: callable) -> Callable:
    """
    count_calls - function to count the number of time the method calls
    Arguments:
        method: the given method to call
    Returns:
        a function it self
    """
    method_name = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """ a wrapper function"""
        self._redis.incr(method_name)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: callable) -> callable:
    """
    call_history - function to store the history of inputs
    & outputs for a function
    Arguments:
        method: the given method
    Returns:
        the function passed as argument
    """
    m_name = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """a wrapper function"""
        input: str = str(args)
        self._redis.rpush(m_name + ":inputs", input)
        output: str = method(self, *args, **kwargs)
        self._redis.rpush(m_name + ":outputs", output)
        return output
    return wrapper


def replay(method: callable) -> None:
    """
    replay- function to display the history of call of a fun
    Arguments:
        None
    Returns:
        None
    """
    name = method.__qualname__
    obj = redis.Redis()
    try:
        calls = obj.get(name).decode("utf-8")
    except Exception:
        calls = 0

    print("{} was called {} times:".format(name, calls))

    input = obj.lrange(name + ":inputs", 0, -1)
    output = obj.lrange(name + ":outputs", 0, -1)
    for i, o in zip(input, output):
        try:
            value = i.decode("utf-8")
        except Exception:
            value = ""
        try:
            key = o.decode("utf-8")
        except Exception:
            key = ""
        print("{}(*{}) -> {}".format(name, value, key))


class Cache:
    """ a cache class for redis implementation"""
    def __init__(self) -> None:
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        store - function that generates & stores a random key
        Arguments:
            data - the given data
        Returns:
            the given data passed as argument
        """
        k = str(uuid4())
        self._redis.set(k, data)
        return k

    def get(self, key: str, fn: Callable = None)\
            -> Union[str, bytes, int, float]:
        """
        get - function that gets the value of the key
        Arguments:
            key: the given key
            Collable: it is used to convert data back to the desired format
        Returns:
            the value of the given key
        """
        v = self._redis.get(key)
        if fn:
            v = fn(v)
        return v

    def get_str(self, key: str) -> str:
        """
        get_str: function that converts a given value to string
        Arguments:
            key: the given key
        Returns:
            the string represenation of a value
        """
        v = self._redis.get(key)
        v = v.decode("utf-8")
        return v

    def get_int(self, key: str) -> int:
        """
        get_int: function that converts a given value to int
        Arguments:
            key: the given key
        Returns:
            the integer representation of a value
        """
        v = self._redis.get(key).decode("utf-8")
        try:
            v = int(v)
        except Exception:
            v = 0
        return v

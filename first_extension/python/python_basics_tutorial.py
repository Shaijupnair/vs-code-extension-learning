"""
Python Basics Tutorial
======================
A comprehensive guide to Python's fundamental language features.
Author: Tutorial Script
Date: 2026-02-03
"""

# ============================================================================
# 1. VARIABLES AND DATA TYPES
# ============================================================================

# Variables: No need to declare type, Python is dynamically typed
name = "Alice"  # String
age = 25        # Integer
height = 5.6    # Float
is_student = True  # Boolean
nothing = None  # NoneType - represents absence of value

# Multiple assignment
x, y, z = 1, 2, 3
a = b = c = 10  # All get the same value

# Variable naming rules:
# - Start with letter or underscore
# - Can contain letters, numbers, underscores
# - Case sensitive (myVar != myvar)
my_variable = "valid"
_private_var = "also valid"
# 2variable = "invalid"  # Cannot start with number


# ============================================================================
# 2. NUMERIC TYPES AND OPERATIONS
# ============================================================================

# Integer operations
int_num = 42
negative_int = -10
big_int = 1_000_000  # Underscores for readability

# Float operations
float_num = 3.14
scientific = 2.5e-3  # Scientific notation: 0.0025

# Complex numbers
complex_num = 3 + 4j

# Arithmetic operators
addition = 10 + 5        # 15
subtraction = 10 - 5     # 5
multiplication = 10 * 5  # 50
division = 10 / 3        # 3.3333... (always returns float)
floor_division = 10 // 3 # 3 (integer division)
modulus = 10 % 3         # 1 (remainder)
exponentiation = 2 ** 3  # 8 (2 to the power of 3)

# Compound assignment operators
counter = 0
counter += 1   # counter = counter + 1
counter -= 1   # counter = counter - 1
counter *= 2   # counter = counter * 2
counter /= 2   # counter = counter / 2
counter //= 2  # counter = counter // 2
counter %= 2   # counter = counter % 2
counter **= 2  # counter = counter ** 2

# Type conversion
int_from_float = int(3.9)      # 3
float_from_int = float(5)      # 5.0
str_from_int = str(42)         # "42"
int_from_str = int("100")      # 100


# ============================================================================
# 3. STRINGS
# ============================================================================

# String creation (multiple ways)
single_quotes = 'Hello'
double_quotes = "World"
triple_quotes = '''Multi-line
string with
multiple lines'''
triple_double = """Also works
with double quotes"""

# String concatenation
full_name = "John" + " " + "Doe"  # "John Doe"
repeated = "Ha" * 3                # "HaHaHa"

# String indexing (0-based)
text = "Python"
first_char = text[0]      # 'P'
last_char = text[-1]      # 'n'
second_last = text[-2]    # 'o'

# String slicing [start:end:step]
substring = text[0:3]     # 'Pyt' (0 to 2, excluding 3)
from_start = text[:3]     # 'Pyt'
to_end = text[3:]         # 'hon'
entire = text[:]          # 'Python'
reverse = text[::-1]      # 'nohtyP'
every_second = text[::2]  # 'Pto'

# String methods
sentence = "  Hello World  "
upper = sentence.upper()           # "  HELLO WORLD  "
lower = sentence.lower()           # "  hello world  "
stripped = sentence.strip()        # "Hello World"
replaced = sentence.replace("World", "Python")  # "  Hello Python  "
split_words = sentence.split()     # ['Hello', 'World']
joined = "-".join(['a', 'b', 'c']) # "a-b-c"
starts = sentence.strip().startswith("Hello")  # True
ends = sentence.strip().endswith("World")      # True
find_pos = sentence.find("World")  # 8 (or -1 if not found)

# String formatting (multiple ways)
name = "Alice"
age = 25

# 1. Old style (%)
old_style = "Name: %s, Age: %d" % (name, age)

# 2. str.format()
format_style = "Name: {}, Age: {}".format(name, age)
format_named = "Name: {n}, Age: {a}".format(n=name, a=age)

# 3. f-strings (Python 3.6+, recommended)
f_string = f"Name: {name}, Age: {age}"
f_expression = f"Next year: {age + 1}"
f_formatted = f"Pi: {3.14159:.2f}"  # "Pi: 3.14"

# Raw strings (ignore escape sequences)
raw = r"C:\new\path"  # Backslashes treated literally

# Escape sequences
escaped = "Line 1\nLine 2\tTabbed"  # \n = newline, \t = tab


# ============================================================================
# 4. BOOLEAN AND COMPARISON OPERATORS
# ============================================================================

# Boolean values
is_true = True
is_false = False

# Comparison operators
equal = (5 == 5)         # True
not_equal = (5 != 3)     # True
greater = (5 > 3)        # True
less = (3 < 5)           # True
greater_eq = (5 >= 5)    # True
less_eq = (3 <= 5)       # True

# Logical operators
and_result = True and False   # False
or_result = True or False     # True
not_result = not True         # False

# Chained comparisons
in_range = 1 < 5 < 10        # True (equivalent to: 1 < 5 and 5 < 10)

# Identity operators
list1 = [1, 2, 3]
list2 = [1, 2, 3]
list3 = list1

same_reference = (list1 is list3)      # True
different_ref = (list1 is list2)       # False
same_value = (list1 == list2)          # True

# Membership operators
fruits = ["apple", "banana", "cherry"]
has_apple = "apple" in fruits          # True
no_grape = "grape" not in fruits       # True


# ============================================================================
# 5. CONTROL FLOW - IF/ELIF/ELSE
# ============================================================================

# Basic if statement
number = 10
if number > 0:
    print("Positive number")

# if-else
if number % 2 == 0:
    print("Even")
else:
    print("Odd")

# if-elif-else
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

# Nested if statements
age = 20
has_license = True
if age >= 18:
    if has_license:
        print("Can drive")
    else:
        print("Get a license first")
else:
    print("Too young to drive")

# Ternary operator (conditional expression)
status = "Adult" if age >= 18 else "Minor"

# Multiple conditions
temp = 25
humidity = 70
if temp > 20 and humidity < 80:
    print("Nice weather")


# ============================================================================
# 6. LOOPS - FOR AND WHILE
# ============================================================================

# For loop with range
for i in range(5):  # 0, 1, 2, 3, 4
    print(i)

# Range with start, stop, step
for i in range(1, 10, 2):  # 1, 3, 5, 7, 9
    print(i)

# Iterating over a list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# Enumerate (get index and value)
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")

# Enumerate with custom start
for index, fruit in enumerate(fruits, start=1):
    print(f"{index}: {fruit}")

# While loop
count = 0
while count < 5:
    print(count)
    count += 1

# Break statement (exit loop)
for i in range(10):
    if i == 5:
        break  # Exit loop when i is 5
    print(i)

# Continue statement (skip to next iteration)
for i in range(5):
    if i == 2:
        continue  # Skip when i is 2
    print(i)

# Else clause with loops (executes if loop completes without break)
for i in range(5):
    print(i)
else:
    print("Loop completed normally")

# Nested loops
for i in range(3):
    for j in range(2):
        print(f"i={i}, j={j}")

# While with else
count = 0
while count < 3:
    print(count)
    count += 1
else:
    print("While loop finished")


# ============================================================================
# 7. DATA STRUCTURES - LISTS
# ============================================================================

# List creation (ordered, mutable, allows duplicates)
empty_list = []
numbers = [1, 2, 3, 4, 5]
mixed = [1, "two", 3.0, True, [5, 6]]  # Can contain different types
from_range = list(range(5))  # [0, 1, 2, 3, 4]

# List indexing and slicing (same as strings)
first = numbers[0]      # 1
last = numbers[-1]      # 5
slice_list = numbers[1:4]  # [2, 3, 4]

# List methods
numbers = [1, 2, 3]
numbers.append(4)           # [1, 2, 3, 4] - add to end
numbers.insert(0, 0)        # [0, 1, 2, 3, 4] - insert at index
numbers.extend([5, 6])      # [0, 1, 2, 3, 4, 5, 6] - add multiple
numbers.remove(0)           # [1, 2, 3, 4, 5, 6] - remove first occurrence
popped = numbers.pop()      # 6, list is [1, 2, 3, 4, 5] - remove and return last
popped_at = numbers.pop(0)  # 1, list is [2, 3, 4, 5] - remove at index
numbers.clear()             # [] - remove all items

numbers = [3, 1, 4, 1, 5, 9, 2]
numbers.sort()              # [1, 1, 2, 3, 4, 5, 9] - sort in place
numbers.reverse()           # [9, 5, 4, 3, 2, 1, 1] - reverse in place
count_1 = numbers.count(1)  # 2 - count occurrences
index_5 = numbers.index(5)  # 1 - find index of first occurrence

# List operations
list1 = [1, 2, 3]
list2 = [4, 5, 6]
combined = list1 + list2    # [1, 2, 3, 4, 5, 6]
repeated = list1 * 2        # [1, 2, 3, 1, 2, 3]
length = len(list1)         # 3
maximum = max(list1)        # 3
minimum = min(list1)        # 1
total = sum(list1)          # 6

# List comprehension (create lists in one line)
squares = [x**2 for x in range(5)]           # [0, 1, 4, 9, 16]
evens = [x for x in range(10) if x % 2 == 0]  # [0, 2, 4, 6, 8]
matrix = [[i*j for j in range(3)] for i in range(3)]  # Nested comprehension

# Copying lists
original = [1, 2, 3]
shallow_copy = original.copy()  # or original[:] or list(original)
import copy
deep_copy = copy.deepcopy(original)


# ============================================================================
# 8. DATA STRUCTURES - TUPLES
# ============================================================================

# Tuple (ordered, immutable, allows duplicates)
empty_tuple = ()
single_element = (1,)  # Note the comma - required for single element
coordinates = (3, 4)
mixed_tuple = (1, "two", 3.0, [4, 5])

# Tuple unpacking
x, y = coordinates  # x=3, y=4
first, *rest = (1, 2, 3, 4)  # first=1, rest=[2, 3, 4]
*start, last = (1, 2, 3, 4)  # start=[1, 2, 3], last=4

# Tuple operations
tuple1 = (1, 2, 3)
tuple2 = (4, 5, 6)
combined = tuple1 + tuple2  # (1, 2, 3, 4, 5, 6)
repeated = tuple1 * 2       # (1, 2, 3, 1, 2, 3)
length = len(tuple1)        # 3
count_2 = tuple1.count(2)   # 1
index_3 = tuple1.index(3)   # 2

# Why use tuples? Faster than lists, can be used as dict keys, data integrity


# ============================================================================
# 9. DATA STRUCTURES - SETS
# ============================================================================

# Set (unordered, mutable, no duplicates)
empty_set = set()  # Note: {} creates a dict, not a set
numbers_set = {1, 2, 3, 4, 5}
from_list = set([1, 2, 2, 3, 3, 3])  # {1, 2, 3} - duplicates removed

# Set methods
numbers_set = {1, 2, 3}
numbers_set.add(4)           # {1, 2, 3, 4}
numbers_set.update([5, 6])   # {1, 2, 3, 4, 5, 6}
numbers_set.remove(1)        # {2, 3, 4, 5, 6} - raises error if not found
numbers_set.discard(10)      # No error if not found
popped = numbers_set.pop()   # Remove and return arbitrary element
numbers_set.clear()          # Empty set

# Set operations
set1 = {1, 2, 3, 4}
set2 = {3, 4, 5, 6}

union = set1 | set2          # {1, 2, 3, 4, 5, 6} - all elements
intersection = set1 & set2   # {3, 4} - common elements
difference = set1 - set2     # {1, 2} - in set1 but not set2
sym_diff = set1 ^ set2       # {1, 2, 5, 6} - in either but not both

# Set methods (alternative syntax)
union = set1.union(set2)
intersection = set1.intersection(set2)
difference = set1.difference(set2)
sym_diff = set1.symmetric_difference(set2)

# Set comparisons
is_subset = {1, 2}.issubset({1, 2, 3})      # True
is_superset = {1, 2, 3}.issuperset({1, 2})  # True
is_disjoint = {1, 2}.isdisjoint({3, 4})     # True (no common elements)

# Frozenset (immutable set)
frozen = frozenset([1, 2, 3])


# ============================================================================
# 10. DATA STRUCTURES - DICTIONARIES
# ============================================================================

# Dictionary (key-value pairs, unordered in Python <3.7, ordered in 3.7+)
empty_dict = {}
person = {
    "name": "Alice",
    "age": 25,
    "city": "New York"
}

# Multiple ways to create dictionaries
dict1 = dict(name="Bob", age=30)
dict2 = dict([("name", "Charlie"), ("age", 35)])

# Accessing values
name = person["name"]              # "Alice" - raises KeyError if not found
age = person.get("age")            # 25
default = person.get("country", "USA")  # "USA" - default if key not found

# Modifying dictionaries
person["age"] = 26                 # Update existing key
person["email"] = "alice@email.com"  # Add new key
del person["city"]                 # Delete key
removed = person.pop("email")      # Remove and return value
last_item = person.popitem()       # Remove and return last (key, value) pair

# Dictionary methods
person = {"name": "Alice", "age": 25, "city": "NYC"}
keys = person.keys()               # dict_keys(['name', 'age', 'city'])
values = person.values()           # dict_values(['Alice', 25, 'NYC'])
items = person.items()             # dict_items([('name', 'Alice'), ...])

# Iterating over dictionaries
for key in person:
    print(key, person[key])

for key, value in person.items():
    print(f"{key}: {value}")

# Dictionary comprehension
squares_dict = {x: x**2 for x in range(5)}  # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
filtered = {k: v for k, v in person.items() if k != "age"}

# Merging dictionaries
dict1 = {"a": 1, "b": 2}
dict2 = {"c": 3, "d": 4}
merged = {**dict1, **dict2}  # Python 3.5+
# Or: dict1.update(dict2)  # Modifies dict1 in place

# Nested dictionaries
students = {
    "student1": {"name": "Alice", "grade": "A"},
    "student2": {"name": "Bob", "grade": "B"}
}


# ============================================================================
# 11. FUNCTIONS
# ============================================================================

# Basic function definition
def greet():
    """This is a docstring - describes what the function does"""
    print("Hello!")

# Call the function
greet()

# Function with parameters
def greet_person(name):
    print(f"Hello, {name}!")

greet_person("Alice")

# Function with return value
def add(a, b):
    return a + b

result = add(5, 3)  # 8

# Multiple return values (returns a tuple)
def get_min_max(numbers):
    return min(numbers), max(numbers)

minimum, maximum = get_min_max([1, 2, 3, 4, 5])

# Default parameter values
def greet_with_title(name, title="Mr."):
    return f"Hello, {title} {name}"

print(greet_with_title("Smith"))           # "Hello, Mr. Smith"
print(greet_with_title("Jones", "Dr."))    # "Hello, Dr. Jones"

# Keyword arguments
def describe_pet(animal, name, age):
    return f"{name} is a {age} year old {animal}"

print(describe_pet(animal="dog", name="Buddy", age=3))
print(describe_pet(name="Whiskers", age=2, animal="cat"))  # Order doesn't matter

# *args - variable number of positional arguments
def sum_all(*numbers):
    return sum(numbers)

print(sum_all(1, 2, 3))        # 6
print(sum_all(1, 2, 3, 4, 5))  # 15

# **kwargs - variable number of keyword arguments
def print_info(**info):
    for key, value in info.items():
        print(f"{key}: {value}")

print_info(name="Alice", age=25, city="NYC")

# Combining all parameter types (order matters: regular, *args, default, **kwargs)
def complex_function(required, *args, default="value", **kwargs):
    print(f"Required: {required}")
    print(f"Args: {args}")
    print(f"Default: {default}")
    print(f"Kwargs: {kwargs}")

complex_function("must have", 1, 2, 3, default="custom", extra="info")

# Lambda functions (anonymous, single-expression functions)
square = lambda x: x**2
add_lambda = lambda a, b: a + b
print(square(5))      # 25
print(add_lambda(3, 4))  # 7

# Lambda with map, filter, reduce
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))      # [1, 4, 9, 16, 25]
evens = list(filter(lambda x: x % 2 == 0, numbers))  # [2, 4]

from functools import reduce
product = reduce(lambda a, b: a * b, numbers)     # 120

# Scope - LEGB Rule: Local, Enclosing, Global, Built-in
global_var = "global"

def outer():
    enclosing_var = "enclosing"
    
    def inner():
        local_var = "local"
        print(local_var)      # Local
        print(enclosing_var)  # Enclosing
        print(global_var)     # Global
    
    inner()

# Modifying global variables
counter = 0

def increment():
    global counter  # Must declare global to modify
    counter += 1

# Recursive functions
def factorial(n):
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)

print(factorial(5))  # 120


# ============================================================================
# 12. FILE I/O
# ============================================================================

# Writing to a file
with open("example.txt", "w") as file:  # 'w' = write mode
    file.write("Hello, World!\n")
    file.write("Python is awesome!")

# Reading from a file
with open("example.txt", "r") as file:  # 'r' = read mode (default)
    content = file.read()  # Read entire file
    print(content)

# Reading line by line
with open("example.txt", "r") as file:
    for line in file:
        print(line.strip())  # strip() removes newline

# Reading lines into a list
with open("example.txt", "r") as file:
    lines = file.readlines()  # List of lines (with \n)

# Appending to a file
with open("example.txt", "a") as file:  # 'a' = append mode
    file.write("\nNew line")

# File modes:
# 'r'  - Read (default)
# 'w'  - Write (overwrites existing file)
# 'a'  - Append
# 'x'  - Create (fails if file exists)
# 'b'  - Binary mode (e.g., 'rb', 'wb')
# '+'  - Read and write (e.g., 'r+', 'w+')

# Binary file operations
with open("image.jpg", "rb") as file:
    binary_data = file.read()

# File operations without 'with' (not recommended)
file = open("example.txt", "r")
content = file.read()
file.close()  # Must manually close

# Check if file exists
import os
if os.path.exists("example.txt"):
    print("File exists")

# Delete a file
if os.path.exists("example.txt"):
    os.remove("example.txt")


# ============================================================================
# 13. EXCEPTION HANDLING
# ============================================================================

# Basic try-except
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")

# Multiple except blocks
try:
    number = int("abc")
except ValueError:
    print("Invalid number format")
except TypeError:
    print("Type error occurred")

# Catch multiple exceptions
try:
    # some code
    pass
except (ValueError, TypeError) as e:
    print(f"Error occurred: {e}")

# Catch all exceptions (not recommended for production)
try:
    # some code
    pass
except Exception as e:
    print(f"An error occurred: {e}")

# Try-except-else-finally
try:
    file = open("example.txt", "r")
except FileNotFoundError:
    print("File not found")
else:
    # Executes if no exception occurred
    content = file.read()
    print(content)
finally:
    # Always executes, even if exception occurred
    if 'file' in locals():
        file.close()

# Raising exceptions
def validate_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    if age > 150:
        raise ValueError("Age too high")
    return age

# Custom exceptions
class CustomError(Exception):
    """Custom exception class"""
    pass

def risky_function():
    raise CustomError("Something went wrong!")

try:
    risky_function()
except CustomError as e:
    print(f"Custom error: {e}")

# Assert statement (raises AssertionError if condition is False)
age = 25
assert age >= 18, "Must be 18 or older"


# ============================================================================
# 14. CLASSES AND OBJECT-ORIENTED PROGRAMMING
# ============================================================================

# Basic class definition
class Dog:
    """A simple Dog class"""
    
    # Class variable (shared by all instances)
    species = "Canis familiaris"
    
    # Constructor (initializer)
    def __init__(self, name, age):
        # Instance variables (unique to each instance)
        self.name = name
        self.age = age
    
    # Instance method
    def bark(self):
        return f"{self.name} says Woof!"
    
    # Instance method with parameters
    def celebrate_birthday(self):
        self.age += 1
        return f"{self.name} is now {self.age} years old!"
    
    # String representation
    def __str__(self):
        return f"Dog(name={self.name}, age={self.age})"

# Creating instances (objects)
dog1 = Dog("Buddy", 3)
dog2 = Dog("Max", 5)

# Accessing attributes and calling methods
print(dog1.name)       # "Buddy"
print(dog1.bark())     # "Buddy says Woof!"
print(dog1.species)    # "Canis familiaris"

# Inheritance
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        pass  # To be overridden by subclasses

class Cat(Animal):  # Cat inherits from Animal
    def speak(self):  # Override parent method
        return f"{self.name} says Meow!"

class Dog(Animal):
    def speak(self):
        return f"{self.name} says Woof!"

# Using inherited classes
cat = Cat("Whiskers")
dog = Dog("Buddy")
print(cat.speak())  # "Whiskers says Meow!"
print(dog.speak())  # "Buddy says Woof!"

# Multiple inheritance
class Flyer:
    def fly(self):
        return "Flying!"

class Swimmer:
    def swim(self):
        return "Swimming!"

class Duck(Animal, Flyer, Swimmer):  # Inherits from multiple classes
    def speak(self):
        return f"{self.name} says Quack!"

# Class methods (work with class, not instance)
class Person:
    population = 0
    
    def __init__(self, name):
        self.name = name
        Person.population += 1
    
    @classmethod
    def get_population(cls):
        return cls.population

# Static methods (don't access instance or class)
class MathUtils:
    @staticmethod
    def add(a, b):
        return a + b

print(MathUtils.add(5, 3))  # 8 - no instance needed

# Property decorators (getters and setters)
class Circle:
    def __init__(self, radius):
        self._radius = radius  # Convention: _ means "private"
    
    @property
    def radius(self):
        return self._radius
    
    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value
    
    @property
    def area(self):
        return 3.14159 * self._radius ** 2

circle = Circle(5)
print(circle.radius)  # 5
print(circle.area)    # 78.53975
circle.radius = 10    # Uses setter
# circle.area = 100   # Error - no setter defined

# Special methods (dunder methods)
class Book:
    def __init__(self, title, pages):
        self.title = title
        self.pages = pages
    
    def __str__(self):      # str(book) or print(book)
        return f"'{self.title}'"
    
    def __repr__(self):     # repr(book) - for developers
        return f"Book(title='{self.title}', pages={self.pages})"
    
    def __len__(self):      # len(book)
        return self.pages
    
    def __eq__(self, other):  # book1 == book2
        return self.title == other.title
    
    def __lt__(self, other):  # book1 < book2
        return self.pages < other.pages


# ============================================================================
# 15. MODULES AND IMPORTS
# ============================================================================

# Import entire module
import math
print(math.pi)      # 3.141592653589793
print(math.sqrt(16))  # 4.0

# Import specific items
from math import pi, sqrt
print(pi)           # 3.141592653589793
print(sqrt(16))     # 4.0

# Import with alias
import datetime as dt
now = dt.datetime.now()

from math import sqrt as square_root
print(square_root(25))  # 5.0

# Import all (not recommended - pollutes namespace)
# from math import *

# Commonly used standard library modules
import os          # Operating system interface
import sys         # System-specific parameters
import json        # JSON encoding/decoding
import random      # Random number generation
import datetime    # Date and time
import re          # Regular expressions
import collections # Specialized container types
import itertools   # Iterator tools
import pathlib     # Object-oriented filesystem paths


# ============================================================================
# 16. LIST/DICT/SET COMPREHENSIONS (Advanced)
# ============================================================================

# List comprehension
squares = [x**2 for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]
upper_words = [word.upper() for word in ["hello", "world"]]

# Nested list comprehension
matrix = [[i*j for j in range(5)] for i in range(5)]

# Dictionary comprehension
squares_dict = {x: x**2 for x in range(5)}
name_lengths = {name: len(name) for name in ["Alice", "Bob", "Charlie"]}
filtered_dict = {k: v for k, v in {"a": 1, "b": 2, "c": 3}.items() if v > 1}

# Set comprehension
unique_squares = {x**2 for x in [-2, -1, 0, 1, 2]}  # {0, 1, 4}

# Generator expression (lazy evaluation, memory efficient)
squares_gen = (x**2 for x in range(1000000))  # Doesn't compute until needed


# ============================================================================
# 17. ADVANCED CONCEPTS
# ============================================================================

# Enumerate with unpacking
pairs = [(1, 'a'), (2, 'b'), (3, 'c')]
for index, (num, letter) in enumerate(pairs):
    print(f"{index}: {num}, {letter}")

# Zip - combine multiple iterables
names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]
for name, age in zip(names, ages):
    print(f"{name}: {age}")

# Zip to create dictionary
person_dict = dict(zip(names, ages))

# Any and all
numbers = [2, 4, 6, 8]
all_even = all(x % 2 == 0 for x in numbers)  # True
any_odd = any(x % 2 == 1 for x in numbers)   # False

# Sorted with key
words = ["banana", "apple", "cherry"]
sorted_words = sorted(words)                    # Alphabetical
sorted_length = sorted(words, key=len)          # By length
sorted_reverse = sorted(words, reverse=True)    # Reverse

# Min/max with key
oldest = max([("Alice", 25), ("Bob", 30)], key=lambda x: x[1])

# F-strings advanced formatting
name = "Alice"
value = 123.456789
print(f"{value:.2f}")        # 123.46 - 2 decimal places
print(f"{value:10.2f}")      # "    123.46" - width 10
print(f"{name:>10}")         # "     Alice" - right align
print(f"{name:<10}")         # "Alice     " - left align
print(f"{name:^10}")         # "  Alice   " - center align
print(f"{1234567:,}")        # "1,234,567" - thousands separator

# Walrus operator (Python 3.8+)
# Assigns and returns value in one expression
if (n := len([1, 2, 3])) > 2:
    print(f"List is long: {n} items")

# Type hints (Python 3.5+, for documentation/IDE support)
def greet_typed(name: str, age: int) -> str:
    return f"Hello {name}, you are {age} years old"

from typing import List, Dict, Tuple, Optional

def process_items(items: List[int]) -> Dict[str, int]:
    return {"sum": sum(items), "count": len(items)}


# ============================================================================
# 18. USEFUL BUILT-IN FUNCTIONS
# ============================================================================

# Type checking
print(type(42))           # <class 'int'>
print(isinstance(42, int))  # True
print(isinstance(42, (int, float)))  # True - check multiple types

# Conversion
print(int("42"))          # 42
print(float("3.14"))      # 3.14
print(str(42))            # "42"
print(list("hello"))      # ['h', 'e', 'l', 'l', 'o']
print(tuple([1, 2, 3]))   # (1, 2, 3)
print(set([1, 2, 2, 3]))  # {1, 2, 3}

# Math operations
print(abs(-5))            # 5
print(pow(2, 3))          # 8 (2**3)
print(round(3.14159, 2))  # 3.14
print(divmod(17, 5))      # (3, 2) - quotient and remainder

# Aggregation
numbers = [1, 2, 3, 4, 5]
print(sum(numbers))       # 15
print(max(numbers))       # 5
print(min(numbers))       # 1
print(len(numbers))       # 5

# Iteration utilities
print(list(reversed([1, 2, 3])))  # [3, 2, 1]
print(list(range(5)))             # [0, 1, 2, 3, 4]

# Input/Output
# name = input("Enter your name: ")  # Commented - waits for user input
print("Hello, World!", end=" ")   # Custom ending (default is \n)
print("More text")

# Help and documentation
# help(len)  # Shows documentation
# dir(str)   # Lists all attributes/methods


# ============================================================================
# 19. COMMON PATTERNS AND IDIOMS
# ============================================================================

# Swapping variables
a, b = 5, 10
a, b = b, a  # a=10, b=5

# Checking for empty collections
my_list = []
if not my_list:  # Pythonic way to check if empty
    print("List is empty")

# Default values with or
name = None
display_name = name or "Guest"  # "Guest"

# Chaining comparisons
age = 25
if 18 <= age < 65:
    print("Working age")

# Iterating with index
fruits = ["apple", "banana", "cherry"]
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# Multiple assignment from function
def get_coordinates():
    return 10, 20

x, y = get_coordinates()

# Context managers (with statement)
with open("file.txt", "w") as f:
    f.write("Hello")
# File automatically closed

# Dictionary get with default
person = {"name": "Alice"}
age = person.get("age", 18)  # 18 if 'age' not in dict

# String checking
text = "hello"
if text:  # Check if non-empty
    print("Has text")

# List as stack
stack = []
stack.append(1)  # Push
stack.append(2)
item = stack.pop()  # Pop (2)

# List as queue (use collections.deque for better performance)
from collections import deque
queue = deque()
queue.append(1)  # Enqueue
queue.append(2)
item = queue.popleft()  # Dequeue (1)


# ============================================================================
# 20. SUMMARY AND BEST PRACTICES
# ============================================================================

"""
PYTHON BEST PRACTICES:

1. Follow PEP 8 style guide (naming conventions, indentation, etc.)
2. Use meaningful variable names (descriptive, not too short)
3. Write docstrings for functions and classes
4. Use list/dict comprehensions when appropriate (but keep them readable)
5. Prefer 'with' statement for file operations
6. Use enumerate() instead of range(len())
7. Use f-strings for string formatting (Python 3.6+)
8. Don't use mutable default arguments
9. Use isinstance() for type checking
10. Keep functions small and focused
11. Use exceptions for error handling, not return codes
12. Use _ for throwaway variables: for _ in range(10)
13. Use is for None comparisons: if x is None
14. Prefer 'in' for membership testing: if 'a' in my_list
15. Use generators for large datasets to save memory

COMMON GOTCHAS:
- Mutable default arguments: def func(lst=[]):  # BAD!
- Integer division vs float division: 10/3 vs 10//3
- Shallow vs deep copy
- Global variables in functions need 'global' keyword
- Dict iteration order (guaranteed in Python 3.7+)
"""

print("\n" + "="*60)
print("Tutorial Complete! You've learned:")
print("- Variables, data types, and operators")
print("- Strings and string operations")
print("- Control flow (if/elif/else)")
print("- Loops (for/while)")
print("- Data structures (list, tuple, set, dict)")
print("- Functions and lambda expressions")
print("- File I/O")
print("- Exception handling")
print("- Object-oriented programming")
print("- Comprehensions and advanced concepts")
print("="*60)

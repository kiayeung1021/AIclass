import sys
import datetime

def run_test():

    print("Hello!")
    print("--- Python Installation Test ---")
    
    # 1. Check Python Version
    print(f"Python Version: {sys.version}")
    
    # 2. Check Date/Time (Standard Library Test)
    now = datetime.datetime.now()
    print(f"Current Date and Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 3. Simple Math Test
    a = 10
    b = 5
    print(f"Math Test: {a} + {b} = {a + b}")
    
    # 4. Interactive Input Test
    user_name = input("\nWhat is your name? ")
    print(f"Hello, {user_name}! Your Python environment is working perfectly.")
    print("--------------------------------")

if __name__ == "__main__":
    run_test()
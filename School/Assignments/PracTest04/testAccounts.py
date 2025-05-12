'''
  Practical Test 4

  testAccounts.py - program to test functions of accounts.py
  
  Student Name   : Thomas Han
  Student Number : 22881119
  Date/prac time : 12/05/2025

'''
from accounts import BankAccount, Portfolio, InsufficientFundsError, AccountNotFoundError

print('\n<--- Bank Accounts Portfolio --->\n')
myAccounts = Portfolio()

# add code for tasks here

#e.g.
#myAccounts.addAccount("Everyday", "1111-007", 1000)
#myAccounts.deposit("Everyday",200)

myAccounts.addAccount("Castle", "999999-1", 1000)
myAccounts.addAccount("Shrubbery", "999999-2", 100)
myAccounts.addAccount("Grail", "999999-3", 100)

myAccounts.balances()

myAccounts.deposit("Castle", 100)
try:
    myAccounts.withdraw("Shrubbery", 10)
except InsufficientFundsError as e:
    print("** exception: ", e)

try:
    myAccounts.withdraw("Shrubbery", 1000)
except InsufficientFundsError as e:
    print("** exception: ", e)

myAccounts.balances()
print(f'Total Balance of Accounts: ${myAccounts.getTotalBalance()}')
print(f'Number of Accounts: {myAccounts.getNumAccounts()}')

try:
    myAccounts.withdraw("Grail", 1000)
except InsufficientFundsError as e:
    print("** exception: ", e)

myAccounts.balances()

<<<<<<< HEAD
import sqlite3
from dbase import *

def main():
    # adminid = input("5820921267")
    # check = check_admin(adminid)
    # if check == True:
    #     print("Admin already exists")
    # else:
    #     try:
    #         create_admin(adminid)
    #         create_user_lifetime(adminid)
    #     except:
    #         print('something went wrong')
    #     else:
    #         print('Admin created...')
    #        create_admin(5820921267)
    james = fetch_UserData_table()
    print(james)
if __name__ == '__main__':
=======
import sqlite3
from dbase import *

def main():
    # adminid = input("5820921267")
    # check = check_admin(adminid)
    # if check == True:
    #     print("Admin already exists")
    # else:
    #     try:
    #         create_admin(adminid)
    #         create_user_lifetime(adminid)
    #     except:
    #         print('something went wrong')
    #     else:
    #         print('Admin created...')
    #        create_admin(5820921267)
    james = fetch_UserData_table()
    print(james)
if __name__ == '__main__':
>>>>>>> 5058b63e17bc5c42e66a4f03a260eae69ba8e457
    main()
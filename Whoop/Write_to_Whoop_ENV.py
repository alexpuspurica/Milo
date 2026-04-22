import getpass
usernameintowhoop = input("Enter your WHOOP E-mail: ")
passwordintowhoop = getpass.getpass("Enter your WHOOP Password: ")

with open (".env", "w") as f:
    f.write(f'USERNAMEinENV={usernameintowhoop}\n')
    f.write(f'PASSWORDinENV={passwordintowhoop}\n')
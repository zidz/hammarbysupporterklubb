#!/usr/bin/env python3
"""User manager CLI - list, add, remove and edit users."""
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.models import User


def prompt_password(prompt="Password: ", confirm=False):
    """Prompt for a password securely."""
    while True:
        password = input(prompt)
        if confirm:
            confirmation = input("Confirm password: ")
            if password != confirmation:
                print("Passwords do not match. Try again.")
                continue
        if len(password) < 8:
            print("Password must be at least 8 characters.")
            continue
        return password


def cmd_list(args):
    """List all users."""
    users = User.load_all()
    if not users:
        print("No users found.")
        return

    print(f"{'ID':<6}{'Username':<20}{'Email':<30}{'Role':<10}")
    print("-" * 66)
    for u in users:
        print(f"{u['id']:<6}{u['username']:<20}{u['email']:<30}{u['role']:<10}")


def cmd_add(args):
    """Add a new user."""
    username = args.username
    email = args.email
    role = args.role

    if not username:
        username = input("Username: ")
    if not email:
        email = input("Email: ")

    if args.password:
        password = args.password
    elif args.set_password:
        password = prompt_password("Password: ", confirm=True)
    else:
        password = prompt_password("Password: ", confirm=True)

    try:
        user = User.create_user(username=username, email=email, password=password, role=role)
        print(f"User created: {user.username} (id={user.id})")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_remove(args):
    """Remove a user by id or username."""
    target = args.id or args.username
    if not target:
        print("Error: provide --id or --username")
        sys.exit(1)

    users = User.load_all()
    found = None

    if args.id:
        for u in users:
            if u['id'] == args.id:
                found = u
                break
    else:
        for u in users:
            if u['username'] == args.username:
                found = u
                break

    if not found:
        print(f"User not found: {target}")
        sys.exit(1)

    if args.force:
        users = [u for u in users if u is not found]
        User.save_all(users)
        print(f"User removed: {found['username']} (id={found['id']})")
    else:
        confirm = input(f"Remove user {found['username']} (id={found['id']})? [y/N] ")
        if confirm.lower() == 'y':
            users = [u for u in users if u is not found]
            User.save_all(users)
            print(f"User removed: {found['username']} (id={found['id']})")
        else:
            print("Aborted.")


def cmd_edit(args):
    """Edit user fields: username, email, password."""
    target = args.id
    if not target:
        print("Error: provide --id")
        sys.exit(1)

    users = User.load_all()
    found = None
    for u in users:
        if u['id'] == target:
            found = u
            break

    if not found:
        print(f"User not found: {target}")
        sys.exit(1)

    print(f"Editing user: {found['username']} (id={found['id']})")

    if args.username:
        existing = User.find_by_username(args.username)
        if existing and existing.id != found['id']:
            print(f"Error: username '{args.username}' is already taken")
            sys.exit(1)
        found['username'] = args.username
        print(f"  username: {found['username']}")

    if args.email:
        found['email'] = args.email
        print(f"  email: {found['email']}")

    if args.password:
        password = args.password
    elif args.set_password:
        password = prompt_password("New password: ", confirm=True)
    else:
        password = None

    if password:
        import bcrypt
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        found['password_hash'] = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
        print("  password: updated")

    if not args.username and not args.email and not args.password and not args.set_password:
        print("No changes specified. Use --username, --email, --password or --set-password")
        return

    User.save_all(users)
    print(f"User {found['username']} (id={found['id']}) updated.")


def main():
    parser = argparse.ArgumentParser(
        prog='user_manager',
        description='Manage users for Hammarby Supporterklubb'
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # list
    subparsers.add_parser('list', help='List all users')

    # add
    add_parser = subparsers.add_parser('add', help='Add a new user')
    add_parser.add_argument('--username', '-u', help='Username')
    add_parser.add_argument('--email', '-e', help='Email address')
    add_parser.add_argument('--password', '-p', help='Password (use --set-password for interactive)')
    add_parser.add_argument('--set-password', action='store_true', help='Set password interactively')
    add_parser.add_argument('--role', '-r', default='member', choices=['admin', 'member'], help='Role (default: member)')

    # remove
    rm_parser = subparsers.add_parser('remove', help='Remove a user')
    rm_parser.add_argument('--id', type=int, help='User ID')
    rm_parser.add_argument('--username', '-u', help='Username')
    rm_parser.add_argument('--force', '-f', action='store_true', help='Skip confirmation')

    # edit
    edit_parser = subparsers.add_parser('edit', help='Edit user (username, email, password)')
    edit_parser.add_argument('--id', type=int, required=True, help='User ID to edit')
    edit_parser.add_argument('--username', '-u', help='New username')
    edit_parser.add_argument('--email', '-e', help='New email')
    edit_parser.add_argument('--password', '-p', help='New password (use --set-password for interactive)')
    edit_parser.add_argument('--set-password', action='store_true', help='Set password interactively')

    args = parser.parse_args()

    if args.command == 'list':
        cmd_list(args)
    elif args.command == 'add':
        cmd_add(args)
    elif args.command == 'remove':
        cmd_remove(args)
    elif args.command == 'edit':
        cmd_edit(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

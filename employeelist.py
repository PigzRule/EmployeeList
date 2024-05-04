import sqlite3
import logging
import shutil
import os
import datetime
import csv
import getpass

logging.basicConfig(filename='employee_directory.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_user_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')


def create_employee_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            department TEXT,
            position TEXT,
            contact TEXT,
            job_history TEXT,
            skills TEXT
        )
    ''')


def authenticate_user(cursor, username, password):
    cursor.execute('''
        SELECT * FROM users
        WHERE username = ? AND password = ?
    ''', (username, password))
    return cursor.fetchone()


def register_user(cursor, username, password, role):
    cursor.execute('''
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
    ''', (username, password, role))
    logging.info("User registered: Username - %s, Role - %s", username, role)


def add_employee(cursor, name, department, position, contact, job_history, skills, user_role):
    try:
        if user_role == 'employee':
            raise PermissionError("You don't have permission to add employees.")
            
        if not (name and department and position):
            raise ValueError("Name, department, and position cannot be empty")

        cursor.execute('''
            INSERT INTO employees (name, department, position, contact, job_history, skills)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, department, position, contact, job_history, skills))
        logging.info("Employee added: Name - %s, Department - %s, Position - %s", name, department, position)
    except Exception as e:
        logging.error("Error adding employee: %s", e)
        raise e


def search_employees(cursor, criteria, sort_by=None, filter_by=None, per_page=10, page=1):
    offset = (page - 1) * per_page
    query = '''
        SELECT * FROM employees
        WHERE name LIKE ? OR department LIKE ? OR position LIKE ? OR contact LIKE ? OR job_history LIKE ? OR skills LIKE ?
    '''
    params = ['%{}%'.format(criteria)] * 6

    if filter_by:
        query += ' AND {} = ?'.format(filter_by[0])
        params.append(filter_by[1])

    if sort_by:
        query += ' ORDER BY {}'.format(sort_by)

    query += ' LIMIT ? OFFSET ?'
    params.extend([per_page, offset])

    cursor.execute(query, tuple(params))
    return cursor.fetchall()


def update_employee(cursor, user_role, username, employee_id, name, department, position, contact, job_history, skills):
    try:
        if user_role == 'admin': 
            cursor.execute('''
                UPDATE employees
                SET name = ?, department = ?, position = ?, contact = ?, job_history = ?, skills = ?
                WHERE id = ?
            ''', (name, department, position, contact, job_history, skills, employee_id))
            logging.info("Employee updated by admin: ID - %d, Name - %s, Department - %s, Position - %s", employee_id, name,
                         department, position)
        else:
            cursor.execute('''
                UPDATE employees
                SET name = ?, department = ?, position = ?, contact = ?, job_history = ?, skills = ?
                WHERE id = ? AND name = ? AND id IN (
                    SELECT e.id FROM employees e
                    JOIN users u ON e.name = ? AND u.username = ? AND u.role = ?
                )
            ''', (name, department, position, contact, job_history, skills, employee_id, name, name, username, user_role))
            logging.info("Employee updated by user: ID - %d, Name - %s, Department - %s, Position - %s", employee_id, name,
                         department, position)
    except Exception as e:
        logging.error("Error updating employee: %s", e)
        raise e


def delete_employee(cursor, user_role, employee_id):
    try:
        if user_role == 'employee':
            raise PermissionError("You don't have permission to delete employees.")
            
        cursor.execute('''
            DELETE FROM employees
            WHERE id = ?
        ''', (employee_id,))
        logging.info("Employee deleted: ID - %d", employee_id)
    except Exception as e:
        logging.error("Error deleting employee: %s", e)
        raise e


def import_from_csv(cursor, user_role, filename='employee_data.csv',):
    try:
        if user_role == 'employee':
            raise PermissionError("You don't have permission to import employees.")
            
        with open(filename, 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)
            for row in csv_reader:
                cursor.execute('''
                    INSERT INTO employees (name, department, position, contact, job_history, skills)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', row[1:])
        print(f"Employee data imported from {filename} successfully.")
    except FileNotFoundError:
        print("Error: File not found.")
    except Exception as e:
        print("Error importing data:", e)

def export_to_csv(cursor, user_role, filename='employee_data.csv', ):
    try:
        if user_role == 'employee':
            raise PermissionError("You don't have permission to export employees.")
            
        cursor.execute("SELECT * FROM employees")
        rows = cursor.fetchall()
        if not rows:
            print("No data to export.")
            return

        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['ID', 'Name', 'Department', 'Position', 'Contact', 'Job History', 'Skills'])
            csv_writer.writerows(rows)
        print(f"Employee data exported to {filename} successfully.")
    except Exception as e:
        print("Error exporting data:", e)

def import_data_from_csv(cursor):
    filename = input("Enter the filename to import from (e.g., employee_data.csv): ")
    import_from_csv(cursor, filename)

def export_data_to_csv(cursor):
    filename = input("Enter the filename to export to (e.g., employee_data.csv): ")
    export_to_csv(cursor, filename)

def delete_user(cursor, username, user_role):
    try:
        if user_role == 'employee':
            raise PermissionError("You don't have permission to delete users.")
            
        cursor.execute('''
            DELETE FROM users
            WHERE username = ?
        ''', (username,))
        logging.info("User deleted: Username - %s", username)
    except Exception as e:
        logging.error("Error deleting user: %s", e)
        raise e

def list_users_by_role(cursor, user):
    role = input("Enter the role to list users (admin/user): ")
    if role.lower() not in ('admin', 'user'):
        print("Invalid role. Please enter 'admin' or 'user'.")
        return

    cursor.execute("SELECT username FROM users WHERE role = ?", (role,))
    users = cursor.fetchall()
    
    if users:
        print(f"Users with role '{role}':")
        for user in users:
            print(user[0])
    else:
        print(f"No users found with role '{role}'.")

def manage_users(conn, cursor, user):
    print("\nUser Management")
    print("1. Register New User")
    print("2. Delete User")
    print("3. List Users by Role")
    print("4. Back to Main Menu")

    user_choice = input("Enter your choice: ")

    if user_choice == '1':
        if user[3] == 'admin':
            username = input("Enter new username: ")
            password = getpass.getpass("Enter new password: ") # Modification to hide password input
            role = input("Enter role (admin/user): ")
            register_user(cursor, username, password, role)
            conn.commit()
            print("User registered successfully!")
        else:
            print("You don't have permission to perform this action.")
    elif user_choice == '2':
        if user[3] == 'admin':
            username = input("Enter the username to delete: ")
            delete_user(cursor, username)
            conn.commit()
            print("User deleted successfully!")
        else:
            print("You don't have permission to perform this action.")
    elif user_choice == '3':
        list_users_by_role(cursor, user)
    elif user_choice == '4':
        return
    else:
        print("Invalid choice. Please enter a valid option.")
        manage_users(cursor, user)

def backup_database(source_db, backup_folder, user_role=None):
    try:
        if user_role != 'admin':
            raise PermissionError("Only admins are allowed to perform database backups.")

        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_folder, f"employee_directory_backup_{timestamp}.db")

        shutil.copy(source_db, backup_file)
        print("Backup completed successfully!")
    except Exception as e:
        print("Error during backup:", e)



def main():
    conn = sqlite3.connect('employee_directory.db')
    cursor = conn.cursor()

    create_user_table(cursor)
    create_employee_table(cursor)

    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, role)
        VALUES (?, ?, ?)
    ''', ('admin', 'admin123', 'admin'))
    conn.commit()

    # Authentication Loop
    while True:
        username = input("Enter username: ")
        password = getpass.getpass("Enter password: ") # Modification to hide password input

        user = authenticate_user(cursor, username, password)

        if user:
            print("Login successful!")
            break
        else:
            print("Invalid username or password. Please try again.")

    while True:
        print("\nEmployee Directory")
        print("1. Add New Employee (Admin)")
        print("2. Search Employees")
        print("3. Update Employee Information (Only yourself)")
        print("4. Delete Employee (Admin)")
        print("5. Import Data from CSV (Admin)")
        print("6. Export Data to CSV (Admin)")
        print("7. User Management (Admin)")
        print("8. Backup Database")
        print("9. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            if user[3] == 'admin':
                try:
                    name = input("Enter employee name: ")
                    department = input("Enter employee department: ")
                    position = input("Enter employee position: ")
                    contact = input("Enter employee contact details (email): ")
                    job_history = input("Enter employee job history: ")
                    skills = input("Enter employee skills: ")

                    if not (name and department and position):
                        raise ValueError("Name, department, and position cannot be empty.")

                    # Pass the user's role to the add_employee function
                    add_employee(cursor, name, department, position, contact, job_history, skills, user[3])
                    conn.commit()
                    print("Employee added successfully!")
                except Exception as e:
                    print("Error:", e)
            else:
                print("You don't have permission to perform this action")



        elif choice == '2':
            criteria = input("Enter search criteria: ")

            try:
                per_page = int(input("Enter number of results per page: "))
            except ValueError:
                per_page = 10 

            page = 1

            sort_by = input("Enter column to sort by (name, department, position), or leave blank: ").strip()
            filter_column = input(
                "Enter column to filter by (name, department, position), or leave blank: ").strip()
            filter_value = input("Enter filter value, or leave blank: ").strip()

            sort_by = sort_by if sort_by else None
            filter_by = (filter_column, filter_value) if filter_column and filter_value else None

            while True:
                results = search_employees(cursor, criteria, sort_by, filter_by, per_page, page)
                if results:
                    print("\nSearch Results (Page {}):".format(page))
                    for employee in results:
                        print(employee)
                    next_page = input("Enter 'n' to view next page, any other key to exit: ")
                    if next_page.lower() == 'n':
                        page += 1
                    else:
                        break
                else:
                    print("No matching employees found.")
                    break

        elif choice == '3':
            try:
                employee_id = int(input("Enter employee ID to update: "))
                cursor.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
                employee = cursor.fetchone()
                
                if not employee:
                    print("Error: Employee ID does not exist.")
                    continue
                
                name = input("Enter updated employee name: ")
                department = input("Enter updated employee department: ")
                position = input("Enter updated employee position: ")
                contact = input("Enter updated employee contact details: ")
                job_history = input("Enter updated employee job history: ")
                skills = input("Enter updated employee skills: ")

                if user[3] == 'admin':
                    update_employee(cursor, user[3], username, employee_id, name, department, position, contact, job_history, skills)
                else:
                    update_employee(cursor, user[3], username, employee_id, name, department, position, contact, job_history, skills)
                conn.commit()
                print("Employee information updated successfully!")
            except Exception as e:
                print("Error:", e)



        elif choice == '4':
            if user[3] == 'admin':
                try:
                    employee_id = int(input("Enter employee ID to delete: "))
                    delete_employee(cursor, employee_id)
                    conn.commit()
                    print("Employee deleted successfully!")
                except Exception as e:
                    print("Error:", e)
            else:
                print("You don't have permission to perform this action.")

        elif choice == '5':
            if user[3] == 'admin':
                import_data_from_csv(cursor)
            else:
                print("You don't have permission to perform this action.")

        elif choice == '6':
            if user[3] == 'admin':
                export_data_to_csv(cursor)
            else:
                print("You don't have permission to perform this action.")

        elif choice == '7':
            if user[3] == 'admin':
                manage_users(conn, cursor, user)
            else:
                print("You don't have permission to perform this action.")

        elif choice == '8':
            backup_folder = input("Enter the backup folder path: ")
            backup_database('employee_directory.db', backup_folder, user[3])

        
        elif choice == '9':
            break

        else:
            print("Invalid choice. Please enter a valid option.")

    conn.close()

if __name__ == "__main__":
    main()
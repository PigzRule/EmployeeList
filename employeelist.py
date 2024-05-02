import sqlite3
import logging

logging.basicConfig(filename='employee_directory.log', level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')

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

def add_employee(cursor, name, department, position, contact, job_history, skills):
    try:
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


def update_employee(cursor, employee_id, name, department, position, contact, job_history, skills):
    try:
        cursor.execute('''
            UPDATE employees
            SET name = ?, department = ?, position = ?, contact = ?, job_history = ?, skills = ?
            WHERE id = ?
        ''', (name, department, position, contact, job_history, skills, employee_id))
        logging.info("Employee updated: ID - %d, Name - %s, Department - %s, Position - %s", employee_id, name, department, position)
    except Exception as e:
        logging.error("Error updating employee: %s", e)
        raise e

def delete_employee(cursor, employee_id):
    try:
        cursor.execute('''
            DELETE FROM employees
            WHERE id = ?
        ''', (employee_id,))
        logging.info("Employee deleted: ID - %d", employee_id)
    except Exception as e:
        logging.error("Error deleting employee: %s", e)
        raise e
    
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
        password = input("Enter password: ")

        user = authenticate_user(cursor, username, password)

        if user:
            print("Login successful!")
            break
        else:
            print("Invalid username or password. Please try again.")

    while True:
        print("\nEmployee Directory")
        print("1. Add New Employee")
        print("2. Search Employees")
        print("3. Update Employee Information")
        print("4. Delete Employee")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            if user[3] == 'admin':
                try:
                    name = input("Enter employee name: ")
                    department = input("Enter employee department: ")
                    position = input("Enter employee position: ")
                    contact = input("Enter employee contact details: ")
                    job_history = input("Enter employee job history: ")
                    skills = input("Enter employee skills: ")
                    
                    if not (name and department and position):
                        raise ValueError("Name, department, and position cannot be empty.")
                    
                    add_employee(cursor, name, department, position, contact, job_history, skills)
                    conn.commit()
                    print("Employee added successfully!")
                except Exception as e:
                    print("Error:", e)
            else:
                print("You don't have permission to perform this action")

        elif choice == '2':
            criteria = input("Enter search criteria: ")
            per_page = int(input("Enter number of results per page: "))
            page = 1

            sort_by = input("Enter column to sort by (name, department, position), or leave blank: ").strip()
            filter_column = input("Enter column to filter by (name, department, position), or leave blank: ").strip()
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
            if user[3] == 'admin':
                try:
                    employee_id = int(input("Enter employee ID to update: "))
                    name = input("Enter updated employee name: ")
                    department = input("Enter updated employee department: ")
                    position = input("Enter updated employee position: ")
                    contact = input("Enter updated employee contact details: ")
                    job_history = input("Enter updated employee job history: ")
                    skills = input("Enter updated employee skills: ")
                    
                    update_employee(cursor, employee_id, name, department, position, contact, job_history, skills)
                    conn.commit()
                    print("Employee information updated successfully!")
                except Exception as e:
                    print("Error:", e)
            else:
                print("You don't have permission to perform this action.")

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
            break

        else:
            print("Invalid choice. Please enter a valid option.")

    conn.close()

if __name__ == "__main__":
    main()

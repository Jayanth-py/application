import streamlit as st
from pymongo import MongoClient
from datetime import datetime

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["todo_app"]

# Load custom CSS with background color and image
def set_background(color, image_url=None):
    style = f"""
    <style>
        .stApp {{
            background-color: {color};
        }}
    """
    if image_url:
        style += f"""
        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }}
        """
    style += "</style>"
    st.markdown(style, unsafe_allow_html=True)

# User and task management functions
def get_user(username):
    """Retrieve a user from the database by username."""
    return db.users.find_one({"username": username})

def create_user(username, password):
    """Create a new user in the database."""
    db.users.insert_one({"username": username, "password": password})

def manage_task(user_id, action, task_data=None):
    """Manage tasks: add, update, or delete."""
    if action == "add":
        db.tasks.insert_one({"user_id": user_id, **task_data, "status": "to do"})
    elif action == "update":
        db.tasks.update_one({"_id": task_data["_id"]}, {"$set": {"status": task_data["status"]}})
    elif action == "delete":
        db.tasks.delete_one({"_id": task_data["_id"]})

def get_tasks(user_id):
    """Retrieve tasks for a specific user."""
    return list(db.tasks.find({"user_id": user_id}))

# User interface functions
def signup():
    """User sign-up interface."""
    set_background("#e0f7fa", "https://example.com/signup-background.jpg")  # Background for Sign Up
    st.markdown('<h2 style="color: teal;">Sign Up</h2>', unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Create Account"):
        if password != confirm_password:
            st.error("Passwords do not match.")
        elif get_user(username):
            st.error("Username already exists.")
        else:
            create_user(username, password)
            st.success("Account created successfully!")

def login():
    """User login interface."""
    set_background("#fce4ec", "https://example.com/login-background.jpg")  # Background for Login
    st.markdown('<h2 style="color: teal;">Login</h2>', unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        user = get_user(username)
        if user and user['password'] == password:
            st.session_state['user_id'] = str(user['_id'])
            st.session_state['page'] = 'Task Manager'  # Set page to 'Task Manager' after login
            st.success("Logged in successfully!")
        else:
            st.error("Invalid credentials.")

def task_manager():
    """Task management interface for logged-in users."""
    if 'user_id' not in st.session_state:
        st.warning("Please login to manage tasks.")
        return

    user_id = st.session_state['user_id']
    tasks = get_tasks(user_id)
    
    task = st.text_input("Task")
    due_datetime = datetime.combine(st.date_input("Due Date"), st.time_input("Due Time"))
    
    if st.button("Add Task") and task:
        manage_task(user_id, "add", {"task": task, "due_date": due_datetime})
        st.success("Task added successfully!")

    # Create tables for each task status
    task_statuses = ["to do", "doing", "done"]
    for status in task_statuses:
        st.markdown(f'<h3 style="color: blue;">{status.capitalize()} Tasks</h3>', unsafe_allow_html=True)
        status_tasks = [t for t in tasks if t['status'] == status]
        
        if status_tasks:
            # Prepare a list for the table without actions
            table_data = [
                {
                    "Task": task['task'],
                    "Due Date": task['due_date'],
                }
                for task in status_tasks
            ]
            
            # Display the tasks in a table format
            st.table(table_data)
            
            # Buttons for actions below the table
            for task in status_tasks:
                if status == "to do" and st.button("Start Doing", key=f"doing_{task['_id']}"):
                    manage_task(user_id, "update", {"_id": task['_id'], "status": "doing"})
                    st.success("Task status updated to 'Doing'!")
                elif status == "doing" and st.button("Mark as Done", key=f"done_{task['_id']}"):
                    manage_task(user_id, "update", {"_id": task['_id'], "status": "done"})
                    st.success("Task marked as done!")
                elif status == "done" and st.button("Delete Task", key=f"del_{task['_id']}"):
                    manage_task(user_id, "delete", {"_id": task['_id']})
                    st.success("Task deleted!")
        else:
            st.write("No tasks available.")

def main():
    """Main function to run the Streamlit app."""
    st.markdown('<h1 style="text-align:center; color: #FF6347;">Welcome to TaskHive</h1>', unsafe_allow_html=True)
    
    if 'user_id' in st.session_state:
        st.sidebar.markdown('<h2 style="color: #FF6347;">Task Manager</h2>', unsafe_allow_html=True)
        if st.sidebar.button("Logout"):  # Move the Logout button to the sidebar
            st.session_state.clear()  # Clear session state
            st.success("You have been logged out.")
            st.experimental_rerun()  # Rerun the app to redirect to login
        task_manager()  # Display the Task Manager directly if logged in
    else:
        choice = st.sidebar.selectbox("Select", ["Sign Up", "Login"])

        if choice == "Sign Up":
            signup()
        elif choice == "Login":
            login()

if __name__ == "__main__":
    main()



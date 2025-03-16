import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:5000"

# Helper function for conditional rerun
def try_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.info("Please refresh the page manually to see updates.")

# -----------------------------
# API Helper Functions
# -----------------------------

# MEDICINES
def get_medicines(order_id=None):
    url = f"{API_BASE_URL}/medicines"
    if order_id:
        url += f"?order_id={order_id}"
    response = requests.get(url)
    if response.ok:
        return response.json()
    else:
        st.error("Failed to fetch medicines")
        return []

def add_medicine(name, quantity, price, order_id):
    # Remove inventory status from the add form; default is "added"
    default_status = "added"
    url = f"{API_BASE_URL}/medicines"
    data = {
        "name": name,
        "quantity": quantity,
        "price": price,
        "inventory_status": default_status,
        "order_id": order_id
    }
    response = requests.post(url, json=data)
    if response.ok:
        st.success("Medicine added successfully!")
    else:
        st.error("Failed to add medicine")

def update_medicine_status(medicine_id, new_status):
    url = f"{API_BASE_URL}/medicines/{medicine_id}"
    data = {"inventory_status": new_status}
    response = requests.put(url, json=data)
    if response.ok:
        st.success("Inventory updated successfully!")
    else:
        st.error("Failed to update inventory")

def delete_medicine(medicine_id):
    url = f"{API_BASE_URL}/medicines/{medicine_id}"
    response = requests.delete(url)
    if response.ok:
        st.success("Medicine deleted successfully!")
    else:
        st.error("Failed to delete medicine")

# CUSTOMERS
def get_customers():
    url = f"{API_BASE_URL}/customers"
    response = requests.get(url)
    if response.ok:
        return response.json()
    else:
        st.error("Failed to fetch customers")
        return []

def add_customer(name, email, phone):
    url = f"{API_BASE_URL}/customers"
    data = {"name": name, "email": email, "phone": phone}
    response = requests.post(url, json=data)
    if response.ok:
        st.success("Customer added successfully!")
    else:
        st.error("Failed to add customer")

def delete_customer(customer_id):
    url = f"{API_BASE_URL}/customers/{customer_id}"
    response = requests.delete(url)
    if response.ok:
        st.success("Customer deleted successfully!")
    else:
        st.error("Failed to delete customer")

# ORDERS
def get_orders(customer_id=None):
    url = f"{API_BASE_URL}/orders"
    if customer_id:
        url += f"?customer_id={customer_id}"
    response = requests.get(url)
    if response.ok:
        return response.json()
    else:
        st.error("Failed to fetch orders")
        return []

def add_order(customer_id, doctor_name, date_prescribed, date, total, status):
    url = f"{API_BASE_URL}/orders"
    data = {
        "customer_id": customer_id,
        "doctor_name": doctor_name,
        "date_prescribed": date_prescribed,
        "date": date,
        "total": total,
        "status": status
    }
    response = requests.post(url, json=data)
    if response.ok:
        st.success("Order added successfully!")
    else:
        st.error("Failed to add order")

def delete_order(order_id):
    url = f"{API_BASE_URL}/orders/{order_id}"
    response = requests.delete(url)
    if response.ok:
        st.success("Order deleted successfully!")
    else:
        st.error("Failed to delete order")

# -----------------------------
# Main App
# -----------------------------
def main():
    st.title("Medical Management System")

    # Sidebar navigation: select an action and an entity
    main_menu = st.sidebar.radio("Select Action", ["Add", "View", "Delete"])
    entity = st.sidebar.radio("Select Entity", ["Medicine", "Customer", "Order"])

    # -----------------------------
    # ADD Section
    # -----------------------------
    if main_menu == "Add":
        st.header(f"Add {entity}")
        if entity == "Medicine":
            with st.form("add_medicine_form"):
                name = st.text_input("Name")
                quantity = st.number_input("Quantity", min_value=1, value=1)
                price = st.number_input("Price", min_value=0.0, value=0.0, step=0.1)
                # Inventory status is not provided here; it defaults to "added"
                order_id = st.number_input("Order ID (enter 0 if none)", min_value=0, value=0)
                submitted = st.form_submit_button("Add Medicine")
                if submitted:
                    add_medicine(name, quantity, price, order_id)
                    try_rerun()
        elif entity == "Customer":
            with st.form("add_customer_form"):
                name = st.text_input("Name")
                email = st.text_input("Email")
                phone = st.text_input("Phone")
                submitted = st.form_submit_button("Add Customer")
                if submitted:
                    add_customer(name, email, phone)
                    try_rerun()
        elif entity == "Order":
            customers = get_customers()
            if customers:
                customer_options = {f"{c['name']} (ID: {c['id']})": c['id'] for c in customers}
                selected_customer = st.selectbox("Select Customer", list(customer_options.keys()))
                customer_id = customer_options[selected_customer]
            else:
                st.info("No customers available. Please add a customer first.")
                st.stop()
            with st.form("add_order_form"):
                doctor_name = st.text_input("Doctor Name")
                date_prescribed = st.text_input("Date Prescribed (YYYY-MM-DD)")
                order_date = st.text_input("Order Date (YYYY-MM-DD)")
                total = st.number_input("Total", min_value=0.0, value=0.0, step=0.1)
                status = st.selectbox("Status", ["pending", "completed", "cancelled"])
                submitted = st.form_submit_button("Add Order")
                if submitted:
                    add_order(customer_id, doctor_name, date_prescribed, order_date, total, status)
                    try_rerun()

    # -----------------------------
    # VIEW Section
    # -----------------------------
    elif main_menu == "View":
        st.header(f"View {entity}s")
        if entity == "Medicine":
            medicines = get_medicines()
            if medicines:
                for med in medicines:
                    st.write(f"ID: {med['id']}, Name: {med['name']}, Quantity: {med['quantity']}, Price: ${med['price']:.2f}, Inventory Status: {med['inventory_status']}")
                    # Provide a selectbox and update button for inventory status
                    new_status = st.selectbox("Update Inventory Status", ["added", "removed", "sold", "in stock", "expired"], key=f"status_{med['id']}")
                    if st.button("Update", key=f"update_{med['id']}"):
                        update_medicine_status(med['id'], new_status)
                        try_rerun()
            else:
                st.info("No medicines found.")
        elif entity == "Customer":
            customers = get_customers()
            st.table(customers)
        elif entity == "Order":
            orders = get_orders()
            st.table(orders)

    # -----------------------------
    # DELETE Section
    # -----------------------------
    elif main_menu == "Delete":
        st.header(f"Delete {entity}")
        if entity == "Medicine":
            medicines = get_medicines()
            if medicines:
                for med in medicines:
                    st.write(f"ID: {med['id']} - {med['name']} (Qty: {med['quantity']})")
                    if st.button(f"Delete Medicine {med['id']}", key=f"delete_med_{med['id']}"):
                        delete_medicine(med['id'])
                        try_rerun()
            else:
                st.info("No medicines to delete.")
        elif entity == "Customer":
            customers = get_customers()
            if customers:
                for cust in customers:
                    st.write(f"ID: {cust['id']} - {cust['name']} (Email: {cust['email']})")
                    if st.button(f"Delete Customer {cust['id']}", key=f"delete_cust_{cust['id']}"):
                        delete_customer(cust['id'])
                        try_rerun()
            else:
                st.info("No customers to delete.")
        elif entity == "Order":
            orders = get_orders()
            if orders:
                for order in orders:
                    st.write(f"ID: {order['id']} - Date: {order['date']} (Status: {order['status']})")
                    if st.button(f"Delete Order {order['id']}", key=f"delete_order_{order['id']}"):
                        delete_order(order['id'])
                        try_rerun()
            else:
                st.info("No orders to delete.")

if __name__ == '__main__':
    main()

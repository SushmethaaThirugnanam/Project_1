import streamlit as st
import pandas as pd
import pymysql

# connector
connection = pymysql.connect(
    host="localhost",
    user="root",
    password="root",
    database="bank"
)
cursor = connection.cursor()

# page title
st.set_page_config(page_title="BankSight Dashboard", layout="wide")

# table names and their respective columns as dictionary
tables = {
        "Customers": {
            "query": "SELECT * FROM BANK.CUSTOMERS",
            "filters": {
                "Customer_ID": "CUSTOMER_ID",
                "Name": "NAME",
                "Gender": "GENDER",
                "Age": "AGE",
                "City": "CITY",
                "Account Type": "ACCOUNT_TYPE",
                "Join Date": "JOIN_DATE"
            },
            "primary_key": "CUSTOMER_ID"
        },
        "Accounts": {
            "query": "SELECT * FROM BANK.ACCOUNTS",
            "filters": {
                "Customer_ID": "CUSTOMER_ID",
                "Account Balance": "ACCOUNT_BALANCE",
                "Last Update": "LAST_UPDATED"
            },
            "primary_key": "CUSTOMER_ID"
        },
        "Branches": {
            "query" : "SELECT * FROM BANK.BRANCHES",
            "filters":{
                "Branch_ID": "Branch_ID",
                "Branch_Name": "Branch_Name",
                "City": "City",
                "Manager_Name": "Manager_Name",
                "Toatal_employees": "Total_Employees",
                "Branch_Revenue": "Branch_Revenue",
                "Opening_Date": "Opening_Date",
                "Performance_Rating": "Performance_Rating"
            },
            "primary_key": "Branch_ID"
        },
        "Loans": {
            "query":"SELECT * FROM BANK.LOANS",
            "filters": {
                    "Loan_ID": "LOAN_ID",
                    "Customer_ID": "CUSTOMER_ID",
                    "Account_ID": "ACCOUNT_ID",
                    "Branch": "BRANCH",
                    "Loan_Type": "LOAN_TYPE",
                    "Loan_Amount": "LOAN_AMOUNT",
                    "Interest_Rate": "INTEREST_RATE",
                    "Loan_Term (Months)": "LOAN_TERM_MONTHS",
                    "Start_Date": "START_DATE",
                    "End_Date": "END_DATE",
                    "Loan_Status": "LOAN_STATUS"
                },
            "primary_key": "LOAN_ID"
            },
        "Credit_Cards" : {
            "query" : "SELECT * FROM BANK.CREDIT_CARDS",
            "filters": {
                    "Card_ID": "Card_ID",
                    "Customer_ID": "Customer_ID",
                    "Account_ID": "Account_ID",
                    "Branch": "Branch",
                    "Card_Number": "Card_Number",
                    "Card_Type": "Card_Type",
                    "Card_Network": "Card_Network",
                    "Credit_Limit": "Credit_Limit",
                    "Current_Balance": "Current_Balance",
                    "Issued_Date": "Issued_Date",
                    "Expiry_Date": "Expiry_Date",
                    "Status": "Status"
                    },
            "primary_key": "Card_ID"
            },
        "Transactions" : {
            "query" : "SELECT * FROM BANK.TRANSACTIONS",
            "filters": {
                    "Transaction_ID": "TXN_ID",
                    "Customer_ID": "CUSTOMER_ID",
                    "Transaction_Type": "TXN_TYPE",
                    "Amount": "AMOUNT",
                    "Transaction_Time": "TXN_TIME",
                    "Status": "STATUS"
                    },
            "primary_key": "TXN_ID"
            },
        "Support_Ticket" : {
            "query" : "SELECT * FROM BANK.SUPPORT_TICK",
            "filters" : {
                "Ticket_ID": "Ticket_ID",
                "Customer_ID": "Customer_ID",
                "Account_ID": "Account_ID",
                "Loan_ID": "Loan_ID",
                "Branch_Name": "Branch_Name",
                "Issue_Category": "Issue_Category",
                "Description": "Description",
                "Date_Opened": "Date_Opened",
                "Date_Closed": "Date_Closed",
                "Priority": "Priority",
                "Status": "Status",
                "Resolution_Remarks": "Resolution_Remarks",
                "Support_Agent": "Support_Agent",
                "Channel": "Channel",
                "Customer_Rating": "Customer_Rating"
                },
            "primary_key": "Ticket_ID"
            }
        }

# Analytic Questions and their queries
quetions = {
        "Q1 : How many customers exist per city, and what is their average account balance?" : 
            """SELECT 
	                C.CITY, 
                    COUNT(DISTINCT C.CUSTOMER_ID) AS Total_Customers,
                    ROUND(AVG(A.ACCOUNT_BALANCE),2) AS Average_Balance
                FROM CUSTOMERS C 
                JOIN ACCOUNTS A ON C.CUSTOMER_ID = A.CUSTOMER_ID 
                GROUP BY C.CITY
                ORDER BY Average_Balance DESC""",
        "Q2: Which account type (Savings, Current, Loan, etc.) holds the highest total balance?" :
            """SELECT 
	                C.ACCOUNT_TYPE 
                FROM CUSTOMERS C
                JOIN ACCOUNTS A ON C.CUSTOMER_ID = A.CUSTOMER_ID
                GROUP BY ACCOUNT_TYPE
                HAVING MAX(A.ACCOUNT_BALANCE)
                ORDER BY C.ACCOUNT_TYPE 
                LIMIT 1""",
        "Q3: Who are the top 10 customers by total account balance across all account types?" :
            """SELECT 
	            C.CUSTOMER_ID, 
                C.Name,
                ROUND(SUM(A.Account_Balance),2) AS Total_Balance 
            FROM ACCOUNTS A 
            JOIN CUSTOMERS C ON C.CUSTOMER_ID = A.CUSTOMER_ID
            GROUP BY C.CUSTOMER_ID
            ORDER BY Total_Balance DESC
            LIMIT 10""",
        "Q4: Which customers opened accounts in 2023 with a balance above ₹1,00,000?" :
            """SELECT 
	            C.CUSTOMER_ID,
                C.Name
            FROM CUSTOMERS C
            JOIN ACCOUNTS A ON C.CUSTOMER_ID = A.CUSTOMER_ID 
            WHERE YEAR(C.JOIN_DATE) = 2023 AND A.ACCOUNT_BALANCE > 100000;""",
        "Q5: What is the total transaction volume (sum of amounts) by transaction type?" :
            """SELECT 
	            TXN_TYPE, 
                ROUND(SUM(AMOUNT),2) AS TOTAL_AMOUNT 
            FROM TRANSACTIONS 
            GROUP BY TXN_TYPE
            ORDER BY TOTAL_AMOUNT DESC""",
        "Q6: How many failed transactions occurred for each transaction type?" :
            """SELECT 
	            TXN_TYPE, 
            COUNT(STATUS) AS Failed_Count 
            FROM TRANSACTIONS WHERE STATUS ="failed"
            GROUP BY TXN_TYPE
            ORDER BY Failed_Count DESC""",
        "Q7: What is the total number of transactions per transaction type?" :
            """SELECT 
	            TXN_TYPE,
	            COUNT(TXN_TYPE) AS Total_Transactions
            FROM TRANSACTIONS
            GROUP BY TXN_TYPE
            ORDER BY Total_Transactions DESC""",
        "Q8: Which accounts have 5 or more high-value transactions above ₹20,000?" :
            """SELECT 
                T.CUSTOMER_ID,
                C.Name,
                COUNT(T.CUSTOMER_ID) AS High_Value_Transactions
            FROM TRANSACTIONS T
            JOIN CUSTOMERS C ON C.CUSTOMER_ID = T.CUSTOMER_ID 
            WHERE AMOUNT > 20000
            GROUP BY T.CUSTOMER_ID 
            HAVING COUNT(T.CUSTOMER_ID) >= 5
            ORDER BY High_Value_Transactions DESC""",
        "Q9: What is the average loan amount and interest rate by loan type (Personal, Auto, Home, etc.)?" :
            """SELECT 
	            LOAN_TYPE, 
                ROUND(AVG(LOAN_AMOUNT),2) AS Loan_Amount, 
                ROUND(AVG(INTEREST_RATE),2) AS Interest_Rate 
            FROM LOANS
            GROUP BY LOAN_TYPE
            ORDER BY Interest_Rate DESC""",
        "Q10: Which customers currently hold more than one active or approved loan?" :
            """SELECT 
                    CUSTOMER_ID,
                    COUNT(*) AS Active_Approved_Loans
                FROM LOANS 
                WHERE LOAN_STATUS IN ('ACTIVE','APPROVED')
                GROUP BY CUSTOMER_ID
                HAVING Active_Approved_Loans>1
                ORDER BY Active_Approved_Loans DESC;""",
        "Q11: Who are the top 5 customers with the highest outstanding (non-closed) loan amounts?" :
            """SELECT 
	                CUSTOMER_ID 
                FROM LOANS 
                WHERE LOAN_STATUS NOT IN ('CLOSED')
                GROUP BY CUSTOMER_ID
                HAVING MAX(LOAN_AMOUNT) 
                ORDER BY MAX(LOAN_AMOUNT) desc
                LIMIT 5;""",
        "Q12: What is the average loan amount per branch?" :
            """SELECT 
	                BRANCH, 
	                ROUND(AVG(LOAN_AMOUNT)) AS AVG_AMOUNT 
                FROM LOANS 
                GROUP BY BRANCH
                ORDER BY AVG_AMOUNT DESC;""",
        "Q13: How many customers exist in each age group (e.g., 18–25, 26–35, etc.)?" :
            """SELECT 
	                CASE WHEN AGE BETWEEN 18 AND 25 THEN '18-25'
		                WHEN AGE BETWEEN 26 AND 35 THEN '26-35'
		                WHEN AGE BETWEEN 36 AND 45 THEN '36-45'
		                WHEN AGE BETWEEN 46 AND 55 THEN '46-55'
		                WHEN AGE BETWEEN 56 AND 69 THEN '56-69'
		                ELSE '70+'
	                END AS AGE_GROUP,
                    COUNT(CUSTOMER_ID) AS COUNT
                FROM CUSTOMERS
                GROUP BY AGE_GROUP
                ORDER BY AGE_GROUP""",
        "Q14: Which issue categories have the longest average resolution time?" :
            """SELECT 
	                ISSUE_CATEGORY 
                FROM SUPPORT_TICK 
                GROUP BY ISSUE_CATEGORY
                ORDER BY AVG(DATEDIFF(DATE_CLOSED , DATE_OPENED)) DESC
                LIMIT 1;""",
        "Q15: Which support agents have resolved the most critical tickets with high customer ratings (≥4)?" :
            """SELECT 
	                SUPPORT_AGENT 
                FROM SUPPORT_TICK 
                WHERE STATUS = 'Resolved' AND PRIORITY ='CRITICAL' AND CUSTOMER_RATING >= 4
                GROUP BY SUPPORT_AGENT"""
    }

#Navigation for the application
st.sidebar.title("Navigation")
page = st.sidebar.radio("Click🖱️on the section you want to travel",
                    ["Introduction👋",
                    "View Tables📋",
                    "Filter Data🔍",
                    "CRUD Operations✏️",
                    "Credit / Debit Simulation💳",
                    "Analytical Insights📈",
                    "About Creator🧑‍💻"])

# Introduction
if page == "Introduction👋":
    st.title("🏦 BankSight: Transaction Intelligence Dashboard")
    st.subheader("Project Overview")
    st.markdown("""
        **BankSight** is a financial analytics system built using Python, Streamlit, and Pandas.  
        It allows users to explore customer, account, transaction, loan, and support data,  
        perform CRUD operations, simulate deposits/withdrawals, and view analytical insights.
        """)
    st.subheader("Objectives")
    st.markdown("""
            - Understand customer & transaction behavior  
            - Detect anomalies and potential fraud  
            - Enable CRUD operations on all datasets""")
    
# Viewing Table
elif page == "View Tables📋":
    st.title("📋View Database Tables")
    tables_view = {
        "Customers": "BANK.CUSTOMERS",
        "Accounts": "BANK.ACCOUNTS",
        "Branches": "BANK.BRANCHES",
        "Loans": "BANK.LOANS",
        "Credit_Cards": "BANK.CREDIT_CARDS",
        "Transactions": "BANK.TRANSACTIONS",
        "Support_Ticket": "BANK.SUPPORT_TICK"
    }
    
    choice = st.selectbox("Select a table",list(tables_view.keys()))
    query = f"SELECT * FROM {tables_view[choice]}"
    df = pd.read_sql(query,connection)
    st.table(df)
    
# Viewing table using filters       
elif page == "Filter Data🔍":
    
    #function to return the filtered values
    def apply_filters(df, filters):
        for label, column in filters.items():
            values = st.multiselect(label, df[column].unique())
            if values:
                df = df[df[column].isin(values)]
        return df
    
    st.title("📋View Database Tables")
    choice = st.selectbox("Select a Table", list(tables.keys()))
    # Load table
    query = tables[choice]["query"]
    df = pd.read_sql(query, connection)

    # Apply filters dynamically
    filter_data = apply_filters(df, tables[choice]["filters"])

    # Show results
    st.dataframe(filter_data)
    
# Create, Read, Update and Delete Operations
elif page == "CRUD Operations✏️":
    st.title("CRUD Operations✏️")
    choice = st.selectbox("Select a table", list(tables.keys()))
    crud = st.radio("Click🖱️on the operation you want to perform",
                    ["View Table📋", 
                     "Add Record ➕", 
                     "Delete Record ❌", 
                     "Update Record 🔄"])
    #Again for Viewing table
    if crud == "View Table📋":
        query = tables[choice]["query"]
        df = pd.read_sql(query, connection)
        st.dataframe(df)
        
    #Adding a record
    if crud == "Add Record ➕":
        st.title("To add a record ➕")
        tables_config = tables[choice]
        inputs = {}
        for labels, columns in tables_config["filters"].items():
            if "date" in columns.lower():
                inputs[columns] = st.date_input(labels, key=f"{choice}_{columns}")
            elif "id" in columns.lower() or "number" in columns.lower():
                inputs[columns] = st.text_input(labels, key=f"{choice}_{columns}")
            elif "age" in columns.lower() or "rating" in columns.lower() or "balance" in columns.lower() or "amount" in columns.lower():
                inputs[columns] = st.number_input(labels, step=1, key=f"{choice}_{columns}")
            else :
                inputs[columns] = st.text_input(labels, key=f"{choice}_{columns}")
                
        if st.button(f"➕ Add {choice}"):
            try :
                cols = ", ".join(inputs.keys())
                placeholders = ", ".join(["%s"] * len(inputs))
                sql = f"INSERT INTO BANK.{choice.upper()}({cols}) VALUES ({placeholders})"
                cursor.execute(sql, tuple(inputs.values()))
                connection.commit()
                st.success(f"✅ {choice} record added successfully!")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
                
    # Deleting a record
    if crud =="Delete Record ❌":
        st.title("To Delete a Record")
        pri_key_col = tables[choice]["primary_key"]
        pri_key_value = st.text_input(f"Enter {pri_key_col} to delete", key=f"delete_{choice}_{pri_key_col}")
        if st.button(f"❌ DELETE in {choice}"):
            try :
                sql = f'DELETE FROM BANK.{choice.upper()} WHERE {pri_key_col} = %s'
                cursor.execute(sql, (pri_key_value,))
                connection.commit()
                st.success(f"✅ Record with {pri_key_col}={pri_key_value} deleted successfully from {choice}!")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
    
    # Updating the record
    elif crud == "Update Record 🔄":
        st.title("To Update a Record")
        table_config = tables[choice]
        pri_key_col = table_config["primary_key"]

        pri_key_value = st.text_input(f"Enter {pri_key_col} of record to update:",key=f"update_{choice}_{pri_key_col}_primary")

        update_col = st.selectbox("Select the column to update",list(table_config["filters"].values()))

        upd_value = st.text_input(f"Enter the {update_col} value",key=f"update_{choice}_{update_col}_value")

        # Handling numeric value by changing the string to float
        if update_col in ["ACCOUNT_BALANCE", "AMOUNT", "LOAN_AMOUNT", "INTEREST_RATE"]:
            if upd_value.strip() != "":
                try:
                    upd_value = float(upd_value)
                except ValueError:
                    st.error("⚠️ Please enter a valid numeric value.")
                    upd_value = None

        if st.button(f"🔄 Update {choice}"):
            if upd_value is None or pri_key_value.strip() == "":
                st.error("⚠️ Missing required values. Please fill all fields.")
            else:
                try:
                    sql = f"UPDATE BANK.{choice.upper()} SET {update_col} = %s WHERE {pri_key_col} = %s"
                    cursor.execute(sql, (upd_value, pri_key_value))
                    connection.commit()
                    st.success(f"✅ Record with {pri_key_col}={pri_key_value} updated successfully in {choice}!")
                except Exception as e:
                    st.error(f"⚠️ Error: {e}")
                       
elif page == "Credit / Debit Simulation💳":
    st.title("Credit / Debit Simulation💳")
    cust_id = st.text_input("Enter Customer ID")
    amt = st.number_input("Enter the Amount")
    options = st.radio("Click🖱️on the operation you want to perform",
                    ["Check Balance", 
                     "Deposit", 
                     "WithDraw"])
    button = st.button(f"Check Balance")
    sql = f"SELECT ACCOUNT_BALANCE FROM BANK.ACCOUNTS WHERE CUSTOMER_ID = %s"
    cursor.execute(sql, (cust_id,))
    result = cursor.fetchone() # stores values in tuple
    if options == "Check Balance":
        if button:
            try:
                if result:
                    st.success(f"Account Balance is ₹{result[0]:,.2f}")
                else:
                    st.warning("⚠️ No account found for this Customer ID")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
    if options == "Deposit":
        if button:
            try:
                balance = float(result[0])
                result_upd = balance + float(amt)
                if result:
                    st.success(f"Account Balance is ₹{result_upd:,.2f}")
                    sql = "UPDATE BANK.ACCOUNTS SET ACCOUNT_BALANCE = %s WHERE CUSTOMER_ID = %s"
                    cursor.execute(sql, (result_upd, cust_id))
                    connection.commit()
                else:
                    st.warning("⚠️ No account found for this Customer ID")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
    if options == "WithDraw":
        if button:
            try:
                balance = float(result[0])
                if balance >= float(amt) and balance >= 1000:
                    result_upd = balance - float(amt)
                    if result:
                        st.success(f"Account Balance is ₹{result_upd:,.2f}")
                        sql = "UPDATE BANK.ACCOUNTS SET ACCOUNT_BALANCE = %s WHERE CUSTOMER_ID = %s"
                        cursor.execute(sql, (result_upd, cust_id))
                        connection.commit()
                    else:
                        st.warning("⚠️ No account found for this Customer ID")
                else:
                    st.warning("Minimum Balance should be 1000")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
# Questions and Answers
elif page == "Analytical Insights📈":
    st.title("Analytical Insights📈")
    option = st.selectbox("Select the quetion", list(quetions.keys()))
    if option:
        query = quetions[option]
        cursor.execute(query)
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        res_table = pd.DataFrame(rows, columns = cols)
        st.dataframe(res_table, width=400, height=250)
        
# About Creator
else :
    st.title("About Creator🧑‍💻")
    st.markdown("""
                - Name : Sushmethaa Thirugnanam
                - Role : Associate Software Engineer in Accenture
                - Creative Interests:
                    - Designing polished, professional dashboards with stylish layouts and emoji-powered navigation
                    - Experimenting with advanced filters (multiselects, sliders) and Seaborn charts for richer insights
                    - Building user-friendly, visually engaging applications that go beyond functionality
                - Email : sushmithiru00@gmail.com""")
          
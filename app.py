import streamlit as st
from datetime import datetime
import json
import os
import re

DATA_FILE = "khataa_data.txt"
ITEM_FILE = "items_data.txt"
USER_FILE = "khataa_users.txt"

# --- Helper Functions for Data ---
def save_data():
    data = {
        "customers": st.session_state["customers"],
        "bills": st.session_state["bills"]
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2))

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            st.session_state["customers"] = [c for c in data.get("customers", []) if c.get("name")]
            st.session_state["bills"] = data.get("bills", [])
    except Exception:
        st.session_state["customers"] = []
        st.session_state["bills"] = []

def save_items():
    with open(ITEM_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(st.session_state["items"], ensure_ascii=False, indent=2))

def load_items():
    try:
        with open(ITEM_FILE, "r", encoding="utf-8") as f:
            st.session_state["items"] = [i for i in json.load(f) if i.get("name") and i.get("type")]
    except Exception:
        st.session_state["items"] = []

# --- Helper Functions for Users (Plain Text Password) ---
def check_login(username, password):
    try:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            for line in f:
                u, p = line.strip().split(",", 1)
                if u == username and p == password:
                    return True
    except Exception:
        pass
    return False

# --- Language Support (Simple Toggle) ---
if "lang" not in st.session_state:
    st.session_state["lang"] = "en"

def t(en, hi):
    return en if st.session_state["lang"] == "en" else hi

st.sidebar.selectbox(
    "Language / भाषा",
    options=["English", "हिन्दी"],
    index=0 if st.session_state["lang"] == "en" else 1,
    key="lang_select",
    on_change=lambda: st.session_state.update({"lang": "en" if st.session_state["lang_select"] == "English" else "hi"})
)

# --- Login State ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# --- Data Load on Start ---
if "data_loaded" not in st.session_state:
    load_data()
    load_items()
    st.session_state["data_loaded"] = True

# --- Login Page (Register option removed) ---
if not st.session_state["logged_in"]:
    st.title("JAINTRIAD")
    st.markdown("<h3 style='color:#444;'>Utensil & Electronics Business</h3>", unsafe_allow_html=True)
    # Images in center, with captions
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        pass
    with col2:
        st.image("husband.jpg", width=120)
        st.markdown("<div style='text-align:center;font-weight:bold'>Husband and Wife</div>", unsafe_allow_html=True)
        st.image("son.jpg", width=120)
        st.markdown("<div style='text-align:center;font-weight:bold'>Tarun Jain</div>", unsafe_allow_html=True)
    with col3:
        pass

    st.header(t("Login", "लॉगिन"))
    login_user = st.text_input(t("Username", "यूज़रनेम"), key="login_user")
    login_pass = st.text_input(t("Password", "पासवर्ड"), type="password", key="login_pass")
    if st.button(t("Login", "लॉगिन")):
        if check_login(login_user, login_pass):
            st.session_state["logged_in"] = True
            st.session_state["username"] = login_user
            st.success(t("Login successful!", "लॉगिन सफल!"))
            st.rerun()
        else:
            st.error(t("Invalid username or password.", "गलत यूज़रनेम या पासवर्ड।"))
    st.stop()

# --- Main App (after login) ---
st.title("JAINTRIAD")
st.markdown("<h3 style='color:#444;'>Utensil & Electronics Business</h3>", unsafe_allow_html=True)
st.sidebar.write(t(f"Logged in as: {st.session_state['username']}", f"लॉगिन: {st.session_state['username']}"))
if st.sidebar.button(t("Logout", "लॉगआउट")):
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.rerun()
    st.stop()

menu = st.sidebar.radio(
    t("Menu", "मेनू"),
    [t("Customers", "ग्राहक"), t("Items", "सामान"), t("Bills", "बिल"), t("Khaata", "खाता")]
)

# --- Customers ---
if menu == t("Customers", "ग्राहक"):
    st.header(t("Add Customer", "ग्राहक जोड़ें"))
    with st.form("add_customer"):
        name = st.text_input(t("Name", "नाम"))
        phone = st.text_input(t("Phone Number", "फोन नंबर"))
        email = st.text_input(t("Email", "ईमेल"))
        address = st.text_input(t("Address", "पता"))
        submitted = st.form_submit_button(t("Add", "जोड़ें"))
        if submitted:
            if not name.strip():
                st.warning(t("Name is required.", "नाम आवश्यक है।"))
            else:
                st.session_state["customers"].append({
                    "name": name.strip(), "phone": phone, "email": email, "address": address
                })
                save_data()
                st.success(t("Customer added!", "ग्राहक जुड़ गया!"))
                st.rerun()

    st.subheader(t("Search Customers", "ग्राहक खोजें"))
    q = st.text_input(t("Search by name/phone/email", "नाम/फोन/ईमेल से खोजें"), value="")
    for idx, c in enumerate(st.session_state["customers"]):
        if not q or q.lower() in c["name"].lower() or q in c["phone"] or q.lower() in c["email"].lower():
            col1, col2 = st.columns([5,1])
            with col1:
                st.write(f"{c['name']} | {c['phone']} | {c['email']} | {c['address']}")
            with col2:
                if st.button(t("Delete", "हटाएं"), key=f"delete_customer_{idx}"):
                    # Delete customer and their bills
                    del st.session_state["customers"][idx]
                    st.session_state["bills"] = [b for b in st.session_state["bills"] if b["customer"] != c["name"]]
                    save_data()
                    st.success(t("Customer deleted!", "ग्राहक हटा दिया गया!"))
                    st.rerun()
            with st.expander(t("Show Details & Past Bills", "विवरण और पिछले बिल")):
                st.write(f"**{t('Name','नाम')}:** {c['name']}")
                st.write(f"**{t('Phone','फोन')}:** {c['phone']}")
                st.write(f"**{t('Email','ईमेल')}:** {c['email']}")
                st.write(f"**{t('Address','पता')}:** {c['address']}")
                cust_bills = [b for b in st.session_state["bills"] if b["customer"] == c["name"]]
                st.write(f"**{t('Total Bills','कुल बिल')}:** {len(cust_bills)}")
                for b in cust_bills:
                    st.write(f"- {b['date']} | ₹{b['total']} | {b['paid']}")
                cust_txt = f"{t('Name','नाम')}: {c['name']}\n{t('Phone','फोन')}: {c['phone']}\n{t('Email','ईमेल')}: {c['email']}\n{t('Address','पता')}: {c['address']}\n\n{t('Past Bills','पिछले बिल')}:\n"
                for b in cust_bills:
                    cust_txt += f"- {b['date']} | ₹{b['total']} | {b['paid']}\n"
                st.download_button(
                    t("Download Details & Bills", "विवरण और बिल डाउनलोड करें"),
                    cust_txt,
                    file_name=f"{c['name']}_details.txt",
                    key=f"cust_{c['name']}_{idx}_details"
                )

# --- Items ---
elif menu == t("Items", "सामान"):
    st.header(t("Add Item", "सामान जोड़ें"))
    with st.form("add_item"):
        item_name = st.text_input(t("Item Name", "सामान का नाम"))
        item_type = st.text_input(t("Type/Variant", "प्रकार"))
        price = st.number_input(t("Price", "कीमत"), min_value=0.0, step=0.01)
        submitted = st.form_submit_button(t("Add", "जोड़ें"))
        if submitted:
            if not item_name.strip() or not item_type.strip():
                st.warning(t("Name and Type are required.", "नाम और प्रकार आवश्यक हैं।"))
            else:
                st.session_state["items"].append({
                    "name": item_name.strip(), "type": item_type.strip(), "price": price
                })
                save_items()
                st.success(t("Item added!", "सामान जुड़ गया!"))
                st.rerun()

    st.subheader(t("All Items", "सभी सामान"))
    item_search = st.text_input(t("Search Items by Name/Type", "नाम/प्रकार से सामान खोजें"), value="", key="item_search")
    filtered_items = [
        (idx, i) for idx, i in enumerate(st.session_state["items"])
        if not item_search or item_search.lower() in i["name"].lower() or item_search.lower() in i["type"].lower()
    ]
    for idx, i in filtered_items:
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        with col1:
            st.write(f"{i['name']} | {i['type']} | ₹{i['price']}")
        with col2:
            new_price = st.number_input(
                t("Update Price", "कीमत बदलें"),
                min_value=0.0,
                step=0.01,
                value=float(i['price']),
                key=f"update_price_{idx}"
            )
        with col3:
            if st.button(t("Save Price", "कीमत सेव करें"), key=f"save_price_{idx}"):
                st.session_state["items"][idx]["price"] = new_price
                save_items()
                st.success(t("Price updated!", "कीमत अपडेट हो गई!"))
                st.rerun()
        with col4:
            if st.button(t("Delete", "हटाएं"), key=f"delete_item_{idx}"):
                st.session_state["items"].pop(idx)
                save_items()
                st.success(t("Item deleted!", "सामान हटा दिया गया!"))
                st.rerun()

# --- Bills ---
elif menu == t("Bills", "बिल"):
    st.header(t("Generate Bill", "बिल बनाएं"))
    bill_download_data = None
    bill_download_name = ""
    bill_download_key = ""
    valid_customers = [c for c in st.session_state["customers"] if c.get("name")]
    valid_items = [i for i in st.session_state["items"] if i.get("name") and i.get("type")]
    if len(valid_customers) == 0 or len(valid_items) == 0:
        st.info(t("Add customers and items first.", "पहले ग्राहक और सामान जोड़ें।"))
    else:
        cust = st.selectbox(
            t("Select Customer", "ग्राहक चुनें"),
            [c["name"] for c in valid_customers]
        )
        item_names = [f"{i['name']} ({i['type']})" for i in valid_items]
        selected_items = st.multiselect(
            t("Select Items", "सामान चुनें"),
            item_names,
            key="bill_selected_items"
        )
        qty_dict = {}
        for idx, sel in enumerate(selected_items):
            safe_key = re.sub(r'\W+', '_', sel) + f"_{idx}"
            qty = st.number_input(
                f"{t('Quantity for','मात्रा')}: {sel}",
                min_value=1, max_value=100, value=1, key=f"qty_{safe_key}"
            )
            qty_dict[sel] = qty
        paid = st.selectbox(t("Paid Status", "भुगतान स्थिति"), [t("Paid", "भुगतान"), t("Unpaid", "अदायगी")], key="bill_paid_status")
        if st.button(t("Generate Bill", "बिल बनाएं"), key="generate_bill_btn"):
            if not selected_items:
                st.warning(t("Please select at least one item.", "कम से कम एक सामान चुनें।"))
            elif any(qty_dict[sel] < 1 for sel in selected_items):
                st.warning(t("Please enter quantity for all items (minimum 1).", "हर सामान की मात्रा कम से कम 1 डालें।"))
            else:
                bill_items = []
                total = 0
                for sel in selected_items:
                    for i in valid_items:
                        item_label = f"{i['name']} ({i['type']})"
                        if sel == item_label:
                            qty = qty_dict[sel]
                            bill_items.append({
                                "name": i["name"],
                                "type": i["type"],
                                "price": i["price"],
                                "qty": qty,
                                "subtotal": i["price"] * qty
                            })
                            total += i["price"] * qty
                bill = {
                    "customer": cust,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "items": bill_items,
                    "total": total,
                    "paid": paid
                }
                st.session_state["bills"].append(bill)
                save_data()
                st.success(t("Bill generated!", "बिल बन गया!"))
                st.write(f"**{t('Customer','ग्राहक')}:** {cust}")
                st.write(f"**{t('Date','तारीख')}:** {bill['date']}")
                st.write("**Items:**")
                for b in bill_items:
                    st.write(f"- {b['name']} ({b['type']}) x {b['qty']} = ₹{b['subtotal']}")
                st.write(f"**{t('Total','कुल')}: ₹{total}**")
                st.write(f"**{t('Status','स्थिति')}: {paid}**")
                bill_txt = f"{t('Customer','ग्राहक')}: {cust}\n{t('Date','तारीख')}: {bill['date']}\n{t('Items','सामान')}:\n"
                for b in bill_items:
                    bill_txt += f"- {b['name']} ({b['type']}) x {b['qty']} = ₹{b['subtotal']}\n"
                bill_txt += f"{t('Total','कुल')}: ₹{total}\n{t('Status','स्थिति')}: {paid}\n"
                bill_download_data = bill_txt
                bill_download_name = f"{cust}_{bill['date'].replace(':','-').replace(' ','_')}_bill.txt"
                bill_download_key = f"bill_{cust}_{bill['date']}"
                st.download_button(
                    t("Download This Bill", "यह बिल डाउनलोड करें"),
                    bill_download_data,
                    file_name=bill_download_name,
                    key=bill_download_key
                )

    st.subheader(t("All Bills", "सभी बिल"))
    if st.session_state["bills"]:
        st.download_button(
            t("Download All Bills (JSON)", "सभी बिल डाउनलोड करें (JSON)"),
            json.dumps(st.session_state["bills"], ensure_ascii=False, indent=2),
            file_name="all_bills.json",
            key="all_bills_json"
        )
    for idx, b in enumerate(st.session_state["bills"]):
        st.write(f"{b['customer']} | {b['date']} | ₹{b['total']} | {b['paid']}")
        bill_txt = f"{t('Customer','ग्राहक')}: {b['customer']}\n{t('Date','तारीख')}: {b['date']}\n{t('Items','सामान')}:\n"
        for item in b["items"]:
            qty = item.get("qty", 1)
            subtotal = item.get("subtotal", item["price"] * qty)
            bill_txt += f"- {item['name']} ({item['type']}) x {qty} = ₹{subtotal}\n"
        bill_txt += f"{t('Total','कुल')}: ₹{b['total']}\n{t('Status','स्थिति')}: {b['paid']}\n"
        st.download_button(
            t("Download Bill", "बिल डाउनलोड करें"),
            bill_txt,
            file_name=f"{b['customer']}_{b['date'].replace(':','-').replace(' ','_')}_bill.txt",
            key=f"allbills_{b['customer']}_{b['date']}_{idx}"
        )

# --- Khaata (Ledger) ---
elif menu == t("Khaata", "खाता"):
    st.header(t("Customer Ledger", "ग्राहक खाता"))
    st.subheader(t("Select Customer", "ग्राहक चुनें"))
    cust_names = [c["name"] for c in st.session_state["customers"] if c.get("name")]
    if not cust_names:
        st.info(t("No customers found.", "कोई ग्राहक नहीं मिला।"))
    else:
        selected_cust = st.selectbox(t("Customer", "ग्राहक"), cust_names)
        bills = [b for b in st.session_state["bills"] if b["customer"] == selected_cust]
        total_due = sum(b["total"] for b in bills if b["paid"] == t("Unpaid", "अदायगी"))
        total_paid = sum(b["total"] for b in bills if b["paid"] == t("Paid", "भुगतान"))
        st.write(f"**{t('Total Bills','कुल बिल')}:** {len(bills)}")
        st.write(f"**{t('Total Paid','कुल भुगतान')}: ₹{total_paid}**")
        st.write(f"**{t('Total Due','कुल बकाया')}: ₹{total_due}**")
        st.subheader(t("All Bills for this Customer", "इस ग्राहक के सभी बिल"))
        for idx, b in enumerate(bills):
            st.write(f"{b['date']} | ₹{b['total']} | {b['paid']}")
            bill_txt = f"{t('Customer','ग्राहक')}: {b['customer']}\n{t('Date','तारीख')}: {b['date']}\n{t('Items','सामान')}:\n"
            for item in b["items"]:
                qty = item.get("qty", 1)
                subtotal = item.get("subtotal", item["price"] * qty)
                bill_txt += f"- {item['name']} ({item['type']}) x {qty} = ₹{subtotal}\n"
            bill_txt += f"{t('Total','कुल')}: ₹{b['total']}\n{t('Status','स्थिति')}: {b['paid']}\n"
            st.download_button(
                t("Download Bill", "बिल डाउनलोड करें"),
                bill_txt,
                file_name=f"{b['customer']}_{b['date'].replace(':','-').replace(' ','_')}_bill.txt",
                key=f"khaata_{b['customer']}_{b['date']}_{idx}"
            )

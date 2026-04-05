import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Budget Tracker",
    page_icon="💰",
    layout="wide"
)

# ── FILE PATHS ─────────────────────────────────────────────────────────────────
DATA_DIR = "data"
CREDIT_CSV = os.path.join(DATA_DIR, "credit.csv")
DEBIT_CSV = os.path.join(DATA_DIR, "debit.csv")
LEARNED_FILE = os.path.join(DATA_DIR, "learned_merchants.json")
CONFIRMED_FILE = os.path.join(DATA_DIR, "confirmed_transactions.json")
BUDGET_FILE = os.path.join(DATA_DIR, "budget_settings.json")

# ── SPENDING CATEGORIES ────────────────────────────────────────────────────────
SPENDING_CATEGORIES = [
    "☕ Coffee",
    "⛽ Gas",
    "🛒 Groceries",
    "🍔 Eating Out",
    "🚗 Car & Maintenance",
    "👟 Shopping & Clothes",
    "🎮 Subscriptions",
    "✈️ Travel",
    "🕌 Donations",
    "💈 Personal Care",
    "🏠 Rent",
    "📱 Phone",
    "🚗 Insurance",
    "🧺 Laundry",
    "💸 Splitting Bills",
    "🏧 ATM Cash",
    "❓ Other"
]

# ── INCOME CATEGORIES ──────────────────────────────────────────────────────────
INCOME_CATEGORIES = [
    "💼 Paystub / Direct Deposit",
    "📨 E-Transfer Received",
    "💳 Refund",
    "🏦 Other Income"
]

ALL_CATEGORIES = SPENDING_CATEGORIES + INCOME_CATEGORIES

# ── MERCHANT RULES (spending) ──────────────────────────────────────────────────
MERCHANT_RULES = {
    "TIM HORTONS": "☕ Coffee",
    "STARBUCKS": "☕ Coffee",
    "PETRO-CANADA": "⛽ Gas",
    "ESSO": "⛽ Gas",
    "CANADIAN TIRE GAS": "⛽ Gas",
    "NORTH ATLANTIC": "⛽ Gas",
    "CIRCLE K": "⛽ Gas",
    "IRVING": "⛽ Gas",
    "SOBEYS": "🛒 Groceries",
    "WAL-MART": "🛒 Groceries",
    "WALMART": "🛒 Groceries",
    "FIVE GUYS": "🍔 Eating Out",
    "OSMOW": "🍔 Eating Out",
    "GRILLEOPATRA": "🍔 Eating Out",
    "SUN SUSHI": "🍔 Eating Out",
    "BURGER KING": "🍔 Eating Out",
    "CASABLANCA": "🍔 Eating Out",
    "DESPACITO BAKERY": "🍔 Eating Out",
    "PERSEPOLIS": "🍔 Eating Out",
    "DOORDASH": "🍔 Eating Out",
    "UBER EATS": "🍔 Eating Out",
    "UBEREATS": "🍔 Eating Out",
    "PUR SIMPLE": "🍔 Eating Out",
    "ON THE ROCKS": "🍔 Eating Out",
    "MR. LUBE": "🚗 Car & Maintenance",
    "FOOT LOCKER": "👟 Shopping & Clothes",
    "PLAYSTATION": "🎮 Subscriptions",
    "APPLE.COM/BILL": "🎮 Subscriptions",
    "GOOGLE": "🎮 Subscriptions",
    "YOUTUBE": "🎮 Subscriptions",
    "AIR CAN": "✈️ Travel",
    "EXPEDIA": "✈️ Travel",
    "ICNA": "🕌 Donations",
    "BARBER": "💈 Personal Care",
    "1949 BARBER": "💈 Personal Care",
    "KOODO": "📱 Phone",
    "BELAIR": "🚗 Insurance",
    "PAYRANGE": "🧺 Laundry",
    "UBER CANADA/UBERTRIP": "🚗 Car & Maintenance",
}

# ── INCOME RULES (auto-categorize money coming IN) ────────────────────────────
INCOME_RULES = {
    "VALE CANADA":        "💼 Paystub / Direct Deposit",
    "PAYROLL":            "💼 Paystub / Direct Deposit",
    "DIRECT DEPOSIT":     "💼 Paystub / Direct Deposit",
    "INTERAC E-TRANSFER": "📨 E-Transfer Received",
    "E-TRANSFER":         "📨 E-Transfer Received",
    "INTERAC":            "📨 E-Transfer Received",
    "REFUND":             "💳 Refund",
    "REMBOURS":           "💳 Refund",
    "TAX REFUND":         "💳 Refund",
    "CRA":                "🏦 Other Income",
    "GST":                "🏦 Other Income",
    "DEPOSIT":            "🏦 Other Income",
}

# ── HELPER FUNCTIONS ───────────────────────────────────────────────────────────

def load_json(filepath, default):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return default

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def parse_date(date_str):
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(str(date_str).strip(), fmt)
        except ValueError:
            continue
    return None

def make_month_fields(parsed_date):
    if parsed_date:
        return parsed_date.strftime("%Y-%m"), parsed_date.strftime("%B %Y")
    return "Unknown", "Unknown"

def categorize_merchant(description, learned):
    desc_upper = description.upper()
    for merchant, category in learned.items():
        if merchant.upper() in desc_upper:
            return category
    for keyword, category in MERCHANT_RULES.items():
        if keyword.upper() in desc_upper:
            return category
    return None

def categorize_income(description, learned):
    desc_upper = description.upper()
    for merchant, category in learned.items():
        if merchant.upper() in desc_upper and category in INCOME_CATEGORIES:
            return category
    for keyword, category in INCOME_RULES.items():
        if keyword.upper() in desc_upper:
            return category
    return None

def is_credit_card_payment(description):
    keywords = ["INTERNET TRANSFER", "PAYMENT THANK YOU", "PAIEMEN T MERCI", "FULFILL REQUEST"]
    desc_upper = description.upper()
    return any(k in desc_upper for k in keywords)

def make_txn(date_str, desc, amount, account, direction):
    parsed = parse_date(date_str)
    mk, ml = make_month_fields(parsed)
    prefix = "cc" if account == "Credit Card" else "dbt"
    dir_tag = "in" if direction == "in" else "out"
    return {
        "date": date_str,
        "parsed_date": parsed,
        "month_key": mk,
        "month_label": ml,
        "description": desc,
        "amount": float(amount),
        "account": account,
        "direction": direction,
        "id": f"{prefix}_{dir_tag}_{date_str}_{desc[:20]}_{amount}"
    }

def extract_etransfer_name(description):
    """Extract person name from CIBC e-transfer description strings.
    
    Handles formats like:
      - 'Internet Banking E-TRANSFER 105875311732 jeff'
      - 'Internet Banking E-TRANSFER 011605211323 AHMED ABDELRAHIM'
      - 'INTERAC E-TFR FROM JOHN SMITH'
      - 'SEND E-TFR TO JANE DOE'
    """
    import re
    desc = description.strip()

    # Format 1: E-TRANSFER <big number> <name>
    # Matches 'Internet Banking E-TRANSFER 011605211323 AHMED ABDELRAHIM'
    match = re.search(r"E-TRANSFER\s+\d{6,}\s+(.+)", desc, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        # Remove any trailing reference codes (all-digit chunks at end)
        name = re.sub(r"\s+\d{4,}\s*$", "", name).strip()
        if name:
            return name.title()

    # Format 2: E-TFR <big number> <name>
    match = re.search(r"E-TFR\s+\d{6,}\s+(.+)", desc, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        name = re.sub(r"\s+\d{4,}\s*$", "", name).strip()
        if name:
            return name.title()

    # Format 3: E-TFR FROM <name> or E-TRANSFER FROM <name>
    match = re.search(r"E-?(?:TRANSFER|TFR)\s+FROM\s+(.+)", desc, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        name = re.sub(r"\s+\d{4,}\s*$", "", name).strip()
        if name:
            return name.title()

    # Format 4: SEND E-TFR TO <name> or SEND E-TRANSFER TO <name>
    match = re.search(r"SEND\s+E-?(?:TRANSFER|TFR)\s+TO\s+(.+)", desc, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        name = re.sub(r"\s+\d{4,}\s*$", "", name).strip()
        if name:
            return name.title()

    return None

def is_etransfer(description):
    """Check if a transaction is an e-transfer."""
    desc_upper = description.upper()
    return any(k in desc_upper for k in ["E-TRANSFER", "E-TFR", "INTERAC"])

def load_transactions():
    transactions = []

    # ── Credit Card ────────────────────────────────────────────────────────
    # Col C = charges (money OUT), Col D = refunds (money IN)
    if os.path.exists(CREDIT_CSV):
        credit_df = pd.read_csv(CREDIT_CSV, header=None,
                                names=["date", "description", "debit", "credit", "card"])
        for _, row in credit_df.iterrows():
            desc = str(row["description"]).strip()
            if is_credit_card_payment(desc):
                continue
            amount_out = row["debit"] if pd.notna(row["debit"]) else 0
            if float(amount_out) > 0:
                transactions.append(make_txn(row["date"], desc, amount_out, "Credit Card", "out"))
            amount_in = row["credit"] if pd.notna(row["credit"]) else 0
            if float(amount_in) > 0:
                transactions.append(make_txn(row["date"], desc, amount_in, "Credit Card", "in"))

    # ── Chequing ───────────────────────────────────────────────────────────
    # Col C = money OUT, Col D = money IN
    if os.path.exists(DEBIT_CSV):
        debit_df = pd.read_csv(DEBIT_CSV, header=None,
                               names=["date", "description", "debit", "credit"])
        for _, row in debit_df.iterrows():
            desc = str(row["description"]).strip()
            if is_credit_card_payment(desc):
                continue
            amount_out = row["debit"] if pd.notna(row["debit"]) else 0
            if float(amount_out) > 0:
                transactions.append(make_txn(row["date"], desc, amount_out, "Chequing", "out"))
            amount_in = row["credit"] if pd.notna(row["credit"]) else 0
            if float(amount_in) > 0:
                transactions.append(make_txn(row["date"], desc, amount_in, "Chequing", "in"))

    return transactions

# ── LOAD STATE ─────────────────────────────────────────────────────────────────
learned          = load_json(LEARNED_FILE, {})
confirmed        = load_json(CONFIRMED_FILE, {})
budget           = load_json(BUDGET_FILE, {})
all_transactions = load_transactions()

# ── CATEGORIZE ALL TRANSACTIONS ────────────────────────────────────────────────
pending     = []
categorized = []

for txn in all_transactions:
    txn_id = txn["id"]
    if txn_id in confirmed:
        txn["category"] = confirmed[txn_id]["category"]
        categorized.append(txn)
        continue

    if txn["direction"] == "out":
        category = categorize_merchant(txn["description"], learned)
    else:
        category = categorize_income(txn["description"], learned)

    if category:
        txn["category"] = category
        categorized.append(txn)
    else:
        txn["category"] = "⏳ Pending"
        pending.append(txn)

# ── DISCOVER MONTHS ────────────────────────────────────────────────────────────
all_month_keys = {}
for txn in all_transactions:
    mk = txn["month_key"]
    ml = txn["month_label"]
    if mk != "Unknown":
        all_month_keys[mk] = ml

sorted_months = sorted(all_month_keys.keys(), reverse=True)
month_labels  = [all_month_keys[mk] for mk in sorted_months]

# ── NAVIGATION ─────────────────────────────────────────────────────────────────
st.sidebar.title("💰 Budget Tracker")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", [
    "📊 Dashboard",
    "⏳ Pending Review",
    "📁 Transactions",
    "⚙️ Settings"
])

if pending:
    st.sidebar.warning(f"{len(pending)} transactions need review")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
if page == "⚙️ Settings":
    st.title("⚙️ Settings")
    st.write("Set your income, fixed bills, and spending budgets.")

    with st.form("budget_form"):
        st.subheader("💵 Income")
        income = st.number_input("Monthly Income ($)", min_value=0.0,
                                  value=float(budget.get("income", 0)), step=100.0)

        st.subheader("🏠 Fixed Bills")
        rent      = st.number_input("Rent ($)",      min_value=0.0, value=float(budget.get("rent", 0)),      step=10.0)
        phone     = st.number_input("Phone ($)",     min_value=0.0, value=float(budget.get("phone", 0)),     step=10.0)
        insurance = st.number_input("Insurance ($)", min_value=0.0, value=float(budget.get("insurance", 0)), step=10.0)

        st.subheader("📊 Spending Budgets")
        coffee        = st.number_input("☕ Coffee ($)",             min_value=0.0, value=float(budget.get("☕ Coffee", 0)),             step=10.0)
        gas           = st.number_input("⛽ Gas ($)",                min_value=0.0, value=float(budget.get("⛽ Gas", 0)),                step=10.0)
        groceries     = st.number_input("🛒 Groceries ($)",          min_value=0.0, value=float(budget.get("🛒 Groceries", 0)),          step=10.0)
        eating_out    = st.number_input("🍔 Eating Out ($)",         min_value=0.0, value=float(budget.get("🍔 Eating Out", 0)),         step=10.0)
        car           = st.number_input("🚗 Car & Maintenance ($)",  min_value=0.0, value=float(budget.get("🚗 Car & Maintenance", 0)),  step=10.0)
        shopping      = st.number_input("👟 Shopping & Clothes ($)", min_value=0.0, value=float(budget.get("👟 Shopping & Clothes", 0)), step=10.0)
        subscriptions = st.number_input("🎮 Subscriptions ($)",      min_value=0.0, value=float(budget.get("🎮 Subscriptions", 0)),      step=10.0)
        travel        = st.number_input("✈️ Travel ($)",             min_value=0.0, value=float(budget.get("✈️ Travel", 0)),             step=10.0)
        donations     = st.number_input("🕌 Donations ($)",          min_value=0.0, value=float(budget.get("🕌 Donations", 0)),          step=10.0)
        personal_care = st.number_input("💈 Personal Care ($)",      min_value=0.0, value=float(budget.get("💈 Personal Care", 0)),      step=10.0)
        laundry       = st.number_input("🧺 Laundry ($)",            min_value=0.0, value=float(budget.get("🧺 Laundry", 0)),            step=10.0)
        other         = st.number_input("❓ Other ($)",              min_value=0.0, value=float(budget.get("❓ Other", 0)),              step=10.0)

        submitted = st.form_submit_button("💾 Save Settings")
        if submitted:
            budget = {
                "income": income, "rent": rent, "phone": phone, "insurance": insurance,
                "☕ Coffee": coffee, "⛽ Gas": gas, "🛒 Groceries": groceries,
                "🍔 Eating Out": eating_out, "🚗 Car & Maintenance": car,
                "👟 Shopping & Clothes": shopping, "🎮 Subscriptions": subscriptions,
                "✈️ Travel": travel, "🕌 Donations": donations,
                "💈 Personal Care": personal_care, "🧺 Laundry": laundry, "❓ Other": other,
            }
            save_json(BUDGET_FILE, budget)
            st.success("✅ Settings saved!")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PENDING REVIEW
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⏳ Pending Review":
    st.title("⏳ Pending Review")

    if not pending:
        st.success("✅ All transactions have been reviewed!")
    else:
        st.write(f"**{len(pending)} transactions** need your attention across all months.")
        st.markdown("---")

        for txn in pending:
            col1, col2, col3, col4 = st.columns([2, 3, 1, 2])
            with col1:
                st.write(f"📅 {txn['date']}")
                direction_label = "⬆️ Money In" if txn["direction"] == "in" else "⬇️ Money Out"
                st.caption(f"{txn['account']} · {txn['month_label']} · {direction_label}")
            with col2:
                st.write(txn['description'])
            with col3:
                prefix = "+" if txn["direction"] == "in" else "-"
                st.write(f"**{prefix}${txn['amount']:.2f}**")
            with col4:
                cat_options = INCOME_CATEGORIES if txn["direction"] == "in" else SPENDING_CATEGORIES
                selected = st.selectbox("Category", cat_options, key=f"cat_{txn['id']}")
                remember = st.checkbox("Remember this merchant", value=True, key=f"rem_{txn['id']}")
                if st.button("✅ Confirm", key=f"btn_{txn['id']}"):
                    confirmed[txn['id']] = {
                        "category": selected,
                        "date": txn['date'],
                        "description": txn['description'],
                        "amount": txn['amount'],
                        "account": txn['account']
                    }
                    save_json(CONFIRMED_FILE, confirmed)
                    if remember:
                        merchant_name = txn['description'].split(" ")[0]
                        learned[merchant_name] = selected
                        save_json(LEARNED_FILE, learned)
                        st.success("✅ Confirmed & learned!")
                    else:
                        st.success("✅ Confirmed!")
                    st.rerun()
            st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: TRANSACTIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📁 Transactions":
    st.title("📁 All Transactions")

    # ── CSV Upload Section ─────────────────────────────────────────────────
    with st.expander("📤 Upload New Transactions", expanded=not sorted_months):
        st.write("Upload your CIBC CSV exports here. New transactions will be merged with existing data.")
        col_up1, col_up2 = st.columns(2)

        with col_up1:
            st.markdown("**💳 Credit Card CSV**")
            credit_upload = st.file_uploader("Credit card transactions", type="csv",
                                              key="credit_upload", label_visibility="collapsed")
            if credit_upload is not None:
                try:
                    new_df = pd.read_csv(credit_upload, header=None,
                                         names=["date", "description", "debit", "credit", "card"])
                    if os.path.exists(CREDIT_CSV):
                        existing_df = pd.read_csv(CREDIT_CSV, header=None,
                                                   names=["date", "description", "debit", "credit", "card"])
                        merged_df = pd.concat([existing_df, new_df]).drop_duplicates()
                    else:
                        merged_df = new_df
                    merged_df.to_csv(CREDIT_CSV, index=False, header=False)
                    st.success(f"✅ Credit card CSV uploaded — {len(new_df)} rows merged.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error reading file: {e}")

        with col_up2:
            st.markdown("**🏦 Chequing CSV**")
            debit_upload = st.file_uploader("Chequing transactions", type="csv",
                                             key="debit_upload", label_visibility="collapsed")
            if debit_upload is not None:
                try:
                    new_df = pd.read_csv(debit_upload, header=None,
                                          names=["date", "description", "debit", "credit"])
                    if os.path.exists(DEBIT_CSV):
                        existing_df = pd.read_csv(DEBIT_CSV, header=None,
                                                   names=["date", "description", "debit", "credit"])
                        merged_df = pd.concat([existing_df, new_df]).drop_duplicates()
                    else:
                        merged_df = new_df
                    merged_df.to_csv(DEBIT_CSV, index=False, header=False)
                    st.success(f"✅ Chequing CSV uploaded — {len(new_df)} rows merged.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error reading file: {e}")

    st.markdown("---")

    if not sorted_months:
        st.info("No transactions yet — upload your CSV files above to get started.")
    else:
        tabs = st.tabs(month_labels)

        for i, (tab, month_key) in enumerate(zip(tabs, sorted_months)):
            with tab:
                month_txns = [t for t in categorized if t["month_key"] == month_key]

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    filter_dir = st.selectbox("Direction",
                                               ["All", "⬇️ Money Out", "⬆️ Money In"],
                                               key=f"tdir_{month_key}")
                with col_b:
                    all_cats = ["All"] + SPENDING_CATEGORIES + INCOME_CATEGORIES
                    filter_cat = st.selectbox("Category", all_cats, key=f"tcat_{month_key}")
                with col_c:
                    filter_account = st.selectbox("Account",
                                                   ["All", "Credit Card", "Chequing"],
                                                   key=f"tacc_{month_key}")

                display = month_txns
                if filter_dir == "⬇️ Money Out":
                    display = [t for t in display if t["direction"] == "out"]
                elif filter_dir == "⬆️ Money In":
                    display = [t for t in display if t["direction"] == "in"]
                if filter_cat != "All":
                    display = [t for t in display if t.get("category") == filter_cat]
                if filter_account != "All":
                    display = [t for t in display if t["account"] == filter_account]

                if display:
                    df = pd.DataFrame(display)
                    df = df.sort_values("date", ascending=False)
                    df["dir_display"] = df["direction"].map({"in": "⬆️ In", "out": "⬇️ Out"})

                    edit_df = df[["date", "description", "amount", "dir_display", "category", "account", "id"]].copy()
                    edit_df = edit_df.rename(columns={
                        "date": "Date",
                        "description": "Description",
                        "amount": "Amount ($)",
                        "dir_display": "Direction",
                        "category": "Category",
                        "account": "Account",
                        "id": "_id"
                    })
                    edit_df = edit_df.set_index("_id")

                    edited = st.data_editor(
                        edit_df,
                        use_container_width=True,
                        key=f"editor_{month_key}",
                        column_config={
                            "Category": st.column_config.SelectboxColumn(
                                "Category",
                                options=SPENDING_CATEGORIES + INCOME_CATEGORIES,
                                required=True,
                            ),
                            "Date":        st.column_config.TextColumn("Date",        disabled=True),
                            "Description": st.column_config.TextColumn("Description", disabled=True),
                            "Amount ($)":  st.column_config.NumberColumn("Amount ($)", disabled=True, format="$%.2f"),
                            "Direction":   st.column_config.TextColumn("Direction",   disabled=True),
                            "Account":     st.column_config.TextColumn("Account",     disabled=True),
                        },
                        hide_index=True,
                    )

                    # Detect category changes and save
                    changed = False
                    for txn_id, row in edited.iterrows():
                        original = next((t for t in display if t["id"] == txn_id), None)
                        if original and row["Category"] != original.get("category"):
                            confirmed[txn_id] = {
                                "category": row["Category"],
                                "date": original["date"],
                                "description": original["description"],
                                "amount": original["amount"],
                                "account": original["account"],
                            }
                            changed = True
                    if changed:
                        save_json(CONFIRMED_FILE, confirmed)

                    total_in  = sum(t["amount"] for t in display if t["direction"] == "in")
                    total_out = sum(t["amount"] for t in display if t["direction"] == "out")
                    net = total_in - total_out
                    c1, c2, c3 = st.columns(3)
                    c1.metric("⬆️ Money In",  f"${total_in:,.2f}")
                    c2.metric("⬇️ Money Out", f"${total_out:,.2f}")
                    c3.metric("📊 Net", f"${net:,.2f}",
                              delta=f"${net:,.2f}" if net >= 0 else f"-${abs(net):,.2f}")
                else:
                    st.info("No transactions match your filters.")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Dashboard":
    st.title("📊 Dashboard")

    if not sorted_months:
        st.info("No transactions found. Upload your CSV files in the Transactions page to get started.")
    else:
        tabs = st.tabs(month_labels)

        for i, (tab, month_key) in enumerate(zip(tabs, sorted_months)):
            with tab:
                month_label       = all_month_keys[month_key]
                month_categorized = [t for t in categorized if t["month_key"] == month_key]
                month_pending     = [t for t in pending     if t["month_key"] == month_key]

                money_in_txns  = [t for t in month_categorized if t["direction"] == "in"]
                money_out_txns = [t for t in month_categorized if t["direction"] == "out"]

                total_money_in  = sum(t["amount"] for t in money_in_txns)
                total_money_out = sum(t["amount"] for t in money_out_txns)
                net_cash        = total_money_in - total_money_out
                pending_amount  = sum(t["amount"] for t in month_pending)

                # ── Cash Flow Summary ──────────────────────────────────────
                st.subheader("💵 Cash Flow This Month")
                col1, col2, col3 = st.columns(3)
                col1.metric("⬆️ Total Money In",  f"${total_money_in:,.2f}")
                col2.metric("⬇️ Total Money Out", f"${total_money_out:,.2f}")
                col3.metric("📊 Net",              f"${net_cash:,.2f}",
                            delta=f"${net_cash:,.2f}" if net_cash >= 0 else f"-${abs(net_cash):,.2f}")

                if month_pending:
                    st.warning(
                        f"⏳ ${pending_amount:,.2f} across {len(month_pending)} transactions "
                        f"still pending review — numbers above may be incomplete."
                    )

                st.markdown("---")

                # ── Money In Breakdown ─────────────────────────────────────
                st.subheader("⬆️ Money In Breakdown")
                income_by_cat = {}
                for txn in money_in_txns:
                    cat = txn.get("category", "🏦 Other Income")
                    income_by_cat[cat] = income_by_cat.get(cat, 0) + txn["amount"]

                if income_by_cat:
                    for cat, amt in sorted(income_by_cat.items(), key=lambda x: -x[1]):
                        pct = amt / total_money_in if total_money_in > 0 else 0
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{cat}** — ${amt:,.2f}")
                            st.progress(pct)
                        with col2:
                            st.metric("Amount", f"${amt:,.2f}")
                else:
                    st.info("No incoming money recorded yet for this month.")

                st.markdown("---")

                # ── Spending vs Budget ─────────────────────────────────────
                st.subheader("⬇️ Spending vs Budget")

                spending = {}
                for txn in money_out_txns:
                    cat = txn.get("category", "❓ Other")
                    spending[cat] = spending.get(cat, 0) + txn["amount"]

                fixed_bills = (float(budget.get("rent", 0)) +
                               float(budget.get("phone", 0)) +
                               float(budget.get("insurance", 0)))

                if fixed_bills > 0:
                    st.write(f"🏠 **Fixed Bills** (Rent + Phone + Insurance) — **${fixed_bills:,.2f}/mo**")
                    st.markdown("---")

                spend_cats = [c for c in SPENDING_CATEGORIES if c not in ["🏠 Rent", "📱 Phone", "🚗 Insurance"]]
                any_shown = False

                for cat in spend_cats:
                    spent    = spending.get(cat, 0)
                    budgeted = float(budget.get(cat, 0))
                    if spent == 0 and budgeted == 0:
                        continue
                    any_shown = True
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if budgeted > 0:
                            pct   = min(spent / budgeted, 1.0)
                            color = "🟢" if pct < 0.75 else "🟡" if pct < 1.0 else "🔴"
                            st.write(f"{color} **{cat}** — ${spent:,.2f} / ${budgeted:,.2f}")
                            st.progress(pct)
                        else:
                            st.write(f"⚪ **{cat}** — ${spent:,.2f} (no budget set)")
                    with col2:
                        if budgeted > 0:
                            remaining = budgeted - spent
                            if remaining >= 0:
                                st.metric("Remaining", f"${remaining:,.2f}")
                            else:
                                st.metric("Over budget", f"${abs(remaining):,.2f}",
                                          delta=f"-${abs(remaining):,.2f}")

                if not any_shown:
                    st.info("No categorized spending yet. Review pending transactions to see your breakdown.")

                st.markdown("---")

                # ── People & E-Transfers ───────────────────────────────────
                st.subheader("👥 People & E-Transfers")

                # Gather all e-transfer transactions for this month (categorized + pending)
                all_month_txns = month_categorized + month_pending
                etransfer_txns = [t for t in all_month_txns if is_etransfer(t["description"])]

                if not etransfer_txns:
                    st.info("No e-transfer transactions found for this month.")
                else:
                    # Group by person name
                    people = {}
                    unnamed = []
                    for txn in etransfer_txns:
                        name = extract_etransfer_name(txn["description"])
                        if not name:
                            unnamed.append(txn)
                            continue
                        if name not in people:
                            people[name] = {"sent": 0.0, "received": 0.0, "txns": []}
                        if txn["direction"] == "out":
                            people[name]["sent"] += txn["amount"]
                        else:
                            people[name]["received"] += txn["amount"]
                        people[name]["txns"].append(txn)

                    # Sort by total volume
                    sorted_people = sorted(people.items(),
                                           key=lambda x: x[1]["sent"] + x[1]["received"],
                                           reverse=True)

                    for name, data in sorted_people:
                        sent     = data["sent"]
                        received = data["received"]
                        net      = received - sent
                        net_label = f"+${net:,.2f}" if net >= 0 else f"-${abs(net):,.2f}"
                        net_color = "🟢" if net > 0 else "🔴" if net < 0 else "⚪"

                        with st.expander(f"👤 **{name}** — {net_color} Net {net_label}"):
                            c1, c2, c3 = st.columns(3)
                            c1.metric("⬆️ Received", f"${received:,.2f}")
                            c2.metric("⬇️ Sent",     f"${sent:,.2f}")
                            c3.metric("📊 Net",       net_label,
                                      delta=net_label if net >= 0 else net_label)

                            # Show individual transactions
                            txn_rows = []
                            for t in sorted(data["txns"], key=lambda x: x["date"], reverse=True):
                                prefix = "+$" if t["direction"] == "in" else "-$"
                                txn_rows.append({
                                    "Date": t["date"],
                                    "Description": t["description"],
                                    "Amount": f"{prefix}{t['amount']:,.2f}",
                                    "Account": t["account"],
                                })
                            st.dataframe(pd.DataFrame(txn_rows), use_container_width=True, hide_index=True)

                    if unnamed:
                        with st.expander(f"❓ Unrecognized e-transfers ({len(unnamed)})"):
                            st.caption("These look like e-transfers but the name couldn't be extracted.")
                            for t in unnamed:
                                st.write(f"• {t['date']} — {t['description']} — ${t['amount']:,.2f}")
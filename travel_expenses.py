import streamlit as st
import json
import os
from datetime import date, datetime

# --- Config ---
DATA_FILE = os.path.join(os.path.dirname(__file__), "travel_expenses_data.json")
PEOPLE = ["Stanley", "Ash", "Kia"]
CURRENCIES = ["HKD", "JPY"]

# --- Data persistence ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for rec in data:
                if isinstance(rec.get("date"), str):
                    rec["date"] = rec["date"]
            return data
    return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


# --- Session state init ---
if "expenses" not in st.session_state:
    st.session_state.expenses = load_data()
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# --- Page config ---
st.set_page_config(page_title="Japan Travel Expenses", page_icon="", layout="wide")

st.title("Japan Travel Expenses")
st.caption("Stanley / Ash / Kia")

# --- Sidebar: Add / Edit Expense ---
st.sidebar.header("Add / Edit Expense")

is_editing = st.session_state.edit_index is not None
edit_rec = (
    st.session_state.expenses[st.session_state.edit_index] if is_editing else None
)

with st.sidebar.form("expense_form", clear_on_submit=True):
    if is_editing:
        st.info(f"Editing record #{st.session_state.edit_index + 1}")

    expense_date = st.date_input(
        "Date",
        value=datetime.strptime(edit_rec["date"], "%Y-%m-%d").date()
        if is_editing
        else date.today(),
    )
    description = st.text_input(
        "Description", value=edit_rec["description"] if is_editing else ""
    )
    currency = st.selectbox(
        "Currency",
        CURRENCIES,
        index=CURRENCIES.index(edit_rec["currency"]) if is_editing else 0,
    )
    amount = st.number_input(
        "Amount",
        min_value=0.0,
        step=0.01 if currency == "HKD" else 1.0,
        format="%.2f" if currency == "HKD" else "%.0f",
        value=float(edit_rec["amount"]) if is_editing else 0.0,
    )
    paid_by = st.selectbox(
        "Paid by",
        PEOPLE,
        index=PEOPLE.index(edit_rec["paid_by"]) if is_editing else 0,
    )
    split_among = st.multiselect(
        "Split among",
        PEOPLE,
        default=edit_rec["split_among"] if is_editing else PEOPLE,
    )

    col_submit, col_cancel = st.columns(2)
    submitted = col_submit.form_submit_button(
        "Update" if is_editing else "Add Expense"
    )
    cancelled = col_cancel.form_submit_button("Cancel") if is_editing else False

    if submitted:
        if amount <= 0:
            st.error("Amount must be greater than 0.")
        elif not split_among:
            st.error("Select at least one person to split among.")
        elif not description.strip():
            st.error("Please enter a description.")
        else:
            record = {
                "date": str(expense_date),
                "description": description.strip(),
                "currency": currency,
                "amount": amount,
                "paid_by": paid_by,
                "split_among": split_among,
            }
            if is_editing:
                st.session_state.expenses[st.session_state.edit_index] = record
                st.session_state.edit_index = None
                st.success("Record updated!")
            else:
                st.session_state.expenses.append(record)
                st.success("Expense added!")
            save_data(st.session_state.expenses)
            st.rerun()

    if cancelled:
        st.session_state.edit_index = None
        st.rerun()

# --- Exchange rate sidebar ---
st.sidebar.markdown("---")
st.sidebar.header("Exchange Rate")
jpy_to_hkd = st.sidebar.number_input(
    "1 JPY = ? HKD", min_value=0.0001, value=0.055, step=0.001, format="%.4f"
)
st.sidebar.caption(f"1 HKD = {1/jpy_to_hkd:,.1f} JPY")

# --- Helpers: currency conversion ---
def to_hkd(amount, currency):
    if currency == "HKD":
        return amount
    return amount * jpy_to_hkd


def to_jpy(amount, currency):
    if currency == "JPY":
        return amount
    return amount / jpy_to_hkd


# --- Main: Expense Records ---
tab_records, tab_balance = st.tabs(["Expense Records", "Balance"])

with tab_records:
    if not st.session_state.expenses:
        st.info("No expenses recorded yet. Use the sidebar to add one.")
    else:
        # Summary row
        total_hkd = sum(
            to_hkd(e["amount"], e["currency"]) for e in st.session_state.expenses
        )
        total_jpy = sum(
            e["amount"] for e in st.session_state.expenses if e["currency"] == "JPY"
        )
        total_hkd_only = sum(
            e["amount"] for e in st.session_state.expenses if e["currency"] == "HKD"
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Total (converted to HKD)", f"HKD {total_hkd:,.2f}")
        c2.metric("Total HKD expenses", f"HKD {total_hkd_only:,.2f}")
        c3.metric("Total JPY expenses", f"JPY {total_jpy:,.0f}")

        st.markdown("---")

        # Column headers
        hdr = st.columns([1, 2, 1.5, 1.2, 1.2, 1.2, 1.5, 0.5, 0.5])
        hdr[0].write("**Date**")
        hdr[1].write("**Item**")
        hdr[2].write("**Original**")
        hdr[3].write("**HKD**")
        hdr[4].write("**JPY**")
        hdr[5].write("**Paid by**")
        hdr[6].write("**Split**")

        for i, exp in enumerate(st.session_state.expenses):
            with st.container():
                cols = st.columns([1, 2, 1.5, 1.2, 1.2, 1.2, 1.5, 0.5, 0.5])

                amt = exp["amount"]
                cur = exp["currency"]
                equiv_hkd = to_hkd(amt, cur)
                equiv_jpy = to_jpy(amt, cur)

                cols[0].write(exp["date"])
                cols[1].write(f"**{exp['description']}**")

                # Original currency and amount
                if cur == "HKD":
                    cols[2].write(f"HK$ {amt:,.2f}")
                else:
                    cols[2].write(f"JPY {amt:,.0f}")

                cols[3].write(f"HK$ {equiv_hkd:,.2f}")
                cols[4].write(f"JPY {equiv_jpy:,.0f}")
                cols[5].write(f"**{exp['paid_by']}**")
                cols[6].write(f"{', '.join(exp['split_among'])}")

                if cols[7].button("Edit", key=f"edit_{i}"):
                    st.session_state.edit_index = i
                    st.rerun()

                if cols[8].button("Del", key=f"del_{i}"):
                    st.session_state.expenses.pop(i)
                    save_data(st.session_state.expenses)
                    if st.session_state.edit_index == i:
                        st.session_state.edit_index = None
                    st.rerun()

# --- Balance Calculation ---
with tab_balance:
    if not st.session_state.expenses:
        st.info("No expenses to calculate balance.")
    else:
        st.subheader("Balance Summary (in HKD)")
        st.caption(f"Exchange rate: 1 JPY = {jpy_to_hkd} HKD")

        # Calculate how much each person paid and owes
        paid = {p: 0.0 for p in PEOPLE}
        owes = {p: 0.0 for p in PEOPLE}

        for exp in st.session_state.expenses:
            amount_hkd = to_hkd(exp["amount"], exp["currency"])
            paid[exp["paid_by"]] += amount_hkd
            share = amount_hkd / len(exp["split_among"])
            for person in exp["split_among"]:
                owes[person] += share

        # Net balance = paid - owes (positive means others owe you)
        net = {p: paid[p] - owes[p] for p in PEOPLE}

        # Display per-person summary
        col_headers = st.columns(4)
        col_headers[0].write("**Person**")
        col_headers[1].write("**Total Paid**")
        col_headers[2].write("**Fair Share**")
        col_headers[3].write("**Net Balance**")

        for p in PEOPLE:
            cols = st.columns(4)
            cols[0].write(f"**{p}**")
            cols[1].write(f"HKD {paid[p]:,.2f}")
            cols[2].write(f"HKD {owes[p]:,.2f}")
            if net[p] > 0.01:
                cols[3].markdown(f":green[+HKD {net[p]:,.2f}] (is owed)")
            elif net[p] < -0.01:
                cols[3].markdown(f":red[HKD {net[p]:,.2f}] (owes)")
            else:
                cols[3].write("Settled")

        st.markdown("---")
        st.subheader("Settlement Plan")
        st.caption("Minimal transfers to settle all debts")

        # Greedy settlement algorithm
        debtors = []
        creditors = []
        for p in PEOPLE:
            if net[p] < -0.01:
                debtors.append([p, -net[p]])
            elif net[p] > 0.01:
                creditors.append([p, net[p]])

        debtors.sort(key=lambda x: x[1], reverse=True)
        creditors.sort(key=lambda x: x[1], reverse=True)

        settlements = []
        di, ci = 0, 0
        while di < len(debtors) and ci < len(creditors):
            transfer = min(debtors[di][1], creditors[ci][1])
            if transfer > 0.01:
                settlements.append(
                    (debtors[di][0], creditors[ci][0], transfer)
                )
            debtors[di][1] -= transfer
            creditors[ci][1] -= transfer
            if debtors[di][1] < 0.01:
                di += 1
            if creditors[ci][1] < 0.01:
                ci += 1

        if settlements:
            for debtor, creditor, amt in settlements:
                st.write(f"**{debtor}** pays **{creditor}**: **HKD {amt:,.2f}**")
        else:
            st.success("All settled! No transfers needed.")

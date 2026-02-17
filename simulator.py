import streamlit as st
import pandas as pd
import os

# --- Page Configuration ---
st.set_page_config(page_title="VRF Load Calculator Pro", layout="wide", page_icon="🏢")

# Local storage file
SAVE_FILE = "project_inventory.csv"

# --- Data Management Functions ---
def save_data(rooms_list):
    pd.DataFrame(rooms_list).to_csv(SAVE_FILE, index=False)

def load_data():
    if os.path.exists(SAVE_FILE):
        try:
            return pd.read_csv(SAVE_FILE).to_dict('records')
        except:
            return []
    return []

# --- Initialize Session State ---
if 'rooms' not in st.session_state:
    st.session_state.rooms = load_data()
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

# --- Header & Branding ---
st.title("🏗️ VRF Professional Project Planner")
st.markdown(f"**Lead Designer:** Mubashira Hamid Aziz")
st.write("Precision Load Calculation & Multi-ODU System Design")
st.divider()

# --- Sidebar ---
st.sidebar.header("📋 System Controls")
st.sidebar.info("Assign rooms to floors and ODU groups for detailed load balancing.")
if st.sidebar.button("🗑️ Clear All Project Data"):
    st.session_state.rooms = []
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
    st.rerun()

# --- Main Interface Tabs ---
tab1, tab2, tab3 = st.tabs(["🔹 Step 1: Unit Inventory", "🔸 Step 2: System Analysis", "📄 Step 3: Technical Report"])

# --- TAB 1: INPUTS & MANAGEMENT ---
with tab1:
    edit_idx = st.session_state.edit_index
    default_val = st.session_state.rooms[edit_idx] if edit_idx is not None else None

    with st.form("input_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            r_name = st.text_input("Room Name/ID", value=default_val["Room Name"] if default_val else "")
            floor_list = ["Basement", "Ground Floor", "1st Floor", "2nd Floor", "3rd Floor", "Roof Top"]
            f_idx = floor_list.index(default_val["Floor"]) if (default_val and "Floor" in default_val) else 1
            floor = st.selectbox("Floor Level", floor_list, index=f_idx)
            odu_id = st.text_input("ODU Group ID", value=default_val["ODU Group"] if default_val else "ODU-1")
        
        with col2:
            length = st.number_input("Length (ft)", value=20.0)
            width = st.number_input("Width (ft)", value=15.0)
            f_val = int(default_val["Factor"]) if (default_val and "Factor" in default_val) else 70
            c_factor = st.slider("Climate Factor (BTU/sqft)", 50, 160, f_val)
        
        with col3:
            people = st.number_input("Occupancy", value=2)
            safety = st.slider("Safety Margin %", 0, 20, 10)
            btn_label = "✅ Update Unit" if edit_idx is not None else "➕ Add Unit"
            submit = st.form_submit_button(btn_label)

        if submit:
            area = length * width
            total_btu = ((area * c_factor) + (people * 500)) * (1 + (safety/100))
            new_entry = {
                "Room Name": r_name if r_name else "Unnamed",
                "Floor": floor,
                "ODU Group": odu_id,
                "Factor": c_factor,
                "Area": area,
                "TR": round(total_btu / 12000, 2)
            }
            if edit_idx is not None:
                st.session_state.rooms[edit_idx] = new_entry
                st.session_state.edit_index = None
            else:
                st.session_state.rooms.append(new_entry)
            save_data(st.session_state.rooms)
            st.rerun()

    if st.session_state.rooms:
        st.write("### 📋 Current Project Inventory")
        for idx, room in enumerate(st.session_state.rooms):
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 1, 1])
            c1.write(f"**{room['Room Name']}** ({room.get('Floor', 'N/A')})")
            c2.write(f"ID: {room.get('ODU Group', 'N/A')}")
            c3.write(f"{room.get('TR', 0.0)} TR")
            if c4.button("📝", key=f"edit_{idx}"):
                st.session_state.edit_index = idx
                st.rerun()
            if c5.button("❌", key=f"del_{idx}"):
                st.session_state.rooms.pop(idx)
                save_data(st.session_state.rooms)
                st.rerun()

# --- TAB 2: ANALYSIS ---
with tab2:
    if st.session_state.rooms:
        df = pd.DataFrame(st.session_state.rooms)
        diversity = st.slider("Diversity Factor (%)", 50, 130, 100)
        
        st.subheader("📊 Load Distribution Chart")
        floor_sum = df.groupby("Floor")["TR"].sum()
        st.bar_chart(floor_sum)
        
        st.subheader("🔌 Outdoor Unit Capacity (Calculated)")
        for g in sorted(df["ODU Group"].unique()):
            g_tr = df[df["ODU Group"] == g]["TR"].sum()
            final_cap = round(g_tr / (diversity/100), 2)
            st.info(f"**{g}:** Total Connected = {g_tr:.2f} TR | **Required ODU = {final_cap} TR**")
    else:
        st.warning("Add units to see analysis.")

# --- TAB 3: REPORT ---
with tab3:
    if st.session_state.rooms:
        df_final = pd.DataFrame(st.session_state.rooms)
        st.subheader("Project Documentation")
        st.table(df_final)
        
        csv_file = df_final.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Technical Data (CSV)", data=csv_file, file_name="VRF_Design_Report.csv")
    else:
        st.info("No data available.")

st.caption(f"© 2026 VRF Design Tool | Lead Engineer: Mubashira Hamid Aziz")
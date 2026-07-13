import streamlit as st
import pandas as pd
import numpy as np
import pickle

st.set_page_config(page_title="NutriBudget AI", layout="wide")

st.markdown("""
    <style>
        .title { color: #1E3A8A; font-size: 38px; font-weight: 800; text-align: center; }
        .card { background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 20px; border-radius: 12px; margin-bottom: 15px; }
        .alert-box { background-color: #FEF2F2; color: #991B1B; border-left: 5px solid #EF4444; padding: 10px; margin-bottom: 10px; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# --- LOAD ARTIFACTS SAFELY USING BINARY READING ('rb') ---
@st.cache_resource
def load_data_and_models():
    # Load dataset
    dataset = pd.read_csv('nutribudget_dataset.csv')
    
    # Explicitly read as binary mode 'rb' to fix pickle loading crash
    with open('model.pkl', 'rb') as f: 
        model = pickle.load(f)
    with open('scaler.pkl', 'rb') as f: 
        scaler = pickle.load(f)
    with open('encoder.pkl', 'rb') as f: 
        encoder = pickle.load(f)
        
    return dataset, model, scaler, encoder

try:
    df, model, scaler, encoder = load_data_and_models()
except Exception as e:
    st.error(f"Initialization Error: {e}")
    st.info("Please ensure model.pkl, scaler.pkl, and encoder.pkl are uploaded to the root repository folder.")
    st.stop()

st.markdown("<div class='title'>🛒 NutriBudget AI</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#64748B;'>AI-Powered Grocery Budget Planner, Nutrition Analyzer & Smart Shopping Assistant</p>", unsafe_allow_html=True)

st.markdown("---")

# Left Column: Build Cart | Right Column: AI Analysis Insight Dashboard
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 🛍️ Build Your Grocery Cart")
    unique_items = df['Product_Name'].unique().tolist()
    selected_items = st.multiselect("Choose Items to Add to Cart:", unique_items, default=unique_items[:3])

if not selected_items:
    st.warning("Please select at least one item to analyze your cart!")
else:
    cart_df = df[df['Product_Name'].isin(selected_items)].drop_duplicates(subset=['Product_Name'])
    
    total_bill = cart_df['Price'].sum()
    avg_health_score = int(cart_df['Health_Score'].mean())
    total_sugar = cart_df['Sugar'].sum()
    total_sodium = cart_df['Sodium'].sum()
    
    monthly_current = cart_df['Monthly_Cost'].sum()
    monthly_expected_saving = (cart_df['Price'] - cart_df['Alternative_Price']).sum() * 3 

    with col2:
        st.markdown("### 📊 Live Analytics Dashboard Summary")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Estimated Cart Bill", f"₹{total_bill}")
        m2.metric("Nutrition Health Index", f"{avg_health_score}/100")
        m3.metric("Projected Monthly Savings", f"₹{monthly_expected_saving}")
        
        st.markdown("#### 🚨 Health Alerts Matrix")
        alerts_found = False
        if total_sugar > 30:
            st.markdown("<div class='alert-box'>⚠️ <b>High Sugar Content Alert:</b> Excessive high-fructose components found in checkout bundle.</div>", unsafe_allow_html=True)
            alerts_found = True
        if total_sodium > 1500:
            st.markdown("<div class='alert-box'>⚠️ <b>High Sodium Content Alert:</b> Elevated blood-pressure liability traces found.</div>", unsafe_allow_html=True)
            alerts_found = True
        if not alerts_found:
            st.success("✅ Vitals Clean! No adverse metabolic risk components detected in this checkout configuration.")

        st.markdown("#### 💡 AI Smart Product Swaps & Substitutions")
        for _, row in cart_df.iterrows():
            if row['Healthy'] == 'No':
                st.info(f"🔄 **Swap Found:** Replace **{row['Product_Name']}** with healthier **{row['Alternative_Product']}** (Save approx ₹{int(row['Price']-row['Alternative_Price'])}!)")

        st.markdown("#### 🏃 AI Metabolic Exercise Prescription")
        walk_time = int(cart_df['Calories'].mean() / 5)
        st.write(f"* To optimize processing of this food selection, we suggest a brisk **{walk_time} Minute Walk** or **{int(walk_time*0.6)} Minutes of Cycling** today.")
        
        report_data = f"NutriBudget AI Bill Report Summary\nTotal Price: ₹{total_bill}\nHealth Index Score: {avg_health_score}"
        st.download_button("📥 Download PDF Text Report", data=report_data, file_name="shopping_audit.txt")

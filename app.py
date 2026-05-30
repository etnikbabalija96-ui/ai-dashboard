import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Config ---
st.set_page_config(
    page_title="AI Data Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .block-container { padding-top: 2rem; }
    h1 { color: #00d4ff; font-size: 2.5rem !important; }
    h2, h3 { color: #ffffff; }
    .stSuccess { background-color: #1a3a2a; }
    .stInfo { background-color: #1a2a3a; }
    .metric-card {
        background-color: #1e2130;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        border: 1px solid #2d3250;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #00d4ff;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #aaaaaa;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("# 📊 AI Data Dashboard")
st.markdown("*Upload a CSV and instantly explore, clean, and visualize your data.*")
st.divider()

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/combo-chart.png", width=80)
    st.title("Dashboard Controls")
    st.divider()
    uploaded_file = st.file_uploader("📁 Upload CSV file", type=["csv"])
    st.divider()
    st.markdown("### 🛠️ About")
    st.markdown("Built with Python, Streamlit & Plotly")

# --- Main Content ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    original_shape = df.shape

    # --- Metric Cards ---
    st.subheader("📋 Dataset Overview")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{df.shape[0]:,}</div>
            <div class="metric-label">Total Rows</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{df.shape[1]}</div>
            <div class="metric-label">Columns</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        missing = df.isnull().sum().sum()
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{missing:,}</div>
            <div class="metric-label">Missing Values</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        dupes = df.duplicated().sum()
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value">{dupes:,}</div>
            <div class="metric-label">Duplicate Rows</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # --- Tabs ---
    tab1, tab2, tab3 = st.tabs(["🔍 Data & Cleaning", "📈 Statistics", "📊 Charts"])

    # =====================
    # TAB 1 - Data Cleaning
    # =====================
    with tab1:
        st.subheader("🔍 Raw Data Preview")
        st.dataframe(df.head(20), use_container_width=True)

        st.subheader("🧹 Data Cleaning Tools")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Remove Duplicate Rows")
            st.info(f"Found **{dupes}** duplicate rows in your dataset.")
            if dupes > 0:
                if st.button("🗑️ Remove Duplicates"):
                    df = df.drop_duplicates()
                    st.success(f"✅ Removed {dupes} duplicates! Dataset now has {df.shape[0]} rows.")

        with col2:
            st.markdown("#### Handle Missing Values")
            st.info(f"Found **{missing}** missing values across all columns.")
            if missing > 0:
                strategy = st.selectbox("Choose strategy", [
                    "Drop rows with missing values",
                    "Fill numbers with column mean",
                    "Fill numbers with column median",
                    "Fill with 0"
                ])
                if st.button("✨ Apply Strategy"):
                    if strategy == "Drop rows with missing values":
                        df = df.dropna()
                        st.success(f"✅ Dropped rows. Dataset now has {df.shape[0]} rows.")
                    elif strategy == "Fill numbers with column mean":
                        df = df.fillna(df.mean(numeric_only=True))
                        st.success("✅ Filled missing values with column means.")
                    elif strategy == "Fill numbers with column median":
                        df = df.fillna(df.median(numeric_only=True))
                        st.success("✅ Filled missing values with column medians.")
                    elif strategy == "Fill with 0":
                        df = df.fillna(0)
                        st.success("✅ Filled all missing values with 0.")

        st.subheader("🗂️ Column Info")
        col_info = pd.DataFrame({
            "Type": df.dtypes,
            "Missing Values": df.isnull().sum(),
            "Missing %": (df.isnull().sum() / len(df) * 100).round(2),
            "Unique Values": df.nunique()
        })
        st.dataframe(col_info, use_container_width=True)

        st.subheader("📥 Export Cleaned Data")
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Cleaned CSV",
            data=csv,
            file_name="cleaned_data.csv",
            mime="text/csv"
        )

    # =====================
    # TAB 2 - Statistics
    # =====================
    with tab2:
        st.subheader("📈 Summary Statistics")
        st.dataframe(df.describe(), use_container_width=True)

    # =====================
    # TAB 3 - Charts
    # =====================
    with tab3:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        categorical_cols = df.select_dtypes(include="object").columns.tolist()

        if numeric_cols:
            st.markdown("#### 📊 Distribution")
            selected_num = st.selectbox("Pick a numeric column", numeric_cols)
            fig1 = px.histogram(df, x=selected_num, nbins=30,
                               title=f"Distribution of {selected_num}",
                               color_discrete_sequence=["#00d4ff"])
            fig1.update_layout(paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
                              font_color="white")
            st.plotly_chart(fig1, use_container_width=True)

        if len(numeric_cols) >= 2:
            st.markdown("#### 🔵 Scatter Plot")
            col1, col2 = st.columns(2)
            with col1:
                x_axis = st.selectbox("X axis", numeric_cols, index=0)
            with col2:
                y_axis = st.selectbox("Y axis", numeric_cols, index=1)
            color_col = None
            if categorical_cols:
                color_col = st.selectbox("Color by (optional)", ["None"] + categorical_cols)
                color_col = None if color_col == "None" else color_col
            fig2 = px.scatter(df, x=x_axis, y=y_axis, color=color_col,
                             title=f"{x_axis} vs {y_axis}")
            fig2.update_layout(paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
                              font_color="white")
            st.plotly_chart(fig2, use_container_width=True)

        if categorical_cols:
            st.markdown("#### 📊 Category Breakdown")
            selected_cat = st.selectbox("Pick a categorical column", categorical_cols)
            value_counts = df[selected_cat].value_counts().reset_index()
            value_counts.columns = [selected_cat, "count"]
            fig3 = px.bar(value_counts.head(20), x=selected_cat, y="count",
                         title=f"Top values in {selected_cat}",
                         color_discrete_sequence=["#00d4ff"])
            fig3.update_layout(paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
                              font_color="white")
            st.plotly_chart(fig3, use_container_width=True)

        if len(numeric_cols) >= 2:
            st.markdown("#### 🔥 Correlation Heatmap")
            corr = df[numeric_cols].corr()
            fig4 = px.imshow(corr, text_auto=True, title="Correlation Matrix",
                            color_continuous_scale="blues")
            fig4.update_layout(paper_bgcolor="#0e1117", font_color="white")
            st.plotly_chart(fig4, use_container_width=True)

else:
    st.markdown("""
    <div style='text-align: center; padding: 80px 0;'>
        <h2 style='color: #00d4ff;'>👈 Upload a CSV file to get started</h2>
        <p style='color: #aaaaaa; font-size: 1.1rem;'>
            Your data never leaves your machine. Everything runs locally.
        </p>
    </div>
    """, unsafe_allow_html=True)
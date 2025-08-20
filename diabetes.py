import pandas as pd
import plotly.express as px
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt
import plotly.express as px

# Function definition
def big_metric(label, value, emoji, bg_color="#dff0d8"):
    st.markdown(f"""
        <div style="padding: 10px; border-radius: 50px; background-color: {bg_color}; 
                    text-align: center; width: 550px; margin: auto; 
                    margin-bottom: 20px; font-size: 20px; border: 2px solid #3c763d; 
                    color: #3c763d; box-shadow: 2px 2px 8px rgba(0,0,0,0.2);">
            {emoji} <strong>{label}</strong><br>
            <span style="font-weight: bold; color: #3c763d;">{value}</span>
        </div>
    """, unsafe_allow_html=True)


st.set_page_config(page_title="Diabetes Dashboard", layout="wide")
#st.set_page_config(page_title="Diabetes", layout="centered")

diabetes = pd.read_csv("C:\\Users\\Pushp\\OneDrive\\My Data\\Learning\\diabetes_data.csv")

# === Title of the page
st.markdown(f"""
    <div style=" background-color: #f0f4f8;
                padding: 20px 10px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
                margin-bottom: 30px;">
        <h1 style=" color: #2c3e50;
                    font-size: 36px;
                    font-weight: 700;
                    margin: 0;">
            Diabetes Dashbboard
        </h1> 
        <div style="text-align: right; 
                    font-size: 20px; 
                    font-weight: 600; 
                    margin-right: 20px;">
        </div>
    </div>
    """, unsafe_allow_html=True)



# === Preprocess Data ===
# Recode Gender and Smoking
diabetes['Gender'] = diabetes['Gender'].map({1: 'Male', 0: 'Female'})
diabetes['Gender'] = diabetes['Gender'].fillna('Unknown')
diabetes['Smoking'] = diabetes['Smoking'].map({1: 'Yes', 0: 'No'})

# Define BMI categories
def categorize_bmi(bmi):
    if pd.isna(bmi):
        return "Missing"
    elif bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal Weight"
    elif 24.9 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obesity"

diabetes['BMI_Category'] = diabetes['BMI'].apply(categorize_bmi)

# === Sidebar Filters ===
st.sidebar.title("Filters")
gender_filter = st.sidebar.multiselect(
    "Select Gender", 
    options=diabetes['Gender'].unique(), 
    default=diabetes['Gender'].unique()
)

# === Filter Data ===
filtered_diabetes = diabetes[diabetes['Gender'].isin(gender_filter)]


# === Total N in Oval Shape at Top ===
# Inside main app
total_n = len(filtered_diabetes)
big_metric("Total N", total_n, emoji="👥")
st.divider()

# === Layout Columns ===
col1, spacer, col3 = st.columns([1, 0.3, 1])

# === Gender Count Table ===
with col1:
    st.subheader("Gender Count")
    gender_counts = filtered_diabetes['Gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    st.table(gender_counts)
    st.markdown("""""")
    # === Age Distribution Line Plot by Gender (Grouped) ===
    st.subheader("Age Distribution by Gender (Age Groups)")

    # Define age bins and labels
    age_bins = [18, 25, 35, 45, 55, 60, 100]
    age_labels = ["18-25", "26-35", "36-45", "46-55", "56-60", "61+"]

    # Create new age group column
    filtered_diabetes['Age_Group'] = pd.cut(
        filtered_diabetes['Age'],
        bins=age_bins,
        labels=age_labels,
        right=True,
        include_lowest=True
    )

    # Group by Age Group and Gender
    age_grouped = filtered_diabetes.groupby(['Age_Group', 'Gender']).size().reset_index(name='Count')

    # Line plot
    age_line_fig = px.line(
        age_grouped,
        x='Age_Group',
        y='Count',
        color='Gender',
        markers=True,
        title='Age Group Distribution by Gender',
        color_discrete_map={
        'Male': '#1f77b4',    # blue
        'Female': '#ff69b4',  # pink
        'Unknown': '#999999'  # gray (optional if present)
    }
)
    
    age_line_fig.update_layout(
        xaxis_title='Age Group',
        yaxis_title='Count',
        template='simple_white'
    )

    st.plotly_chart(age_line_fig, use_container_width=True)

    # === BMI Category Summary Table ===
    st.markdown("---")
    #st.subheader("BMI Category Summary Table")

    bmi_summary = {
        "BMI Category": ["Underweight", "Normal Weight", "Overweight", "Obesity"],
        "Count": [
            (filtered_diabetes['BMI'] < 18.5).sum(),
            ((filtered_diabetes['BMI'] >= 18.5) & (filtered_diabetes['BMI'] < 24.9)).sum(),
            ((filtered_diabetes['BMI'] >= 24.9) & (filtered_diabetes['BMI'] < 29.9)).sum(),
            (filtered_diabetes['BMI'] >= 29.9).sum()
        ]
    }
    bmi_table = pd.DataFrame(bmi_summary)
    #st.table(bmi_table)
    # === BMI Category Pie Chart ===
    st.subheader("BMI Category Distribution (Pie Chart)")

    bmi_pie_fig = px.pie(
        bmi_table,
        names='BMI Category',
        values='Count',
        title='BMI Category Distribution',
        color_discrete_sequence=px.colors.qualitative.Set3  # Optional: use a custom color palette
    )

    bmi_pie_fig.update_traces(textposition='inside', textinfo='percent+label')
    bmi_pie_fig.update_layout(showlegend=True)

    st.plotly_chart(bmi_pie_fig, use_container_width=True)



# === Smoking Status Plot ===
with col3:
    st.subheader("Smoking Status Distribution by Gender")
    smoking_fig = px.histogram(filtered_diabetes, x="Smoking", color="Gender", barmode='group',
                               title="", text_auto=True)
    smoking_fig.update_layout(xaxis_title='Smoking Status', yaxis_title='Count')
    st.plotly_chart(smoking_fig, use_container_width=True)

    st.markdown("""""""")

    # === BMI Category Distribution Plot by Gender ===
    bmi_grouped = filtered_diabetes.groupby(['Gender', 'BMI_Category'], as_index=False).size()
    bmi_grouped.rename(columns={"size": "Count"}, inplace=True)

    category_order = ["Underweight", "Normal Weight", "Overweight", "Obesity", "Missing"]
    bmi_grouped['BMI_Category'] = pd.Categorical(bmi_grouped['BMI_Category'], categories=category_order, ordered=True)
    bmi_grouped = bmi_grouped.sort_values(by='BMI_Category')

    total_n_bmi = bmi_grouped['Count'].sum()

    fig = px.bar(
        bmi_grouped,
        x="BMI_Category",
        y="Count",
        color="Gender",
        barmode="group",
        text="Count",
        category_orders={"BMI_Category": category_order},
        title=f"BMI Category Distribution by Gender (n = {total_n_bmi})",
        color_discrete_map={
            "Male" : "Lightgreen",
            "Female" : "mediumseagreen"
        }
    )

    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis_title="BMI Category",
        yaxis_title="Number of Individuals",
        legend_title="Gender",
        xaxis_tickangle=-45,
        template="simple_white"
    )

    st.plotly_chart(fig, use_container_width=True)

# Define big_metric function first
    
def big_metric2(label, value, proportion, emoji, bg_color="#dff0d8"):
    st.markdown(f"""
        <div style="padding: 10px; border-radius: 50px; background-color: {bg_color}; 
                    text-align: center; width: 250px; margin: auto; 
                    font-size: 16px; border: 2px solid #3c763d; 
                    color: #3c763d; box-shadow: 2px 2px 8px rgba(0,0,0,0.2);">
            {emoji} <strong>{label}</strong><br>
            <span style="font-weight: bold; color: #3c763d;">{value} ({proportion:.1f}%)</span>
        </div>
    """, unsafe_allow_html=True)

# Calculate Total N
#total_n = len(filtered_diabetes)
#big_metric("Total N", total_n, 100, emoji="👩‍👩‍👦‍👦")  
#st.divider()

# Define variables and emojis for display
variables = {
    "Family History of Diabetes": ("FamilyHistoryDiabetes", "👨‍👩‍👦"),
    "Gestational Diabetes": ("GestationalDiabetes", "🤰"),
    "Polycystic Ovary Syndrome": ("PolycysticOvarySyndrome", "🧬"),
    "Previous Pre-Diabetes": ("PreviousPreDiabetes", "🩸"),
    "Hypertension": ("Hypertension", "💓")
}

# Create columns for each variable
#st.header("Overview of the health condition data")

st.markdown(
    "<h4 style='text-align: ; color: black;'>Overview of the health condition data(n=1879)</h4>", 
    unsafe_allow_html=True
)
cols = st.columns(len(variables))

# Loop through and display counts & proportions side-by-side
for col_obj, (label, (col, emoji)) in zip(cols, variables.items()):
    count = (filtered_diabetes[col] == 1).sum()
    proportion = (count / total_n) * 100
    with col_obj:
        big_metric2(label, count, proportion, emoji)


# Gender Wise Health Condition Data
def big_metric3(label, value, proportion, emoji, bg_color="#d8f0ec"):
    st.markdown(f"""
        <div style="padding: 10px; border-radius: 50px; background-color: {bg_color}; 
                    text-align: center; width: 250px; margin: auto; 
                    font-size: 16px; border: 2px solid #3c763d; 
                    color: #3c763d; box-shadow: 2px 2px 8px rgba(0,0,0,0.2);">
            {emoji} <strong>{label}</strong><br>
            <span style="font-weight: bold; color: #3c763d;">{value} ({proportion:.1f}%)</span>
        </div>
    """, unsafe_allow_html=True)


# Define variables and emojis for display
variables = {
    "Family History of Diabetes": ("FamilyHistoryDiabetes", "👨‍👩‍👦"),
    "Gestational Diabetes": ("GestationalDiabetes", "🤰"),
    "Polycystic Ovary Syndrome": ("PolycysticOvarySyndrome", "🧬"),
    "Previous Pre-Diabetes": ("PreviousPreDiabetes", "🩸"),
    "Hypertension": ("Hypertension", "💓")
}

# Display title
st.markdown(
    "<h4 style='color: black;'>Overview of the health condition data by Gender</h4>", 
    unsafe_allow_html=True
)

# Detect gender categories
gender_values = filtered_diabetes["Gender"].unique()

# Try to map values to Male/Female
gender_map = {}
for val in gender_values:
    val_str = str(val).strip().lower()
    if val_str in ["male", "m", "1"]:
        gender_map["Male"] = val
    elif val_str in ["female", "f", "0"]:
        gender_map["Female"] = val

# Loop for each gender found in the dataset
for gender_label in ["Male", "Female"]:
    if gender_label in gender_map:
        gender_val = gender_map[gender_label]
        st.markdown(f"### {gender_label}")
        gender_df = filtered_diabetes[filtered_diabetes["Gender"] == gender_val]
        total_n_gender = len(gender_df)

        cols = st.columns(len(variables))
        for col_obj, (label, (col, emoji)) in zip(cols, variables.items()):
            count = (gender_df[col] == 1).sum()
            proportion = (count / total_n_gender) * 100 if total_n_gender > 0 else 0
            with col_obj:
                big_metric3(label, count, proportion, emoji)

# -*- coding: utf-8 -*-
"""FINAL_EXAM.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/12CZs5RBgMxwD4AbiyAV9cVqtidIK8bFQ

# **Nutrition, Physical Activity, and Obesity - Behavioral Risk Factor Surveillance System**

**Libraries**
"""

import warnings
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GridSearchCV

"""**Dataset & Preferences**"""

warnings.filterwarnings('ignore')

sns.set_theme(style='whitegrid', font='serif')

DATASETURL = 'https://raw.githubusercontent.com/Jerald011003/Nutrition-Physical_Activity-and-Obesity-Analysis/refs/heads/main/Nutrition__Physical_Activity__and_Obesity_-_Behavioral_Risk_Factor_Surveillance_System.csv'

"""# I. Exploratory Data **Analysis**"""

data = pd.read_csv(DATASETURL)

data.head()

# Display the dataset information
data.info()

# Display the dataset statistics
data.describe(include='all')

# Preview columns
data.columns

# Preview dataset numerical and categorical columns
num_cols = data.select_dtypes(include=np.number).columns
cat_cols = data.select_dtypes(include='object').columns

print(f'Numerical Columns\n{num_cols}\n')
print(f'Categorical Columns\n{cat_cols}')

"""# **II. Data Cleaning and Preprocessing**"""

# Summation of missing values
print("Missing values per column:")
data.isnull().sum()

# Summation of duplicated rows
data.duplicated().sum()

irrelevant_columns = ['ClassID', 'TopicID', 'QuestionID', 'DataValueTypeID', 'Data_Value_Unit',
                      'LocationID', 'StratificationCategoryId1', 'StratificationID1']
data_cleaned = data.drop(columns=irrelevant_columns)

data_cleaned.columns = data_cleaned.columns.str.strip()

data_cleaned = data_cleaned.dropna(subset=['Data_Value', 'Low_Confidence_Limit', 'High_Confidence_Limit'])

# Fill missing values in categorical columns with 'Unknown'
categorical_columns = data_cleaned.select_dtypes(include=['object']).columns
data_cleaned[categorical_columns] = data_cleaned[categorical_columns].fillna('Unknown')

# Fill missing values in numeric columns with the column mean
numeric_columns = data_cleaned.select_dtypes(include=['float64', 'int64']).columns
data_cleaned[numeric_columns] = data_cleaned[numeric_columns].fillna(data_cleaned[numeric_columns].mean())

print("\nMissing values after cleaning:")
data_cleaned.isnull().sum()

"""**Saved Cleaned Data**

"""

# cleaned_file_path = 'cleaned_data.csv'
# data_cleaned.to_csv(cleaned_file_path, index=False)

data_cleaned.head()

# Preview cleaned dataset numerical and categorical columns
num_cols = data_cleaned.select_dtypes(include=np.number).columns
cat_cols = data_cleaned.select_dtypes(include='object').columns
# data_cleaned = data_cleaned[data_cleaned['cat_cols'].notna()]
# data_cleaned['cat_cols'].fillna('Unknown', inplace=True)

print(f'Numerical Columns\n{num_cols}\n')
print(f'Categorical Columns\n{cat_cols}')

scaler = StandardScaler()
data_cleaned[num_cols] = scaler.fit_transform(data_cleaned[num_cols])

# Loop through each numerical column to detect and remove outliers
for column in num_cols:
    Q1 = data_cleaned[column].quantile(0.25)
    Q3 = data_cleaned[column].quantile(0.75)
    IQR = Q3 - Q1
    data_cleaned = data_cleaned[~((data_cleaned[column] < (Q1 - 1.5 * IQR)) |
                                   (data_cleaned[column] > (Q3 + 1.5 * IQR)))]
print("Final dataset info:")
print(data_cleaned.info())
print(data_cleaned.isnull().sum())

"""# **III. Data Visualization**"""

# Numerical Categories Visualization
# def distribution_of_data(data_cleaned, column):
#     fig, ax = plt.subplots(figsize=(12, 6))

#     # Filter out 'Unknown' values before plotting
#     filtered_data = data_cleaned[data_cleaned[column] != 'Unknown']

#     sns.histplot(filtered_data[column], kde=True, ax=ax)

#     # !!! THE UNKNOWNS ARE EXCLUDED TO UNDERSTAND TRENDS/RELATIONSHIP MORE CLEARER
#     ax.set_title(f'Distribution of {column}')
#     ax.set_xlabel(column)
#     ax.set_ylabel('Frequency')

#     plt.show()

#     # !!! EXCLUDING THESE COLUMNS IT SHOWS FOR MORE CLEARER DISTRIBUTIONS
# exclude_cols = ['Datasource', 'Data_Value_Type', 'Data_Value_Footnote_Symbol',
#                  'Data_Value_Footnote', 'Total']

# # Loop through the categorical columns and plot distributions, excluding the specified columns
# for col in cat_cols:
#     if col not in exclude_cols:
#         distribution_of_data(data_cleaned, col)

# Numerical Categories Visualization
def distribution_of_data(data_cleaned, column):
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot the distribution of the data with dynamic bins
    sns.histplot(data_cleaned[column], kde=True, ax=ax)

    # Set the title and labels
    ax.set_title(f'Distribution of {column}')
    ax.set_xlabel(column)
    ax.set_ylabel('Frequency')

    # Show the plot
    plt.show()

for col in num_cols:
    distribution_of_data(data_cleaned, col)

def count_plot(data_cleaned, column):
    plt.figure(figsize=(12, 6))
    sns.countplot(data=data_cleaned, x=column, order=data_cleaned[column].value_counts().index)
    plt.title(f'Count Plot of {column}')
    plt.xlabel(column)
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.show()

for col in cat_cols:
    count_plot(data_cleaned, col)

# Box plot for Data_Value
plt.figure(figsize=(10, 6))
sns.boxplot(x=data_cleaned['Data_Value'])
plt.title('Box Plot of Data_Value')
plt.xlabel('Data_Value')
plt.show()

numerical_data = data_cleaned[num_cols]
corr = numerical_data.corr()

fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax, fmt='.2f', linewidths=.5, mask=np.triu(corr))

ax.set_title('Correlation Matrix')

plt.show()

"""# **IV. Model Development**
*   Use at least four (4) algorithms.

1.   Logistic Regression
2.   Support Vector Machine (SVM)
3.   Random Forest
4.   Gradient Boosting
"""

columns_to_drop = ["YearStart", "YearEnd", "LocationAbbr", "LocationDesc", "Datasource",
                   "Question", "Data_Value_Type", "GeoLocation", "StratificationCategory1",
                   "Stratification1", "Data_Value_Footnote_Symbol", "Data_Value_Footnote"]
data_filtered = data_cleaned.drop(columns=columns_to_drop)

label_encoders = {col: LabelEncoder() for col in data_filtered.select_dtypes(include='object').columns}
for col, le in label_encoders.items():
    data_filtered[col] = le.fit_transform(data_filtered[col])

X = data_filtered.drop(columns="Class")
y = data_filtered["Class"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

imputer = SimpleImputer(strategy="mean")
X_train = imputer.fit_transform(X_train)
X_test = imputer.transform(X_test)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Support Vector Machine": SVC(),
    "Random Forest": RandomForestClassifier(),
    "Gradient Boosting": GradientBoostingClassifier()
}

model_performance = {}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    model_performance[name] = {"Accuracy": accuracy, "Classification Report": report}

print(model_performance)

"""# **V. Model Evaluation**"""

# print("First 5 rows of the training dataset (features):")
# print(X_train[:5])
# print("\nFirst 5 rows of the training dataset (labels):")
# print(y_train[:5])

# print("\nFirst 5 rows of the test dataset (features):")
# print(X_test[:5])
# print("\nFirst 5 rows of the test dataset (labels):")
# print(y_test[:5])

model_performance = {}

def evaluate_model(model, X_train, y_train, X_test, y_test):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    return accuracy, report, y_pred

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Support Vector Machine": SVC(),
    "Random Forest": RandomForestClassifier(),
    "Gradient Boosting": GradientBoostingClassifier()
}

for name, model in models.items():
    accuracy, report, y_pred = evaluate_model(model, X_train, y_train, X_test, y_test)

    model_performance[name] = {
        "Accuracy": accuracy,
        "Classification Report": report,
        "Confusion Matrix": confusion_matrix(y_test, y_pred)
    }

    if accuracy < 0.85:
        print(f"{name} did not meet the accuracy threshold. Tuning hyperparameters...")

        if name == "Random Forest":
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10]
            }
            grid_search = GridSearchCV(model, param_grid, cv=5, scoring='accuracy')
            grid_search.fit(X_train, y_train)
            best_model = grid_search.best_estimator_
            accuracy, report, y_pred = evaluate_model(best_model, X_train, y_train, X_test, y_test)

            model_performance[name] = {
                "Accuracy": accuracy,
                "Classification Report": report,
                "Confusion Matrix": confusion_matrix(y_test, y_pred)
            }

for name, metrics in model_performance.items():
    print(f"Model: {name}")
    print(f"Accuracy: {metrics['Accuracy']* 100:.2f}%")
    print("Classification Report:")
    print(metrics["Classification Report"])
    print("Confusion Matrix:")
    print(metrics["Confusion Matrix"])
    print("-" * 40)
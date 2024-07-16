import json
import pandas as pd
import re
from pathlib import Path

def read_sonar_java_files(java_visitor_files_path):
    """
    Description:
        Reads the java visitor files and extracts the rule id and the java visitor code.
        This will also remove the copyright headers to clean the java visitor code.

    Parameters:
        java_visitor_files_path (String): path to the folder containing the java visitor files

    Returns:
        object: an object containing the rule id and the java visitor code
    """
    java_files = list(Path(java_visitor_files_path).rglob('*.java'))
    java_info = {}
    for java_file in java_files:
        content = java_file.read_text(encoding='utf-8')
        rule_id_match = re.search(r'@Rule\(key = "(S\d+)"\)', content)
        if rule_id_match:
            rule_id = rule_id_match.group(1)
            
            # Remove copyright header from the content
            content = re.sub(r'\s*/\*.*?\*/\s*', '', content, flags=re.DOTALL)
            
            java_info[rule_id] = {'Java Visitor': content}
    return java_info

def read_sonar_json_files(json_files_path, java_info):
    """
    Description: 
        Reads the json rule files and extracts the rule id, rule type, NL query and java visitor code.
    
    Parameters:
        json_files_path (String): path to the folder containing the json rule files
        java_info (object): an object containing the rule id and the java visitor code
    
    Returns:
        list: a list of dictionaries containing the rule id, rule type, NL query and java visitor code
    """
    json_files = list(Path(json_files_path).rglob('*.json'))
    rows = []
    for json_file in json_files:
        rule_id = json_file.stem
        if rule_id in java_info:
            with open(json_file) as f:
                json_data = json.load(f)
            rows.append({
                'Rule ID': rule_id,
                'Rule Type': json_data['type'],
                'NL Query': json_data['title'],
                'Java Visitor': java_info[rule_id]['Java Visitor']
            })
    return rows

def create_dataframe(rows, columns):
    """
    Description:
        Creates a DataFrame from the list of dictionaries.

    Parameters:
        rows (list): a list of dictionaries containing the rule id, rule type, NL query and java visitor code
        columns (list): a list of column names
    
    Returns:
        DataFrame: a DataFrame containing the rule id, rule type, NL query and java visitor code
    """
    return pd.DataFrame(rows, columns=columns)

def write_to_csv(df, csv_file_name):
    """
    Description:
        Writes the DataFrame to a CSV file.
        
    Parameters:
        df (DataFrame): a DataFrame containing the rule id, rule type, NL query and java visitor code
        csv_file_name (String): name of the CSV file
    """
    df.to_csv(csv_file_name, index=False)
    print(f"CSV file '{csv_file_name}' has been created successfully.")


def main():
    java_visitor_files_path = "D:/OneDrive/Desktop/sonar-java/java-checks/src/main/java/org/sonar/java/checks"
    json_files_path = "D:/OneDrive/Desktop/sonar-java/sonar-java-plugin/src/main/resources/org/sonar/l10n/java/rules/java"
    csv_columns = ['Rule ID', 'Rule Type', 'NL Query', 'Java Visitor']
    
    java_info = read_sonar_java_files(java_visitor_files_path)
    rows = read_sonar_json_files(json_files_path, java_info)
    df = create_dataframe(rows, csv_columns)
    print(df)
    
    csv_file_name = 'query_to_visitor_dataset.csv'
    write_to_csv(df, csv_file_name)

if __name__ == "__main__":
    main()
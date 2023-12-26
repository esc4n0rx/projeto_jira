import requests
import pandas as pd
from tqdm import tqdm


url = "https://hnt.atlassian.net/rest/api/2/search?jql=project=LOG"
email = "geovana.costa@hortifruti.com.br"
token = "ATATT3xFfGF0kLnE7UPCTIz6hYhpDtDqPkdKxbJ9EiB25ZxsfGl6a7uDJ5QuYMWyckZJIGOtXh26sS3I-8c5tC57umsvyL1aoygb9YZN_44K4GzibrFNl3WRghdnDzqyb9-foxR9eHv1xTK7uAVftgJaZYv1gGQt2Dzu5LdnD0bx1lAtrq6oBwg=6C15CBC8"



headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}


auth = (email, token)


fields_response = requests.get("https://hnt.atlassian.net/rest/api/2/field", headers=headers, auth=auth)

if fields_response.status_code != 200:
    print(f"Erro na requisição dos campos: {fields_response.status_code}")
    print(fields_response.text)
    exit()

fields = fields_response.json()


custom_fields_map = {field['id']: field['name'] for field in fields if field.get('custom', False)}


response = requests.get(url, headers=headers, auth=auth)
data_to_save = []


if response.status_code == 200:
    data = response.json()
    total_issues = data['total']
    
    max_results = 100  
    pages = -(-total_issues // max_results)
    
   
    for page in tqdm(range(pages), desc='Fetching data', unit='page'):
        start_at = page * max_results
        
        paginated_url = f"{url}&startAt={start_at}&maxResults={max_results}"
        
        response = requests.get(paginated_url, headers=headers, auth=auth)
        if response.status_code != 200:
            print(f"Erro na requisição: {response.status_code}, Página: {page + 1}")
            continue
        
        data = response.json()
        issues = data["issues"]
        
        for issue in issues:
            LOG = issue["key"]
            fields = issue["fields"]
            
            non_null_fields = {key: (value if not isinstance(value, dict) else value.get('value', None)) 
                       for key, value in fields.items() if value is not None}
    
            non_null_fields = {custom_fields_map.get(key, key): value for key, value in non_null_fields.items()}
            non_null_fields["LOG"] = LOG
            data_to_save.append(non_null_fields)
    
    df = pd.DataFrame(data_to_save)
    df = df[['LOG'] + [col for col in df if col != 'LOG']]
    
    df.to_excel("C:\\Users\\paulo.cunha\\OneDrive - Hortifruti Natural da Terra\\Documents\\projeto-jira\\planilha.xlsx", index=False)
else:
    print(f"Erro na requisição: {response.status_code}")

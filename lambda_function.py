import json
import boto3
import urllib.request
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

DATASTORE_ID = 'b1f04342d94dcc96c47f9528f039f5a8'
REGION = 'us-west-2'

def search_healthlake(resource_type, params=None):
    """Search HealthLake FHIR resources"""
    import requests
    from botocore.auth import SigV4Auth
    from botocore.awsrequest import AWSRequest
    
    endpoint = f"https://healthlake.{REGION}.amazonaws.com/datastore/{DATASTORE_ID}/r4/"
    
    # Use boto3 default session which uses Lambda execution role
    session = boto3.Session()
    credentials = session.get_credentials()
    
    url = f"{endpoint}{resource_type}"
    if params:
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    
    request = AWSRequest(method='GET', url=url)
    SigV4Auth(credentials, 'healthlake', REGION).add_auth(request)
    
    try:
        response = requests.get(url, headers=dict(request.headers))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTPError: {e.response.status_code} - {e.response.text[:200]}")
        print(f"URL: {url}")
        return {'entry': [], 'total': 0}
    except Exception as e:
        print(f"Error: {str(e)}")
        return {'entry': [], 'total': 0}

def lambda_handler(event, context):
    """Lambda handler for Bedrock Agent"""
    print(f"Event: {json.dumps(event)}")
    
    action = event.get('actionGroup')
    api_path = event.get('apiPath')
    parameters = event.get('parameters', [])
    
    # Convert parameters to dict
    params = {p['name']: p['value'] for p in parameters}
    
    result = {}
    
    if api_path == '/search-patients':
        count = params.get('count', '10')
        data = search_healthlake('Patient', {'_count': count})
        patients = []
        for entry in data.get('entry', []):
            p = entry['resource']
            name = p.get('name', [{}])[0]
            patients.append({
                'id': p.get('id'),
                'name': f"{name.get('given', [''])[0]} {name.get('family', '')}",
                'gender': p.get('gender'),
                'birthDate': p.get('birthDate')
            })
        # HealthLake total is often 0, so use actual count
        total = data.get('total', 0) if data.get('total', 0) > 0 else len(patients)
        result = {'patients': patients, 'total': total, 'returned': len(patients)}
    
    elif api_path == '/search-conditions':
        patient_id = params.get('patient_id')
        search_params = {'_count': '50'}
        if patient_id:
            search_params['patient'] = patient_id
        
        data = search_healthlake('Condition', search_params)
        conditions = []
        for entry in data.get('entry', [])[:20]:
            c = entry['resource']
            code = c.get('code', {}).get('coding', [{}])[0]
            conditions.append({
                'condition': code.get('display', 'Unknown'),
                'patient': c.get('subject', {}).get('reference', '')
            })
        result = {'conditions': conditions, 'total': data.get('total', 0)}
    
    elif api_path == '/search-observations':
        patient_id = params.get('patient_id')
        search_params = {'_count': '50'}
        if patient_id:
            search_params['patient'] = patient_id
        
        data = search_healthlake('Observation', search_params)
        observations = []
        for entry in data.get('entry', [])[:20]:
            o = entry['resource']
            code = o.get('code', {}).get('coding', [{}])[0]
            value = o.get('valueQuantity', {})
            observations.append({
                'observation': code.get('display', 'Unknown'),
                'value': f"{value.get('value', '')} {value.get('unit', '')}" if value else 'N/A'
            })
        result = {'observations': observations, 'total': data.get('total', 0)}
    
    elif api_path == '/search-medications':
        patient_id = params.get('patient_id')
        search_params = {'_count': '50'}
        if patient_id:
            search_params['patient'] = patient_id
        
        data = search_healthlake('MedicationRequest', search_params)
        medications = []
        for entry in data.get('entry', [])[:20]:
            m = entry['resource']
            med = m.get('medicationCodeableConcept', {}).get('coding', [{}])[0]
            medications.append({
                'medication': med.get('display', 'Unknown'),
                'status': m.get('status', 'Unknown'),
                'authoredOn': m.get('authoredOn', 'N/A')
            })
        result = {'medications': medications, 'total': data.get('total', 0)}
    
    elif api_path == '/search-encounters':
        patient_id = params.get('patient_id')
        search_params = {'_count': '50'}
        if patient_id:
            search_params['patient'] = patient_id
        
        data = search_healthlake('Encounter', search_params)
        encounters = []
        for entry in data.get('entry', [])[:20]:
            e = entry['resource']
            enc_type = e.get('type', [{}])[0].get('coding', [{}])[0] if e.get('type') else {}
            period = e.get('period', {})
            encounters.append({
                'type': enc_type.get('display', 'Unknown'),
                'status': e.get('status', 'Unknown'),
                'start': period.get('start', 'N/A'),
                'end': period.get('end', 'N/A')
            })
        result = {'encounters': encounters, 'total': data.get('total', 0)}
    
    elif api_path == '/search-procedures':
        patient_id = params.get('patient_id')
        search_params = {'_count': '50'}
        if patient_id:
            search_params['patient'] = patient_id
        
        data = search_healthlake('Procedure', search_params)
        procedures = []
        for entry in data.get('entry', [])[:20]:
            p = entry['resource']
            code = p.get('code', {}).get('coding', [{}])[0]
            period = p.get('performedPeriod', {})
            procedures.append({
                'procedure': code.get('display', 'Unknown'),
                'status': p.get('status', 'Unknown'),
                'performed': period.get('start', 'N/A')
            })
        result = {'procedures': procedures, 'total': data.get('total', 0)}
    
    elif api_path == '/search-allergies':
        patient_id = params.get('patient_id')
        search_params = {'_count': '50'}
        if patient_id:
            search_params['patient'] = patient_id
        
        data = search_healthlake('AllergyIntolerance', search_params)
        allergies = []
        for entry in data.get('entry', [])[:20]:
            a = entry['resource']
            code = a.get('code', {}).get('coding', [{}])[0]
            allergies.append({
                'allergy': code.get('display', 'Unknown'),
                'criticality': a.get('criticality', 'Unknown'),
                'type': a.get('type', 'Unknown')
            })
        result = {'allergies': allergies, 'total': data.get('total', 0)}
    
    elif api_path == '/search-immunizations':
        patient_id = params.get('patient_id')
        search_params = {'_count': '50'}
        if patient_id:
            search_params['patient'] = patient_id
        
        data = search_healthlake('Immunization', search_params)
        immunizations = []
        for entry in data.get('entry', [])[:20]:
            i = entry['resource']
            vaccine = i.get('vaccineCode', {}).get('coding', [{}])[0]
            immunizations.append({
                'vaccine': vaccine.get('display', 'Unknown'),
                'status': i.get('status', 'Unknown'),
                'date': i.get('occurrenceDateTime', 'N/A')
            })
        result = {'immunizations': immunizations, 'total': data.get('total', 0)}
    
    elif api_path == '/search-diagnostic-reports':
        patient_id = params.get('patient_id')
        search_params = {'_count': '50'}
        if patient_id:
            search_params['patient'] = patient_id
        
        data = search_healthlake('DiagnosticReport', search_params)
        reports = []
        for entry in data.get('entry', [])[:20]:
            r = entry['resource']
            code = r.get('code', {}).get('coding', [{}])[0]
            reports.append({
                'report': code.get('display', 'Unknown'),
                'status': r.get('status', 'Unknown'),
                'issued': r.get('issued', 'N/A')
            })
        result = {'reports': reports, 'total': data.get('total', 0)}
    
    elif api_path == '/search-careplans':
        patient_id = params.get('patient_id')
        search_params = {'_count': '50'}
        if patient_id:
            search_params['patient'] = patient_id
        
        data = search_healthlake('CarePlan', search_params)
        careplans = []
        for entry in data.get('entry', [])[:20]:
            cp = entry['resource']
            category = cp.get('category', [{}])[0].get('coding', [{}])[0] if cp.get('category') else {}
            period = cp.get('period', {})
            careplans.append({
                'careplan': category.get('display', 'Unknown'),
                'status': cp.get('status', 'Unknown'),
                'start': period.get('start', 'N/A')
            })
        result = {'careplans': careplans, 'total': data.get('total', 0)}
    
    elif api_path == '/get-summary':
        # Get counts for all resource types (HealthLake max _count is 100)
        resource_types = ['Patient', 'Condition', 'Observation', 'MedicationRequest', 
                         'Encounter', 'Procedure', 'AllergyIntolerance', 'Immunization',
                         'DiagnosticReport', 'CarePlan']
        
        summary = {}
        for resource_type in resource_types:
            data = search_healthlake(resource_type, {'_count': '100'})
            count = len(data.get('entry', []))
            summary[resource_type] = count
        
        result = {'summary': summary, 'total_resources': sum(summary.values()), 'note': 'Counts limited to 100 per resource type'}
    
    elif api_path == '/search-patient-by-name':
        search_name = params.get('name', '').lower()
        data = search_healthlake('Patient', {'_count': '100'})
        
        matching_patients = []
        for entry in data.get('entry', []):
            p = entry['resource']
            name = p.get('name', [{}])[0]
            given = ' '.join(name.get('given', []))
            family = name.get('family', '')
            full_name = f"{given} {family}".lower()
            
            if search_name in full_name or search_name in given.lower() or search_name in family.lower():
                matching_patients.append({
                    'id': p.get('id'),
                    'name': f"{given} {family}",
                    'gender': p.get('gender'),
                    'birthDate': p.get('birthDate')
                })
        
        result = {'patients': matching_patients, 'count': len(matching_patients)}
    
    return {
        'messageVersion': '1.0',
        'response': {
            'actionGroup': action,
            'apiPath': api_path,
            'httpMethod': 'GET',
            'httpStatusCode': 200,
            'responseBody': {
                'application/json': {
                    'body': json.dumps(result)
                }
            }
        }
    }

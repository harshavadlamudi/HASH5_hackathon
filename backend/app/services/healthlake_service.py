import boto3
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from app.core.config import settings

class HealthLakeService:
    def __init__(self):
        self.region = settings.AWS_REGION
        self.datastore_id = settings.HEALTHLAKE_DATASTORE_ID
        self.endpoint = f"https://healthlake.{self.region}.amazonaws.com/datastore/{self.datastore_id}/r4/"
        self.session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,
            region_name=self.region
        )
    
    def search(self, resource_type: str, params: dict = None):
        """Search HealthLake FHIR resources"""
        credentials = self.session.get_credentials()
        url = f"{self.endpoint}{resource_type}"
        
        if params:
            url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        request = AWSRequest(method='GET', url=url)
        SigV4Auth(credentials, 'healthlake', self.region).add_auth(request)
        
        response = requests.get(url, headers=dict(request.headers))
        return response.json()
    
    def get_all_patients(self, count: int = 100):
        """Get all patients from HealthLake"""
        result = self.search('Patient', {'_count': str(count)})
        patients = []
        
        if result.get('entry'):
            for entry in result['entry']:
                resource = entry['resource']
                patient_id = resource['id']
                name = 'Unknown'
                
                if 'name' in resource and resource['name']:
                    name_obj = resource['name'][0]
                    given = ' '.join(name_obj.get('given', []))
                    family = name_obj.get('family', '')
                    name = f"{given} {family}".strip()
                
                patients.append({
                    'id': patient_id,
                    'name': name,
                    'gender': resource.get('gender', 'Unknown'),
                    'birthDate': resource.get('birthDate', 'Unknown')
                })
        
        return patients
    
    def get_patient_summary(self, patient_id: str):
        """Get comprehensive patient summary"""
        summary = {
            'id': patient_id,
            'name': 'Unknown',
            'gender': 'Unknown',
            'birthDate': 'Unknown',
            'conditions': [],
            'medications': [],
            'allergies': [],
            'has_ecg': False,
            'mri_reports_count': 0
        }
        
        # Get patient demographics
        patient_data = self.search('Patient', {'_id': patient_id})
        if patient_data.get('entry'):
            p = patient_data['entry'][0]['resource']
            if 'name' in p and p['name']:
                name_obj = p['name'][0]
                given = ' '.join(name_obj.get('given', []))
                family = name_obj.get('family', '')
                summary['name'] = f"{given} {family}".strip()
            summary['gender'] = p.get('gender', 'Unknown')
            summary['birthDate'] = p.get('birthDate', 'Unknown')
        
        # Get conditions
        conditions = self.search('Condition', {'patient': patient_id, '_count': '10'})
        if conditions.get('entry'):
            for entry in conditions['entry']:
                c = entry['resource']
                if 'code' in c and 'text' in c['code']:
                    summary['conditions'].append(c['code']['text'])
        
        # Get medications
        meds = self.search('MedicationRequest', {'patient': patient_id, '_count': '10'})
        if meds.get('entry'):
            for entry in meds['entry']:
                m = entry['resource']
                if 'medicationCodeableConcept' in m and 'text' in m['medicationCodeableConcept']:
                    summary['medications'].append(m['medicationCodeableConcept']['text'])
        
        # Get allergies
        allergies = self.search('AllergyIntolerance', {'patient': patient_id, '_count': '10'})
        if allergies.get('entry'):
            for entry in allergies['entry']:
                a = entry['resource']
                if 'code' in a and 'text' in a['code']:
                    summary['allergies'].append(a['code']['text'])
        
        # Check for ECG
        ecg_obs = self.search('Observation', {'patient': patient_id, 'code': '131328', '_count': '1'})
        summary['has_ecg'] = bool(ecg_obs.get('entry'))
        
        # Get MRI reports count
        reports = self.search('DiagnosticReport', {'patient': patient_id, '_count': '10'})
        summary['mri_reports_count'] = len(reports.get('entry', []))
        
        return summary

healthlake_service = HealthLakeService()

import sys
sys.path.append('.')

from app.services.healthlake_service import healthlake_service

# Test HealthLake connection
try:
    print("Testing HealthLake connection...")
    patients = healthlake_service.get_all_patients()
    print(f"Found {len(patients)} patients")
    
    if patients:
        print("\nFirst patient:")
        print(patients[0])
    else:
        print("\nNo patients found. Testing raw search...")
        result = healthlake_service.search('Patient', {'_count': '10'})
        print(f"Raw result: {result}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

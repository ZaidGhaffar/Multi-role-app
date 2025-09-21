#!/usr/bin/env python3
"""
Comprehensive test script to demonstrate company creation and employee association
This shows how the company system works in the Backend
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def print_separator(title):
    """Print a nice separator with title"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_company_creation_flow():
    """Test the complete company creation and employee association flow"""
    
    print_separator("COMPANY CREATION & EMPLOYEE ASSOCIATION TEST")
    
    # Step 1: Create HR Account (which creates a company)
    print("\n🏢 STEP 1: Creating HR Account (This creates a company)")
    print("-" * 50)
    
    hr_data = {
        "email": "hr@techcorp.com",
        "password": "hrpassword123",
        "company_name": "Tech Corp"
    }
    
    print(f"Creating HR account for: {hr_data['email']}")
    print(f"Company name: {hr_data['company_name']}")
    
    response = requests.post(f"{BASE_URL}/hr/signup", json=hr_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        hr_user = response.json()
        print(f"✅ HR Account Created:")
        print(f"   - ID: {hr_user['id']}")
        print(f"   - Username: {hr_user['username']}")
        print(f"   - Role: {hr_user['role']}")
        print(f"   - Company 'Tech Corp' has been created!")
    else:
        print(f"❌ Error: {response.text}")
        return
    
    # Step 2: HR Login to get company info
    print("\n🔐 STEP 2: HR Login")
    print("-" * 50)
    
    hr_login_data = {
        "username": "hr@techcorp.com",
        "password": "hrpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/hr/login", json=hr_login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        hr_token = response.json()["access_token"]
        print("✅ HR Login successful!")
        print(f"   - JWT Token received")
    else:
        print(f"❌ Error: {response.text}")
        return
    
    # Step 3: Try to create employee in EXISTING company (should work)
    print("\n👤 STEP 3: Employee Signup in EXISTING Company")
    print("-" * 50)
    
    employee_data = {
        "username": "john.doe@techcorp.com",
        "password": "employeepassword123",
        "company_name": "Tech Corp"  # Same company as HR created
    }
    
    print(f"Creating employee account for: {employee_data['username']}")
    print(f"Company name: {employee_data['company_name']}")
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=employee_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200 or response.status_code == 201:
        employee_user = response.json()
        print(f"✅ Employee Account Created:")
        print(f"   - ID: {employee_user['id']}")
        print(f"   - Username: {employee_user['username']}")
        print(f"   - Role: {employee_user['role']}")
        print(f"   - Associated with existing company 'Tech Corp'!")
    else:
        print(f"❌ Error: {response.text}")
    
    # Step 4: Try to create employee in NON-EXISTING company (should fail)
    print("\n❌ STEP 4: Employee Signup in NON-EXISTING Company")
    print("-" * 50)
    
    invalid_employee_data = {
        "username": "jane.smith@fakecompany.com",
        "password": "employeepassword123",
        "company_name": "Fake Company"  # Company doesn't exist
    }
    
    print(f"Trying to create employee account for: {invalid_employee_data['username']}")
    print(f"Company name: {invalid_employee_data['company_name']}")
    print("(This should FAIL because company doesn't exist)")
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=invalid_employee_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 400:
        error_detail = response.json()["detail"]
        print(f"✅ Expected Error Received:")
        print(f"   - Status: {response.status_code}")
        print(f"   - Message: {error_detail}")
        print("   - This is correct behavior! Employees can only join existing companies.")
    else:
        print(f"❌ Unexpected response: {response.text}")
    
    # Step 5: Create another HR account (different company)
    print("\n🏢 STEP 5: Creating Another HR Account (Different Company)")
    print("-" * 50)
    
    hr2_data = {
        "email": "hr@startup.com",
        "password": "hrpassword123",
        "company_name": "Startup Inc"
    }
    
    print(f"Creating second HR account for: {hr2_data['email']}")
    print(f"Company name: {hr2_data['company_name']}")
    
    response = requests.post(f"{BASE_URL}/hr/signup", json=hr2_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        hr2_user = response.json()
        print(f"✅ Second HR Account Created:")
        print(f"   - ID: {hr2_user['id']}")
        print(f"   - Username: {hr2_user['username']}")
        print(f"   - Role: {hr2_user['role']}")
        print(f"   - Company 'Startup Inc' has been created!")
    else:
        print(f"❌ Error: {response.text}")
    
    # Step 6: Try to create employee in the new company
    print("\n👤 STEP 6: Employee Signup in Second Company")
    print("-" * 50)
    
    employee2_data = {
        "username": "alice.johnson@startup.com",
        "password": "employeepassword123",
        "company_name": "Startup Inc"
    }
    
    print(f"Creating employee account for: {employee2_data['username']}")
    print(f"Company name: {employee2_data['company_name']}")
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=employee2_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200 or response.status_code == 201:
        employee2_user = response.json()
        print(f"✅ Second Employee Account Created:")
        print(f"   - ID: {employee2_user['id']}")
        print(f"   - Username: {employee2_user['username']}")
        print(f"   - Role: {employee2_user['role']}")
        print(f"   - Associated with company 'Startup Inc'!")
    else:
        print(f"❌ Error: {response.text}")

def test_duplicate_company_creation():
    """Test what happens when trying to create duplicate companies"""
    
    print_separator("DUPLICATE COMPANY CREATION TEST")
    
    print("\n🔄 Testing duplicate company creation...")
    print("-" * 50)
    
    # Try to create HR account with same company name
    duplicate_hr_data = {
        "email": "hr2@techcorp.com",
        "password": "hrpassword123",
        "company_name": "Tech Corp"  # Same company name as before
    }
    
    print(f"Trying to create another HR account with company: {duplicate_hr_data['company_name']}")
    print("(This should FAIL because company already exists)")
    
    response = requests.post(f"{BASE_URL}/hr/signup", json=duplicate_hr_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 400:
        error_detail = response.json()["detail"]
        print(f"✅ Expected Error Received:")
        print(f"   - Status: {response.status_code}")
        print(f"   - Message: {error_detail}")
        print("   - This is correct! Each company can only have one HR account.")
    else:
        print(f"❌ Unexpected response: {response.text}")

def test_case_insensitive_company_names():
    """Test case insensitive company name handling"""
    
    print_separator("CASE INSENSITIVE COMPANY NAMES TEST")
    
    print("\n🔤 Testing case insensitive company names...")
    print("-" * 50)
    
    # Try employee signup with different case
    case_test_data = {
        "username": "test.case@techcorp.com",
        "password": "employeepassword123",
        "company_name": "TECH CORP"  # Different case
    }
    
    print(f"Trying employee signup with company name: {case_test_data['company_name']}")
    print("(Should work because company names are case insensitive)")
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=case_test_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200 or response.status_code == 201:
        employee_user = response.json()
        print(f"✅ Case Insensitive Test Passed:")
        print(f"   - Employee created successfully")
        print(f"   - Username: {employee_user['username']}")
        print(f"   - Role: {employee_user['role']}")
        print("   - Company name matching is case insensitive!")
    else:
        print(f"❌ Error: {response.text}")

def show_company_structure():
    """Show the database structure for companies"""
    
    print_separator("COMPANY DATABASE STRUCTURE")
    
    print("""
📊 Company Database Structure:

1. Companies Table:
   - id: String (UUID) - Primary Key
   - name: String (lowercase, unique) - Company name
   - created_at: DateTime - When company was created
   - users: Relationship to Users table

2. Users Table:
   - id: String (UUID) - Primary Key  
   - username: String - User's email/username
   - email: String - User's email
   - hashed_password: String - Encrypted password
   - role: String - "hr" or "employee"
   - company_id: String (UUID) - Foreign Key to Companies.id

3. Company Creation Flow:
   - HR signup → Creates new company → Creates HR user
   - Employee signup → Finds existing company → Creates employee user
   
4. Validation Rules:
   - Each company can only have ONE HR account
   - Employees can only join EXISTING companies
   - Company names are case insensitive
   - Usernames must be unique across all users
""")

if __name__ == "__main__":
    print("🏢 COMPANY MANAGEMENT SYSTEM TEST")
    print("This test demonstrates how companies are created and managed")
    
    try:
        # Test if Backend is running
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Backend is not running! Please start it first.")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Backend! Please start it first.")
        print("   Run: python -m uvicorn main:app --reload --host 0.0.0.0 --port 8080")
        exit(1)
    
    print("✅ Backend is running!")
    
    # Run all tests
    show_company_structure()
    test_company_creation_flow()
    test_duplicate_company_creation()
    test_case_insensitive_company_names()
    
    print_separator("TEST COMPLETE")
    print("🎉 All tests completed! Check the results above.")
    print("\nKey Takeaways:")
    print("• HR accounts create new companies")
    print("• Employee accounts can only join existing companies") 
    print("• Each company can only have one HR account")
    print("• Company names are case insensitive")
    print("• Proper error messages guide users")

import base64
import time
import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime
import os

# State code to department mapping
STATE_DEPARTMENTS = {
    'AS': '6~ASVC01',    # Assam
    'CH': '27~CHVC01',   # Chandigarh
    'CG': '18~CGVC01',   # Chhattisgarh
    'DL': '26~DLVC01',   # Delhi Traffic
    'DL2': '26~DLVC02',  # Delhi Notice
    'GJ': '17~GJVC01',   # Gujarat Transport
    'GJ2': '17~GJVC02',  # Gujarat Traffic
    'HR': '14~HRVC01',   # Haryana
    'HP': '5~HPVC01',    # Himachal Pradesh
    'JK': '12~JKVC01',   # Jammu Kashmir (Jammu)
    'JK2': '12~JKVC02',  # Jammu Kashmir (Kashmir)
    'KA': '3~KAVC01',    # Karnataka
    'KL': '4~KLVC01',    # Kerala Transport
    'KL2': '4~KLVC02',   # Kerala Police
    'MP': '23~MPVC01',   # Madhya Pradesh
    'MH': '1~MHVC01',    # Maharashtra Nashik
    'MH2': '1~MHVC03',   # Maharashtra Transport
    'MN': '25~MNVC01',   # Manipur Traffic
    'MN2': '25~MNVC02',  # Manipur Transport
    'ML': '21~MLVC01',   # Meghalaya
    'OD': '11~ODVC01',   # Odisha
    'RJ': '9~RJVC01',    # Rajasthan
    'TN': '10~TNVC01',   # Tamil Nadu
    'TR': '20~TRVC01',   # Tripura
    'UK': '15~UKVC02',   # Uttarakhand Transport
    'UK2': '15~UKVC01',  # Uttarakhand Traffic
    'UP': '13~UPVC01',   # Uttar Pradesh
    'WB': '16~WBVC01',   # West Bengal
}


# def setup_driver():
#     chrome_options = Options()
#     chrome_options.add_argument('--headless')  # Run in headless mode
#     chrome_options.add_argument('--no-sandbox')
#     chrome_options.add_argument('--disable-dev-shm-usage')
#     chrome_options.add_argument('--disable-gpu')
#     chrome_options.add_argument('--window-size=1920,1080')
#     chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
#     chrome_options.add_argument('--ignore-certificate-errors')
#     chrome_options.add_argument('--ignore-ssl-errors')
    
#     # Different driver setup for production vs development
#     if os.environ.get('ENVIRONMENT') == 'production':
#         # In production, use the system Chrome installation
#         service = Service('/usr/bin/chromedriver')
#         return webdriver.Chrome(service=service, options=chrome_options)
#     else:
#         # In development, use webdriver_manager
#         service = Service(ChromeDriverManager().install())
#         return webdriver.Chrome(service=service, options=chrome_options)


def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    
    # Use the system installed Chrome
    chrome_options.binary_location = "/usr/bin/google-chrome-stable"
    
    # Direct path to ChromeDriver
    service = Service('/usr/bin/chromedriver')
    return webdriver.Chrome(service=service, options=chrome_options)

# [Rest of your functions remain unchanged]
def select_department(driver, state_code):
    try:
        wait = WebDriverWait(driver, 10)
        dropdown = wait.until(EC.presence_of_element_located((By.ID, "fstate_code")))
        select = Select(dropdown)
        
        if state_code in STATE_DEPARTMENTS:
            select.select_by_value(STATE_DEPARTMENTS[state_code])
            time.sleep(1)  # Wait for any JavaScript to execute
            return True
        return False
    except Exception as e:
        print(f"Error selecting department: {str(e)}")
        return False

def click_proceed_button(driver):
    try:
        wait = WebDriverWait(driver, 10)
        proceed_button = wait.until(EC.element_to_be_clickable((By.ID, "payFineBTN")))
        proceed_button.click()
        return True
    except Exception as e:
        print(f"Error clicking proceed button: {str(e)}")
        return False

def click_challan_vehicle_tab(driver):
    try:
        wait = WebDriverWait(driver, 10)
        # Try multiple selectors to find the element
        selectors = [
            "//div[@class='col-6 p-0 mainmenu']//a[contains(.,'Challan/Vehicle No.')]",
            "//a[contains(text(),'Challan/Vehicle No.')]",
            "//a[contains(@href,'#police')]"
        ]
        
        for selector in selectors:
            try:
                challan_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                challan_button.click()
                time.sleep(2)  # Increased wait time
                
                # Verify if tab switched successfully
                if driver.find_element(By.ID, "challan_no").is_displayed():
                    return {"status": True, "message": "Successfully clicked challan tab"}
                
            except Exception:
                continue
                
        raise Exception("Could not find or click the Challan/Vehicle tab")
        
    except Exception as e:
        error_msg = f"Error clicking Challan/Vehicle tab: {str(e)}"
        print(error_msg)
        return {"status": False, "message": error_msg}

def submit_captcha(driver):
    try:
        captcha_element = driver.find_elements(By.CSS_SELECTOR, "img[alt='CAPTCHA Image']")[1]
        print(captcha_element.get_attribute('src'))

        base_64_image_data = driver.execute_script(f"""
                var canvas = document.createElement('canvas');
                var img = arguments[0];
                canvas.width = img.naturalWidth;
                canvas.height = img.naturalHeight;
                canvas.getContext('2d').drawImage(img, 0, 0);
                return canvas.toDataURL('image/png').substring(22); // Extract base64 part
            """, captcha_element)

        # Yet to submit captcha
        print(f"base64 captcha image: " + base_64_image_data)

        url = 'https://api.apitruecaptcha.org/one/gettext'
        data = { 
			'userid':'anshulstartups@gmail.com', 
			'apikey':'WczhL1HGgcRhrXFGxMAV',  
			'data': base_64_image_data
		}
        response = requests.post(url = url, json = data)
        data = response.json()
        print(data)

        input_captcha_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#fcaptcha_code_police"))
        )
        input_captcha_element.clear() #clear any previous text
        input_captcha_element.send_keys(data['result'])
        time.sleep(1)  # Wait for captcha to register

        # Click the submit button for police form
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[onclick='submitpoliceForm()']"))
        )
        submit_button.click()
        time.sleep(20)  # Wait for submission
        return True
    except Exception as e:
        print(f"Failed to submit captcha: {str(e)}")
        time.sleep(20)
        return True

def enter_challan_number(driver, challan_no):
    try:
        wait = WebDriverWait(driver, 10)
        challan_input = wait.until(EC.presence_of_element_located((By.ID, "challan_no")))
        challan_input.clear()
        challan_input.send_keys(challan_no)
        time.sleep(1)  # Wait for input to register
        return True
    except Exception as e:
        print(f"Error entering challan number: {str(e)}")
        return False

def click_view_link(driver):
    try:
        wait = WebDriverWait(driver, 10)
        # Using JavaScript click since the element has onclick attribute
        view_link = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "viewDetlink")))
        driver.execute_script("arguments[0].click();", view_link)
        time.sleep(2)  # Wait for view action to complete
        return True
    except Exception as e:
        print(f"Error clicking view link: {str(e)}")
        return False

def extract_table_data(driver):
    try:
        wait = WebDriverWait(driver, 20)
        tables = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "table")))   
        print(f"Found {len(tables)} tables")
        
        # Initialize data structure
        case_data = {
            "case_details": {},
            "current_status": {},
            "offence_details": [],
            "proposed_fine": "",
            "all_tables": []
        }
        
        # Process all tables for raw data collection
        for i, table in enumerate(tables):
            table_data = {
                "index": i,
                "title": "",
                "headers": [],
                "rows": []
            }
            
            # Try to get title from previous element
            try:
                prev_element = driver.execute_script("return arguments[0].previousElementSibling", table)
                if prev_element:
                    table_data["title"] = prev_element.text.strip()
            except:
                pass
                
            # Get headers
            header_cells = table.find_elements(By.TAG_NAME, "th")
            if header_cells:
                table_data["headers"] = [cell.text.strip() for cell in header_cells]
                
            # Get rows
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if cells:
                    row_data = [cell.text.strip() for cell in cells]
                    if any(row_data):  # Skip empty rows
                        table_data["rows"].append(row_data)
                        
            case_data["all_tables"].append(table_data)
            
            # Print table data for debugging
            print(f"\nTable {i + 1}:")
            print("-" * 50)
            if table_data["title"]:
                print(f"Title: {table_data['title']}")
            if table_data["headers"]:
                print(f"Headers: {' | '.join(table_data['headers'])}")
            for row in table_data["rows"]:
                print(" | ".join(row))
        
        # We'll specifically handle the case details and offence details tables
        # Based on their structure rather than index, as table order may vary
        
        # Find and process Case Details table (typically has two columns with key-value pairs)
        for table in tables:
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) == 2:
                    key = cells[0].text.strip().rstrip('.').replace('  ', ' ').replace(' ', '_').lower()
                    value = cells[1].text.strip()
                    # Determine if this is case detail or current status
                    if key.startswith("registration") or key.startswith("challan") or key.startswith("name") or key.startswith("place"):
                        if value:  # Only add non-empty values
                            case_data["case_details"][key] = value
                    elif key.startswith("received") or key.startswith("verified") or key.startswith("allocated"):
                        if value:  # Only add non-empty values
                            case_data["current_status"][key] = value
        
        # Find and process Offence Details table (usually has multiple columns including offence code, act, section)
        offence_table = None
        for table in tables:
            headers = table.find_elements(By.TAG_NAME, "th")
            header_texts = [h.text.strip().lower() for h in headers]
            if any(text in header_texts for text in ["offence", "act", "section"]):
                offence_table = table
                break
                
        if offence_table:
            # Get headers
            header_cells = offence_table.find_elements(By.TAG_NAME, "th")
            headers = [cell.text.strip().lower().replace(' ', '_') for cell in header_cells if cell.text.strip()]
            
            # Process data rows
            rows = offence_table.find_elements(By.TAG_NAME, "tr")
            
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                
                # Check if this is the proposed fine row
                if cells and len(cells) > 0 and "Proposed Fine" in row.text:
                    case_data["proposed_fine"] = cells[-1].text.strip()
                
                # Process as offence data if not the proposed fine row and matches header count
                elif cells and len(cells) > 0 and len(headers) > 0:
                    offence_data = {}
                    for i, cell in enumerate(cells):
                        if i < len(headers):
                            value = cell.text.strip()
                            if value:  # Only add non-empty values
                                offence_data[headers[i]] = value
                    
                    if offence_data and len(offence_data) > 1:  # Only add rows with actual data
                        case_data["offence_details"].append(offence_data)
        
        # Clean up the data structure to remove empty objects and arrays
        if not case_data["case_details"]:
            del case_data["case_details"]
        if not case_data["current_status"]:
            del case_data["current_status"]
        if not case_data["offence_details"]:
            del case_data["offence_details"]
        if not case_data["proposed_fine"]:
            del case_data["proposed_fine"]
        
        # Print the extracted data as JSON for verification
        print("\nExtracted data as JSON:")
        # print(json.dumps(case_data, indent=2, ensure_ascii=False))
        
        return case_data
           
    except Exception as e:
        print(f"Error extracting table data: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def read_challan_numbers(excel_path):
    try:
        # Check if file exists
        if not os.path.exists(excel_path):
            print(f"Input file {excel_path} not found!")
            return []
            
        # Read Excel file using openpyxl engine
        df = pd.read_excel(excel_path, engine='openpyxl')
        
        # Check if required column exists
        if 'challan_no' not in df.columns:
            print("Error: Column 'challan_no' not found in Excel file!")
            print(f"Available columns: {', '.join(df.columns)}")
            return []
            
        # Get only the first challan number
        challan_no = str(df['challan_no'].iloc[0]).strip()
        print(f"Processing first challan number: {challan_no}")
        return [challan_no]  # Return as list with single item
        
    except Exception as e:
        print(f"Error reading Excel: {str(e)}")
        print("Please ensure you have installed required packages:")
        print("pip install pandas openpyxl")
        return []

def save_to_excel(data_list):
    try:
        if not data_list:
            print("No data to save!")
            return False
            
        # Convert list of dictionaries to DataFrame
        df = pd.DataFrame(data_list)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # output_file = f"challan_results_{timestamp}.xlsx"
        
        # # Save to Excel using openpyxl engine
        # df.to_excel(output_file, index=False, engine='openpyxl')
        # print(f"Results saved to {output_file}")
        
        # Also save as JSON for easier inspection
        with open(f"challan_results_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(data_list, f, indent=2, ensure_ascii=False)
        print(f"Results also saved to challan_results_{timestamp}.json")
        
        return True
        
    except Exception as e:
        print(f"Error saving to Excel: {str(e)}")
        print("Please ensure you have installed required packages:")
        print("pip install pandas openpyxl")
        return False

from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "online", "message": "Challan checking service is running"})

@app.route('/search', methods=['GET'])
def search_challan():
    challan_no = request.args.get('challan')
    state_id = request.args.get('state')
    if state_id:
        state_id = state_id.upper()
    
    # Check if either challan_no or state_id is provided
    if challan_no and state_id:
        try:
            driver = setup_driver()
            
            driver.get("https://vcourts.gov.in/virtualcourt/index.php")
    
            # Select department and proceed
            dept_result = select_department(driver, state_id)
            if not dept_result:
                return jsonify({"error": "Failed to select department"}), 500
                
            time.sleep(1)

            proceed_result = click_proceed_button(driver)
            if not proceed_result:
                return jsonify({"error": "Failed to proceed"}), 500
                
            time.sleep(2)
            
            # Enter challan details with error handling
            tab_result = click_challan_vehicle_tab(driver)
            if not tab_result.get("status"):
                return jsonify({"error": tab_result.get("message")}), 500
                
            time.sleep(2)
            enter_challan_number(driver, challan_no)

            submit_captcha(driver)
            time.sleep(4)
            
            # Get case details
            click_view_link(driver)
            time.sleep(1)
            
            case_data = extract_table_data(driver)
            
            # Clean up
            driver.quit()
            
            if case_data:
                # Return JSON response
                return jsonify(case_data)
            else:
                return jsonify({"error": "No data found for the given challan number"}), 404
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if 'driver' in locals():
                driver.quit()
    else:
        return jsonify({"error": "Missing challan number or state ID"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
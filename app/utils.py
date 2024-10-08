# utils.py
import os
from werkzeug.utils import secure_filename
from flask_mail import Message
from app import mail
import json
import PyPDF2
import importlib.util
import re 

# Get the absolute path to the parent directory of the current folder
parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
# Construct the full path to the gpt.py file in the model folder using a raw string
model_file_path = os.path.join(parent_directory, r'app\model', 'gpt.py')

# Load the model
spec = importlib.util.spec_from_file_location("train", model_file_path)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)

def allowed_file(filename):
    """Check if the uploaded file has a valid extension."""
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, upload_folder):
    """Save uploaded file securely."""
    if allowed_file(file.filename):
        # Create the upload directory if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)

        # Secure the filename and create the complete file path
        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_folder, filename)

        # Save the file to the specified path
        file.save(filepath)
        
        # Return just the filename, not the full path
        return filename
    return None

def input_pdf_text(uploaded_file):
    """Extract text from the uploaded PDF file."""
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()
    return text

def extract_match_percentage(response):
    """Extract match percentage from the response."""
    try:
        data = json.loads(response)
        if "Criteria Match" in data:
            match_percentage = data["Criteria Match"]
            if isinstance(match_percentage, (int, float)):
                return match_percentage
            elif isinstance(match_percentage, str) and match_percentage.endswith('%'):
                return float(match_percentage.strip('%'))
    except ValueError:
        pass
    return None

def extract_missing_keywords(response):
    """Extract missing keywords from the response."""
    try:
        data = json.loads(response)
        if "MissingKeywords" in data and isinstance(data["MissingKeywords"], list):
            return data["MissingKeywords"]
    except ValueError:
        pass
    return []

def generate_evaluation_summary(response):
    """Generate evaluation summary from the response."""
    try:
        data = json.loads(response)
        if "Evaluation Summary" in data:
            return data["Evaluation Summary"]
    except ValueError:
        pass
    return "Evaluation summary not available"

def generate_company_name(response):
    """Generate company name from the response."""
    try:
        data = json.loads(response)
        if "Company Name" in data:
            return data["Company Name"]
    except ValueError:
        pass
    return "Unknown Company"

def evaluate_bids(bid_documents, general_tender_description, project_timeline, bid_amount, required_experience, additional_criteria):
    """Use GPT-4 to evaluate bids and return a ranked list."""
    evaluation_results = []

    current_directory = os.path.dirname(__file__)  
    bids_directory = os.path.abspath(os.path.join(current_directory, '..', 'uploads', 'bids'))  

    for bid_id, document_path in bid_documents:  # Unpack the tuple directly
        try:
            # Create the full document path using the document name
            full_document_path = os.path.join(bids_directory, document_path)
            text = input_pdf_text(full_document_path)

            input_prompt = f"""
            Hey, act like a skilled tender evaluation system with a deep understanding of procurement processes, contract management, and evaluation criteria. Your task is to evaluate the tender document based on the given evaluation criteria.
            Assign the percentage Matching based on the criteria and provide feedback. The feedback shouldn't mention areas of improvement i.e. To improve the evaluation, these criteria should be included and evaluated thoroughly. It should just be feedback on why it got the score (match percentage) and why it was approved and not approved based on Criteria for evaluation. Be comprehensive and exhaustive. Your score (match percentage) should be thought critically.
            The Project Timeline, Required Experience, and Bid Amount have higher importance in evaluation. The additional criteria are an icing on the cake.
            Tender Document: {text}
            General Tender Description: {general_tender_description}
            Project Timeline: should be less than {project_timeline} years
            Bid Amount: should be less than ${bid_amount}
            Required Experience: should be greater than or equal to {required_experience} years
            Additional Criteria Description: {additional_criteria}

            I want the response as per below structure:
            {{"Company Name" : "","Criteria Match": "%", "MissingKeywords": [], "Evaluation Summary": ""}}
            """
            response = model.get_gemini_response(input_prompt)

            # Clean the response to remove any invalid control characters
            response = response.replace('\r', '').replace('\n', '')
            response = re.sub(r'[\x00-\x1F\x7F]', '', response)  # Remove control characters

            try:
                response_data = json.loads(response)
                company_name = response_data.get("Company Name", "Unknown")
                match_percentage = int(response_data.get("Criteria Match", "0%").replace('%', '')) if response_data.get("Criteria Match") else None
                missing_keywords = response_data.get("MissingKeywords", [])
                evaluation_summary = response_data.get("Evaluation Summary", "")

                if match_percentage is not None:
                    approved_status = "Approved" if match_percentage >= 70 else "Not Approved"
                else:
                    approved_status = "Not Approved"

                evaluation_results.append({
                    "bid_id": bid_id,  
                    "Company": company_name,
                    "Score": match_percentage,
                    "Missing Keywords": missing_keywords,
                    "Approved/Not": approved_status,
                    "Evaluation Summary": evaluation_summary
                })

            except json.JSONDecodeError as json_err:
                evaluation_results.append({
                    "bid_id": bid_id,
                    "Company": None,
                    "Score": None,
                    "Missing Keywords": [],
                    "Approved/Not": "Error",
                    "Evaluation Summary": f"Error parsing response for {document_path}: {str(json_err)}"
                })

        except Exception as e:
            evaluation_results.append({
                "bid_id": bid_id,
                "Company": None,
                "Score": None,
                "Missing Keywords": [],
                "Approved/Not": "Error",
                "Evaluation Summary": f"Error processing {document_path}: {str(e)}"
            })
            continue

    evaluation_results.sort(key=lambda x: x["Score"] if x["Score"] is not None else float('-inf'), reverse=True)

    return evaluation_results

def send_email(subject, recipient, body):
    """Send an email notification."""
    msg = Message(subject, recipients=[recipient])
    msg.body = body
    mail.send(msg)
import boto3
import json
from openai import OpenAI
import re
import os

client = OpenAI(
    api_key= os.environ.get("OpenAI_key")
)

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
lambda_client = boto3.client('lambda')

S3_BUCKET_HTML = 'smartresume-html'
S3_BUCKET_PDF = 'smartresume-result'

DYNAMODB_TABLE_NAME = 'smartresume'
COL_BASIC_DTLS = 'user_name'
COL_COMMUNICATION = 'DOB'
COL_EDUCATION = 'education'
COL_TARGET_JOB = 'headline'
COL_ACHIEVEMENTS = 'achievements'
COL_SKILLSETS = 'skillsets'
COL_EXPERIENCE = 'orgs'

table = dynamodb.Table(DYNAMODB_TABLE_NAME)

REGION = 'us-east-1'

TRIGGER_PARAM = COL_EDUCATION # for invoking OpenAI

def lambda_handler(event, context):
    
    try:
        print("event in POST: ", event)

        # For First Page, id = session id. Next page onwards, sequence = session id
        sequence = event.get('sequence')
        if sequence != '1':
            event['id'] = sequence
            print("session parameter['id']: " , event['id'])
        
        pk = event['id'] # partition key for table
        param_names = list(event.keys())
        for key, value in event.items():
            if key == 'id' or key == 'sequence': #skip id and sequence
                continue
            save_record(pk, key, value)
        
            if(key == TRIGGER_PARAM):
                print(f"Inside TRIGGER_PARAM.." )
                # Fetch the DB record based on the session id passed
                items = get_records(pk)
                data = {}
                for item in items:
                    data[item['parameter']] = item['user_input']

                basicDetail = data[COL_BASIC_DTLS]
                communication = data[COL_COMMUNICATION]
                education = data[COL_EDUCATION]
                target_job = data[COL_TARGET_JOB]
                achievement = data[COL_ACHIEVEMENTS]
                skill = data[COL_ACHIEVEMENTS]
                experience = data[COL_EXPERIENCE]
                
                content = __consult_openai__(basicDetail, communication, education, target_job, achievement, skill, experience)
                
                #print("HTMLTemplate(content): ", content)
                html_file_name = create_html(sequence, content)                

    except Exception as e:
        print("ErrorException in catch block: ", str(e))
        #raise Exception("Exception by default")


def save_record(pk, key, value):
    try:
        
        item = {
            'id': pk,
            'parameter': key,
            'user_input': value
        }
        table.put_item(Item=item)

    except Exception as e:
        print("Error saving parameters: ", str(e))

def get_records(id):
    try:
        print("id from get_records: ", id)
        partition_key_value = id
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('id').eq(partition_key_value)
        )
        items = response.get('Items')
        if not items:
            print('No record found')
        
        # Print the records
        #for item in items:
        #   print("record: ", item)

        return items
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def get_record_pk(id):
    try:
        print("id in get_record_pk: ",id)
        response = table.get_item(
            Key={
                'id': id
            }
        )
        item = response.get('Item')

        print("Data from get_record_pk: ", item)

        if not item:
            print('No record found')
        
        return item

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def __consult_openai__(basicDetail, communication, education, target_job, achievement, skill, experience):
    print("Inside __consult_openai__")
    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "developer",
                "content": "Create a html resume based on user input"
            },
            {
                "role": "developer",
                "content": "can you please share your basic details e.g. name , sex and date of birth"
            },
            {
                "role": "user",
                "content": basicDetail
            },
            {
                "role": "developer",
                "content": "can you please provide your contact details like email address, phone number and physical address"
            },
            {
                "role": "user",
                "content": communication
            },
            {
                "role": "developer",
                "content": "please input your education details"
            },
            {
                "role": "user",
                "content": education
            },
            {
                "role": "developer",
                "content": "please provide your skill details"
            },
            {
                "role": "user",
                "content": skill
            },
            {
                "role": "developer",
                "content": "Do you have any achievements?"
            },
            {
                "role": "user",
                "content": achievement
            },
            {
                "role": "developer",
                "content": "please provide experience details"
            },
            {
                "role": "user",
                "content": experience
            },
            {
                "role": "developer",
                "content": "what kind of job you are looking for"
            },
            {
                "role": "user",
                "content": target_job
            },
            {
                "role": "developer",
                "content": "Please create a one page html resume with resume summary in 5 bullets. Resume should contain sections like education, skills and experience etc. "
            }
        ]
    )
    print("AI response done")
    return response.output_text

def create_html(file_id, content):
    print("Inside create_html: ") 
    filename = file_id + ".html"

    # Sanitize the content to pickup only the HTML part - '''html<start>...<end>'''
    san_content = extract_html_block(content)

    # Use /tmp directory in Lambda (only writable space)
    tmp_file_path = '/tmp/output.html'

    # Write the HTML to a file
    with open(tmp_file_path, 'w', encoding='utf-8') as f:
        f.write(san_content)

    # Upload the file to S3
    try:
        s3.upload_file(
            Filename=tmp_file_path,
            Bucket=S3_BUCKET_HTML,
            Key=filename,
            ExtraArgs={'ContentType': 'text/html'}
        )
    except Exception as e:
        print(f"Error uploading to S3: {e}")


def extract_html_block(content):
    start_marker = "```html"
    end_marker = "```"

    # Find the start of the html block
    start_index = content.find(start_marker)
    if start_index == -1:
        return "Start marker not found"

    # Move past the start marker
    content_after_start = content[start_index + len(start_marker):]

    # Find the end marker in the remaining content
    end_index = content_after_start.find(end_marker)
    if end_index == -1:
        return "End marker not found"

    # Extract and clean the html block
    extracted = content_after_start[:end_index].strip()
    return extracted

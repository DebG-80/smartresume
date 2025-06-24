# Arhitecture
![/images/ChatGPT Image Jun 24, 2025, 01_00_01 PM.png]

## Typical work flow

1. User sends an HTTP POST request to the / smartresume API endpoint, specifying the job parameters in the request body.

2. The smartresume API, which is an API Gateway REST API, returns an HTTP response that contains the request Id identifier. This identifier will act as the session id w.r.t. the particular ..

3. The smartresume API invokes asynchronously the event-processing Lambda function. 

4. The event-processing function processes the event by invoking an OPENAI API, uploads the generated PDF in S3 smartresume bucket bucket and saves the corresponding URL in smartresume Amazon DynamoDB table against session id from step 2 as the key.

5. User sends an HTTP GET request to the /final API endpoint, with the session id from step 2.

6. The /final API queries the smartresume DynamoDB table to retrieve the S3 URL.

7. The /final API returns the file URL of the generated PDF.

8. User would access the PDF file using the URL. 

9. If the event processing fails, it is sent to the error-handling lambda function.

10. The error-handling function puts the session id in the smartresume DynamoDB table along with relevant message.

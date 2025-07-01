# Arhitecture Design
![Design](images/ChatGPT_Image_Architecture.png)

# Typical work flow

1. Landing page of the website is hosted on S3, but it can only be accessed through Cloudfront URL for HTTP to HTTPS redirection. This is only for accessing the first page, hence represnted outside the main AWS block. 
2. User sends an HTTP POST request to the '/' of smartresume API endpoint, specifying the required information in the request body.
3. The smartresume API, which is an API Gateway REST API, returns an HTTP response to the user that contains the request Id identifier. This identifier will act as the session id w.r.t. the particular communication series with the user & application.
4. The smartresume API invokes asynchronously the event-processing Lambda function. 
5. The event-processing Lambda function processes the event by saving the data in DynamoDB table first, then invoking an OpenAI API & writing the response into a HTML file, & finally uploading the same in S3. Key in S3 is the session Id shared with the user in second step.
6. User sends a HTTP GET request to the /final API endpoint for requesting the final output, with the session id from step 2. 
7. This request is synchronous, hence it invokes the event-processing lambda function in the same flow. It checks if the file has been created in S3. It will return the hyperlink of the file if generarated, otherwise a suitable message.
8. The /final API endpoint returns the HTTP response to the user. 
9. If the smartresume lambda function somehow fails, it is sent to the error-handling smartresumeError lambda function. 
10. The smartresumeError lambda function puts the session id in the same smartresume DynamoDB table along with any relevant message.

# Built with

* AWS API Gateway ![AWS API Gateway](images/Aws-Api-Gateway.png)
* AWS Cloudfront ![AWS Cloudfront](images/Aws-Cloudfront.png)
* AWS DynamoDB ![AWS DynamoDB](images/Aws-Dynamodb.png)
* AWS Lambda ![AWS Lambda](images/Aws-Lambda.png)
* AWS S3 ![AWS S3](images/Aws-S3.png)
* Python ![Python](images/Python.png)
* OpenAI ![OpenAI](images/Openai.png)

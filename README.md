# Arhitecture Design
![Design](images/ChatGPT_Image_Architecture.png)

# Typical work flow

1. User sends an HTTP POST request to the '/' of smartresume API endpoint, specifying the job parameters in the request body.

2. The smartresume API, which is an API Gateway REST API, returns an HTTP response that contains the request Id identifier. This identifier will act as the session id w.r.t. the particular ..

3. The smartresume API invokes asynchronously the event-processing Lambda function. 

4. The event-processing function processes the event by invoking an OPENAI API, uploads the generated PDF in S3 smartresume bucket bucket and saves the corresponding URL in smartresume Amazon DynamoDB table against session id from step 2 as the key.

5. User sends an HTTP GET request to the /final API endpoint, with the session id from step 2.

6. This request is synchronous, hence it invokes lambda function in the same flow. It queries the smartresume DynamoDB table to retrieve the S3 URL. 

7. The Lambda function fetches the S3 file URL based on the session id from dynamodb table. Then file itself is then fetched fromo S3 and written as HTTP response.

8. The /final API endpoint returns an HTTP response that contains the requested file. 

9. If the event processing fails, it is sent to the error-handling lambda function.

10. The error-handling function puts the session id in the smartresume DynamoDB table along with relevant message.

# Built with

* [![Lambda](https://images.app.goo.gl/mw5MLWo8zF1WrPWH9)]
* [![React][React.js]][React-url]
* [![Vue][Vue.js]][Vue-url]
* [![Angular][Angular.io]][Angular-url]
* [![Svelte][Svelte.dev]][Svelte-url]
* [![Laravel][Laravel.com]][Laravel-url]

This is a simple 'serverless application' that allows you to create a VM in
an SDDC on VMware Cloud on AWS using a few cool tools including: Lambda,
Cognito, S3, and VMware Cloud on AWS.

Matt Dreyer
August 16, 2017


To make this work you need to do the following:

1. Make sure that the vCenter in your SDDC is open to the world, or painfully configure Lambda
   to run in an VPC and NAT to a specific IP address (which requires even more IAM roles for VPC access).
2. Create a working VM, and then Clone it to an OVF template in Content Library
3. Use the vCenter API browser to discover the UUID of the your OVF template
4. Update the HTML in index.html to match the UUID(s) of the VMs you wish to deploy
5. Create a new Lambda function and upload vm-request-form.zip as your code
6. Create a new Cognito "Federated Identity" for "anonymous access"
7. Update the javascript in index.html to match your new Cognito role
8. Create an S3 bucket and configure it for Webhosting
9. Upload index.html and vmc-sticker.png into your bucket
10. Muck with IAM until Lambda and Cognito get along together 
   (required Cognito role permissions are AWSLambdaExecute and AWSLambdaRole)
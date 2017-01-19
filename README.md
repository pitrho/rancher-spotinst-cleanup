# Rancher-Spotinst-Cleanup

This repo contains a lambda function that could be used to clean up Spotinst
hosts in Rancher after they have been terminated.

## How it works?

Spotinst comes with the ability to send notifications to AWS SNS when a host
is terminated. When a notification is sent, SNS will trigger the execution of
the lambda function in AWS, and then the function will simply interact with
Rancher to remove the desired host.

## How to make changes and build a new deployment package?

1. Clone this repo and cd into the directory

2. Create a python virtual environment. Do not use virtualenvwrapper, use
virtualenv instead.

    $ virtualenv env

2. Activate the virtual environment and install the requirements

    $ . ./env/bin/Activate
    $ pip install -r requirements.txt

4. If you added new requirements, then you need to enhance the build script
to include them. See the `Copy the sources` section in the build script.

3. Once you have made the necessary changes, use the build script to create
the package.

    $ ./build.sh


## How to deploy the package to AWS Lambda?

1. Go to AWS SNS and create a new topic (e.g spotinst-messages)

2. In Spotinst, under your Elasticgroup, create a new notification with the
the following parameters:

    a. SNS Topic ARN: Select the newly created SNS topic from above

    b. Event Type: Instance Terminated

    c. Format:
        ```
        {
            "instance_id": "%instance-id%",
            "event": "%event%",
            "resource_id": "%resource-id%",
            "resource_name": "%resource-name%",
            "rancher_project_id": "1a2159"
        }
        ```

        IMPORANT!!! Make sure to change the rancher_project_id in the format
        object above to the correct project id from your rancher environment.

3. Now create the AWS lambda function
    a. From te AWS Lambda web console click `Create a Lambda Function`

    b. Select `Blank Function` under the `Select Blueprint` section

    c. Under `Confiure Trigger` click the blank trigger box, select SNS, select
the SNS topic created before and click `Enable trigger`

    d. Under `Configure Function`, select the following parameters:
        * Name: Some name for the function
        * Description: Give it a good Description
        * Runtime: Python 2.7
        * Under `Code entry type`, select `Upload a .ZIP file` and click the
        upload button to select the ZIP file created with the build script.
        * Under `Environment variables` add the following:
            * RANCHER_URL = The rancher server url (e.g https://rancher.pitrho.com)
            * RANCHER_ACCESS_KEY = The Rancher API access key
            * RANCHER_SECRET_KEY = The Rancher API secret keys
        * Under `Lambda function handler and role` enter the follwing:
            * Handler: handler.lambda_handler
            * Role: Select the role needed to execute the lambda function
        * Under `Advanced settings` select any parameters that you need to
        execute the funciton

4. Under the `Review` section validate that you configuration parameters are
correct and click Create Function to finish.

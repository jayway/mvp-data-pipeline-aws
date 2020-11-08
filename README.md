# MVP Data Pipeline

Prod: ![Deploy](https://github.com/erikmunkby/mvp-data-pipeline-aws/workflows/CDK%20Deploy/badge.svg?branch=master)
, QA: ![Deploy](https://github.com/erikmunkby/mvp-data-pipeline-aws/workflows/CDK%20Deploy/badge.svg?branch=qa)

This is a "plug n play" MVP version for a data pipeline, best described 
by the following image:
![Pipeline Image](https://github.com/erikmunkby/mvp-data-pipeline-aws/blob/master/pipeline_image.png?raw=true)

Contains code for:

- Data pipeline in AWS
- Jupyter notebook for testing
- Github actions workflow for cdk deploy

## Requirements
Must have an AWS account with deploy access rights.

## Deploy

- Fork the repository
- Install the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- Install [poetry](https://python-poetry.org/)
- Install AWS CDK

    `$ npm install -g aws-cdk`
    
- (Optional) Set poetry config settings to local virtual environments

    `$ poetry config virtualenvs.in-project true`

- Install dependencies and build Virual Environment

    `$ poetry install`
    
- Start the venv shell

    `$ poetry shell`
    
- (Optional) Load a specific AWS profile, default used otherwise.

    `$ export AWS_PROFILE=<your profile name>`

- Set up AWS CDK in the AWS environment

    `$ cdk bootstrap`
    
- Set up your github secrets with the following parameters (used for deploys in github actions):
    - AWSPUBLICKEY
    - AWSSECRETKEY
    
- Change names and ids for stack resources (in `pipeline_stack.py`). 
Bucket name is required to change as it has to be globally unique, rest optional.
    
- Push to Master and watch your github actions deploy!

## Development
If you want to make changes there is also a qa branch. Pushing against the qa
branch will deploy everything with separate naming and on a different region.
A useful cdk function when making changes is cdk diff that will tell you what
changes will be made to the stack.

    $ cdk diff

## Set up Jupyter
- Start the poetry shell (if you haven't already)
    
    `$ poetry shell`
    
- (Optional) Load a specific AWS profile, default used otherwise.

    `$ export AWS_PROFILE=<your profile name>`
    
- Build a jupyter kernel that the notebooks can use

    `$ python -m ipykernel install --user --name mvp-pipeline`
    
- Load up a jupyter notebook

    `$ jupyter notebook`
    
- Add `api_creds.json` file with the following parameters filled:
```
{
    "endpoint": "https://*******.amazonaws.com/prod/",
    "api-key": "******"
}
```

## Adding Packages
If you want to install and work with new python packages you can add them by:

    $ poetry add <package name here>

If your Lambda also needs the package installed, add it in the `requirements.txt` file found in your lambda folder. 
The github actions will install and package them for you.

## Taking it for a spin
In the `jupyter` folder there exists 2 notebooks:

- **api_tests:** For querying the API.
- **analyse:** To help you download and start to analyse your data! 

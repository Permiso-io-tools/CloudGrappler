![LogLicker](https://permiso.io/hubfs/Cloud-Grappler.png "CloudGrappler Logo")
# CloudGrappler
**Permiso:** https://permiso.io  
**Read our release blog:** https://permiso.io/blog/cloudgrappler-a-powerful-open-source-threat-detection-tool-for-cloud-environments

CloudGrappler is a purpose-built tool designed for effortless querying of high-fidelity and single-event detections related to well-known threat actors in popular cloud environments such as AWS and Azure.

## Notes

To optimize your utilization of CloudGrappler, we recommend using shorter time ranges when querying for results. This approach enhances efficiency and accelerates the retrieval of information, ensuring a more seamless experience with the tool.

## Required Packages

>```bash
>pip3 install -r requirements.txt
>```

## Cloning cloudgrep locally

To clone the cloudgrep repository locally, run the clone.sh file. Alternatively, you can manually clone the repository into the same directory where CloudGrappler was cloned.

>```bash
>chmod +x clone.sh
>./clone.sh
>```

## Input

This tool offers a CLI (Command Line Interface). As such, here we review its use:

## Example 1 - Running the tool with default queries file

Define the scanning scope inside data_sources.json file based on your cloud infrastructure configuration. The following example showcases a structured data_sources.json file for both AWS and Azure environments:

### Note

Modifying the source inside the queries.json file to a wildcard character (*) will scan the corresponding query across both AWS and Azure environments.

```json
{
  "AWS": [
    {
      "bucket": "cloudtrail-logs-00000000-ffffff",
      "prefix": [
        "testTrails/AWSLogs/00000000/CloudTrail/eu-east-1/2024/03/03",
        "testTrails/AWSLogs/00000000/CloudTrail/us-west-1/2024/03/04"
      ]
    },
    {
      "bucket": "aws-kosova-us-east-1-00000000"
    }

  ],
  "AZURE": [
    {
      "accountname": "logs",
      "container": [
        "cloudgrappler"
      ]
    }
  ]
}
```

Run command

```python3 main.py```

## Example 2 - Permiso Intel Use Case

``` python3 main.py -p ```

``` text
[+] Running GetFileDownloadUrls.*secrets_ for AWS 
[+] Threat Actor: LUCR3 
[+] Severity: MEDIUM 
[+] Description: Review use of CloudShell. Permiso seldom witnesses use of CloudShell outside of known attackers.This however may be a part of your normal business use case. 

```

## Example 3 - Generate report

``` python3 main.py -p -jo ```

``` text
reports
└── json
    ├── AWS
    │   └── 2024-03-04 01:01 AM
    │       └── cloudtrail-logs-00000000-ffffff--
    │           └── testTrails/AWSLogs/00000000/CloudTrail/eu-east-1/2024/03/03
    │               └── GetFileDownloadUrls.*secrets_.json
    └── AZURE
        └── 2024-03-04 01:01 AM
            └── logs
                └── cloudgrappler
                    └── okta_key.json
```

## Example 4 - Filtering logs based on date or time

```python3 main.py  -p  -sd 2024-02-15  -ed  2024-02-16```


## Example 5 - Manually adding queries and data source types

```python3 main.py  -q “GetFileDownloadUrls.*secret”, ”UpdateAccessKey”  -s '*'```


## Example 6 - Running the tool with your own queries file

``` python3 main.py -f new_file.json ```


### Running in your Cloud and Authentication [cloudgrep](https://github.com/cado-security/cloudgrep)

#### AWS

Your system will need access to the S3 bucket. For example, if you are running on your laptop, you will need to [configure the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).
If you are running on an EC2, an [Instance Profile](https://devopscube.com/aws-iam-role-instance-profile/) is likely the best choice.

If you run on an EC2 instance in the same region as the S3 bucket with a [VPC endpoint for S3](https://aws.amazon.com/blogs/architecture/overview-of-data-transfer-costs-for-common-architectures/) you can [avoid egress charges](https://awsmadeeasy.com/blog/aws-s3-vpc-endpoint-transfer-cost-reduction/).
You can authenticate in a [number of ways](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).

#### Azure

The simplest way to authenticate with Azure is to first run:

``` az login ```

This will open a browser window and prompt you to login to Azure.

# socless_repo_parser
Takes a socless repo names and queries github api for their raw lambda .py files and serverless.yml, parsing key elements into a single json output

## Usage

By default, output is saved to `./socless_info.json`

### For open source:
```bash
python3 main.py "socless, socless-slack" --org-name="<your_github_organization_or_twilio-labs>"
```

### For Github Enterprise:
First set environment variables for your Github Enterprise Domain and a Personal Access Token
```bash
export GHE_DOMAIN=<Your_GHE_Domain.com>
export GHE_TOKEN=<Personal_Access_Token>
```
Then run this script with flag `--ghe=True`
```bash
python3 main.py "socless, socless-slack" --org-name="<github_organization>" --ghe=True
```



## Example of scraper output
```json
{
    "integrations": [
        {
            "meta": {
                "repo_url": "https://www.github.com/twilio-labs/socless-slack",
                "integration_family": "socless-slack"
            },
            "functions": [
                {
                    "meta": {
                        "lambda_folder_name": "check_user_in_channel",
                        "deployed_lambda_name": "socless_slack_check_user_in_channel",
                        "serverless_lambda_name": "CheckIfUserInChannel",
                        "supported_in_playbook": true
                    },
                    "resource_type": "socless_task | socless_interaction",
                    "arguments": [
                        {
                            "name": "user_id",
                            "data_type": "string",
                            "required": true,
                            "description": "",
                            "placeholder": ""
                        },
                        {
                            "name": "target_channel_id",
                            "data_type": "string",
                            "required": true,
                            "description": "",
                            "placeholder": ""
                        }
                    ],
                    "return_statements": [
                        {
                            "ok": true
                        },
                        {
                            "ok": false
                        }
                    ]
                }
            ]
        },
        {
            "meta": {
                "repo_url": "https://www.github.com/twilio-labs/socless",
                "integration_family": "socless"
            }, 
            "functions" : [...]
        }
    ]
}

```

# TODO
- [ ] add meta to each function
  - [ ] "meta" : {
           "lambda_folder_name": "check_user_in_channel",
            "deployed_lambda_name": "socless_slack_check_user_in_channel",
            "serverless_lambda_name": "CheckIfUserInChannel",
            "supported_in_playbook" : true
        }
- [ ] add resource_type (probably by trigger_id arg presence)
- [ ] add meta to integration family
  - [ ] {
           "repo_url" : "https://www.github.com/twilio-labs/socless-slack",
           "integration_family" : "socless-slack"
       }
- [ ] add `data_type` & `placeholder` to each argument
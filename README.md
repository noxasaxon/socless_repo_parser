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
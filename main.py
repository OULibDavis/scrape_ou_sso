import requests
from lxml import etree

username = ""
password = ""

s = requests.Session()

resp = s.get("https://accounts.ou.edu/")

if "sso.ou.edu" in resp.url:
    print("Redirected to SSO sign-in")
    # Send credentials to SSO page
    sso_resp = s.post(resp.url, data={"pf.username": username, "pf.pass": password})
    # Parse out application authentication page and SAML token
    sso_content = sso_resp.content
    tree = etree.HTML(sso_content)
    redirect_form = tree.cssselect("form")[0]
    redirect_url = redirect_form.get("action")
    saml_token = redirect_form.cssselect("input")[0].get("value")
    print(redirect_url, saml_token)
    # Submit SAML token to application authentication page - this redirects to application page
    resp = s.post(redirect_url, data={"SAMLResponse": saml_token})

# Parse content on application page behind SSO auth
tree = etree.HTML(resp.content)
# Fetch the email alias item on the accounts page as an example
print(tree.cssselect("#EmailSettings_EmailAlias")[0].get("value"))

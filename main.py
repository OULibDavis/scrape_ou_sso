import requests
from lxml import etree
from urllib.parse import urlparse
from secrets import username, password

s = requests.Session()

resp = s.get("https://accounts.ou.edu/")

if "sso.ou.edu" in resp.url:
    print("Redirected to SSO sign-in")

    # Make sure we have the valid login url to send authentication
    tree = etree.HTML(resp.content)
    login_url = tree.cssselect("#loginForm")[0].get("action")
    parsed_url = urlparse(login_url)
    if not parsed_url.netloc:
        login_url = f"https://sso.ou.edu{parsed_url.path}"

    # Send credentials
    sso_resp = s.post(login_url, data={"pf.username": username, "pf.pass": password})

    # Parse out application authentication page for required arguments to pass to site
    sso_content = sso_resp.content
    if b"<title>Error</title>" in sso_content:
        print("Failed to get SAML token - received error response from identity provider")
        exit(1)
    tree = etree.HTML(sso_content)
    redirect_form = tree.cssselect("form")[0]
    redirect_url = redirect_form.get("action")
    form_args = {arg.get("name"): arg.get("value") for arg in redirect_form.cssselect("input")}
    print(redirect_url, form_args)

    # Submit SAML token to application authentication page - this redirects to application page
    resp = s.post(redirect_url, data=form_args)


#### The following is specific to the accounts example ####

# Parse content on application page behind SSO auth
tree = etree.HTML(resp.content)
# Fetch the email alias item on the accounts page as an example
print(tree.cssselect("#EmailSettings_EmailAlias")[0].get("value"))

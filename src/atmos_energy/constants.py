# Default billing period for usage data retrieval
DEFAULT_BILLING_PERIOD = 'Current'
DEFAULT_USAGE_MONTHS = 1

# URLs for login and data download
LOGIN_FORM_ID_URL = 'https://www.atmosenergy.com/accountcenter/logon/login.html'
LOGIN_URL = 'https://www.atmosenergy.com/accountcenter/logon/authenticate.html'
LOGGED_IN_URL = 'https://www.atmosenergy.com/accountcenter/landing/landingScreen.html'
LOGOUT_URL = 'https://www.atmosenergy.com/accountcenter/logout/index.html'

DOWNLOAD_URL = 'https://www.atmosenergy.com/accountcenter/usagehistory/dailyUsageDownload.html?&billingPeriod={billing_period}&{timestamp}'
DOWNLOAD_CONTENT_TYPE = 'application/vnd.ms-excel'

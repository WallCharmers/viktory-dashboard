# 🇺🇦 Viktory Dashboard

WallCharmers real-time analytics dashboard with Amazon SP-API integration.

## Features

- 🔐 **Password Protection** - Secure access to your dashboard
- ⚡ **Real-time Data** - Live Amazon SP-API integration with demo fallback
- 📊 **Interactive Analytics** - Period-based views (Today/Week/Month)
- 📈 **Rich Visualizations** - Charts and tables with Plotly
- 🛍️ **Product Performance** - Detailed SKU analysis with filtering/sorting
- 🌟 **Mobile Responsive** - Works on all devices

## Deployment on Streamlit Community Cloud

### 1. Prepare Repository

1. Fork or clone this repository to your GitHub account
2. Make sure it's set to **Private** if it will contain sensitive data

### 2. Configure Secrets

1. Go to your Streamlit Cloud app settings
2. In the "Secrets" section, add your configuration:

```toml
# Required: App password
app_password = "your_secure_password_here"

# Optional: For live Amazon data
[sp_api]
client_id = "your_sp_api_client_id"
client_secret = "your_sp_api_client_secret" 
refresh_token = "your_sp_api_refresh_token"

[aws]
access_key_id = "your_aws_access_key_id"
secret_access_key = "your_aws_secret_access_key"
region = "us-east-1"
role_arn = "arn:aws:iam::your_account:role/your_role_name"

[wallcharmers]
seller_id = "your_seller_id"
marketplace_id = "ATVPDKIKX0DER"
```

### 3. Deploy

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repository
3. Set main file path: `streamlit_app.py`
4. Deploy!

## Local Development

### Prerequisites

- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd viktory-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create local secrets (copy from example):
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

4. Edit `.streamlit/secrets.toml` with your values

5. Run locally:
```bash
streamlit run streamlit_app.py
```

## Data Sources

- **🟢 Live**: Real-time Amazon SP-API data (requires configuration)
- **🔶 Demo**: Realistic demo data based on WallCharmers patterns
- **📊 Historical**: January 2026 spreadsheet data for monthly comparisons

## Architecture

- **Frontend**: Streamlit with Plotly visualizations
- **Backend**: Python with SP-API integration
- **Auth**: Session-based password protection
- **Data**: Amazon SP-API + fallback demo data
- **Deployment**: Streamlit Community Cloud

## File Structure

```
viktory-dashboard/
├── streamlit_app.py          # Main Streamlit application
├── requirements.txt          # Python dependencies  
├── README.md                # This file
├── .streamlit/
│   └── secrets.toml.example # Configuration template
├── backend/                 # SP-API integration modules
│   ├── sp_api_aws.py
│   ├── sp_api_client.py
│   └── app.py              # Original Flask backend
└── .gitignore              # Excludes secrets and cache files
```

## Security Notes

- Never commit real secrets to git
- Use strong passwords for app access
- Keep your GitHub repository private
- Regularly rotate API keys and passwords
- Monitor Streamlit Cloud usage and access logs

## Support

For issues or questions, please check the repository issues or create a new one.

---

**Ви готові до перемоги! 🇺🇦**
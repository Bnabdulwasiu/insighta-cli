# Insighta CLI

Command-line interface for the Insighta Labs+ platform.

## Installation

```bash
git clone https://github.com/Bnabdulwasiu/insighta-cli.git
cd insighta-cli
pip install -e .
```

After installation, `insighta` is available globally from any directory.

---

## Commands

### Auth
```bash
insighta login       # authenticate with GitHub OAuth
insighta logout      # revoke session and clear credentials
insighta whoami      # show current logged in user
```

### Profiles
```bash
# List
insighta profiles list
insighta profiles list --gender male
insighta profiles list --country NG
insighta profiles list --age-group adult
insighta profiles list --min-age 25 --max-age 40
insighta profiles list --sort-by age --order desc
insighta profiles list --page 2 --limit 20

# Get single
insighta profiles get <id>

# Search (natural language)
insighta profiles search "young males from nigeria"
insighta profiles search "adult females from kenya above 30"

# Create (admin only)
insighta profiles create --name "Harriet Tubman"

# Export
insighta profiles export --format csv
insighta profiles export --format csv --gender male --country NG
```

---

## Login Flow
# Handball Analytics Dashboard

A comprehensive Streamlit dashboard for analyzing handball match data stored in Supabase.

## Features

- 📊 **League Management**: Browse and filter league information
- 🏆 **Team Analytics**: View team statistics and performance
- 👥 **Player Profiles**: Analyze individual player statistics
- 🤾 **Match Analysis**: Detailed match information and action tracking
- 📈 **Interactive Visualizations**: Charts and graphs for data exploration

## Database Structure

The dashboard connects to a Supabase database with the following tables:

- **leagues**: Competition information (name, group, season)
- **teams**: Team profiles
- **players**: Player information linked to teams
- **matches**: Match results with home/away scores
- **player_stats**: Detailed player performance metrics per match
- **actions**: Chronological match events and actions

## Setup

### Prerequisites

- Python 3.8+
- Supabase account with a configured database
- The SQL schema from `src/sql/create_tables.sql` applied to your Supabase database

### Installation

1. Clone this repository:

```bash
git clone <repository-url>
cd hb_data_analyst_v2
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure secrets:

   **For local development:**

   - Option A: Create a `.env` file (recommended for scripts)

     ```bash
     cp .env.example .env
     ```

     Then edit `.env` and add your Supabase credentials

   - Option B: Create `.streamlit/secrets.toml` (recommended for dashboard)
     ```bash
     cp .streamlit/secrets.toml.example .streamlit/secrets.toml
     ```
     Then edit `.streamlit/secrets.toml` and add your Supabase credentials

   **For Streamlit Cloud deployment:**

   - Go to https://share.streamlit.io/
   - Select your app → Settings → Secrets
   - Add your credentials in TOML format:
     ```toml
     SUPABASE_URL = "https://your-project.supabase.co"
     SUPABASE_KEY = "your_supabase_anon_key"
     ```

4. Set up your Supabase database:
   - Run the SQL script in `src/sql/create_tables.sql` in your Supabase SQL Editor
   - This will create all necessary tables and indexes

### Running the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`

## Project Structure

```
hb_data_analyst_v2/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── README.md                  # This file
└── src/
    ├── config.py              # Configuration management
    ├── database.py            # Supabase connection and queries
    ├── pages/                 # Streamlit pages
    │   └── 1_📊_Leagues.py   # Leagues page
    ├── scripts/
    │   └── read-match.py      # Match data processing
    └── sql/
        └── create_tables.sql  # Database schema
```

## Usage

1. **Home Page**: Overview of your handball data with quick statistics
2. **Leagues Page**: Browse and filter league information by season and group
3. _More pages coming soon..._

## Development

To add new pages:

1. Create a new Python file in `src/pages/` with the naming convention `N_🎯_PageName.py`
2. The number determines the order in the sidebar
3. Use the emoji before the page name for visual appeal

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
